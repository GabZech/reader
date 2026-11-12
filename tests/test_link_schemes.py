"""Only web addresses become links: an item's Original and its thumbnail.

An address with any other scheme (`javascript:`, `data:`, ...) would run or
load something as the app when tapped, so it is never stored, and one already
stored is never drawn.
"""

from __future__ import annotations

import html
import re
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import db as dbmod
from app.main import app
from app.urls import css_url, web_url

PAGE = "<html><body><article><p>" + "word " * 80 + "</p></article></body></html>"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    monkeypatch.delenv("OBSIDIAN_GITHUB_TOKEN", raising=False)
    with TestClient(app) as test_client:
        yield test_client


def _item(tmp_path, item_id):
    conn = sqlite3.connect(tmp_path / "reader.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    finally:
        conn.close()


@pytest.mark.parametrize(
    "raw",
    [
        "javascript:alert(1)",
        " JaVa\tScRiPt:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:x",
        "/relative/path",
        "https:no-host",
        "",
        None,
    ],
)
def test_web_url_refuses_anything_but_an_absolute_web_address(raw):
    assert web_url(raw) is None


@pytest.mark.parametrize(
    ("raw", "kept"),
    [
        ("https://example.test/a?b=1#c", "https://example.test/a?b=1#c"),
        ("http://example.test/", "http://example.test/"),
        ("  https://example.test/x  ", "https://example.test/x"),
        ("//cdn.example.test/i.png", "https://cdn.example.test/i.png"),
    ],
)
def test_web_url_keeps_a_web_address(raw, kept):
    assert web_url(raw) == kept


def test_css_url_cannot_break_out_of_its_quotes():
    sneaky = "https://img.test/a.png');background:url('https://evil.test/x"
    kept = css_url(sneaky)
    for char in "'\"()\\ ":
        assert char not in kept


def test_capture_refuses_an_address_that_is_not_a_web_page(client, tmp_path):
    response = client.post("/capture", data={"url": "javascript:alert(document.cookie)//", "html": PAGE})
    assert response.status_code == 400
    conn = sqlite3.connect(tmp_path / "reader.db")
    try:
        assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0
    finally:
        conn.close()


def test_a_feed_link_that_is_not_a_web_address_is_not_stored(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        dbmod.init_db(conn)
        dbmod.upsert_item(
            conn,
            source_id="captured",
            guid="g1",
            title="t",
            author=None,
            url="javascript:alert(1)",
            published_at=None,
            body_html="<p>x</p>",
            image_url="javascript:alert(2)",
            word_count=1,
        )
        row = conn.execute("SELECT url, image_url FROM items WHERE guid = 'g1'").fetchone()
    finally:
        conn.close()
    assert tuple(row) == (None, None)


def _plant(tmp_path, url, image_url):
    """An item stored before this rule existed."""
    conn = sqlite3.connect(tmp_path / "reader.db")
    try:
        conn.execute(
            "INSERT INTO items (source_id, guid, title, url, body_html, image_url, word_count)"
            " VALUES ('captured', 'old', 'Old', ?, '<p>x</p>', ?, 1)",
            (url, image_url),
        )
        item_id = conn.execute("SELECT id FROM items WHERE guid = 'old'").fetchone()[0]
        conn.execute("INSERT INTO item_lists (item_id, list_slug, added_at)"
            " VALUES (?, 'later', '2026-11-01T00:00:00+00:00')", (item_id,))
        conn.commit()
    finally:
        conn.close()
    return item_id


def test_an_item_stored_with_a_script_link_shows_no_original_link(client, tmp_path):
    client.get("/")  # makes the database
    item_id = _plant(tmp_path, "javascript:alert(1)", None)
    page = client.get(f"/items/{item_id}").text
    assert "javascript:" not in page
    assert ">Original<" not in page


def test_a_stored_thumbnail_cannot_break_out_of_its_style(client, tmp_path):
    client.get("/")
    _plant(tmp_path, "https://ok.test/", "https://img.test/a.png');background:url('https://evil.test/x")
    page = client.get("/lists/later").text
    style = html.unescape(re.search(r'class="thumb"[^>]*style="([^"]*)"', page).group(1))
    # The browser reads the attribute decoded: one url('...') and nothing after it.
    assert re.fullmatch(r"background-image:url\('[^'()\\ ]*'\)", style), style
