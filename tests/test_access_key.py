"""The access key: lets a developer's tooling use the whole app except the
parts that manage devices and keys. Sent as a bearer header, tied to the password."""

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
DATA = {"Accept": "*/*"}
START = datetime(2026, 11, 3, 15, 0, tzinfo=UTC)
PAGE = (Path(__file__).parent / "fixtures" / "capture" / "blog.html").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def _real_sign_ins(anonymous, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    monkeypatch.setattr(auth, "now", lambda: START)


def _owner():
    client = TestClient(app, follow_redirects=False)
    client.post("/login", data={"password": TEST_PASSWORD})
    return client


def _make(owner, kind="access"):
    response = owner.post("/settings/devices/keys", data={"kind": kind}, headers=NAVIGATE)
    assert response.status_code == 200
    return re.search(r"[ar]k_[A-Za-z0-9_-]+", response.text).group(0), response


def _tool(key):
    return TestClient(app, follow_redirects=False, headers={"Authorization": f"Bearer {key}"})


def _rows(tmp_path, kind="access"):
    conn = sqlite3.connect(tmp_path / "reader.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM devices WHERE kind = ? ORDER BY id", (kind,)).fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def _later(monkeypatch, **delta):
    moment = START + timedelta(**delta)
    monkeypatch.setattr(auth, "now", lambda: moment)


# ---------- making one ----------


def test_the_add_page_offers_it_with_what_it_can_do():
    page = _owner().get("/settings/devices/keys/new", headers=NAVIGATE).text
    assert "Claude access" in page
    assert "everything except" in page.lower()


def test_the_key_is_shown_once_with_how_to_send_it(tmp_path):
    key, response = _make(_owner())
    assert key.startswith("ak_")
    assert "shown only once" in response.text
    assert "Authorization: Bearer" in response.text
    assert 'data-copy-text="' + key in response.text
    (row,) = _rows(tmp_path)
    assert row["name"] == "Claude access"
    assert key not in tuple(row)
    assert row["token_hash"] == auth.token_hash(key)
    assert row["epoch"] == auth.epoch()


def test_a_stranger_cannot_make_one(tmp_path):
    stranger = TestClient(app, follow_redirects=False)
    stranger.post("/settings/devices/keys", data={"kind": "access"}, headers=NAVIGATE)
    assert _rows(tmp_path) == []


# ---------- what it can do ----------


def test_it_reads_pages_and_data():
    key, _ = _make(_owner())
    tool = _tool(key)
    for path in ("/", "/lists", "/sources", "/settings", "/offline/articles"):
        assert tool.get(path, headers=DATA).status_code == 200, path
    report = tool.get("/diagnostics?format=json", headers=DATA)
    assert report.status_code == 200
    assert "requests" in report.json()


def test_it_changes_things_too():
    key, _ = _make(_owner())
    tool = _tool(key)
    assert tool.post("/lists/add", data={"name": "From the tool"}, headers=NAVIGATE).status_code == 303
    assert "From the tool" in tool.get("/lists", headers=DATA).text
    assert tool.post("/capture", data={"url": "https://blog.test/x", "html": PAGE}).status_code == 200


def test_it_cannot_touch_devices_or_keys(tmp_path):
    owner = _owner()
    key, _ = _make(owner)
    other_id = _rows(tmp_path)[0]["id"]
    tool = _tool(key)
    for method, path, data in (
        ("get", "/settings/devices", None),
        ("get", "/settings/devices/keys/new", None),
        ("post", "/settings/devices/keys", {"kind": "access"}),
        ("post", "/settings/devices/sign-out-others", None),
        ("post", f"/settings/devices/{other_id}/revoke", None),
        ("get", f"/settings/devices/{other_id}/rename", None),
        ("post", f"/settings/devices/{other_id}/rename", {"name": "x"}),
        ("post", "/logout", None),
    ):
        response = getattr(tool, method)(path, headers=DATA, **({"data": data} if data else {}))
        assert response.status_code == 403, path
    assert len(_rows(tmp_path)) == 1
    assert len(_rows(tmp_path, "browser")) == 1


@pytest.mark.parametrize("how", ["query", "form", "cookie", "wrong-scheme", "empty"])
def test_it_only_counts_as_a_bearer_header(how):
    key, _ = _make(_owner())
    tool = TestClient(app, follow_redirects=False)
    if how == "query":
        response = tool.get("/lists", params={"key": key, "access_key": key}, headers=DATA)
    elif how == "form":
        response = tool.post("/lists/add", data={"name": "x", "key": key}, headers=DATA)
    elif how == "cookie":
        tool.cookies.set(auth.SESSION_COOKIE, key)
        response = tool.get("/lists", headers=DATA)
    elif how == "wrong-scheme":
        response = tool.get("/lists", headers={**DATA, "Authorization": f"Token {key}"})
    else:
        response = tool.get("/lists", headers={**DATA, "Authorization": "Bearer "})
    assert response.status_code == 401


def test_a_save_key_is_not_an_access_key_and_the_reverse():
    owner = _owner()
    save, _ = _make(owner, "shortcut")
    access, _ = _make(owner)
    assert _tool(save).get("/lists", headers=DATA).status_code == 401
    form = TestClient(app, follow_redirects=False).post(
        "/capture", data={"url": "https://blog.test/y", "html": PAGE, "key": access}
    )
    assert form.status_code == 401


def test_a_made_up_key_is_refused():
    assert _tool("ak_made-up").get("/lists", headers=DATA).status_code == 401


# ---------- keeping and ending it ----------


def test_it_does_not_expire_from_not_being_used(monkeypatch):
    key, _ = _make(_owner())
    _later(monkeypatch, days=400)
    assert _tool(key).get("/lists", headers=DATA).status_code == 200


def test_changing_the_password_ends_it(monkeypatch, tmp_path):
    key, _ = _make(_owner())
    monkeypatch.setenv("LOGIN_PASSWORD", "a different one")
    assert _tool(key).get("/lists", headers=DATA).status_code == 401
    assert _rows(tmp_path) == []


def test_without_a_password_set_it_is_refused(monkeypatch):
    key, _ = _make(_owner())
    monkeypatch.delenv("LOGIN_PASSWORD")
    assert _tool(key).get("/lists", headers=DATA).status_code == 401


def test_revoking_it_stops_it_at_once(tmp_path):
    owner = _owner()
    key, _ = _make(owner)
    key_id = _rows(tmp_path)[0]["id"]
    assert owner.post(f"/settings/devices/{key_id}/revoke", headers=NAVIGATE).status_code == 303
    assert _tool(key).get("/lists", headers=DATA).status_code == 401


def test_signing_out_other_browsers_leaves_it_alone(tmp_path):
    owner = _owner()
    key, _ = _make(owner)
    _owner()
    owner.post("/settings/devices/sign-out-others", headers=NAVIGATE)
    assert _tool(key).get("/lists", headers=DATA).status_code == 200


def test_using_it_is_noted_from_the_first_time(monkeypatch, tmp_path):
    owner = _owner()
    key, _ = _make(owner)
    _later(monkeypatch, seconds=20)
    _tool(key).get("/lists", headers=DATA)
    assert _rows(tmp_path)[0]["last_used_at"] == (START + timedelta(seconds=20)).isoformat()
    assert "not used yet" not in owner.get("/settings/devices", headers=NAVIGATE).text


def _devices_page(owner):
    """The Devices page split into its <title> and its body, so a section that
    lands in the title instead of the body is not mistaken for one on the page."""
    html = owner.get("/settings/devices", headers=NAVIGATE).text
    title = re.search(r"<title>(.*?)</title>", html, re.DOTALL).group(1)
    return title, html.split("</head>", 1)[1]


def test_the_devices_page_lists_it_apart_with_what_it_can_do():
    owner = _owner()
    assert "Access keys" not in _devices_page(owner)[1]
    _make(owner)
    title, page = _devices_page(owner)
    assert title.strip() == "Devices"
    assert "Access keys" in page
    assert "Claude access" in page
    assert "Everything except devices and keys" in page
    assert 'data-confirm-title="Revoke this access key?"' in page
    # After the save keys, as the last section.
    assert page.index("Save keys") < page.index("Access keys")


def test_settings_counts_it():
    owner = _owner()
    assert "access key" not in owner.get("/settings", headers=NAVIGATE).text
    _make(owner)
    assert "1 access key" in owner.get("/settings", headers=NAVIGATE).text


def test_it_does_not_get_around_the_host_check():
    key, _ = _make(_owner())
    response = _tool(key).get("/lists", headers={**DATA, "Host": "testserver/static"})
    assert response.status_code == 400
