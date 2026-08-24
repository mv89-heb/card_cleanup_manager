from app.scanner import _findings, _looks_like_login_page, validate_scan_target


def test_scan_target_requires_https():
    for url in ("http://example.com", "javascript:alert(1)", "example.com"):
        try:
            validate_scan_target(url)
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe scan target accepted")


def test_scan_target_rejects_embedded_credentials():
    try:
        validate_scan_target("https://user:password@example.com/billing")
    except ValueError:
        pass
    else:
        raise AssertionError("credentials in URL accepted")


def test_scan_target_rejects_localhost():
    try:
        validate_scan_target("https://localhost/billing")
    except ValueError:
        pass
    else:
        raise AssertionError("local host accepted")


def test_login_page_is_not_reported_as_billing_finding():
    assert _looks_like_login_page("Sign in to your account", "Email Password Sign in", "https://example.com/login")


def test_generic_cancel_does_not_create_false_positive():
    assert _findings("Help center article: how to cancel an account") == ()


def test_billing_context_is_reported():
    assert _findings("Your subscription renewal and billing payment") == ("subscription", "billing")
