"""Google account connector metadata.

Important: Google's documented consumer OAuth APIs do not expose a general
personal subscriptions/payments listing. The Android Publisher API is for app
developers and their Play apps, not a consumer's purchase history. This
connector therefore reports billing discovery as unsupported rather than
pretending OAuth grants access to it.
"""

from .base import ConnectorCapability, ConnectorResult

GOOGLE_OAUTH_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_SCOPES = ("openid", "email", "profile")


class GoogleConnector:
    key = "google"
    display_name = "Google"
    capabilities = frozenset()

    def authorization_url(self, state: str, client_id: str, redirect_uri: str) -> str:
        from urllib.parse import urlencode

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{GOOGLE_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"

    def scan(self, access_token: str) -> ConnectorResult:
        if not access_token:
            return ConnectorResult(
                provider=self.key,
                connected=False,
                status="not_connected",
                message="Google account is not connected.",
            )
        return ConnectorResult(
            provider=self.key,
            connected=True,
            status="billing_unavailable",
            message=(
                "Google account connected, but Google does not expose a general "
                "consumer subscriptions/payments listing through this OAuth scope."
            ),
        )
