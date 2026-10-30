"""The "Available offline" switch on a list's or a source's own screen:
its unread articles are kept on the phone, and leave once read."""

from __future__ import annotations

import time

from test_offline_actions_browser import FIRST, SECOND, _ready, _seed_news
from test_service_worker_browser import (
    _go_offline,
    _live_server,
    _wait_until_cached,
    quick_reopen,
)

from app import db as dbmod
from app import main as mainmod


def _reopen(phone, origin):
    """Open the app again, as a fresh launch, and wait for its run to end."""
    phone.wait_for_timeout(2500)
    again = phone.context.new_page()
    again.goto(f"{origin}/")
    again.wait_for_function("navigator.serviceWorker.controller !== null")
    again.wait_for_selector("#sync-status.is-updating", timeout=5000)
    again.wait_for_selector("#sync-status:not(.is-updating)", timeout=20000)
    return again


def _stored(phone, url):
    return phone.evaluate(
        "(u) => caches.open('reader-shell-v4').then(c => c.match(u, { ignoreSearch: true })).then(r => !!r)",
        url,
    )


def test_a_list_switched_on_is_readable_offline(phone, monkeypatch, tmp_path):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news/edit")
        phone.goto(f"{origin}/lists/news/edit")
        phone.click(".offline-toggle button[value='1']")
        phone.wait_for_selector(".offline-toggle button[value='1'].is-active")

        again = _reopen(phone, origin)
        _wait_until_cached(again, f"{origin}/items/{first}?from_list=news")
        _go_offline(again, server)
        again.goto(f"{origin}/items/{first}?from_list=news")

        assert f"Words of {FIRST}" in again.inner_text(".article-body")


def test_a_read_article_leaves_the_phone_unless_a_save_waits_for_it(
    phone, monkeypatch, tmp_path
):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        first, second = _seed_news(tmp_path, [FIRST, SECOND])
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            dbmod.set_list_offline(conn, "news", True)
            conn.commit()
        finally:
            conn.close()
        _ready(phone, origin, f"/items/{first}", f"/items/{second}")
        # Both read elsewhere; a reading spot for the second still waits here.
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            dbmod.mark_item_read(conn, first, "news")
            dbmod.mark_item_read(conn, second, "news")
            conn.commit()
        finally:
            conn.close()
        phone.evaluate(
            """(path) => localStorage.setItem('reader-progress',
                 JSON.stringify({ [path]: { index: 3, at: Date.now(), unsent: true } }))""",
            f"/items/{second}",
        )
        # Kept unsent: the server fails to save it.
        def broken(*args):
            raise RuntimeError("down")

        monkeypatch.setattr(mainmod, "set_item_progress", broken)

        again = _reopen(phone, origin)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and _stored(again, f"{origin}/items/{first}"):
            time.sleep(0.2)

        assert not _stored(again, f"{origin}/items/{first}")
        assert _stored(again, f"{origin}/items/{second}")
