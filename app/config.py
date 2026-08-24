from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = Path(os.getenv("CARD_CLEANUP_DB", str(BASE_DIR / "card_cleanup.db"))).expanduser()
APP_ENV = os.getenv("APP_ENV", "development").lower()
CSRF_COOKIE = "ccm_csrf"
CSRF_MAX_AGE = 60 * 60 * 8
MAX_NAME_LENGTH = 120
MAX_CATEGORY_LENGTH = 80
MAX_BRAND_LENGTH = 40
MAX_URL_LENGTH = 500
MAX_NOTES_LENGTH = 2000

# Local-first by default. Set CARD_CLEANUP_ALLOWED_HOSTS when exposing the app.
DEFAULT_ALLOWED_HOSTS = "127.0.0.1,localhost,[::1]"
ALLOWED_HOSTS = [
    item.strip() for item in os.getenv("CARD_CLEANUP_ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS).split(",")
    if item.strip()
]

# The application is intentionally not an authentication system in this MVP.
# A deployment that is reachable by untrusted users should put authentication in front of it.
