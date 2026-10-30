"""Online, a page the phone has stored opens from that copy, without asking
the server; changes made on this phone still show on the next visit."""

from __future__ import annotations

import time

from playwright.sync_api import expect
from test_offline_actions_browser import FIRST, SECOND, _ready, _seed_news, _seen
from test_service_worker_browser import _live_server, _wait_until_cached

from app import db as dbmod


def _wait_for(check, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(0.2)
    raise AssertionError("never happened")


def _downloaded(phone):
    """Wait for the background download to finish, so it stores nothing more."""
    phone.wait_for_function(
        """() => JSON.parse(localStorage.getItem('reader-log') || '[]')
             .some((x) => x.e === 'sw-precache' && x.d.startsWith('pages+'))"""
    )


def _retitle(tmp_path, item_id, title):
    """What another device, or a feed sync, changes behind the phone's back."""
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        conn.execute("UPDATE items SET title = ? WHERE id = ?", (title, item_id))
        conn.commit()
    finally:
        conn.close()


def test_a_stored_page_opens_from_the_phone_while_online(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news")
        _downloaded(phone)
        _retitle(tmp_path, first, "Changed elsewhere")

        phone.goto(f"{origin}/lists/news")

        expect(phone.locator(".item", has_text=FIRST)).to_have_count(1)
        expect(phone.locator(".item", has_text="Changed elsewhere")).to_have_count(0)


def test_a_change_made_on_the_phone_shows_on_the_next_visit(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _seed_news(tmp_path, [FIRST])
        _ready(phone, origin, "/lists", "/lists/news")
        _downloaded(phone)
        phone.goto(f"{origin}/lists/news/edit")
        phone.fill("input[name=name]", "Morning papers")
        phone.click("button.top-edit.is-strong")
        phone.wait_for_url(f"{origin}/lists/news")

        expect(phone.locator("h1")).to_contain_text("Morning papers")
        phone.goto(f"{origin}/lists")
        expect(phone.locator(".list-row", has_text="Morning papers")).to_have_count(1)


def test_an_article_opened_from_its_stored_copy_is_still_marked_opened(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news")
        phone.goto(f"{origin}/lists/news")
        phone.evaluate("(u) => fetch(u)", f"{origin}/items/{first}?from_list=news")
        _wait_until_cached(phone, f"{origin}/items/{first}?from_list=news")
        _downloaded(phone)
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            conn.execute("UPDATE items SET seen_at = NULL WHERE id = ?", (first,))
            conn.commit()
        finally:
            conn.close()

        phone.goto(f"{origin}/items/{first}?from_list=news")
        phone.wait_for_selector(".article-body")
        _wait_for(lambda: _seen(tmp_path, first))
        phone.goto(f"{origin}/lists/news")

        expect(phone.locator(".item.is-seen", has_text=FIRST)).to_have_count(1)


def test_an_article_reached_another_way_keeps_that_ways_close(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        [first] = _seed_news(tmp_path, [FIRST])
        _ready(phone, origin, "/lists/news")
        phone.goto(f"{origin}/items/{first}?from_list=news")
        _wait_until_cached(phone, f"{origin}/items/{first}?from_list=news")

        phone.goto(f"{origin}/items/{first}?from_source=fixture")

        assert phone.get_attribute(".bar-close", "href") == "/sources/fixture/items"


def test_a_stored_article_resumes_at_this_phones_later_spot(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        [first] = _seed_news(tmp_path, [FIRST])
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            body = "".join(f"<p>Paragraph {n}</p>" for n in range(40))
            conn.execute("UPDATE items SET body_html = ? WHERE id = ?", (body, first))
            conn.commit()
        finally:
            conn.close()
        _ready(phone, origin, "/lists/news")
        phone.goto(f"{origin}/items/{first}?from_list=news")
        _wait_until_cached(phone, f"{origin}/items/{first}?from_list=news")
        # Read on to paragraph 30 since the copy was stored, and sent.
        phone.evaluate(
            """(path) => localStorage.setItem('reader-progress',
                 JSON.stringify({ [path]: { index: 30, at: Date.now(), unsent: false } }))""",
            f"/items/{first}",
        )

        phone.goto(f"{origin}/items/{first}?from_list=news")

        expect(phone.locator(".article-body > .is-resume")).to_have_text("Paragraph 30")
