from __future__ import annotations

from contextlib import contextmanager

import pytest
from playwright.sync_api import expect, sync_playwright
from test_app import _add_to_news, _client, _first_item_id
from test_highlight_browser import ORIGIN, _serve_through

from app import db as dbmod

FIRST = "First fixture item"
SECOND = "Second fixture item"


@pytest.fixture
def phone():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            yield browser.new_page(viewport={"width": 390, "height": 844})
        finally:
            browser.close()


@contextmanager
def _news(page, monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        _serve_through(page, client)
        yield client, _first_item_id(tmp_path)


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


def _titles(tmp_path, slug, **view):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [row["title"] for row in dbmod.items_for_list(conn, slug, **view)]
    finally:
        conn.close()


def _exists(tmp_path, item_id):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return dbmod.get_item(conn, item_id) is not None
    finally:
        conn.close()


def _save_later(client, title, tmp_path):
    for row_title, item_id in _ids(tmp_path):
        if row_title == title:
            client.post(f"/items/{item_id}/later")
            return item_id
    raise AssertionError(title)


def _ids(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [(r["title"], r["id"]) for r in conn.execute("SELECT id, title FROM items")]
    finally:
        conn.close()


def test_swiping_left_on_unread_marks_it_read(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path):
        phone.goto(f"{ORIGIN}/lists/news")
        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")
        expect(phone.locator(".actions")).to_contain_text("Read (1)")
        assert _titles(tmp_path, "news", read=True) == [FIRST]


def test_swiping_left_on_read_marks_it_unread(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (client, item_id):
        client.post(f"/items/{item_id}/read?from_list=news")
        phone.goto(f"{ORIGIN}/lists/news?view=read")
        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Unread (2)")
        expect(phone.locator(".actions")).to_contain_text("Read (0)")
        assert _titles(tmp_path, "news", read=True) == []


def test_swiping_left_in_library_archives(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (client, _):
        _save_later(client, FIRST, tmp_path)
        phone.goto(f"{ORIGIN}/lists/later")
        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Library (0)")
        expect(phone.locator(".actions")).to_contain_text("Archive (1)")
        assert _titles(tmp_path, "later", archived=True) == [FIRST]


def test_swiping_left_in_archive_moves_back_to_library(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (client, _):
        item_id = _save_later(client, FIRST, tmp_path)
        client.post(f"/items/{item_id}/archive?from_list=later")
        phone.goto(f"{ORIGIN}/lists/later?view=archive")
        _left(phone, FIRST)

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Library (1)")
        expect(phone.locator(".actions")).to_contain_text("Archive (0)")
        assert _titles(tmp_path, "later") == [FIRST]


def test_a_short_drag_snaps_back_and_changes_nothing(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path):
        phone.goto(f"{ORIGIN}/lists/news")
        _swipe(phone, FIRST, -40)
        _swipe(phone, FIRST, 40)

        expect(_row(phone, FIRST)).to_have_count(1)
        expect(phone.get_by_role("alertdialog")).to_have_count(0)
        assert _titles(tmp_path, "news", read=True) == []


def test_swiping_right_asks_before_deleting(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (_, item_id):
        phone.goto(f"{ORIGIN}/lists/news")
        _right(phone, FIRST)

        dialog = phone.get_by_role("alertdialog")
        expect(dialog).to_be_visible()
        expect(dialog).to_contain_text("Delete this article?")
        expect(dialog).to_contain_text(FIRST)
        assert _exists(tmp_path, item_id)


def test_cancelling_the_delete_keeps_the_article(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (_, item_id):
        phone.goto(f"{ORIGIN}/lists/news")
        _right(phone, FIRST)
        phone.get_by_role("alertdialog").get_by_role("button", name="Cancel").click()

        expect(phone.get_by_role("alertdialog")).to_have_count(0)
        expect(_row(phone, FIRST)).to_have_count(1)
        assert _exists(tmp_path, item_id)


def test_confirming_the_delete_removes_the_article(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (_, item_id):
        phone.goto(f"{ORIGIN}/lists/news")
        _right(phone, FIRST)
        phone.get_by_role("alertdialog").get_by_role("button", name="Delete").click()

        expect(_row(phone, FIRST)).to_have_count(0)
        expect(phone.locator(".actions")).to_contain_text("Unread (1)")
        assert not _exists(tmp_path, item_id)


def test_a_source_page_only_deletes(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (_, item_id):
        source_id = _source_id(tmp_path)
        phone.goto(f"{ORIGIN}/sources/{source_id}/items")
        _left(phone, FIRST)
        expect(_row(phone, FIRST)).to_have_count(1)
        assert _titles(tmp_path, "news", read=True) == []

        _right(phone, FIRST)
        phone.get_by_role("alertdialog").get_by_role("button", name="Delete").click()
        expect(_row(phone, FIRST)).to_have_count(0)
        assert not _exists(tmp_path, item_id)


def test_a_failed_save_puts_the_row_back(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path):
        phone.goto(f"{ORIGIN}/lists/news")
        phone.route(
            f"{ORIGIN}/items/*/read*", lambda route: route.fulfill(status=500, body="")
        )
        _left(phone, FIRST)

        expect(phone.get_by_role("status")).to_contain_text("Couldn't save")
        expect(_row(phone, FIRST)).to_have_count(1)
        expect(phone.locator(".actions")).to_contain_text("Unread (2)")


def test_tapping_a_row_still_opens_the_article(monkeypatch, tmp_path, phone):
    with _news(phone, monkeypatch, tmp_path) as (_, item_id):
        phone.goto(f"{ORIGIN}/lists/news")
        _row(phone, FIRST).locator("a.item").click()
        expect(phone).to_have_url(f"{ORIGIN}/items/{item_id}?from_list=news")


def _source_id(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return conn.execute("SELECT id FROM sources").fetchone()["id"]
    finally:
        conn.close()


@pytest.fixture
def touch_phone():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            context = browser.new_context(
                viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True
            )
            yield context.new_page()
        finally:
            browser.close()


def _finger_swipe(page, title, dx):
    box = _row(page, title).bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    cdp = page.context.new_cdp_session(page)

    def touch(kind, at_x):
        points = [] if kind == "touchEnd" else [{"x": at_x, "y": y}]
        cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": points})

    touch("touchStart", x)
    for step in range(1, 13):
        touch("touchMove", x + dx * step / 12)
    touch("touchEnd", x + dx)


def test_a_finger_swipe_marks_read_on_a_phone(monkeypatch, tmp_path, touch_phone):
    with _news(touch_phone, monkeypatch, tmp_path):
        touch_phone.goto(f"{ORIGIN}/lists/news")
        _finger_swipe(touch_phone, FIRST, -170)

        expect(_row(touch_phone, FIRST)).to_have_count(0)
        assert _titles(tmp_path, "news", read=True) == [FIRST]


def test_a_finger_swipe_right_asks_before_deleting_on_a_phone(
    monkeypatch, tmp_path, touch_phone
):
    with _news(touch_phone, monkeypatch, tmp_path):
        touch_phone.goto(f"{ORIGIN}/lists/news")
        _finger_swipe(touch_phone, FIRST, 170)

        expect(touch_phone.get_by_role("alertdialog")).to_be_visible()
