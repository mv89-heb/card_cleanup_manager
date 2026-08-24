"""Local connected-account state without credentials or provider secrets."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConnectedAccountView:
    provider: str
    name: str
    status: str
    status_he: str
    detail: str
    connected_at: datetime | None = None


STATUS_HE = {
    "not_connected": "לא מחובר",
    "connected": "מחובר",
    "reauthorize": "נדרשת הרשאה מחדש",
    "unsupported": "אין חיבור זמין",
}
