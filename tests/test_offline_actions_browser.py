"""Archiving, marking read and saving to Read later without a connection.

The phone keeps what was done in a queue and shows it at once on the stored
pages; the server gets it when the connection returns. Run on a real server
behind a relay that can cut the connection (see test_service_worker_browser).
"""

from __future__ import annotations

import httpx
from playwright.sync_api import expect
from test_service_worker_browser import (
    _go_offline,
    _go_online,
    _live_server,
    _wait_for,
    _wait_until_cached,
)

from app import db as dbmod

FIRST = "First story"
SECOND = "Second story"
THIRD = "Third story"


def _seed_news(tmp_path, titles):
    """A news source with one item per title, newest first, filed under News."""
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        dbmod.init_db(conn)
        dbmod.insert_source(
            conn,
            source_id="fixture",
            kind="mail",
            title="Fixture news",
            feed_url=None,
            backfill=None,
            mail_address="fixture@example.test",
        )
        dbmod.add_source_to_list(conn, "fixture", "news", None)
        for n, title in enumerate(titles):
            dbmod.upsert_item(
                conn,
                source_id="fixture",
                guid=f"fixture-{n}",
                title=title,
                author=None,
                url=f"https://example.test/{n}",
                published_at=f"2026-10-2{9 - n}T10:00:00+00:00",
                body_html=f"<p>Words of {title}</p>",
                image_url=None,
                word_count=300,
            )
        conn.commit()
        return [
            conn.execute("SELECT id FROM items WHERE title = ?", (title,)).fetchone()["id"]
            for title in titles
        ]
    finally:
        conn.close()


def _titles(tmp_path, slug, **view):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [row["title"] for row in dbmod.items_for_list(conn, slug, **view)]
    finally:
        conn.close()


def _seen(tmp_path, item_id):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return dbmod.get_item(conn, item_id)["seen_at"] is not None
    finally:
        conn.close()


def _ready(phone, origin, *paths):
    """Open the app so the worker takes over and has downloaded these pages."""
    phone.goto(f"{origin}/settings")
    phone.wait_for_function("navigator.serviceWorker.controller !== null")
    for path in paths:
        _wait_until_cached(phone, f"{origin}{path}")


def _row(page, title):
    return page.locator(".item-swipe", has_text=title)


def _swipe(page, title, dx):
    box = _row(page, title).bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + dx, y, steps=12)
    page.mouse.up()


def _left(page, title):
    _swipe(page, title, -170)


def _right(page, title):
    _swipe(page, title, 170)


def _outbox_empty(page):
    return page.evaluate("(localStorage.getItem('reader-outbox') || '[]') === '[]'")


def _toast(page):
    return page.locator(".toast")


def _home(phone, origin):
    """Home syncs once and reloads itself; wait for that to be over."""
    phone.goto(f"{origin}/")
    phone.wait_for_function("sessionStorage.getItem('reader-synced') === '1'")
    phone.wait_for_timeout(1000)
    phone.wait_for_load_state("load")


def test_swiping_a_news_row_to_read_offline_moves_it_and_sends_it_later(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        phone.goto(f"{origin}/lists/news")
        _ready(phone, origin, "/lists/news?view=read")
        phone.goto(f"{origin}/lists/news")
        _go_offline(phone, server)

        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")
        expect(phone.locator(".actions")).to_contain_text("Read (1)")
        expect(_toast(phone)).to_contain_text("will sync")

        # Reopened from storage it is still gone, and it is on the Read tab.
        phone.reload()
        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")
        phone.goto(f"{origin}/lists/news?view=read")
        expect(_row(phone, FIRST)).to_have_count(1)
        expect(phone.locator(".actions")).to_contain_text("Read (1)")
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")
        assert _titles(tmp_path, "news", read=True) == []

        _go_online(phone, server)
        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [FIRST])
        assert _titles(tmp_path, "news") == [SECOND]


def test_a_moved_row_can_be_moved_back_offline_from_its_new_tab(phone, monkeypatch, tmp_path):
    # Read, then unread, offline: the item ends where it began.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news", "/lists/news?view=read")
        phone.goto(f"{origin}/lists/news")
        _go_offline(phone, server)
        _left(phone, FIRST)
        phone.goto(f"{origin}/lists/news?view=read")
        expect(_row(phone, FIRST)).to_have_count(1)

        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        phone.goto(f"{origin}/lists/news")
        expect(_row(phone, FIRST)).to_have_count(1)
        expect(phone.locator(".actions")).to_contain_text("Unread (2)")
        expect(phone.locator(".actions")).to_contain_text("Read (0)")

        _go_online(phone, server)
        _wait_for(lambda: _outbox_empty(phone))
        assert _titles(tmp_path, "news", read=True) == []
        assert sorted(_titles(tmp_path, "news")) == [FIRST, SECOND]


