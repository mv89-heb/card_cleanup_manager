from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import (
    ALLOWED_HOSTS,
    MAX_BRAND_LENGTH,
    MAX_CATEGORY_LENGTH,
    MAX_NAME_LENGTH,
    MAX_NOTES_LENGTH,
    MAX_URL_LENGTH,
)
from .db import get_session, init_db
from .models import Audit, Card, Service
from .security import ensure_csrf_cookie, get_or_create_csrf_token, validate_csrf, validate_url

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

SEED_SERVICES = [
    ("Claude", "AI", "2689", "Canceled", "Support required", "https://support.claude.com/en/"),
    ("Google", "Account", "", "Unknown", "Needs review", "https://myaccount.google.com/payments-and-subscriptions"),
    ("Microsoft", "Account", "", "Unknown", "Needs review", "https://account.microsoft.com/services"),
    ("PayPal", "Payments", "", "Unknown", "Needs review", "https://www.paypal.com/myaccount/wallet"),
    ("Amazon", "Shopping", "", "Unknown", "Needs review", "https://www.amazon.com/cpe/yourpayments"),
]
ALLOWED_CLEANUP_STATUSES = {"Needs review", "Requested", "Removed"}
STATUS_FLOW = {"Needs review": "Requested", "Requested": "Removed", "Removed": "Needs review"}


def seed_services() -> None:
    with get_session() as session:
        if session.scalar(select(Service.id).limit(1)) is not None:
            return
        for name, category, last4, subscription_status, cleanup_status, billing_url in SEED_SERVICES:
            session.add(
                Service(
                    name=name,
                    category=category,
                    payment_last4=last4,
                    subscription_status=subscription_status,
                    cleanup_status=cleanup_status,
                    billing_url=billing_url,
                )
            )
        session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_services()
    yield


app = FastAPI(title="Card Cleanup Manager", version="1.0.0", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)


def clean_text(value: str, maximum: int, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} is required")
    if len(value) > maximum:
        raise ValueError(f"{field} is too long")
    return value


def clean_last4(value: str, required: bool = False) -> str:
    value = value.strip()
    if not value:
        if required:
            raise ValueError("Last four digits are required")
        return ""
    if len(value) != 4 or not value.isdigit():
        raise ValueError("Last four digits must contain exactly 4 digits")
    return value


def safe_redirect() -> RedirectResponse:
    return RedirectResponse("/", status_code=303)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    with get_session() as session:
        cards = session.scalars(select(Card).order_by(Card.created_at.desc())).all()
        services = session.scalars(select(Service).order_by(Service.name)).all()
        audits = session.scalars(select(Audit).order_by(Audit.created_at.desc()).limit(20)).all()

    csrf_token = get_or_create_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "cards": cards,
            "services": services,
            "audits": audits,
            "csrf_token": csrf_token,
        },
    )
    ensure_csrf_cookie(request, response, csrf_token)
    return response


@app.post("/cards")
def add_card(request: Request, csrf_token: str = Form(...), brand: str = Form(...), last4: str = Form(...)):
    validate_csrf(request, csrf_token)
    try:
        brand = clean_text(brand, MAX_BRAND_LENGTH, "Brand")
        last4 = clean_last4(last4, required=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with get_session() as session:
        session.add(Card(brand=brand, last4=last4))
        session.commit()
    return safe_redirect()


@app.post("/services")
def add_service(request: Request, csrf_token: str = Form(...), name: str = Form(...),
                category: str = Form("Other"), last4: str = Form(""),
                billing_url: str = Form(""), notes: str = Form("")):
    validate_csrf(request, csrf_token)
    try:
        name = clean_text(name, MAX_NAME_LENGTH, "Service name")
        category = clean_text(category or "Other", MAX_CATEGORY_LENGTH, "Category")
        last4 = clean_last4(last4)
        billing_url = validate_url(billing_url[:MAX_URL_LENGTH])
        notes = notes.strip()
        if len(notes) > MAX_NOTES_LENGTH:
            raise ValueError("Notes are too long")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with get_session() as session:
        session.add(Service(name=name, category=category, payment_last4=last4, billing_url=billing_url, notes=notes))
        session.commit()
    return safe_redirect()


@app.post("/services/{service_id}/status")
def update_status(service_id: int, request: Request, csrf_token: str = Form(...), status: str = Form(...)):
    validate_csrf(request, csrf_token)
    if status not in ALLOWED_CLEANUP_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid cleanup status")

    with get_session() as session:
        service = session.get(Service, service_id)
        if service is None:
            raise HTTPException(status_code=404, detail="Service not found")
        service.cleanup_status = status
        session.add(Audit(service=service.name, action=f"Status → {status}"))
        session.commit()
    return safe_redirect()


@app.post("/services/{service_id}/cycle")
def cycle_status(service_id: int, request: Request, csrf_token: str = Form(...)):
    validate_csrf(request, csrf_token)
    with get_session() as session:
        service = session.get(Service, service_id)
        if service is None:
            raise HTTPException(status_code=404, detail="Service not found")
        next_status = STATUS_FLOW.get(service.cleanup_status, "Needs review")
        service.cleanup_status = next_status
        session.add(Audit(service=service.name, action=f"Status → {next_status}"))
        session.commit()
    return safe_redirect()


@app.get("/health")
def health():
    return {"status": "ok"}
