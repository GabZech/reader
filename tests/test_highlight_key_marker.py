from __future__ import annotations

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


def _mark_key(tmp_path, highlight_id, section=None):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        dbmod.set_highlight_key(conn, highlight_id, True)
        if section:
            dbmod.set_highlight_section_title(conn, highlight_id, section)
        conn.commit()
    finally:
        conn.close()


def _key_markers(page):
    """Each ★ marker's highlight id and whether the highlight's own first
    mark follows it directly."""
    return page.eval_on_selector_all(
        ".article-body .hl-key-marker",
        """els => els.map(el => {
          const next = el.nextElementSibling;
          return [
            el.dataset.highlightId,
            !!next && next.matches("mark.hl") &&
              next.dataset.highlightId === el.dataset.highlightId,
          ];
        })""",
    )


def test_a_key_highlight_gets_a_star_before_it(monkeypatch, tmp_path, browser_page):  # noqa: F811
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        key = _save_highlight(client, item_id, 0, 0, 0, 36, "One player is paid to grow the fire.")
        _save_highlight(client, item_id, 1, 0, 1, 16, "The architecture")
        _mark_key(tmp_path, key)
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        assert _key_markers(browser_page) == [[str(key), True]]


def test_a_plain_highlight_has_no_star(monkeypatch, tmp_path, browser_page):  # noqa: F811
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        _save_highlight(client, item_id, 0, 0, 0, 36, "One player is paid to grow the fire.")
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        assert _key_markers(browser_page) == []


def test_a_titled_key_highlight_shows_the_section_sign_before_the_star(
    monkeypatch, tmp_path, browser_page  # noqa: F811
):
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        key = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _mark_key(tmp_path, key, section="Economics")
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        order = browser_page.eval_on_selector(
            ".article-body .hl-title-marker",
            """el => [
              el.nextElementSibling.className,
              el.nextElementSibling.nextElementSibling.tagName,
            ]""",
        )
        assert order == ["hl-key-marker", "MARK"]


def test_the_star_does_not_shift_later_highlights_in_the_block(
    monkeypatch, tmp_path, browser_page  # noqa: F811
):
    # Highlights are stored as character offsets into a block's text; a
    # marker that added text would move every later highlight in the block.
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        key = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _save_highlight(client, item_id, 0, 37, 0, 46, "The other")
        _mark_key(tmp_path, key)
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        texts = browser_page.eval_on_selector_all(
            ".article-body mark.hl", "els => els.map(el => el.textContent)"
        )
        assert texts == ["One player", "The other"]


def test_merging_into_a_key_highlight_keeps_one_star(monkeypatch, tmp_path, browser_page):  # noqa: F811
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        key = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _mark_key(tmp_path, key)
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        mark = "b[0].querySelector('mark.hl')"
        _select_and_save(
            browser_page, f"{mark}.firstChild, 4", f"{mark}.nextSibling, 26"
        )
        browser_page.wait_for_function(
            f"!document.querySelector('mark.hl[data-highlight-id=\"{key}\"]')"
        )
        markers = _key_markers(browser_page)
        assert len(markers) == 1 and markers[0][1] is True


def test_tapping_the_star_opens_the_highlight(monkeypatch, tmp_path, browser_page):  # noqa: F811
    with _opened(browser_page, monkeypatch, tmp_path, TEXT_BODY) as (client, item_id):
        key = _save_highlight(client, item_id, 0, 0, 0, 10, "One player")
        _mark_key(tmp_path, key)
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        browser_page.click(".article-body .hl-key-marker", timeout=5000)
        browser_page.wait_for_url(f"**/items/{item_id}/highlights/{key}")
