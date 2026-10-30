"""The password gate: who gets in, how a device stays in, and who is locked out."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta

import pytest
from conftest import TEST_PASSWORD
from fastapi.testclient import TestClient

from app import auth
from app.main import app

NAVIGATE = {"Sec-Fetch-Mode": "navigate", "Accept": "text/html,application/xhtml+xml"}
IPHONE_SAFARI = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
)


@pytest.fixture
def stranger(anonymous, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    return TestClient(app, follow_redirects=False)


def _clock(monkeypatch, moment):
    monkeypatch.setattr(auth, "now", lambda: moment)


def _sign_in(client, password=TEST_PASSWORD, **headers):
    return client.post("/login", data={"password": password}, headers=headers)


def _devices(tmp_path):
    conn = sqlite3.connect(tmp_path / "reader.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM devices ORDER BY id").fetchall()
    finally:
        conn.close()


# ---------- who is turned away ----------


def test_a_stranger_opening_a_page_is_sent_to_the_login_page(stranger):
    response = stranger.get("/lists", headers=NAVIGATE)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=%2Flists"


def test_a_stranger_reaching_for_data_gets_a_plain_refusal_not_a_redirect(stranger):
    # The phone's own background fetches follow redirects: sent to the login
    # page they would store it as the page they asked for.
    for method, path in (
        ("get", "/items/1"),
        ("get", "/offline/articles"),
        ("post", "/sync"),
        ("post", "/items/1/archive"),
        ("post", "/capture"),
    ):
        response = getattr(stranger, method)(path, headers={"Accept": "*/*"})
        assert response.status_code == 401, path
        assert "location" not in response.headers


def test_a_browser_without_fetch_metadata_is_treated_by_what_it_accepts(stranger):
    page = stranger.get("/", headers={"Accept": "text/html"})
    assert page.status_code == 303
    data = stranger.get("/", headers={"Accept": "*/*"})
    assert data.status_code == 401


def test_a_form_posted_by_a_stranger_goes_to_the_login_page(stranger):
    response = stranger.post("/lists/add", data={"name": "x"}, headers=NAVIGATE)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


@pytest.mark.parametrize(
    "path",
    ["/health", "/login", "/static/styles.css", "/sw.js", "/manifest.webmanifest"],
)
def test_the_few_open_paths_stay_open(stranger, path):
    assert stranger.get(path, headers=NAVIGATE).status_code == 200


def test_a_made_up_cookie_is_a_stranger(stranger):
    stranger.cookies.set(auth.SESSION_COOKIE, "not-a-real-token")
    assert stranger.get("/", headers=NAVIGATE).status_code == 303


def test_without_a_password_set_nobody_gets_in(stranger, monkeypatch):
    monkeypatch.delenv("LOGIN_PASSWORD")
    assert stranger.get("/", headers=NAVIGATE).status_code == 303
    page = stranger.get("/login")
    assert page.status_code == 200
    assert "no password" in page.text.lower()
    refused = _sign_in(stranger, TEST_PASSWORD)
    assert refused.status_code == 401
    assert "isn't right" not in refused.text
    assert _sign_in(stranger, "").status_code == 401
    assert stranger.get("/", headers=NAVIGATE).status_code == 303


# ---------- signing in ----------


def test_the_login_page_asks_for_a_password_and_nothing_else(stranger):
    page = stranger.get("/login")
    assert page.status_code == 200
    assert 'type="password"' in page.text
    assert 'autocomplete="current-password"' in page.text
    assert "tabbar" not in page.text
    # The app's script registers the service worker and starts downloading.
    assert "/static/app.js" not in page.text


def test_the_right_password_signs_in_and_lands_where_the_visitor_was_going(stranger):
    response = stranger.post("/login", data={"password": TEST_PASSWORD, "next": "/lists"})
    assert response.status_code == 303
    assert response.headers["location"] == "/lists"
    assert stranger.get("/lists", headers=NAVIGATE).status_code == 200


def test_a_wrong_password_says_so_and_does_not_sign_in(stranger):
    response = _sign_in(stranger, "nope")
    assert response.status_code == 401
    assert "That password isn" in response.text
    assert auth.SESSION_COOKIE not in response.headers.get("set-cookie", "")
    assert stranger.get("/", headers=NAVIGATE).status_code == 303


def test_the_cookie_is_private_and_lasts(stranger):
    response = _sign_in(stranger, **{"X-Forwarded-Proto": "https"})
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{auth.SESSION_COOKIE}=")
    lowered = cookie.lower()
    assert "httponly" in lowered
    assert "samesite=lax" in lowered
    assert "path=/" in lowered
    max_age = int(lowered.split("max-age=")[1].split(";")[0])
    assert max_age >= 100 * 24 * 3600


def test_the_cookie_is_secure_on_https_only(stranger):
    secure = stranger.post(
        "/login", data={"password": TEST_PASSWORD}, headers={"X-Forwarded-Proto": "https"}
    )
    assert "secure" in secure.headers["set-cookie"].lower()
    plain = stranger.post("/login", data={"password": TEST_PASSWORD})
    assert "secure" not in plain.headers["set-cookie"].lower()


def test_where_to_go_next_must_be_a_path_on_this_app(stranger):
    for hostile in ("//evil.test/x", "https://evil.test", "/\\evil.test", "javascript:alert(1)"):
        response = stranger.post("/login", data={"password": TEST_PASSWORD, "next": hostile})
        assert response.headers["location"] == "/", hostile


def test_a_signed_in_visitor_is_sent_on_from_the_login_page(stranger):
    _sign_in(stranger)
    response = stranger.get("/login", headers=NAVIGATE)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_the_server_keeps_only_a_scrambled_copy_of_the_sign_in(stranger, tmp_path):
    response = _sign_in(stranger)
    token = response.headers["set-cookie"].split("=")[1].split(";")[0]
    (device,) = _devices(tmp_path)
    assert token not in tuple(device)
    assert device["token_hash"] == auth.token_hash(token)


def test_each_sign_in_is_its_own_device_named_from_the_browser(stranger, tmp_path):
    _sign_in(stranger, **{"User-Agent": IPHONE_SAFARI})
    other = TestClient(app, follow_redirects=False)
    _sign_in(other, **{"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/120 Edg/120"})
    names = [row["name"] for row in _devices(tmp_path)]
    assert names == ["iPhone · Safari", "Windows · Edge"]


def test_a_sign_in_from_the_installed_app_is_named_so(stranger, tmp_path):
    stranger.post(
        "/login",
        data={"password": TEST_PASSWORD, "installed": "1"},
        headers={"User-Agent": IPHONE_SAFARI},
    )
    assert _devices(tmp_path)[0]["name"] == "iPhone · Safari (installed app)"


@pytest.mark.parametrize(
    ("agent", "name"),
    [
        (IPHONE_SAFARI, "iPhone · Safari"),
        ("Mozilla/5.0 (iPhone) AppleWebKit/605 CriOS/120 Mobile/15E148", "iPhone · Chrome"),
        ("Mozilla/5.0 (iPad; CPU OS 17) AppleWebKit/605 Version/17 Mobile Safari/604", "iPad · Safari"),
        ("Mozilla/5.0 (Linux; Android 14) Chrome/120 Mobile Safari/537", "Android · Chrome"),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) Chrome/120 Safari/537", "Mac · Chrome"),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) Version/17 Safari/605", "Mac · Safari"),
        ("Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0", "Windows · Firefox"),
        ("Mozilla/5.0 (X11; Linux x86_64) Chrome/120 Safari/537", "Linux · Chrome"),
        ("Mozilla/5.0 (Windows NT 10.0) Chrome/120 Safari/537 OPR/105", "Windows · Opera"),
        ("curl/8.0", "Unknown device"),
        ("", "Unknown device"),
    ],
)
def test_a_device_is_named_from_its_browser(agent, name):
    assert auth.device_name(agent) == name


# ---------- staying in, and going out ----------


def test_a_device_stays_in_while_it_keeps_being_used(stranger, monkeypatch):
    start = datetime(2026, 11, 1, 9, tzinfo=UTC)
    _clock(monkeypatch, start)
    _sign_in(stranger)
    for days in (20, 40, 60):
        _clock(monkeypatch, start + timedelta(days=days))
        assert stranger.get("/", headers=NAVIGATE).status_code == 200


def test_a_device_unused_for_thirty_days_is_signed_out(stranger, monkeypatch, tmp_path):
    start = datetime(2026, 11, 1, 9, tzinfo=UTC)
    _clock(monkeypatch, start)
    _sign_in(stranger)
    _clock(monkeypatch, start + timedelta(days=30, minutes=1))
    assert stranger.get("/", headers=NAVIGATE).status_code == 303
    assert _devices(tmp_path) == []


def test_a_device_just_inside_thirty_days_is_still_in(stranger, monkeypatch):
    start = datetime(2026, 11, 1, 9, tzinfo=UTC)
    _clock(monkeypatch, start)
    _sign_in(stranger)
    _clock(monkeypatch, start + timedelta(days=29, hours=23))
    assert stranger.get("/", headers=NAVIGATE).status_code == 200


def test_using_a_device_notes_when_without_a_write_on_every_tap(stranger, monkeypatch, tmp_path):
    start = datetime(2026, 11, 1, 9, tzinfo=UTC)
    _clock(monkeypatch, start)
    _sign_in(stranger)
    _clock(monkeypatch, start + timedelta(minutes=1))
    stranger.get("/", headers=NAVIGATE)
    assert _devices(tmp_path)[0]["last_used_at"] == start.isoformat()
    _clock(monkeypatch, start + timedelta(hours=2))
    stranger.get("/", headers=NAVIGATE)
    assert _devices(tmp_path)[0]["last_used_at"] == (start + timedelta(hours=2)).isoformat()


def test_changing_the_password_signs_every_browser_out(stranger, monkeypatch):
    _sign_in(stranger)
    assert stranger.get("/", headers=NAVIGATE).status_code == 200
    monkeypatch.setenv("LOGIN_PASSWORD", "a different one")
    assert stranger.get("/", headers=NAVIGATE).status_code == 303
    assert _sign_in(stranger, "a different one").status_code == 303
    assert stranger.get("/", headers=NAVIGATE).status_code == 200


def test_signing_out_ends_this_device_only(stranger, tmp_path):
    _sign_in(stranger)
    other = TestClient(app, follow_redirects=False)
    _sign_in(other)
    response = stranger.post("/logout", headers=NAVIGATE)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert stranger.get("/", headers=NAVIGATE).status_code == 303
    assert other.get("/", headers=NAVIGATE).status_code == 200
    assert len(_devices(tmp_path)) == 1


def test_settings_has_a_sign_out_button(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    response = TestClient(app).get("/settings")
    assert response.status_code == 200
    assert 'action="/logout"' in response.text
    assert "Sign out of this device" in response.text


# ---------- guessing ----------


def test_five_wrong_passwords_lock_that_network_out_for_fifteen_minutes(stranger, monkeypatch):
    start = datetime(2026, 11, 1, 9, tzinfo=UTC)
    _clock(monkeypatch, start)
    for _ in range(auth.LOCK_AFTER - 1):
        assert _sign_in(stranger, "nope").status_code == 401
    # The fifth already says so.
    assert _sign_in(stranger, "nope").status_code == 429
    # Even the right password is refused while locked, or guessing goes on.
    locked = _sign_in(stranger)
    assert locked.status_code == 429
    assert "Too many wrong tries" in locked.text
    assert "15 minutes" in locked.text
    assert "disabled" in locked.text
    _clock(monkeypatch, start + timedelta(minutes=10))
    assert "5 minutes" in _sign_in(stranger).text
    _clock(monkeypatch, start + timedelta(minutes=15, seconds=1))
    assert _sign_in(stranger).status_code == 303


def test_a_lockout_is_per_network_so_a_stranger_cannot_lock_the_owner_out(stranger):
    for _ in range(auth.LOCK_AFTER + 1):
        _sign_in(stranger, "nope", **{"Fly-Client-IP": "203.0.113.9"})
    assert _sign_in(stranger, **{"Fly-Client-IP": "203.0.113.9"}).status_code == 429
    assert _sign_in(stranger, **{"Fly-Client-IP": "198.51.100.4"}).status_code == 303


def test_the_network_is_read_from_the_hosting_header_not_a_spoofable_one(stranger):
    for _ in range(auth.LOCK_AFTER):
        _sign_in(
            stranger,
            "nope",
            **{"Fly-Client-IP": "203.0.113.9", "X-Forwarded-For": "1.1.1.1"},
        )
    again = _sign_in(
        stranger, **{"Fly-Client-IP": "203.0.113.9", "X-Forwarded-For": "2.2.2.2"}
    )
    assert again.status_code == 429


def test_a_right_password_clears_the_count_of_wrong_ones(stranger):
    for _ in range(auth.LOCK_AFTER - 1):
        _sign_in(stranger, "nope")
    assert _sign_in(stranger).status_code == 303
    stranger.post("/logout", headers=NAVIGATE)
    for _ in range(auth.LOCK_AFTER - 1):
        assert _sign_in(stranger, "nope").status_code == 401


def test_a_wrong_password_is_compared_without_leaking_how_close_it_was():
    assert not auth.password_matches("")
    assert not auth.password_matches(TEST_PASSWORD + " ")
    assert auth.password_matches(TEST_PASSWORD)


def test_the_login_page_shows_a_lockout_that_is_already_running(stranger):
    for _ in range(auth.LOCK_AFTER):
        _sign_in(stranger, "nope")
    page = stranger.get("/login")
    assert "Too many wrong tries" in page.text
    assert "disabled" in page.text


# ---------- the address the request names ----------


@pytest.mark.parametrize(
    "host",
    ["testserver/static", "testserver/login?", "testserver/health#", "x/static/a?", "a@testserver"],
)
def test_a_crafted_host_header_cannot_open_a_protected_page(stranger, host):
    # The gate once read the path back out of a URL built from the Host
    # header, so "Host: x/static" made /lists look like /static/lists.
    for path in ("/lists", "/", "/settings", "/offline/articles"):
        response = stranger.get(path, headers={**NAVIGATE, "Host": host})
        assert response.status_code in (303, 400, 401), (host, path)
        assert "Lists" not in response.text or response.status_code != 200


def test_a_crafted_host_header_cannot_mint_a_save_key(stranger, tmp_path):
    response = stranger.post(
        "/settings/devices/keys",
        data={"kind": "shortcut"},
        headers={**NAVIGATE, "Host": "testserver/static"},
    )
    assert response.status_code in (303, 400, 401)
    assert "rk_" not in response.text


@pytest.mark.parametrize("host", ["testserver", "127.0.0.1:8000", "reader.fly.dev", "[::1]:8000"])
def test_an_ordinary_host_header_is_fine(stranger, host):
    assert stranger.get("/health", headers={"Host": host}).status_code == 200


def test_pages_cannot_be_framed_by_another_site(stranger):
    for path in ("/login", "/health"):
        response = stranger.get(path)
        assert response.headers["x-frame-options"] == "DENY"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_the_gate_holds_even_if_a_crafted_host_got_past_the_host_check(stranger, monkeypatch):
    # Two layers: the Host check, and a gate that reads the router's own path.
    monkeypatch.setattr(auth, "host_is_plain", lambda host: True)
    for host in ("testserver/static", "x/login?", "x/health#"):
        response = stranger.get("/lists", headers={**NAVIGATE, "Host": host})
        assert response.status_code == 303, host


def test_an_ipv6_network_is_counted_as_one_however_many_addresses_it_uses(stranger):
    # One IPv6 line comes with a /64 block: a new address per guess must not
    # mean a fresh count.
    for n in range(auth.LOCK_AFTER):
        _sign_in(stranger, "nope", **{"Fly-Client-IP": f"2001:db8:1:2::{n + 1}"})
    assert _sign_in(stranger, **{"Fly-Client-IP": "2001:db8:1:2::99"}).status_code == 429
    assert _sign_in(stranger, **{"Fly-Client-IP": "2001:db8:1:3::1"}).status_code == 303
