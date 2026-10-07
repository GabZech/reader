from __future__ import annotations

import socket
import threading
import time
from contextlib import contextmanager

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from app.main import app


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextmanager
def _live_server(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started
    try:
        yield f"http://127.0.0.1:{port}", server
    finally:
        server.should_exit = True
        thread.join(timeout=10)


@pytest.fixture
def phone():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            yield browser.new_context(
                viewport={"width": 390, "height": 844}, service_workers="allow"
            ).new_page()
        finally:
            browser.close()


def test_a_page_that_cannot_load_or_be_found_offline_shows_a_retry_page(
    phone, monkeypatch, tmp_path
):
    # When the network fails and the page was never cached, the service worker
    # used to answer with nothing. An installed iPhone app shows that as a plain
    # white screen with no way out.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        server.should_exit = True
        time.sleep(1.5)

        response = phone.goto(f"{origin}/sources/never-cached")

        assert response is not None
        assert "Couldn't load this page" in phone.inner_text("body")
        assert phone.locator("a", has_text="Try again").count() == 1
        assert phone.evaluate("getComputedStyle(document.body).backgroundColor") != (
            "rgba(0, 0, 0, 0)"
        )
        logged = phone.evaluate("JSON.parse(localStorage.getItem('reader-log') || '[]').map(x => x.e)")
        assert "retry-page" in logged


def test_a_page_seen_before_still_opens_offline(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        phone.goto(f"{origin}/lists")
        server.should_exit = True
        time.sleep(1.5)

        phone.goto(f"{origin}/lists")

        assert phone.locator("h1", has_text="Lists").count() == 1


def test_pages_leave_breadcrumbs_that_reach_the_server(phone, monkeypatch, tmp_path):
    # A white screen on the phone can only be traced if the page records what
    # it did and the next page sends that record to the server.
    import httpx

    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/sources")
        phone.wait_for_timeout(3600)
        phone.click(".tabbar >> text=Home")
        phone.wait_for_url(f"{origin}/")
        phone.wait_for_timeout(1500)

        events = httpx.get(f"{origin}/diagnostics?format=json").json()["events"]
        seen = {(e["e"], e["p"]) for e in events}

        assert ("start", "/sources") in seen
        assert ("load", "/sources") in seen
        assert ("check", "/sources") in seen
        assert ("tap", "/sources") in seen
        assert ("start", "/") in seen
        check = next(e for e in events if e["e"] == "check" and e["p"] == "/sources")
        assert "fcp=1" in check["d"]


def test_pages_record_where_the_bar_sits_while_scrolling(phone, monkeypatch, tmp_path):
    # The bottom bar leaves a gap on the phone while scrolling; the log has to
    # carry the numbers (viewport, safe areas, bar position) to explain it.
    import httpx

    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/sources")
        phone.evaluate("document.body.style.minHeight = '3000px'")
        phone.wait_for_timeout(900)
        phone.evaluate("window.scrollTo(0, 400)")
        phone.wait_for_timeout(900)
        phone.click(".tabbar >> text=Home")
        phone.wait_for_url(f"{origin}/")
        phone.wait_for_timeout(1200)

        events = httpx.get(f"{origin}/diagnostics?format=json").json()["events"]
        geo = [e["d"] for e in events if e["e"] == "geo" and e["p"] == "/sources"]

        assert any(d.startswith("load ") for d in geo)
        assert any(d.startswith("scroll ") for d in geo)
        scrolled = next(d for d in geo if d.startswith("scroll "))
        for part in ("ih=", "sh=", "vv=", "y=", "safe=", "bar=", "standalone="):
            assert part in scrolled
