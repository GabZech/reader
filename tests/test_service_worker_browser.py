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


def test_a_page_seen_before_still_opens_offline(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        phone.goto(f"{origin}/lists")
        server.should_exit = True
        time.sleep(1.5)

        phone.goto(f"{origin}/lists")

        assert phone.locator("h1", has_text="Lists").count() == 1
