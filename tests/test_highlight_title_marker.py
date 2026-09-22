from __future__ import annotations

import pytest
from test_app import _save_highlight
from test_highlight_browser import (
    ORIGIN,
    _opened,
    _select_and_save,
    browser_page,  # noqa: F401 - pytest fixture
)

from app import db as dbmod

TEXT_BODY = (
    "<p>One player is paid to grow the fire. The other is paid to put it out.</p>"
    "<p>The architecture follows the economics.</p>"
)


def _set_titles(tmp_path, highlight_id, section=None, subsection=None):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        if section:
            dbmod.set_highlight_section_title(conn, highlight_id, section)
        if subsection:
            dbmod.set_highlight_subsection_title(conn, highlight_id, subsection)
        conn.commit()
    finally:
        conn.close()


def _markers(page):
    """Each marker's highlight id and whether the highlight's own first mark
    follows it directly."""
    return page.eval_on_selector_all(
        ".article-body .hl-title-marker",
        """els => els.map(el => {
          const next = el.nextElementSibling;
          return [
            el.dataset.highlightId,
            !!next && next.matches("mark.hl") &&
              next.dataset.highlightId === el.dataset.highlightId,
          ];
        })""",
    )


@pytest.mark.parametrize(
    ("section", "subsection"),
    [
        pytest.param("Economics", None, id="section"),
        pytest.param(None, "Incentives", id="subsection"),
    ],
)
def test_a_titled_highlight_gets_a_marker_before_it(
    monkeypatch, tmp_path, browser_page, section, subsection  # noqa: F811
):
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        titled = _save_highlight(client, item_id, 0, 0, 0, 36, "One player is paid to grow the fire.")
        _save_highlight(client, item_id, 1, 0, 1, 16, "The architecture")
        _set_titles(tmp_path, titled, section, subsection)
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        assert _markers(browser_page) == [[str(titled), True]]


def test_an_untitled_highlight_has_no_marker(monkeypatch, tmp_path, browser_page):  # noqa: F811
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        _save_highlight(client, item_id, 0, 0, 0, 36, "One player is paid to grow the fire.")
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        assert _markers(browser_page) == []


def test_the_marker_does_not_shift_later_highlights_in_the_block(
    monkeypatch, tmp_path, browser_page  # noqa: F811
):
    # Highlights are stored as character offsets into a block's text; a
    # marker that added text would move every later highlight in the block.
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        titled = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _save_highlight(client, item_id, 0, 37, 0, 46, "The other")
        _set_titles(tmp_path, titled, "Economics")
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        texts = browser_page.eval_on_selector_all(
            ".article-body mark.hl", "els => els.map(el => el.textContent)"
        )
        assert texts == ["One player", "The other"]


def test_merging_into_a_titled_highlight_keeps_one_marker(
    monkeypatch, tmp_path, browser_page  # noqa: F811
):
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        titled = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _set_titles(tmp_path, titled, "Economics")
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        # The saved highlight already wraps "One player" in a mark: select
        # from inside it to the end of the sentence that follows it.
        mark = "b[0].querySelector('mark.hl')"
        _select_and_save(
            browser_page, f"{mark}.firstChild, 4", f"{mark}.nextSibling, 26"
        )
        browser_page.wait_for_function(
            f"!document.querySelector('mark.hl[data-highlight-id=\"{titled}\"]')"
        )
        markers = _markers(browser_page)
        assert len(markers) == 1 and markers[0][1] is True


def test_tapping_the_marker_opens_the_highlight(monkeypatch, tmp_path, browser_page):  # noqa: F811
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        titled = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _set_titles(tmp_path, titled, "Economics")
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        browser_page.click(".article-body .hl-title-marker", timeout=5000)
        browser_page.wait_for_url(f"**/items/{item_id}/highlights/{titled}")
