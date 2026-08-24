"""Provider-neutral connector contracts.

Connectors never receive user passwords. Authenticated providers should use an
OAuth flow and return normalized, minimal data through ConnectorResult.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ConnectorCapability(str, Enum):
    SUBSCRIPTIONS = "subscriptions"
    RECURRING_CHARGES = "recurring_charges"
    PAYMENT_METHODS = "payment_methods"


@dataclass(frozen=True)
class ConnectorResult:
    provider: str
    connected: bool
    status: str
    message: str
    subscriptions: list[dict] = field(default_factory=list)
    recurring_charges: list[dict] = field(default_factory=list)
    payment_methods: list[dict] = field(default_factory=list)


class Connector(Protocol):
    key: str
    display_name: str
    capabilities: frozenset[ConnectorCapability]

    def authorization_url(self, state: str) -> str: ...

    def scan(self, access_token: str) -> ConnectorResult: ...
