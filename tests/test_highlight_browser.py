from __future__ import annotations

import json
from contextlib import contextmanager
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

from app import db as dbmod

ORIGIN = "http://reader.test"
IMAGE_BODY = (
    "<p>First paragraph</p>"
    '<p><img src="/static/favicon.svg" alt="chart"></p>'
    "<p>Second paragraph</p>"
)
BARE_IMAGE_BODY = (
    "<p>First paragraph</p>"
    '<img src="/static/favicon.svg" alt="chart">'
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


def _stored_images(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        rows = conn.execute("SELECT image_urls FROM highlights").fetchall()
    finally:
        conn.close()
    return [json.loads(row["image_urls"] or "[]") for row in rows]


def _select_and_save(page, start, end):
    """Select from `start` to `end`, each a JS (container, offset) pair over
    `b`, the article's top-level blocks, and let the page save it."""
    page.evaluate(
        f"""() => {{
          const b = document.querySelector(".article-body").children;
          const range = document.createRange();
          range.setStart({start});
          range.setEnd({end});
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          document.querySelector(".article-body").dispatchEvent(
            new MouseEvent("mouseup", {{ bubbles: true }})
          );
        }}"""
    )
    # The text highlight lands, so the save went through.
    page.wait_for_selector(".article-body mark.hl", timeout=5000)


@contextmanager
def _opened(page, monkeypatch, tmp_path, body=IMAGE_BODY):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(tmp_path, item_id, body)
        _serve_through(page, client)
        page.goto(f"{ORIGIN}/items/{item_id}")
        yield client, item_id


@pytest.mark.parametrize(
    ("start", "end"),
    [
        pytest.param("b[0].firstChild, 0", "b[2].firstChild, 6", id="across"),
        pytest.param("b[1], 0", "b[2].firstChild, 6", id="starts-on-image"),
        pytest.param("b[0].firstChild, 0", "b[1], 1", id="ends-on-image"),
    ],
)
def test_selecting_over_an_image_marks_and_stores_it(
    monkeypatch, tmp_path, browser_page, start, end
):
    with _opened(browser_page, monkeypatch, tmp_path):
        assert _outlined(browser_page) == 0
        _select_and_save(browser_page, start, end)
        assert _outlined(browser_page) == 1
        assert _stored_images(tmp_path) == [["/static/favicon.svg"]]


def test_selection_stopping_just_before_an_image_leaves_it_out(
    monkeypatch, tmp_path, browser_page
):
    # A browser often reports a selection that ends at a paragraph's end as
    # ending at the very start of the next block; that touches the image
    # block without covering the image.
    with _opened(browser_page, monkeypatch, tmp_path):
        _select_and_save(browser_page, "b[0].firstChild, 0", "b[1], 0")
        assert _outlined(browser_page) == 0
        assert _stored_images(tmp_path) == [[]]


@pytest.mark.parametrize(
    ("body", "end_block", "end_offset"),
    [
        pytest.param(IMAGE_BODY, 2, 6, id="spanning"),
        pytest.param(IMAGE_BODY, 1, 0, id="ending-on-image"),
        pytest.param(BARE_IMAGE_BODY, 2, 6, id="bare-img-block"),
    ],
)
def test_saved_highlight_over_an_image_marks_it_on_reload(
    monkeypatch, tmp_path, browser_page, body, end_block, end_offset
):
    with _opened(browser_page, monkeypatch, tmp_path, body) as (client, item_id):
        _save_highlight(
            client, item_id, start_block=0, start_offset=0,
            end_block=end_block, end_offset=end_offset,
        )
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        assert _outlined(browser_page) == 1
