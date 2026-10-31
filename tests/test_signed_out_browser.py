"""A phone the server no longer lets in: what it keeps, what it shows.

Run on a real server behind a relay that can cut the connection (see
test_service_worker_browser). The gate itself is tested in test_auth; here it
is the phone's own copies and queue that matter.
"""

from __future__ import annotations

import re
from contextlib import contextmanager

from conftest import TEST_PASSWORD, _SignedInForTests
from playwright.sync_api import expect
from test_offline_actions_browser import (
    FIRST,
    SECOND,
    _go_offline,
    _go_online,
    _left,
    _outbox_empty,
    _ready,
    _seed_news,
    _titles,
)
from test_service_worker_browser import (
    _live_server,
    _wait_for,
    _wait_until_cached,
    quick_reopen,
)


@contextmanager
def _let_out():
    """The server stops recognising this phone (revoked, or the password
    changed) for as long as the block lasts."""
    _SignedInForTests.on = False
    try:
        yield
    finally:
        _SignedInForTests.on = True


def _stored(phone, url):
    return phone.evaluate("(u) => caches.match(u).then(r => !!r)", url)


def test_signing_in_in_the_browser_keeps_the_phone_in_and_fills_its_copies(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out():
        _seed_news(tmp_path, [FIRST])
        phone.goto(f"{origin}/lists/news")
        expect(phone).to_have_url(re.compile(r"/login\?next=%2Flists%2Fnews"))

        phone.fill("input[type=password]", "wrong")
        phone.click("button[type=submit]")
        expect(phone.locator(".field-error")).to_contain_text("isn't right")

        phone.fill("input[type=password]", TEST_PASSWORD)
        phone.click("button[type=submit]")
        expect(phone).to_have_url(f"{origin}/lists/news")
        expect(phone.locator("body")).to_contain_text(FIRST)

        (cookie,) = [c for c in phone.context.cookies() if c["name"] == "reader_session"]
        assert cookie["httpOnly"] is True
        assert cookie["sameSite"] == "Lax"
        assert cookie["expires"] > 0

        # The worker takes over and downloads, signed in by that cookie alone.
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        _wait_until_cached(phone, f"{origin}/lists")
        phone.reload()
        expect(phone.locator("body")).to_contain_text(FIRST)


def _sign_in(phone, origin, path):
    """The real login form, for the test's phone only."""
    phone.goto(f"{origin}{path}")
    phone.fill("input[type=password]", TEST_PASSWORD)
    phone.click("button[type=submit]")
    expect(phone).to_have_url(f"{origin}{path}")
    phone.wait_for_function("navigator.serviceWorker.controller !== null")
    _wait_until_cached(phone, f"{origin}{path}")


def test_signing_out_in_settings_shows_the_login_page_and_clears_the_phone(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out():
        _seed_news(tmp_path, [FIRST])
        _sign_in(phone, origin, "/lists/news")

        phone.goto(f"{origin}/settings")
        phone.click("text=Sign out of this device")
        expect(phone).to_have_url(f"{origin}/login")
        _wait_for(lambda: not _stored(phone, f"{origin}/lists/news"))
        # A page that used to open from the phone now asks for the password.
        phone.goto(f"{origin}/lists/news")
        expect(phone).to_have_url(re.compile(r"/login"))
        assert phone.locator("input[type=password]").count() == 1


def test_a_revoked_phone_finds_out_when_the_app_opens_and_clears_its_copies(
    phone, monkeypatch, tmp_path
):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _seed_news(tmp_path, [FIRST])
        _ready(phone, origin, "/lists/news")
        phone.wait_for_timeout(2500)

        with _let_out():
            phone.evaluate(
                "navigator.serviceWorker.controller.postMessage({ type: 'precache', keep: [] })"
            )
            expect(phone).to_have_url(re.compile(r"/login"))
            _wait_for(lambda: not _stored(phone, f"{origin}/lists/news"))
            assert not _stored(phone, f"{origin}/settings")


def test_the_login_page_is_never_kept_as_a_copy_of_the_page_asked_for(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _seed_news(tmp_path, [FIRST])
        _ready(phone, origin, "/lists/news")
        with _let_out():
            phone.goto(f"{origin}/lists/news?x=1")
            expect(phone).to_have_url(re.compile(r"/login"))
        assert not _stored(phone, f"{origin}/lists/news?x=1")
        assert not _stored(phone, f"{origin}/login")


def test_saves_waiting_on_a_phone_survive_being_signed_out_and_go_after_signing_in(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        phone.goto(f"{origin}/lists/news")
        _ready(phone, origin, "/lists/news?view=read")
        phone.goto(f"{origin}/lists/news")
        _go_offline(phone, server)
        _left(phone, FIRST)
        assert not _outbox_empty(phone)

        with _let_out():
            _go_online(phone, server)
            expect(phone).to_have_url(re.compile(r"/login"))
            # Refused, not lost: still waiting, and the server has not seen it.
            assert not _outbox_empty(phone)
            assert _titles(tmp_path, "news", read=True) == []

        # Signed in again (the test's own cookie stands for the password).
        phone.goto(f"{origin}/lists/news")
        _go_online(phone, server)
        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [FIRST])
        _wait_for(lambda: _outbox_empty(phone))


def test_a_worker_installs_even_when_nobody_is_signed_in(phone, monkeypatch, tmp_path):
    # A phone that lost its sign-in while the app was updated must still take
    # the new worker: the old one keeps showing its stored pages and never
    # asks for the password.
    with _live_server(monkeypatch, tmp_path) as (origin, _server), _let_out():
        phone.goto(f"{origin}/login")
        installed = phone.evaluate(
            """async () => {
              await navigator.serviceWorker.register("/sw.js");
              const registration = await navigator.serviceWorker.ready;
              return !!registration.active;
            }"""
        )
        assert installed
        assert not _stored(phone, f"{origin}/lists")
