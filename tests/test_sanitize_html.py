from __future__ import annotations

from app.ingest import sanitize_html


def test_strips_style_tag_and_its_css_text():
    raw = "<style>:root { color-scheme: light dark; } p { margin: 0; }</style><p>Hello</p>"
    assert sanitize_html(raw) == "<p>Hello</p>"


def test_strips_script_tag_and_its_js_text():
    raw = "<script>var x = 1;</script><p>Hello</p>"
    assert sanitize_html(raw) == "<p>Hello</p>"


def test_keeps_allowed_tags_and_drops_disallowed_wrapper():
    raw = '<div><h2>Title</h2><p>Body <a href="https://x.test">link</a></p></div>'
    assert (
        sanitize_html(raw)
        == '<h2>Title</h2><p>Body <a href="https://x.test" rel="noreferrer">link</a></p>'
    )


def test_drops_inline_style_attribute():
    raw = '<p style="color:red">Hello</p>'
    assert sanitize_html(raw) == "<p>Hello</p>"
