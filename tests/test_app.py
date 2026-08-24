import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("test_card_cleanup.db")
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["CARD_CLEANUP_DB"] = str(TEST_DB)
os.environ["CARD_CLEANUP_ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1,[::1]"

from fastapi.testclient import TestClient

from app.main import app


def csrf_from_html(html: str) -> str:
    marker = 'name="csrf_token" value="'
    start = html.index(marker) + len(marker)
    return html[start:html.index('"', start)]


def test_healthcheck():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_sets_csrf_cookie_and_renders_seed_data():
    with TestClient(app) as client:
        response = client.get("/")
        token = csrf_from_html(response.text)
    assert response.status_code == 200
    assert "Claude" in response.text
    assert "ccm_csrf" in response.cookies
    assert token
    assert token == response.cookies["ccm_csrf"]


def test_post_without_csrf_is_rejected():
    with TestClient(app) as client:
        client.get("/")
        response = client.post("/cards", data={"brand": "Visa", "last4": "1234"})
    assert response.status_code == 422


def test_add_card_with_csrf_succeeds():
    with TestClient(app) as client:
        page = client.get("/")
        token = csrf_from_html(page.text)
        response = client.post(
            "/cards",
            data={"csrf_token": token, "brand": "Visa", "last4": "1234"},
        )
        assert response.status_code == 303
        dashboard = client.get("/")
        assert "Visa" in dashboard.text


def test_invalid_billing_url_is_rejected():
    with TestClient(app) as client:
        page = client.get("/")
        token = csrf_from_html(page.text)
        response = client.post(
            "/services",
            data={
                "csrf_token": token,
                "name": "Example",
                "category": "Other",
                "last4": "",
                "billing_url": "javascript:alert(1)",
            },
        )
    assert response.status_code == 400


TEST_DB.unlink(missing_ok=True)
