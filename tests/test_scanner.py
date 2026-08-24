from app.scanner import validate_scan_target


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
