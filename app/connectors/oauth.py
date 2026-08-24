"""Provider-neutral OAuth state helpers.

This module intentionally does not perform provider authentication. It provides
safe, expiring state values that concrete OAuth adapters can use later.
"""

from dataclasses import dataclass
from secrets import token_urlsafe
import time


@dataclass(frozen=True)
class OAuthState:
    value: str
    created_at: float
    expires_at: float


def create_oauth_state(ttl_seconds: int = 600) -> OAuthState:
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")
    now = time.time()
    return OAuthState(token_urlsafe(32), now, now + ttl_seconds)


def is_oauth_state_valid(state: OAuthState, now: float | None = None) -> bool:
    current = time.time() if now is None else now
    return bool(state.value) and current < state.expires_at
