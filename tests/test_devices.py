"""The Devices page: every browser that can open the library, and ending any of them."""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime, timedelta

import pytest
from conftest import TEST_PASSWORD
from fastapi.testclient import TestClient

from app import auth
from app.main import app

NAVIGATE = {"Sec-Fetch-Mode": "navigate", "Accept": "text/html"}
IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
)
MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605 Chrome/120 Safari/537"
WINDOWS = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537 Chrome/120 Edg/120"
START = datetime(2026, 11, 3, 15, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _real_sign_ins(anonymous, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    monkeypatch.setattr(auth, "now", lambda: START)


def _browser(agent, installed=False):
    client = TestClient(app, follow_redirects=False)
    client.post(
        "/login",
        data={"password": TEST_PASSWORD, "installed": "1" if installed else "0"},
        headers={"User-Agent": agent},
    )
    return client


def _rows(tmp_path):
    conn = sqlite3.connect(tmp_path / "reader.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM devices ORDER BY id").fetchall()
    finally:
        conn.close()


def _id_of(tmp_path, name):
    (row,) = [r for r in _rows(tmp_path) if r["name"] == name]
    return row["id"]


def _later(monkeypatch, **delta):
    moment = START + timedelta(**delta)
    monkeypatch.setattr(auth, "now", lambda: moment)


def test_the_page_lists_each_browser_and_marks_this_one(tmp_path):
    phone = _browser(IPHONE, installed=True)
    _browser(MAC)
    page = phone.get("/settings/devices", headers=NAVIGATE)
    assert page.status_code == 200
    assert "iPhone · Safari (installed app)" in page.text
    assert "Mac · Chrome" in page.text
    assert page.text.count("This device") == 1
    mac_id = _id_of(tmp_path, "Mac · Chrome")
    own_id = _id_of(tmp_path, "iPhone · Safari (installed app)")
    assert f'action="/settings/devices/{mac_id}/revoke"' in page.text
    assert f'action="/settings/devices/{own_id}/revoke"' not in page.text
    assert f'href="/settings/devices/{own_id}/rename"' in page.text


def test_this_device_comes_first_then_the_most_recently_used(monkeypatch):
    mac = _browser(MAC)
    _later(monkeypatch, hours=1)
    _browser(WINDOWS)
    _later(monkeypatch, hours=2)
    phone = _browser(IPHONE)
    _later(monkeypatch, hours=3)
    mac.get("/", headers=NAVIGATE)  # the Mac is used again
    page = phone.get("/settings/devices", headers=NAVIGATE).text
    order = [page.index(name) for name in ("iPhone · Safari", "Mac · Chrome", "Windows · Edge")]
    assert order == sorted(order)


def test_each_row_says_when_it_signed_in_and_when_it_was_last_used(monkeypatch):
    _browser(WINDOWS)
    _later(monkeypatch, days=18)
    phone = _browser(IPHONE)
    page = phone.get("/settings/devices", headers=NAVIGATE).text
    assert "Signed in today, 12:00" in page
    assert "last used just now" in page
    assert "Signed in 3 Nov" in page
    assert "last used 18 days ago" in page


@pytest.mark.parametrize(
    ("delta", "said"),
    [
        (timedelta(seconds=30), "just now"),
        (timedelta(minutes=14), "14 minutes ago"),
        (timedelta(hours=1, minutes=5), "1 hour ago"),
        (timedelta(hours=5), "5 hours ago"),
        (timedelta(days=1, hours=2), "yesterday"),
        (timedelta(days=9), "9 days ago"),
    ],
)
def test_last_used_is_said_in_ordinary_words(monkeypatch, tmp_path, delta, said):
    _browser(MAC)
    _later(monkeypatch, hours=2)
    phone = _browser(IPHONE)
    conn = sqlite3.connect(tmp_path / "reader.db")
    conn.execute(
        "UPDATE devices SET last_used_at = ? WHERE name = 'Mac · Chrome'",
        ((auth.now() - delta).isoformat(),),
    )
    conn.commit()
    conn.close()
    assert f"last used {said}" in phone.get("/settings/devices", headers=NAVIGATE).text


def test_revoking_a_browser_signs_it_out_at_once(tmp_path):
    phone = _browser(IPHONE)
    mac = _browser(MAC)
    assert mac.get("/", headers=NAVIGATE).status_code == 200
    mac_id = _id_of(tmp_path, "Mac · Chrome")
    response = phone.post(f"/settings/devices/{mac_id}/revoke", headers=NAVIGATE)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/settings/devices")
    assert "flash=" in response.headers["location"]
    assert mac.get("/", headers=NAVIGATE).status_code == 303
    assert mac.get("/items/1", headers={"Accept": "*/*"}).status_code == 401
    assert "Mac · Chrome" not in phone.get("/settings/devices", headers=NAVIGATE).text


def test_a_browser_cannot_revoke_itself_from_here(tmp_path):
    phone = _browser(IPHONE)
    own_id = _id_of(tmp_path, "iPhone · Safari")
    assert phone.post(f"/settings/devices/{own_id}/revoke", headers=NAVIGATE).status_code == 400
    assert phone.get("/", headers=NAVIGATE).status_code == 200


def test_revoking_one_already_gone_is_quietly_fine(tmp_path):
    phone = _browser(IPHONE)
    response = phone.post("/settings/devices/9999/revoke", headers=NAVIGATE)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/settings/devices")


def test_signing_out_every_other_browser_keeps_this_one(tmp_path):
    phone = _browser(IPHONE)
    mac = _browser(MAC)
    windows = _browser(WINDOWS)
    response = phone.post("/settings/devices/sign-out-others", headers=NAVIGATE)
    assert response.status_code == 303
    assert "2+other+browsers" in response.headers["location"].replace("%20", "+")
    assert mac.get("/", headers=NAVIGATE).status_code == 303
    assert windows.get("/", headers=NAVIGATE).status_code == 303
    assert phone.get("/", headers=NAVIGATE).status_code == 200
    assert [r["name"] for r in _rows(tmp_path)] == ["iPhone · Safari"]


def test_signing_out_others_with_none_left_says_so():
    phone = _browser(IPHONE)
    response = phone.post("/settings/devices/sign-out-others", headers=NAVIGATE)
    assert "No+other+browsers" in response.headers["location"].replace("%20", "+")


def test_the_sign_out_others_button_only_shows_when_there_are_others():
    phone = _browser(IPHONE)
    assert "Sign out all other browsers" not in phone.get("/settings/devices", headers=NAVIGATE).text
    _browser(MAC)
    assert "Sign out all other browsers" in phone.get("/settings/devices", headers=NAVIGATE).text


def test_a_browser_can_be_renamed(tmp_path):
    phone = _browser(IPHONE)
    mac = _browser(MAC)
    mac_id = _id_of(tmp_path, "Mac · Chrome")
    form = phone.get(f"/settings/devices/{mac_id}/rename", headers=NAVIGATE)
    assert form.status_code == 200
    assert 'value="Mac · Chrome"' in form.text
    done = phone.post(
        f"/settings/devices/{mac_id}/rename", data={"name": "  Work laptop  "}, headers=NAVIGATE
    )
    assert done.status_code == 303
    assert done.headers["location"].startswith("/settings/devices")
    assert "Work laptop" in phone.get("/settings/devices", headers=NAVIGATE).text
    assert mac.get("/", headers=NAVIGATE).status_code == 200


def test_a_name_cannot_be_empty_or_endless(tmp_path):
    phone = _browser(IPHONE)
    own_id = _id_of(tmp_path, "iPhone · Safari")
    empty = phone.post(f"/settings/devices/{own_id}/rename", data={"name": "   "}, headers=NAVIGATE)
    assert empty.status_code == 200
    assert "field-error" in empty.text
    assert _id_of(tmp_path, "iPhone · Safari") == own_id
    phone.post(f"/settings/devices/{own_id}/rename", data={"name": "x" * 200}, headers=NAVIGATE)
    assert len(_rows(tmp_path)[0]["name"]) == 60


def test_renaming_one_that_is_gone_is_a_not_found():
    phone = _browser(IPHONE)
    assert phone.get("/settings/devices/9999/rename", headers=NAVIGATE).status_code == 404
    assert (
        phone.post("/settings/devices/9999/rename", data={"name": "x"}, headers=NAVIGATE).status_code
        == 404
    )


def test_a_stranger_cannot_reach_the_devices_page_or_end_a_device(tmp_path):
    _browser(IPHONE)
    _browser(MAC)
    mac_id = _id_of(tmp_path, "Mac · Chrome")
    stranger = TestClient(app, follow_redirects=False)
    assert stranger.get("/settings/devices", headers=NAVIGATE).status_code == 303
    assert stranger.post(f"/settings/devices/{mac_id}/revoke", headers=NAVIGATE).status_code == 303
    assert stranger.post("/settings/devices/sign-out-others", headers=NAVIGATE).status_code == 303
    assert len(_rows(tmp_path)) == 2


def test_settings_links_to_devices_with_a_count():
    phone = _browser(IPHONE)
    page = phone.get("/settings", headers=NAVIGATE).text
    assert 'href="/settings/devices"' in page
    assert "1 browser" in page
    _browser(MAC)
    assert "2 browsers" in phone.get("/settings", headers=NAVIGATE).text
    assert re.search(r"Security.*Devices.*Sign out of this device", page, re.DOTALL)
