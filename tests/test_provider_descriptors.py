from app.connectors.providers import PROVIDERS


def test_provider_descriptors_never_claim_unconfigured_oauth():
    assert PROVIDERS
    assert all(provider.oauth_ready is False for provider in PROVIDERS)


def test_paypal_descriptor_exposes_only_declared_capabilities():
    paypal = next(provider for provider in PROVIDERS if provider.key == "paypal")
    assert "subscriptions" in {cap.value for cap in paypal.capabilities}
    assert "recurring_charges" in {cap.value for cap in paypal.capabilities}
