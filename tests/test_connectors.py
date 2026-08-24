from app.connectors.base import ConnectorCapability, ConnectorResult
from app.connectors.registry import ConnectorRegistry


class FakeConnector:
    key = "fake"
    display_name = "Fake"
    capabilities = frozenset({ConnectorCapability.SUBSCRIPTIONS})

    def authorization_url(self, state: str) -> str:
        return f"https://example.test/oauth?state={state}"

    def scan(self, access_token: str) -> ConnectorResult:
        return ConnectorResult(provider=self.key, connected=True, status="ok", message="ok")


def test_registry_registers_and_lists_descriptor():
    registry = ConnectorRegistry()
    registry.register(FakeConnector())
    descriptor = registry.descriptors()[0]
    assert descriptor.key == "fake"
    assert ConnectorCapability.SUBSCRIPTIONS in descriptor.capabilities


def test_registry_rejects_duplicate_key():
    registry = ConnectorRegistry()
    registry.register(FakeConnector())
    try:
        registry.register(FakeConnector())
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("duplicate connector should fail")
