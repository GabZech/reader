"""The app's pages work under its own script policy: its scripts run and
the browser refuses nothing. (Every browser test runs under the policy; this
one says so outright, for every kind of page.)"""

from __future__ import annotations

from conftest import TEST_PASSWORD, _SignedInForTests, wait_for_js
from playwright.sync_api import sync_playwright
from test_offline_actions_browser import FIRST, _seed_news
from test_service_worker_browser import _live_server


def test_the_apps_own_scripts_run_and_nothing_is_refused(engine, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server), sync_playwright() as p:
        _seed_news(tmp_path, [FIRST])
        browser = getattr(p, engine).launch()
        try:
            page = browser.new_context(service_workers="allow").new_page()
            refused: list[str] = []
            page.on(
                "console",
                lambda message: refused.append(message.text)
                if "Content Security Policy" in message.text or "Refused" in message.text
                else None,
            )

            _SignedInForTests.on = False
            try:
                page.goto(f"{origin}/login")
                assert page.evaluate("document.documentElement.dataset.theme") == "dark"
                page.fill("input[type=password]", TEST_PASSWORD)
                page.click("button[type=submit]")
                page.wait_for_url(f"{origin}/")
            finally:
                _SignedInForTests.on = True

            for path in ["/", "/lists/news", "/settings", "/settings/devices/keys/new"]:
                page.goto(f"{origin}{path}")
                # theme.js ran before the page drew, trace.js noted the page.
                assert page.evaluate("document.documentElement.dataset.theme") == "dark"
                wait_for_js(page, "(localStorage.getItem('reader-log') || '').includes(location.pathname)")

            # app.js ran: it registers the worker.
            wait_for_js(page, "navigator.serviceWorker.getRegistration().then(r => !!r)")
            assert refused == []
        finally:
            browser.close()
