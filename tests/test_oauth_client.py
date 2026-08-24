from app.connectors.oauth_client import OAuthClientConfig


def test_authorization_url_contains_required_oauth_parameters():
    config = OAuthClientConfig(
        provider="example",
        authorization_endpoint="https://provider.example/oauth/authorize",
        client_id_env="EXAMPLE_CLIENT_ID",
        redirect_uri_env="EXAMPLE_REDIRECT_URI",
        scopes=("subscriptions.read",),
    )
    url = config.authorization_url("state-123", "client-1", "https://app.example/callback")
    assert "response_type=code" in url
    assert "state=state-123" in url
    assert "client_id=client-1" in url
    assert "subscriptions.read" in url


def test_authorization_url_rejects_missing_client_configuration():
    config = OAuthClientConfig(
        provider="example",
        authorization_endpoint="https://provider.example/oauth/authorize",
        client_id_env="CLIENT_ID",
        redirect_uri_env="REDIRECT_URI",
        scopes=(),
    )
    try:
        config.authorization_url("state", "", "https://app.example/callback")
    except ValueError:
        pass
    else:
        raise AssertionError("missing client id should fail")
