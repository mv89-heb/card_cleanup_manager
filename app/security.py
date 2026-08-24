import secrets
from urllib.parse import urlparse

from fastapi import HTTPException, Request
from starlette.responses import Response

from .config import CSRF_COOKIE, CSRF_MAX_AGE


def get_or_create_csrf_token(request: Request) -> str:
    return request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(32)


def ensure_csrf_cookie(request: Request, response: Response, token: str | None = None) -> str:
    existing = request.cookies.get(CSRF_COOKIE)
    token = existing or token or secrets.token_urlsafe(32)
    if not existing:
        response.set_cookie(
            CSRF_COOKIE,
            token,
            max_age=CSRF_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=request.url.scheme == "https",
        )
    return token


def validate_csrf(request: Request, token: str) -> None:
    cookie_token = request.cookies.get(CSRF_COOKIE)
    if not cookie_token or not token or not secrets.compare_digest(cookie_token, token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def validate_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Billing URL must use http or https")
    if parsed.username or parsed.password:
        raise ValueError("Billing URL cannot contain embedded credentials")
    return value
