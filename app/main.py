from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "card_cleanup.db"

engine = create_engine(f"sqlite:///{DB}", connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(40))
    last4: Mapped[str] = mapped_column(String(4))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80), default="Other")
    payment_last4: Mapped[str] = mapped_column(String(4), default="")
    subscription_status: Mapped[str] = mapped_column(String(40), default="Unknown")
    cleanup_status: Mapped[str] = mapped_column(String(40), default="Needs review")
    billing_url: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Audit(Base):
    __tablename__ = "audit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(engine)

app = FastAPI(title="Card Cleanup Manager")
templates = Jinja2Templates(directory=str(BASE / "app" / "templates"))

SEED_SERVICES = [
    ("Claude", "AI", "2689", "Canceled", "Support required", "https://support.claude.com/en/"),
    ("Google", "Account", "", "Unknown", "Needs review", "https://myaccount.google.com/payments-and-subscriptions"),
    ("Microsoft", "Account", "", "Unknown", "Needs review", "https://account.microsoft.com/services"),
    ("PayPal", "Payments", "", "Unknown", "Needs review", "https://www.paypal.com/myaccount/wallet"),
    ("Amazon", "Shopping", "", "Unknown", "Needs review", "https://www.amazon.com/cpe/yourpayments"),
]

def seed():
    with Session(engine) as s:
        if s.query(Service).count() == 0:
            for row in SEED_SERVICES:
                s.add(Service(name=row[0], category=row[1], payment_last4=row[2],
                               subscription_status=row[3], cleanup_status=row[4], billing_url=row[5]))
            s.commit()
seed()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    with Session(engine) as s:
        cards = s.query(Card).all()
        services = s.query(Service).order_by(Service.name).all()
        audits = s.query(Audit).order_by(Audit.created_at.desc()).limit(10).all()
    return templates.TemplateResponse("index.html", {
        "request": request, "cards": cards, "services": services, "audits": audits
    })

@app.post("/cards")
def add_card(brand: str = Form(...), last4: str = Form(...)):
    last4 = last4.strip()
    if len(last4) != 4 or not last4.isdigit():
        return RedirectResponse("/", status_code=303)
    with Session(engine) as s:
        s.add(Card(brand=brand.strip(), last4=last4))
        s.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/services/{service_id}/status")
def update_status(service_id: int, status: str = Form(...)):
    with Session(engine) as s:
        service = s.get(Service, service_id)
        if service:
            service.cleanup_status = status
            s.add(Audit(service=service.name, action=f"Status → {status}"))
            s.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/services")
def add_service(name: str = Form(...), category: str = Form("Other"),
                last4: str = Form(""), billing_url: str = Form("")):
    with Session(engine) as s:
        s.add(Service(name=name.strip(), category=category.strip(),
                      payment_last4=last4.strip()[-4:] if last4.strip().isdigit() else "",
                      billing_url=billing_url.strip()))
        s.commit()
    return RedirectResponse("/", status_code=303)
