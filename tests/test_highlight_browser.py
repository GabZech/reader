from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright
from test_app import (
    _add_to_news,
    _client,
    _first_item_id,
    _save_highlight,
    _set_body_html,
)

ORIGIN = "http://reader.test"
IMAGE_BODY = (
    "<p>First paragraph</p>"
    '<p><img src="/static/favicon.svg" alt="chart"></p>'
    "<p>Second paragraph</p>"
)


@pytest.fixture
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            yield browser.new_page()
        finally:
            browser.close()


def _serve_through(page, client):
    """Answer every request the page makes from the app's TestClient."""

    def handle(route):
        request = route.request
        parts = urlsplit(request.url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        response = client.request(
            request.method,
            path,
            content=request.post_data_buffer,
            headers={k: v for k, v in request.headers.items() if k.lower() == "content-type"},
            follow_redirects=False,
        )
        route.fulfill(
            status=response.status_code,
            headers=dict(response.headers),
            body=response.content,
        )

    page.route(f"{ORIGIN}/**", handle)


def _outlined(page):
    return page.eval_on_selector_all(".article-body img.hl-image", "els => els.length")


def test_selecting_across_an_image_marks_it_highlighted(monkeypatch, tmp_path, browser_page):
    page = browser_page
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(tmp_path, item_id, IMAGE_BODY)
        _serve_through(page, client)

        page.goto(f"{ORIGIN}/items/{item_id}")
        assert _outlined(page) == 0

        page.evaluate(
            """() => {
              const blocks = document.querySelector(".article-body").children;
              const range = document.createRange();
              range.setStart(blocks[0].firstChild, 0);
              range.setEnd(blocks[2].firstChild, 6);
              const selection = window.getSelection();
              selection.removeAllRanges();
              selection.addRange(range);
              document.querySelector(".article-body").dispatchEvent(
                new MouseEvent("mouseup", { bubbles: true })
              );
            }"""
        )
        # The text highlight lands, so the save went through...
        page.wait_for_selector(".article-body mark.hl", timeout=5000)
        # ...and the image it spans is marked too.
        assert _outlined(page) == 1


def _open_with_saved_highlight(page, monkeypatch, tmp_path, end_block, end_offset):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(tmp_path, item_id, IMAGE_BODY)
        _serve_through(page, client)
        _save_highlight(
            client, item_id, start_block=0, start_offset=0,
            end_block=end_block, end_offset=end_offset,
        )
        page.goto(f"{ORIGIN}/items/{item_id}")
        return _outlined(page)


def test_saved_highlight_spanning_an_image_marks_it(monkeypatch, tmp_path, browser_page):
    assert _open_with_saved_highlight(browser_page, monkeypatch, tmp_path, 2, 6) == 1


def test_saved_highlight_stopping_on_an_image_leaves_it_unmarked(
    monkeypatch, tmp_path, browser_page
):
    # Mirrors the export: an image on the boundary block is not stored.
    assert _open_with_saved_highlight(browser_page, monkeypatch, tmp_path, 1, 0) == 0
