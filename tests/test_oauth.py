from app.connectors.oauth import create_oauth_state, is_oauth_state_valid


def test_oauth_state_is_valid_until_expiry():
    state = create_oauth_state(ttl_seconds=60)
    assert is_oauth_state_valid(state, now=state.created_at + 59)
    assert not is_oauth_state_valid(state, now=state.expires_at)


def test_oauth_state_is_unique():
    first = create_oauth_state()
    second = create_oauth_state()
    assert first.value != second.value
