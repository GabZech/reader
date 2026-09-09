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


def test_table_layout_sections_get_separate_paragraphs():
    # TLDR-style newsletters lay each item out in a <table>/<div> instead of
    # <p> tags. Dropping those wrappers without a paragraph break used to run
    # every section's text together.
    raw = (
        "<table><tr><td>"
        "<div>Headline one</div>"
        "<div>Body text one.</div>"
        "</td></tr></table>"
        "<table><tr><td>"
        "<div>Headline two</div>"
        "<div>Body text two.</div>"
        "</td></tr></table>"
    )
    assert sanitize_html(raw) == (
        "<p>Headline one</p><p>Body text one.</p>"
        "<p>Headline two</p><p>Body text two.</p>"
    )


def test_inline_bold_style_becomes_strong():
    raw = '<div><span style="font-weight:700">Headline</span></div>'
    assert sanitize_html(raw) == "<p><strong>Headline</strong></p>"


def test_alternate_heading_and_bold_tags_are_aliased():
    raw = "<h1>Title</h1><h4>Sub</h4><b>Bold</b><i>Italic</i>"
    assert sanitize_html(raw) == (
        "<h2>Title</h2><h3>Sub</h3><p><strong>Bold</strong><em>Italic</em></p>"
    )
