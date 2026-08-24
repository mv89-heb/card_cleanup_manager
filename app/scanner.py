from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

SCAN_KEYWORDS = {
    "subscription": ("subscription", "membership", "plan", "renewal", "מנוי"),
    "billing": ("billing", "payment", "invoice", "receipt", "חיוב", "תשלום"),
    "cancel": ("cancel", "cancellation", "unsubscribe", "ביטול"),
}


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        self._in_title = tag.lower() == "title"

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        self.text_parts.append(text)
        if self._in_title:
            self.title_parts.append(text)


@dataclass(frozen=True)
class ScanResult:
    url: str
    status: str
    http_status: int | None
    title: str
    findings: tuple[str, ...]
    message: str


def _is_public_hostname(hostname: str) -> bool:
    try:
        addresses = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    for item in addresses:
        address = ipaddress.ip_address(item[4][0])
        if not address.is_global:
            return False
    return True


def validate_scan_target(url: str) -> str:
    value = url.strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("ניתן לסרוק רק כתובות HTTPS תקינות")
    if parsed.username or parsed.password:
        raise ValueError("כתובת הסריקה אינה יכולה להכיל פרטי התחברות")
    if not _is_public_hostname(parsed.hostname):
        raise ValueError("ניתן לסרוק רק אתר ציבורי")
    return value


def _findings(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    return tuple(label for label, keywords in SCAN_KEYWORDS.items() if any(k.lower() in lowered for k in keywords))


def scan_url(url: str, timeout: float = 8.0) -> ScanResult:
    url = validate_scan_target(url)
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent": "CardCleanupManager/1.0"}) as client:
            response = client.get(url)
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return ScanResult(url, "unsupported", response.status_code, "", (), "האתר לא החזיר עמוד HTML לסריקה.")
        parser = _TextParser()
        parser.feed(response.text[:2_000_000])
        title = " ".join(parser.title_parts)[:160]
        text = " ".join(parser.text_parts)[:500_000]
        findings = _findings(text)
        if response.status_code in (401, 403):
            return ScanResult(url, "login_required", response.status_code, title, findings, "האתר דורש הרשאה או חסם את הבקשה. לא נעשה ניסיון לעקוף זאת.")
        if response.status_code >= 400:
            return ScanResult(url, "error", response.status_code, title, findings, f"האתר החזיר HTTP {response.status_code}.")
        if findings:
            return ScanResult(url, "found", response.status_code, title, findings, "נמצאו אינדיקציות הקשורות למנוי או חיוב בעמוד הציבורי.")
        return ScanResult(url, "no_findings", response.status_code, title, (), "לא נמצאו אינדיקציות בעמוד שנסרק.")
    except httpx.TimeoutException:
        return ScanResult(url, "timeout", None, "", (), "הסריקה חרגה מזמן ההמתנה.")
    except (httpx.HTTPError, ValueError, OSError) as exc:
        return ScanResult(url, "error", None, "", (), f"הסריקה נכשלה: {type(exc).__name__}.")
