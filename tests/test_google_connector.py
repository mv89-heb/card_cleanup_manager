from app.connectors.google import GOOGLE_SCOPES, GoogleConnector


def test_google_authorization_url_contains_required_oauth_parameters():
    url = GoogleConnector().authorization_url(
        state="test-state",
        client_id="client-id",
        redirect_uri="http://localhost/callback",
    )
    assert "client-id" in url
    assert "test-state" in url
    assert "openid" in url
    assert "email" in url
    assert "profile" in url
    assert set(GOOGLE_SCOPES) == {"openid", "email", "profile"}


def test_google_connector_does_not_claim_consumer_billing_access():
    result = GoogleConnector().scan("token")
    assert result.connected is True
    assert result.status == "billing_unavailable"
    assert result.subscriptions == []
    assert result.recurring_charges == []
    assert result.payment_methods == []


def test_google_connector_handles_missing_token():
    result = GoogleConnector().scan("")
    assert result.connected is False
    assert result.status == "not_connected"
