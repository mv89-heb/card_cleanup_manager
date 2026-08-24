"""Connector registry; concrete providers are added independently."""

from dataclasses import dataclass

from .base import Connector, ConnectorCapability


@dataclass(frozen=True)
class ConnectorDescriptor:
    key: str
    display_name: str
    capabilities: frozenset[ConnectorCapability]
    configured: bool = False


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, Connector] = {}

    def register(self, connector: Connector) -> None:
        if connector.key in self._connectors:
            raise ValueError(f"Connector already registered: {connector.key}")
        self._connectors[connector.key] = connector

    def get(self, key: str) -> Connector | None:
        return self._connectors.get(key)

    def descriptors(self) -> list[ConnectorDescriptor]:
        return [
            ConnectorDescriptor(
                key=connector.key,
                display_name=connector.display_name,
                capabilities=connector.capabilities,
            )
            for connector in self._connectors.values()
        ]


def build_default_registry() -> ConnectorRegistry:
    # Provider implementations are intentionally not registered until their
    # OAuth configuration exists. This prevents the UI from implying a live
    # integration that cannot safely authenticate yet.
    return ConnectorRegistry()
