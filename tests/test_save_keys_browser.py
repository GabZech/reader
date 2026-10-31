"""The bookmarklet from another website, in a real browser.

It posts a form from the page being saved to this app: a cross-site request, so
the browser sends no sign-in cookie and the save key is all that lets it in.
"""

from __future__ import annotations

import http.server
import threading
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import expect
from test_service_worker_browser import _live_server
from test_signed_out_browser import _let_out, _sign_in

PAGE = (Path(__file__).parent / "fixtures" / "capture" / "blog.html").read_bytes()


@contextmanager
def _other_site():
    """Another website, on another host (localhost, not 127.0.0.1)."""

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


def _run_bookmarklet(phone, href):
    code = href.removeprefix("javascript:")
    with phone.context.expect_page() as opened:
        phone.evaluate("(code) => (0, eval)(code)", code)
    result = opened.value
    result.wait_for_load_state()
    return result


def test_the_bookmarklet_saves_from_another_site_until_its_key_is_revoked(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out(), _other_site() as blog:
        _sign_in(phone, origin, "/settings")
        phone.goto(f"{origin}/settings/devices/keys/new")
        phone.get_by_role("button", name="Computer bookmarklet").click()
        href = phone.locator("a.bookmarklet").get_attribute("href")
        assert href.startswith("javascript:")

        phone.goto(blog)
        saved = _run_bookmarklet(phone, href)
        expect(saved.locator("body")).to_contain_text("Saved to Read later")
        saved.close()

        # The key is listed, was used, and can be revoked.
        phone.goto(f"{origin}/settings/devices")
        row = phone.locator(".device-row", has_text="Computer bookmarklet")
        expect(row).to_contain_text("last used")
        row.get_by_role("button", name="Revoke").click()
        phone.locator(".swipe-dialog").get_by_role("button", name="Revoke").click()
        expect(phone.locator(".device-row", has_text="Computer bookmarklet")).to_have_count(0)

        phone.goto(blog)
        refused = _run_bookmarklet(phone, href)
        expect(refused.locator("body")).to_contain_text("valid save key")
