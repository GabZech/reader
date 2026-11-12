"""The bookmarklet from another website, in a real browser.

It opens Reader's hand-off page in a new tab and passes it the page as the
browser rendered it; that tab saves it with the browser's own sign-in. No key
is involved, so nothing secret runs inside the page being saved.
"""

from __future__ import annotations

import http.server
import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from conftest import TEST_PASSWORD
from playwright.sync_api import expect
from test_service_worker_browser import _live_server
from test_signed_out_browser import _let_out, _sign_in

from app import ingest

PAGE = (Path(__file__).parent / "fixtures" / "capture" / "blog.html").read_bytes()
TITLE = "Hiten Shah"


@contextmanager
def _other_site():
    """Another website, on another host (localhost, not 127.0.0.1). The
    server cannot fetch it (it is not a public address), so a page that gets
    saved can only have come from the browser."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGE)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://localhost:{server.server_address[1]}/post"
    finally:
        server.shutdown()


def _bookmarklet(phone, origin):
    phone.goto(f"{origin}/settings/bookmarklet")
    href = phone.locator("a.bookmarklet").get_attribute("href")
    assert href.startswith("javascript:")
    return href


def _run_bookmarklet(phone, href):
    code = href.removeprefix("javascript:")
    with phone.context.expect_page() as opened:
        phone.evaluate("(code) => (0, eval)(code)", code)
    tab = opened.value
    tab.wait_for_load_state()
    return tab


def _saved_urls(tmp_path):
    conn = sqlite3.connect(tmp_path / "reader.db")
    try:
        return [row[0] for row in conn.execute("SELECT url FROM items")]
    finally:
        conn.close()


def test_the_bookmarklet_hands_the_rendered_page_to_a_reader_tab(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out(), _other_site() as blog:
        _sign_in(phone, origin, "/settings")
        href = _bookmarklet(phone, origin)

        phone.goto(blog)
        tab = _run_bookmarklet(phone, href)
        expect(tab.locator("body")).to_contain_text("Saved to Read later")
        expect(tab.locator("blockquote.quote")).to_contain_text(TITLE)
        assert _saved_urls(tmp_path) == [blog]


def test_signed_out_the_bookmarklet_saves_once_signed_in(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out(), _other_site() as blog:
        # Signed in once to pick up the button, then signed out.
        _sign_in(phone, origin, "/settings")
        href = _bookmarklet(phone, origin)
        phone.context.clear_cookies()

        phone.goto(blog)
        tab = _run_bookmarklet(phone, href)
        expect(tab).to_have_url(re.compile(r"/login\?next=%2Fcapture%2Ffrom-page%3Furl%3D"))
        tab.fill("input[type=password]", TEST_PASSWORD)
        tab.click("button[type=submit]")
        expect(tab.locator("body")).to_contain_text("Saved to Read later")
        assert _saved_urls(tmp_path) == [blog]


def test_a_page_that_cannot_hand_itself_over_offers_its_address(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out():
        _sign_in(phone, origin, "/settings")
        # Opened with no page behind it: nothing to hand over, nothing saved yet.
        phone.goto(f"{origin}/capture/from-page?url=https%3A%2F%2Fblog.test%2Fpost")
        save = phone.get_by_role("button", name="Save the address only")
        expect(save).to_be_visible()
        assert _saved_urls(tmp_path) == []

        monkeypatch.setattr(ingest, "fetch_url", lambda url, timeout=8.0: (url, PAGE.decode()))
        save.click()
        expect(phone.locator("body")).to_contain_text("Saved to Read later")
        assert _saved_urls(tmp_path) == ["https://blog.test/post"]
