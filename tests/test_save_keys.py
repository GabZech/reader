"""Save keys: what the bookmarklet and the iPhone Shortcut use to send a page to Read later."""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from conftest import TEST_PASSWORD
from fastapi.testclient import TestClient

from app import auth
from app.main import app

NAVIGATE = {"Sec-Fetch-Mode": "navigate", "Accept": "text/html"}
START = datetime(2026, 11, 3, 15, 0, tzinfo=UTC)
PAGE = (Path(__file__).parent / "fixtures" / "capture" / "blog.html").read_text(encoding="utf-8")
CAPTURE = {"url": "https://blog.test/post", "html": PAGE}


@pytest.fixture(autouse=True)
def _real_sign_ins(anonymous, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    monkeypatch.setattr(auth, "now", lambda: START)


def _browser():
    client = TestClient(app, follow_redirects=False)
    client.post("/login", data={"password": TEST_PASSWORD})
    return client


def _make_key(client, kind="shortcut"):
    response = client.post("/settings/devices/keys", data={"kind": kind}, headers=NAVIGATE)
    assert response.status_code == 200
    return re.search(r"rk_[A-Za-z0-9_-]+", response.text).group(0), response


def _rows(tmp_path, kind="key"):
    conn = sqlite3.connect(tmp_path / "reader.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM devices WHERE kind = ? ORDER BY id", (kind,)).fetchall()
    except sqlite3.OperationalError:
        return []  # nothing ever opened the database
    finally:
        conn.close()


def _later(monkeypatch, **delta):
    moment = START + timedelta(**delta)
    monkeypatch.setattr(auth, "now", lambda: moment)


# ---------- making one ----------


def test_the_add_page_offers_the_two_tools():
    page = _browser().get("/settings/devices/keys/new", headers=NAVIGATE)
    assert page.status_code == 200
    assert "iPhone Shortcut" in page.text
    assert "Computer bookmarklet" in page.text
    assert 'action="/settings/devices/keys"' in page.text


def test_a_shortcut_key_is_shown_once_with_where_to_put_it(tmp_path):
    key, response = _make_key(_browser(), "shortcut")
    assert "shown only once" in response.text
    assert "Copy key" in response.text
    assert 'data-copy-text="' + key in response.text
    (row,) = _rows(tmp_path)
    assert row["name"] == "iPhone Shortcut"


def test_a_bookmarklet_key_is_built_into_the_button(tmp_path):
    key, response = _make_key(_browser(), "bookmarklet")
    link = re.search(r'href="(javascript:[^"]*)"', response.text).group(1)
    assert key in link
    assert "/capture" in link
    assert "outerHTML" in link
    assert _rows(tmp_path)[0]["name"] == "Computer bookmarklet"


def test_only_a_scrambled_copy_of_the_key_is_kept(tmp_path):
    key, _ = _make_key(_browser())
    (row,) = _rows(tmp_path)
    assert key not in tuple(row)
    assert row["token_hash"] == auth.token_hash(key)
    assert row["epoch"] is None


def test_the_key_is_not_shown_again_on_the_devices_page():
    client = _browser()
    key, _ = _make_key(client)
    assert key not in client.get("/settings/devices", headers=NAVIGATE).text


def test_an_unknown_kind_of_key_is_refused(tmp_path):
    response = _browser().post(
        "/settings/devices/keys", data={"kind": "carrier-pigeon"}, headers=NAVIGATE
    )
    assert response.status_code == 400
    assert _rows(tmp_path) == []


def test_a_stranger_cannot_make_a_key(tmp_path):
    stranger = TestClient(app, follow_redirects=False)
    response = stranger.post("/settings/devices/keys", data={"kind": "shortcut"}, headers=NAVIGATE)
    assert response.status_code == 303
    assert _rows(tmp_path) == []


# ---------- using one ----------


def test_a_key_lets_a_page_be_saved_to_read_later():
    key, _ = _make_key(_browser())
    tool = TestClient(app, follow_redirects=False)
    response = tool.post("/capture", data={**CAPTURE, "key": key})
    assert response.status_code == 200
    assert response.json()["item_url"].startswith("/items/")


def test_a_key_works_for_the_bookmarklets_confirmation_page_too():
    key, _ = _make_key(_browser(), "bookmarklet")
    tool = TestClient(app, follow_redirects=False)
    response = tool.post("/capture?format=html", data={**CAPTURE, "key": key}, headers=NAVIGATE)
    assert response.status_code == 200
    assert "Saved to Read later" in response.text


@pytest.mark.parametrize("key", [None, "", "rk_made-up", " "])
def test_without_a_good_key_nothing_is_saved(key):
    tool = TestClient(app, follow_redirects=False)
    data = dict(CAPTURE) if key is None else {**CAPTURE, "key": key}
    for headers in ({"Accept": "*/*"}, NAVIGATE):
        response = tool.post("/capture", data=data, headers=headers)
        assert response.status_code == 401
        assert "location" not in response.headers


def test_a_key_opens_nothing_but_saving():
    key, _ = _make_key(_browser())
    tool = TestClient(app, follow_redirects=False)
    for method, path in (("get", "/"), ("get", "/lists"), ("post", "/sync"), ("get", "/settings")):
        sent = getattr(tool, method)(path, headers={"Accept": "*/*"}, **(
            {"data": {"key": key}} if method == "post" else {"params": {"key": key}}
        ))
        assert sent.status_code == 401, path


def test_a_key_is_not_a_sign_in_when_used_as_a_cookie():
    key, _ = _make_key(_browser())
    tool = TestClient(app, follow_redirects=False)
    tool.cookies.set(auth.SESSION_COOKIE, key)
    assert tool.get("/", headers=NAVIGATE).status_code == 303


def test_a_signed_in_browser_can_still_save_without_a_key():
    response = _browser().post("/capture", data=CAPTURE)
    assert response.status_code == 200


def test_without_a_password_set_even_a_key_is_refused(monkeypatch):
    key, _ = _make_key(_browser())
    monkeypatch.delenv("LOGIN_PASSWORD")
    tool = TestClient(app, follow_redirects=False)
    assert tool.post("/capture", data={**CAPTURE, "key": key}).status_code == 401


# ---------- keeping and ending them ----------


def test_a_key_never_expires_and_survives_a_password_change(monkeypatch):
    key, _ = _make_key(_browser())
    _later(monkeypatch, days=400)
    monkeypatch.setenv("LOGIN_PASSWORD", "a different one")
    tool = TestClient(app, follow_redirects=False)
    assert tool.post("/capture", data={**CAPTURE, "key": key}).status_code == 200


def test_using_a_key_notes_when(monkeypatch, tmp_path):
    key, _ = _make_key(_browser())
    _later(monkeypatch, days=2)
    TestClient(app).post("/capture", data={**CAPTURE, "key": key})
    assert _rows(tmp_path)[0]["last_used_at"] == (START + timedelta(days=2)).isoformat()


def test_revoking_a_key_stops_it_at_once(tmp_path):
    client = _browser()
    key, _ = _make_key(client)
    key_id = _rows(tmp_path)[0]["id"]
    response = client.post(f"/settings/devices/{key_id}/revoke", headers=NAVIGATE)
    assert response.status_code == 303
    assert "flash=" in response.headers["location"]
    tool = TestClient(app, follow_redirects=False)
    assert tool.post("/capture", data={**CAPTURE, "key": key}).status_code == 401
    assert _rows(tmp_path) == []


def test_signing_out_other_browsers_leaves_the_keys_alone(tmp_path):
    client = _browser()
    key, _ = _make_key(client)
    _browser()
    client.post("/settings/devices/sign-out-others", headers=NAVIGATE)
    assert len(_rows(tmp_path)) == 1
    assert TestClient(app).post("/capture", data={**CAPTURE, "key": key}).status_code == 200


def test_the_devices_page_lists_keys_apart_from_browsers(monkeypatch):
    client = _browser()
    _make_key(client, "shortcut")
    _make_key(client, "bookmarklet")
    _later(monkeypatch, days=9)
    page = client.get("/settings/devices", headers=NAVIGATE).text
    assert "Save keys" in page
    assert "iPhone Shortcut" in page
    assert "Computer bookmarklet" in page
    assert "Saves to Read later" in page
    assert "not used yet" in page
    assert 'href="/settings/devices/keys/new"' in page
    assert "Add a save key" in page
    assert page.count('data-confirm-title="Revoke this save key?"') == 2


def test_a_key_that_was_used_says_when(monkeypatch):
    client = _browser()
    key, _ = _make_key(client)
    _later(monkeypatch, days=2)
    TestClient(app).post("/capture", data={**CAPTURE, "key": key})
    _later(monkeypatch, days=4)
    page = client.get("/settings/devices", headers=NAVIGATE).text
    assert "last used 2 days ago" in page


def test_the_save_keys_section_is_there_even_with_none():
    page = _browser().get("/settings/devices", headers=NAVIGATE).text
    assert "Save keys" in page
    assert "Add a save key" in page
    assert "can only send a page to Read later" in page


def test_settings_counts_the_keys_next_to_the_browsers():
    client = _browser()
    assert "save key" not in client.get("/settings", headers=NAVIGATE).text
    _make_key(client)
    assert "1 browser · 1 save key" in client.get("/settings", headers=NAVIGATE).text
    _make_key(client, "bookmarklet")
    assert "1 browser · 2 save keys" in client.get("/settings", headers=NAVIGATE).text


def test_the_first_use_of_a_key_is_noted_at_once(monkeypatch, tmp_path):
    client = _browser()
    key, _ = _make_key(client)
    _later(monkeypatch, seconds=20)
    TestClient(app).post("/capture", data={**CAPTURE, "key": key})
    assert "not used yet" not in client.get("/settings/devices", headers=NAVIGATE).text
    assert _rows(tmp_path)[0]["last_used_at"] == (START + timedelta(seconds=20)).isoformat()
