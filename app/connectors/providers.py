"""Safe provider descriptors for the Connected Accounts UI.

These descriptors advertise capabilities only. A provider is not considered
connected until a real OAuth adapter is configured and completes its callback.
"""

from dataclasses import dataclass

from .base import ConnectorCapability


@dataclass(frozen=True)
class ProviderDescriptor:
    key: str
    name: str
    description: str
    capabilities: frozenset[ConnectorCapability]
    oauth_ready: bool = False


PROVIDERS = (
    ProviderDescriptor(
        key="paypal",
        name="PayPal",
        description="חיובים ומנויים דרך חשבון PayPal, בכפוף להרשאות API.",
        capabilities=frozenset({ConnectorCapability.SUBSCRIPTIONS, ConnectorCapability.RECURRING_CHARGES}),
    ),
    ProviderDescriptor(
        key="google",
        name="Google",
        description="זיהוי חשבון בלבד. אין API צרכני כללי לקריאת כל המנויים.",
        capabilities=frozenset(),
    ),
    ProviderDescriptor(
        key="microsoft",
        name="Microsoft",
        description="חיבור יופעל רק כאשר API צרכני מתאים יהיה מוגדר.",
        capabilities=frozenset(),
    ),
    ProviderDescriptor(
        key="amazon",
        name="Amazon",
        description="חיבור יופעל רק כאשר API צרכני מתאים יהיה מוגדר.",
        capabilities=frozenset(),
    ),
)
