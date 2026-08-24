from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ux_assets_are_referenced():
    html = (ROOT / "app/templates/index.html").read_text(encoding="utf-8")
    assert html.count('/static/app.css') == 1
    assert '/static/ux.css' not in html
    assert html.count('/static/ux.js') == 1


def test_ux_js_has_no_external_dependencies():
    js = (ROOT / "app/static/ux.js").read_text(encoding="utf-8")
    assert "http://" not in js
    assert "https://" not in js


def test_template_keeps_csrf_on_post_forms():
    html = (ROOT / "app/templates/index.html").read_text(encoding="utf-8")
    assert html.count('method="post"') == html.count('name="csrf_token"')


def test_css_keeps_core_ux_selectors():
    css = (ROOT / "app/static/app.css").read_text(encoding="utf-8")
    for selector in ('.panel', '.service-row', '.ux-tools', '.filter-pill', '.empty', '.credit-card'):
        assert selector in css
