"""Whole days offline, start to finish: the way the app is really used.

The smaller tests next door check each piece; these check the pieces together,
including what happens on the way back online.
"""

from __future__ import annotations

from playwright.sync_api import expect
from test_offline_actions_browser import (
    FIRST,
    SECOND,
    THIRD,
    _home,
    _left,
    _outbox_empty,
    _ready,
    _row,
    _seed_news,
    _titles,
    _toast,
)
from test_service_worker_browser import (
    _go_offline,
    _go_online,
    _live_server,
    _saved_article,
    _select,
    _wait_for,
)

ARTICLE = "<p>Highlight me on the train today</p><p>The rest of the piece</p>"


def _pages_fresh(page):
    """Every save has been sent and the stored pages fetched again after it."""
    return page.evaluate("(localStorage.getItem('reader-stale-copies') || '[]') === '[]'")


def test_a_morning_on_the_train_and_the_way_back_online(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND, THIRD])
        article = _saved_article(origin, tmp_path, "train", ARTICLE)
        _ready(
            phone,
            origin,
            "/lists/news?view=read",
            "/lists/later?view=archive",
            "/sources",
            f"/items/{article}",
        )
        _home(phone, origin)
        _go_offline(phone, server)

        # Home, offline: triage the news with swipes.
        phone.goto(f"{origin}/")
        expect(_row(phone, FIRST)).to_have_count(1)
        _left(phone, FIRST)
        _left(phone, SECOND)
        expect(phone.locator("[data-list=news] .count")).to_have_text("1")

        # Open the saved article from Home, highlight, archive.
        phone.locator("[data-list=later] a.item").first.click()
        phone.wait_for_selector(".article-body")
        _select(phone, 0, 0, 12)
        phone.wait_for_selector(".article-body mark.hl.is-pending")
        expect(phone.locator(".sync-state")).to_contain_text("Offline")
        phone.click(".act-archive")
        phone.wait_for_url(f"{origin}/?flash=*")
        expect(_toast(phone)).to_contain_text("Archived · will sync")
        expect(phone.locator("[data-list=later]")).to_have_count(0)

        # Lists, Sources and Settings still open and agree with what was done.
        phone.click(".tabbar >> text=Lists")
        expect(phone.locator("a.list-row[href='/lists/news'] .count")).to_have_text("1")
        expect(phone.locator("a.list-row[href='/lists/later'] .count")).to_have_text("0")
        phone.click(".tabbar >> text=Sources")
        expect(phone.locator("h1")).to_have_text("Sources")
        phone.goto(f"{origin}/lists/later?view=archive")
        expect(phone.locator(".item-swipe a.item")).to_have_count(1)
        phone.goto(f"{origin}/lists/news?view=read")
        expect(phone.locator(".item-swipe a.item")).to_have_count(2)

        # Back online: everything arrives, in order.
        _go_online(phone, server)
        _wait_for(lambda: _outbox_empty(phone))
        _wait_for(lambda: sorted(_titles(tmp_path, "news", read=True)) == sorted([FIRST, SECOND]))
        _wait_for(lambda: _titles(tmp_path, "later", archived=True) != [])
        assert _titles(tmp_path, "later") == []
        _wait_for(lambda: _pages_fresh(phone))

        # Offline again straight away: nothing moved comes back.
        _go_offline(phone, server)
        phone.goto(f"{origin}/")
        expect(_row(phone, FIRST)).to_have_count(0)
        expect(_row(phone, SECOND)).to_have_count(0)
        expect(_row(phone, THIRD)).to_have_count(1)
        expect(phone.locator("[data-list=later]")).to_have_count(0)
        phone.goto(f"{origin}/lists/news?view=read")
        expect(phone.locator(".item-swipe a.item")).to_have_count(2)
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")


def test_a_swipe_when_the_signal_is_dead_but_the_phone_thinks_it_is_online(
    phone, monkeypatch, tmp_path
):
    # navigator.onLine is not always right: the tap is what finds out.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        _ready(phone, origin, "/lists/news?view=read")
        phone.goto(f"{origin}/lists/news")
        server.network.down()

        _left(phone, FIRST)

        expect(_toast(phone)).to_contain_text("Read · will sync")
        expect(_row(phone, FIRST)).to_have_count(0)
        assert _titles(tmp_path, "news", read=True) == []
        server.network.up()
        phone.evaluate("window.dispatchEvent(new Event('online'))")
        _wait_for(lambda: _titles(tmp_path, "news", read=True) == [FIRST])
