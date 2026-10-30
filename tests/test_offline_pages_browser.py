"""Settings, Sources and the pages under them, without a connection.

What writes (rename, delete, Home order, adding) needs the server: offline it
says so instead of failing in the browser's own way.
"""

from __future__ import annotations

import httpx
from playwright.sync_api import expect
from test_offline_actions_browser import FIRST, SECOND, _app, _ready, _seed_news, _toast
from test_service_worker_browser import _go_offline, _go_online, _live_server

from app import db as dbmod

SOURCE = "fixture"


def _home_flags(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return {r["slug"]: r["on_home"] for r in dbmod.lists_for_home_edit(conn)}
    finally:
        conn.close()


def _source_ids(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        dbmod.init_db(conn)
        return [r["id"] for r in dbmod.all_sources(conn)]
    finally:
        conn.close()


def _source_titles(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [r["title"] for r in dbmod.all_sources(conn)]
    finally:
        conn.close()


def _open_everything(phone, origin, tmp_path):
    """Seed a source (if the test has not), then wait for its pages to be stored."""
    if "fixture" not in _source_ids(tmp_path):
        _seed_news(tmp_path, [FIRST])
    return _ready(
        phone,
        origin,
        "/sources",
        f"/sources/{SOURCE}/items",
        f"/sources/{SOURCE}",
        "/lists/news/edit",
    )


def test_settings_sources_and_the_pages_under_them_open_offline(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST, SECOND])
        _open_everything(phone, origin, tmp_path)
        _go_offline(phone, server)

        phone.goto(f"{origin}/settings")
        expect(phone.locator("h1")).to_have_text("Settings")
        phone.click(".tabbar >> text=Sources")
        expect(phone.locator("h1")).to_have_text("Sources")
        phone.click("text=Fixture news")
        expect(phone.locator("h1")).to_have_text("Fixture news")
        expect(phone.locator(".item-swipe", has_text=FIRST)).to_have_count(1)
        phone.click("[aria-label=Settings]")
        expect(phone.locator("#source-name")).to_have_count(1)
        phone.goto(f"{origin}/lists/news/edit")
        expect(phone.locator("h1")).to_be_visible()
        assert "Couldn't load" not in phone.inner_text("body")


def test_the_theme_switch_still_works_offline(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _open_everything(phone, origin, tmp_path)
        _go_offline(phone, server)
        phone.goto(f"{origin}/settings")

        phone.click("[data-theme-value=light]")

        assert phone.evaluate("document.documentElement.dataset.theme") == "light"


def test_buttons_that_need_the_server_say_so_offline_and_send_nothing(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST])
        _open_everything(phone, origin, tmp_path)
        _go_offline(phone, server)

        # Home order and Shown / Hidden, in Settings.
        phone.goto(f"{origin}/settings")
        phone.click("text=Shown >> nth=0")
        expect(_toast(phone)).to_contain_text("This needs a connection")
        assert phone.url == f"{origin}/settings"
        assert _home_flags(tmp_path)["news"] == 1

        # Renaming and deleting a source.
        phone.goto(f"{origin}/sources/{SOURCE}")
        phone.fill("#source-name", "Renamed")
        phone.click("text=Save")
        expect(_toast(phone)).to_contain_text("This needs a connection")
        phone.click("text=Delete source")
        assert phone.url == f"{origin}/sources/{SOURCE}"

        # Renaming a list.
        phone.goto(f"{origin}/lists/news/edit")
        phone.click("button[type=submit] >> nth=0")
        assert phone.url == f"{origin}/lists/news/edit"

        _go_online(phone, server)
        phone.wait_for_timeout(500)
        assert _source_titles(tmp_path) == ["Fixture news"]
        assert _home_flags(tmp_path)["news"] == 1


def test_a_button_pressed_when_the_phone_only_finds_out_it_is_offline_shows_a_page(
    phone, monkeypatch, tmp_path
):
    # navigator.onLine says online while the connection is dead (a weak
    # signal): only the tap finds out. A page that says so, with a way back.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _open_everything(phone, origin, tmp_path)
        phone.goto(f"{origin}/settings")
        server.network.down()

        phone.click("text=Shown >> nth=0")

        expect(phone.locator("h1")).to_have_text("This needs a connection")
        phone.click("text=Go back")
        phone.wait_for_url(f"{origin}/settings")
        expect(phone.locator("h1")).to_have_text("Settings")


def test_a_form_sent_online_still_comes_back_to_its_page(phone, monkeypatch, tmp_path):
    # The worker now stands between the form and the server: the redirect the
    # server answers with must still be followed.
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open_everything(phone, origin, tmp_path)
        phone.goto(f"{origin}/settings")

        phone.click("text=Shown >> nth=0")

        phone.wait_for_function("document.querySelector('.set-row.is-off') !== null")
        assert phone.url.startswith(f"{origin}/settings")
        assert _home_flags(tmp_path)["news"] == 0


def test_an_article_not_saved_offline_says_so_and_goes_back(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _seed_news(tmp_path, [FIRST])
        _open_everything(phone, origin, tmp_path)
        phone.goto(f"{origin}/sources/{SOURCE}/items")
        _go_offline(phone, server)

        phone.click(".item-swipe a.item")

        expect(phone.locator("h1")).to_have_text("This article isn't saved for offline")
        phone.click("text=Go back")
        phone.wait_for_url(f"{origin}/sources/{SOURCE}/items")
        expect(phone.locator(".item-swipe", has_text=FIRST)).to_have_count(1)


def test_adding_a_source_or_list_offline_says_it_needs_a_connection(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        _open_everything(phone, origin, tmp_path)
        phone.goto(f"{origin}/sources")
        _go_offline(phone, server)

        phone.click("[aria-label='Add source']")

        expect(phone.locator("h1")).to_have_text("This needs a connection")
        phone.click("text=Go back")
        expect(phone.locator("h1")).to_have_text("Sources")


def test_delete_on_an_article_needs_a_connection_and_says_so(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        first, _ = _seed_news(tmp_path, [FIRST, SECOND])
        _open_everything(phone, origin, tmp_path)
        phone.goto(f"{origin}/lists/news")
        phone.goto(f"{origin}/items/{first}?from_list=news")
        _go_offline(phone, server)

        phone.click(".act-delete")

        expect(_toast(phone)).to_contain_text("This needs a connection")
        assert phone.url == f"{origin}/items/{first}?from_list=news"
        assert httpx.get(f"{_app(server)}/items/{first}").status_code == 200
