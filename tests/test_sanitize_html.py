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


def test_keeps_http_https_and_mailto_links():
    raw = (
        '<p><a href="http://a.test">a</a> <a href="https://b.test/x?y=1">b</a> '
        '<a href="mailto:c@d.test">c</a></p>'
    )
    assert sanitize_html(raw) == (
        '<p><a href="http://a.test" rel="noreferrer">a</a> '
        '<a href="https://b.test/x?y=1" rel="noreferrer">b</a> '
        '<a href="mailto:c@d.test" rel="noreferrer">c</a></p>'
    )


def test_drops_the_target_of_a_link_with_an_unsafe_scheme():
    # The text stays; the href that would run script (or smuggle data) goes.
    for href in (
        "javascript:alert(1)",
        " JavaScript:alert(1)",
        "java\tscript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:msgbox(1)",
    ):
        raw = f'<p>See <a href="{href}">this</a> now</p>'
        assert sanitize_html(raw) == "<p>See <a>this</a> now</p>", href


def test_keeps_relative_and_fragment_links():
    raw = '<p><a href="/about">about</a> <a href="#notes">notes</a></p>'
    assert sanitize_html(raw) == (
        '<p><a href="/about" rel="noreferrer">about</a> '
        '<a href="#notes" rel="noreferrer">notes</a></p>'
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


def test_preserve_tables_keeps_a_real_content_table_intact():
    # A captured article's table is usually real tabular content, unlike a
    # newsletter's layout table (above) - preserve_tables keeps its
    # structure instead of flattening it into a run of paragraphs.
    raw = (
        "<table><tr><th>Model</th><th>Score</th></tr>"
        "<tr><td>A</td><td>27%</td></tr></table>"
    )
    assert sanitize_html(raw, preserve_tables=True) == (
        "<table><tr><th>Model</th><th>Score</th></tr>"
        "<tr><td>A</td><td>27%</td></tr></table>"
    )


def test_centering_does_not_leak_past_an_uncentered_nested_wrapper():
    # A newsletter's outermost table is usually centered to position the
    # whole email column on the page, not to center its text. A section
    # further inside, in its own plain (uncentered) wrapper, must not
    # inherit that outer centering just because it's nested within it.
    raw = (
        '<table align="center">'
        "<tr><td><h1>Section</h1><p>Body text.</p></td></tr>"
        "</table>"
    )
    assert sanitize_html(raw) == "<h2>Section</h2><p>Body text.</p>"


def test_inline_bold_style_becomes_strong():
    raw = '<div><span style="font-weight:700">Headline</span></div>'
    assert sanitize_html(raw) == "<p><strong>Headline</strong></p>"


def test_alternate_heading_and_bold_tags_are_aliased():
    raw = "<h1>Title</h1><h4>Sub</h4><b>Bold</b><i>Italic</i>"
    assert sanitize_html(raw) == (
        "<h2>Title</h2><h3>Sub</h3><p><strong>Bold</strong><em>Italic</em></p>"
    )


def test_center_align_attribute_on_dropped_wrapper_carries_to_content():
    # TLDR-style section headers use the deprecated `align="center"`
    # attribute on a <td>/<div> wrapper that gets dropped along with every
    # other attribute, which used to lose the centering entirely.
    raw = '<table><tr><td align="center"><p>Icon</p><h1>Title</h1></td></tr></table><p>Body</p>'
    assert sanitize_html(raw) == (
        '<p style="text-align:center">Icon</p>'
        '<h2 style="text-align:center">Title</h2>'
        "<p>Body</p>"
    )


def test_drops_hidden_preheader_text():
    # Newsletters hide an inbox-preview sentence off screen with
    # display:none (or visibility:hidden) so it's never meant to render.
    raw = (
        '<div style="display:none">Preview sentence for the inbox.</div>'
        "<p>Real body.</p>"
    )
    assert sanitize_html(raw) == "<p>Real body.</p>"


def test_drops_hidden_content_with_nested_tags_and_void_elements():
    # A hidden wrapper's subtree can contain arbitrary nested tags, including
    # void elements like <br> that never get a matching closing tag - both
    # must be fully skipped without breaking the parser's depth tracking for
    # what follows.
    raw = (
        '<div style="display:none">Hidden <b>bold</b> text<br>more<span>x</span></div>'
        "<p>Real body.</p>"
    )
    assert sanitize_html(raw) == "<p>Real body.</p>"


def _icon(name: str) -> str:
    return f'<a href="https://{name}.test"><img src="https://x.test/{name}.png" alt="{name}"></a>'


def _clean_icon(name: str) -> str:
    return (
        f'<a href="https://{name}.test" rel="noreferrer">'
        f'<img src="https://x.test/{name}.png" alt="{name}"></a>'
    )


def test_row_of_icon_cells_stays_on_one_line():
    # A newsletter footer's social buttons are one <td> per icon in a single
    # row. Each cell used to become its own paragraph, stacking the icons in
    # a column instead of the horizontal row the email shows.
    raw = (
        "<table><tr>"
        f'<td align="center">{_icon("facebook")}</td>'
        f'<td align="center">{_icon("instagram")}</td>'
        f'<td align="center">{_icon("youtube")}</td>'
        "</tr></table>"
    )
    assert sanitize_html(raw) == (
        '<p style="text-align:center">'
        f'{_clean_icon("facebook")} {_clean_icon("instagram")} {_clean_icon("youtube")}'
        "</p>"
    )


def test_empty_spacer_cells_do_not_break_an_icon_row():
    raw = (
        "<table><tr>"
        f"<td>{_icon('facebook')}</td><td>&nbsp;</td><td></td>"
        f"<td>{_icon('instagram')}</td>"
        "</tr></table>"
    )
    assert sanitize_html(raw) == (
        f'<p>{_clean_icon("facebook")} {_clean_icon("instagram")}</p>'
    )


def test_icon_row_nested_under_a_logo_row_stays_separate_from_it():
    raw = (
        "<table>"
        '<tr><td><img src="https://x.test/logo.png" alt="logo"></td></tr>'
        "<tr><td><table><tr>"
        f"<td>{_icon('facebook')}</td><td>{_icon('instagram')}</td>"
        "</tr></table></td></tr>"
        "</table>"
    )
    assert sanitize_html(raw) == (
        '<p><img src="https://x.test/logo.png" alt="logo"></p>'
        f'<p>{_clean_icon("facebook")} {_clean_icon("instagram")}</p>'
    )


def test_images_in_separate_rows_stay_stacked():
    # Only cells of one row sit side by side; rows are stacked, so a column of
    # full-width pictures is not squeezed onto one line.
    raw = (
        "<table>"
        '<tr><td><img src="https://x.test/a.png" alt="a"></td></tr>'
        '<tr><td><img src="https://x.test/b.png" alt="b"></td></tr>'
        "</table>"
    )
    assert sanitize_html(raw) == (
        '<p><img src="https://x.test/a.png" alt="a"></p>'
        '<p><img src="https://x.test/b.png" alt="b"></p>'
    )


def test_row_with_text_in_a_cell_keeps_one_paragraph_per_cell():
    raw = (
        "<table><tr>"
        f"<td>{_icon('facebook')}</td><td>Follow us</td>"
        "</tr></table>"
    )
    assert sanitize_html(raw) == (
        f"<p>{_clean_icon('facebook')}</p><p>Follow us</p>"
    )
