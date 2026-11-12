"""The bookmarklet: no key, a hand-off to a Reader tab.

It opens Reader's own page in a new tab and passes it the page being saved,
as the browser rendered it. That tab saves it with the browser's own sign-in,
so nothing secret ever runs inside the page being saved.
"""

from __future__ import annotations

import html
import re
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

NAVIGATE = {"Sec-Fetch-Mode": "navigate", "Accept": "text/html"}
PAGE = (Path(__file__).parent / "fixtures" / "capture" / "blog.html").read_text(encoding="utf-8")


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app, base_url="https://reader.test") as test_client:
        yield test_client


def _devices(tmp_path) -> int:
    conn = sqlite3.connect(tmp_path / "reader.db")
    try:
        return conn.execute("SELECT COUNT(*) FROM devices WHERE kind != 'browser'").fetchone()[0]
    finally:
        conn.close()


def test_the_bookmarklet_page_offers_a_button_with_no_key_in_it(client, tmp_path):
    page = client.get("/settings/bookmarklet", headers=NAVIGATE)
    assert page.status_code == 200
    link = html.unescape(re.search(r'class="bookmarklet" href="([^"]*)"', page.text).group(1))
    assert link.startswith("javascript:")
    assert 'var o="https://reader.test"' in link
    assert 'o+"/capture/from-page?url="' in link
    assert "outerHTML" in link
    # Handed only to this app's own tab, never broadcast to any page.
    assert "postMessage(" in link and '"*"' not in link and "'*'" not in link
    assert not re.search(r"rk_|ak_|key", link)
    assert _devices(tmp_path) == 0


def test_the_bookmarklet_page_needs_a_sign_in(anonymous, client):
    response = client.get("/settings/bookmarklet", headers=NAVIGATE, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


def test_the_hand_off_page_saves_with_the_browsers_sign_in(client):
    page = client.get("/capture/from-page?url=https%3A%2F%2Fblog.test%2Fpost", headers=NAVIGATE)
    assert page.status_code == 200
    assert "data-capture-handoff" in page.text
    form = re.search(r"<form[^>]*data-capture-handoff[^>]*>", page.text).group(0)
    assert 'method="post"' in form
    assert 'action="/capture?format=html"' in form
    assert 'enctype="multipart/form-data"' in form
    # Nothing is saved from the address alone: only the hand-off, or a tap.
    assert "Save the address only" in page.text
    assert 'value="https://blog.test/post"' in page.text


def test_the_hand_off_page_sends_a_stranger_to_sign_in_and_back(anonymous, client):
    response = client.get(
        "/capture/from-page?url=https%3A%2F%2Fblog.test%2Fpost",
        headers=NAVIGATE,
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "next=%2Fcapture%2Ffrom-page%3Furl%3D" in response.headers["location"]


def test_the_hand_off_page_never_shows_an_address_that_is_not_a_web_page(client):
    page = client.get("/capture/from-page?url=javascript%3Aalert(1)", headers=NAVIGATE)
    assert page.status_code == 200
    assert "javascript:" not in page.text


def test_a_large_rendered_page_can_be_saved(client):
    big = PAGE.replace("</body>", "<p>" + "padding " * 400_000 + "</p></body>")
    assert len(big) > 3_000_000
    response = client.post(
        "/capture?format=html",
        files={"url": (None, "https://blog.test/big"), "html": (None, big)},
        headers=NAVIGATE,
    )
    assert response.status_code == 200
    assert "Saved to Read later" in response.text


def test_a_large_page_from_the_shortcut_can_be_saved_too(client):
    # The Shortcut sends a plain form, which the server also caps per field.
    big = PAGE.replace("</body>", "<p>" + "padding " * 400_000 + "</p></body>")
    response = client.post("/capture", data={"url": "https://blog.test/big2", "html": big})
    assert response.status_code == 200
