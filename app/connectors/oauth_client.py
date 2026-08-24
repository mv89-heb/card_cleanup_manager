"""Safe OAuth client configuration primitives.

Provider adapters supply their own authorization/token endpoints and scopes.
No client secrets or tokens are stored in source code.
"""

from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class OAuthClientConfig:
    provider: str
    authorization_endpoint: str
    client_id_env: str
    redirect_uri_env: str
    scopes: tuple[str, ...]

    def authorization_url(self, state: str, client_id: str, redirect_uri: str) -> str:
        if not client_id or not redirect_uri:
            raise ValueError("OAuth client_id and redirect_uri are required")
        query = urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        })
        return f"{self.authorization_endpoint}?{query}"
