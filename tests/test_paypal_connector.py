from app.connectors.paypal import PayPalConnector


def test_paypal_connector_declares_supported_capabilities():
    connector = PayPalConnector()
    assert connector.key == "paypal"
    assert "subscriptions" in {cap.value for cap in connector.capabilities}
    assert "recurring_charges" in {cap.value for cap in connector.capabilities}


def test_paypal_scan_requires_authorization():
    result = PayPalConnector().scan("")
    assert result.connected is False
    assert result.status == "authorization_required"


def test_paypal_does_not_fake_authorization_url():
    try:
        PayPalConnector().authorization_url("state")
    except NotImplementedError as exc:
        assert "configured" in str(exc)
    else:
        raise AssertionError("unconfigured provider must not return a fake OAuth URL")
