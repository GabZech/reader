"""A page on screen catches up with what changed on the server behind the phone's back.

The phone shows a stored copy of Home and the lists, and fetches them again each
time the app opens. Something saved from elsewhere (the Shortcut, the computer,
a newsletter) used to show only on the next visit; now the page on screen
reloads once the new copy is stored, unless the reader is in the middle of
something. Run on a real server (see test_service_worker_browser).
"""

from __future__ import annotations

from playwright.sync_api import expect
from test_offline_actions_browser import _ready
from test_service_worker_browser import (
    _live_server,
    _saved_article,
    _wait_for,
    quick_reopen,
)

from app import diag


def _run_precache(phone):
    """Ask the worker for a refresh, and wait for it to finish."""
    phone.wait_for_timeout(2500)  # the worker spaces runs 2 seconds apart (quick_reopen)
    before = _finished_runs(phone)
    phone.evaluate("navigator.serviceWorker.controller.postMessage({ type: 'precache', keep: [] })")
    _wait_for(lambda: _finished_runs(phone) > before)


def _finished_runs(phone):
    # The phone sends its breadcrumbs to the server (Diagnostics) as it goes.
    return sum(
        1
        for event in diag.snapshot()["events"]
        if event["e"] == "sw-precache" and "images+" in event["d"]
    )


def _open_read_later(phone, origin):
    _ready(phone, origin, "/lists/later")
    phone.goto(f"{origin}/lists/later")
    expect(phone.locator(".actions")).to_contain_text("Library (1)")


def test_something_saved_elsewhere_appears_on_the_page_already_open(phone, monkeypatch, tmp_path):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _saved_article(origin, tmp_path, "first", "<p>one</p>")
        _open_read_later(phone, origin)

        _saved_article(origin, tmp_path, "second", "<p>two</p>")  # what the Shortcut does
        _run_precache(phone)

        expect(phone.locator(".actions")).to_contain_text("Library (2)")


def test_a_page_that_did_not_change_is_left_alone(phone, monkeypatch, tmp_path):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _saved_article(origin, tmp_path, "first", "<p>one</p>")
        _open_read_later(phone, origin)
        phone.evaluate("window.__still_here = true")

        _run_precache(phone)
        phone.wait_for_timeout(1500)

        assert phone.evaluate("window.__still_here === true")


def test_the_page_waits_while_the_reader_has_a_finger_down(phone, monkeypatch, tmp_path):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _saved_article(origin, tmp_path, "first", "<p>one</p>")
        _open_read_later(phone, origin)
        phone.evaluate("window.__still_here = true")
        phone.evaluate(
            "document.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }))"
        )

        _saved_article(origin, tmp_path, "second", "<p>two</p>")
        _run_precache(phone)
        phone.wait_for_timeout(1200)
        assert phone.evaluate("window.__still_here === true")

        phone.evaluate("document.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }))")
        expect(phone.locator(".actions")).to_contain_text("Library (2)")


def test_a_page_with_a_dialog_open_is_not_reloaded_under_the_reader(phone, monkeypatch, tmp_path):
    quick_reopen(monkeypatch, tmp_path)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _saved_article(origin, tmp_path, "first", "<p>one</p>")
        _open_read_later(phone, origin)
        phone.evaluate("window.__still_here = true")
        phone.evaluate(
            "document.body.insertAdjacentHTML('beforeend', '<div class=\"swipe-dialog-backdrop\"></div>')"
        )

        _saved_article(origin, tmp_path, "second", "<p>two</p>")
        _run_precache(phone)
        phone.wait_for_timeout(1200)

        assert phone.evaluate("window.__still_here === true")
