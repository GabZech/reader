"""The Devices page in a real browser: revoking asks first."""

from __future__ import annotations

from datetime import UTC, datetime

from playwright.sync_api import expect
from test_service_worker_browser import _live_server

from app import auth
from app import db as dbmod


def _another_browser(tmp_path, name):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        dbmod.init_db(conn)
        dbmod.create_device(
            conn, "browser", name, auth.token_hash(name), auth.epoch(), datetime.now(UTC)
        )
        conn.commit()
    finally:
        conn.close()


def _names(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [row["name"] for row in dbmod.devices_of_kind(conn, "browser")]
    finally:
        conn.close()


def test_revoking_asks_first_and_cancel_changes_nothing(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _another_browser(tmp_path, "Old laptop")
        phone.goto(f"{origin}/settings/devices")
        row = phone.locator(".device-row", has_text="Old laptop")

        row.get_by_role("button", name="Revoke").click()

        dialog = phone.locator(".swipe-dialog")
        expect(dialog).to_contain_text("Sign out this browser?")
        expect(dialog).to_contain_text("Old laptop")
        dialog.get_by_role("button", name="Cancel").click()
        expect(dialog).to_have_count(0)
        assert "Old laptop" in _names(tmp_path)


def test_confirming_revokes_the_browser_and_says_so(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _another_browser(tmp_path, "Old laptop")
        phone.goto(f"{origin}/settings/devices")

        phone.locator(".device-row", has_text="Old laptop").get_by_role(
            "button", name="Revoke"
        ).click()
        phone.locator(".swipe-dialog").get_by_role("button", name="Revoke").click()

        expect(phone.locator(".toast")).to_contain_text("Signed out Old laptop")
        expect(phone.locator(".device-row", has_text="Old laptop")).to_have_count(0)
        assert "Old laptop" not in _names(tmp_path)


def test_signing_out_every_other_browser_asks_first_too(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _another_browser(tmp_path, "Old laptop")
        _another_browser(tmp_path, "Old tablet")
        phone.goto(f"{origin}/settings/devices")

        phone.get_by_role("button", name="Sign out all other browsers").click()
        phone.locator(".swipe-dialog").get_by_role("button", name="Sign out").click()

        expect(phone.locator(".toast")).to_contain_text("Signed out 2 other browsers")
        assert _names(tmp_path) == ["Test browser"]
