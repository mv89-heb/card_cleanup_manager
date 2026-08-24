# Card Cleanup Manager

Local-first MVP for finding services that may have stored a payment card and tracking cleanup requests.

## Safety model
- Does not store full card numbers.
- Stores only brand + last four digits.
- No password collection.
- No automated login to third-party sites.
- Email scanning is designed around OAuth connectors and can be added without storing mailbox passwords.
- Third-party deletion is always user-confirmed.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Current MVP
- Local SQLite database
- Card records with last-four only
- Service inventory
- Cleanup status tracking
- Service action links
- Audit log
- Dashboard