def test_swiping_in_the_library_archives_offline_and_the_archive_tab_has_it(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, second = _seed_news(tmp_path, [FIRST, SECOND])
        for item_id in (first, second):
            httpx.post(f"{origin}/items/{item_id}/later")
        _ready(phone, origin, "/lists/later", "/lists/later?view=archive")
        phone.goto(f"{origin}/lists/later")
        _go_offline(phone, server)

        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Library (1)")
        expect(phone.locator(".actions")).to_contain_text("Archive (1)")
        phone.goto(f"{origin}/lists/later?view=archive")
        expect(_row(phone, FIRST)).to_have_count(1)
        # The row that arrived can be swiped back, offline too.
        _left(phone, FIRST)
        expect(_row(phone, FIRST)).to_have_count(0)
        phone.goto(f"{origin}/lists/later")
        expect(_row(phone, FIRST)).to_have_count(1)

        _go_online(phone, server)
        _wait_for(lambda: _outbox_empty(phone))
        assert _titles(tmp_path, "later", archived=True) == []
        assert sorted(_titles(tmp_path, "later")) == [FIRST, SECOND]


def test_a_row_swiped_on_home_offline_leaves_home_and_is_sent_later(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND, THIRD])
        _ready(phone, origin, "/lists/news")
        _home(phone, origin)
        expect(_row(phone, FIRST)).to_have_count(1)
        _go_offline(phone, server)

        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator("[data-list=news] .count")).to_have_text("2")
        phone.reload()
        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator("[data-list=news] .count")).to_have_text("2")

        _go_online(phone, server)
        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [FIRST])


def test_mark_as_read_on_an_article_offline_returns_to_the_list_without_it(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news", "/lists/news?view=read")
        phone.goto(f"{origin}/lists/news")
        phone.goto(f"{origin}/items/{first}?from_list=news")
        _go_offline(phone, server)

        phone.click("text=Mark as read")

        phone.wait_for_url(f"{origin}/lists/news")
        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")
        expect(_toast(phone)).to_contain_text("Read · will sync")
        phone.goto(f"{origin}/lists/news?view=read")
        expect(_row(phone, FIRST)).to_have_count(1)

        _go_online(phone, server)
        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [FIRST])


def test_archive_and_read_later_on_an_article_work_offline(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, second = _seed_news(tmp_path, [FIRST, SECOND])
        httpx.post(f"{origin}/items/{first}/later")
        _ready(phone, origin, "/lists/later", "/lists/later?view=archive")
        phone.goto(f"{origin}/lists/later")
        phone.goto(f"{origin}/items/{first}?from_list=later")
        phone.goto(f"{origin}/items/{second}?from_list=news")
        _go_offline(phone, server)

        # Save the News article to Read later: the button says so at once.
        phone.click("text=Read later")
        expect(phone.locator(".article-actions")).to_contain_text("Saved to Read later")
        expect(phone.locator(".act-archive")).to_have_count(1)
        phone.goto(f"{origin}/lists/later")
        expect(_row(phone, SECOND)).to_have_count(1)
        expect(phone.locator(".actions")).to_contain_text("Library (2)")

        # Archive the other one from its own page.
        phone.goto(f"{origin}/items/{first}?from_list=later")
        phone.click(".act-archive")
        phone.wait_for_url(f"{origin}/lists/later")
        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Library (1)")
        expect(phone.locator(".actions")).to_contain_text("Archive (1)")
        phone.goto(f"{origin}/lists/later?view=archive")
        expect(_row(phone, FIRST)).to_have_count(1)

        _go_online(phone, server)
        _wait_for(lambda: _titles(tmp_path, "later") == [SECOND])
        assert _titles(tmp_path, "later", archived=True) == [FIRST]


def test_delete_still_needs_a_connection_and_says_so(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        phone.goto(f"{origin}/lists/news")
        _ready(phone, origin, "/lists/news")
        phone.goto(f"{origin}/lists/news")
        _go_offline(phone, server)

        _right(phone, FIRST)
        phone.click("text=Delete >> nth=-1")

        expect(_toast(phone)).to_contain_text("Delete needs a connection")
        expect(_row(phone, FIRST)).to_have_count(1)
        _go_online(phone, server)
        phone.wait_for_timeout(500)
        assert sorted(_titles(tmp_path, "news")) == [FIRST, SECOND]


def _app(server):
    return f"http://127.0.0.1:{server.network.upstream_port}"


def test_an_article_opened_offline_is_marked_seen_once_back_online(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news")
        phone.goto(f"{origin}/lists/news")
        # Stored the way the background download does, without opening it.
        phone.evaluate(
            "(u) => fetch(u, { headers: { 'X-Reader-Prefetch': '1' } })",
            f"{origin}/items/{first}",
        )
        _wait_until_cached(phone, f"{origin}/items/{first}")
        assert not _seen(tmp_path, first)
        _go_offline(phone, server)

        phone.goto(f"{origin}/items/{first}?from_list=news")
        phone.wait_for_selector(".article-body")
        phone.goto(f"{origin}/lists/news")

        expect(phone.locator(".item.is-seen", has_text=FIRST)).to_have_count(1)
        assert not _seen(tmp_path, first)
        _go_online(phone, server)
        _wait_for(lambda: _seen(tmp_path, first))


def test_an_item_deleted_elsewhere_is_dropped_and_the_rest_still_sent(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news")
        phone.goto(f"{origin}/lists/news")
        _go_offline(phone, server)
        _left(phone, FIRST)
        _left(phone, SECOND)
        # Another device deletes the first meanwhile.
        httpx.post(f"{_app(server)}/items/{first}/delete")

        _go_online(phone, server)

        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [SECOND])
        _wait_for(lambda: _outbox_empty(phone))


def test_a_swipe_made_online_is_still_there_when_the_phone_goes_offline_right_after(
    phone, monkeypatch, tmp_path
):
    # The stored list must not bring back a row that was moved online.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news", "/lists/news?view=read")
        phone.goto(f"{origin}/lists/news")

        _left(phone, FIRST)
        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [FIRST])
        phone.wait_for_timeout(1500)
        _go_offline(phone, server)

        phone.goto(f"{origin}/lists/news")
        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Read (1)")
        phone.goto(f"{origin}/lists/news?view=read")
        expect(_row(phone, FIRST)).to_have_count(1)
