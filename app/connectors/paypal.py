"""PayPal capability descriptor.

PayPal exposes REST APIs for transaction search and subscriptions, but the
available APIs and permissions depend on the integration/account context.
This connector therefore advertises capabilities only after explicit
configuration; it never treats a public wallet page as proof of account data.
"""

from .base import ConnectorCapability, ConnectorResult


class PayPalConnector:
    key = "paypal"
    display_name = "PayPal"
    capabilities = frozenset(
        {
            ConnectorCapability.RECURRING_CHARGES,
            ConnectorCapability.SUBSCRIPTIONS,
        }
    )

    def authorization_url(self, state: str) -> str:
        raise NotImplementedError(
            "PayPal OAuth requires configured application credentials and an "
            "approved redirect flow; configure the provider before enabling it."
        )

    def scan(self, access_token: str) -> ConnectorResult:
        if not access_token:
            return ConnectorResult(
                provider=self.key,
                connected=False,
                status="authorization_required",
                message="A configured PayPal authorization is required before scanning.",
            )
        raise NotImplementedError(
            "PayPal API access must be implemented with configured provider credentials."
        )
