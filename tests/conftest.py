"""Which browser engine the browser tests run on.

WebKit by default: it is Safari's engine, the one the installed iPhone app
runs on. Chromium on top before a pull request:

    uv run pytest --browsers=webkit,chromium

or set READER_BROWSERS the same way (CI does for pull requests).
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from playwright.sync_api import sync_playwright

from app import auth
from app.db import connect, create_device, find_device, init_db
from app.main import app


def pytest_addoption(parser):
    parser.addoption(
        "--browsers",
        default=os.environ.get("READER_BROWSERS", "webkit"),
        help="comma-separated engines for the browser tests: webkit, chromium",
    )


def pytest_generate_tests(metafunc):
    # Any browser fixture that asks for `engine` runs once per chosen engine.
    if "engine" in metafunc.fixturenames:
        engines = [e.strip() for e in metafunc.config.getoption("browsers").split(",") if e.strip()]
        metafunc.parametrize("engine", engines)


# Fixtures that start a real browser. A test using any of them is marked
# `browser`, so the fast tier is `pytest -m "not browser"`.
BROWSER_FIXTURES = {"phone", "browser_page", "touch_phone"}


def pytest_collection_modifyitems(items):
    for item in items:
        if BROWSER_FIXTURES & set(item.fixturenames):
            item.add_marker("browser")


# The page learns it is offline the way a phone tells it: navigator.onLine
# and the offline/online events. Kept per tab, so it holds across pages.
TELL_ONLINE_STATE = """
Object.defineProperty(Navigator.prototype, "onLine", {
  configurable: true,
  get: () => sessionStorage.getItem("test-offline") !== "1",
});
"""


# WebKit is Safari's engine, which the installed iPhone app runs on: bugs
# there (saving a form offline, the worker's lifetime) never showed in
# Chromium. Which engines run is set by --browsers, above.
@pytest.fixture
def phone(engine):
    with sync_playwright() as p:
        browser = getattr(p, engine).launch()
        try:
            page = browser.new_context(
                viewport={"width": 390, "height": 844}, service_workers="allow"
            ).new_page()
            page.add_init_script(TELL_ONLINE_STATE)
            yield page
        finally:
            browser.close()


# The app asks everyone to sign in. Every test starts signed in, so the
# existing ones stay about what they test: an outer layer adds a valid
# sign-in cookie to each request, and makes sure the test's own database
# knows that sign-in. Tests about signing in itself ask for the `anonymous`
# fixture to be a stranger instead.
TEST_PASSWORD = "correct horse battery staple"
TEST_TOKEN = "test-sign-in-token"


class _SignedInForTests:
    on = True

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and self.on:
            conn = connect()
            try:
                init_db(conn)
                digest = auth.token_hash(TEST_TOKEN)
                if find_device(conn, digest) is None:
                    create_device(
                        conn, "browser", "Test browser", digest, auth.epoch(), datetime.now(UTC)
                    )
                conn.commit()
            finally:
                conn.close()
            headers = [(k, v) for k, v in scope["headers"] if k != b"cookie"]
            cookies = [v for k, v in scope["headers"] if k == b"cookie"]
            cookies.append(f"{auth.SESSION_COOKIE}={TEST_TOKEN}".encode())
            headers.append((b"cookie", b"; ".join(cookies)))
            scope = {**scope, "headers": headers}
        await self.inner(scope, receive, send)


app.add_middleware(_SignedInForTests)


@pytest.fixture(autouse=True)
def _a_password_is_set(monkeypatch):
    monkeypatch.setenv("READER_PASSWORD", TEST_PASSWORD)
    auth.forget_failed_logins()


@pytest.fixture
def anonymous():
    _SignedInForTests.on = False
    yield
    _SignedInForTests.on = True
