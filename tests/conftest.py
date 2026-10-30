"""Which browser engine the browser tests run on.

WebKit by default: it is Safari's engine, the one the installed iPhone app
runs on. Chromium on top before a pull request:

    uv run pytest --browsers=webkit,chromium

or set READER_BROWSERS the same way (CI does for pull requests).
"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import sync_playwright


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
