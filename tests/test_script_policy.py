"""Pages run only the app's own script files.

The Content-Security-Policy refuses inline scripts, inline event handlers and
`javascript:` links, so markup that slips into a page cannot run as the app.
"""

from __future__ import annotations

import re

import pytest
from conftest import TEST_PASSWORD
from fastapi.testclient import TestClient

from app.main import app

NAVIGATE = {"Sec-Fetch-Mode": "navigate", "Accept": "text/html"}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as test_client:
        yield test_client


def _policy(response) -> dict[str, str]:
    header = response.headers["content-security-policy"]
    return {
        part.split(" ", 1)[0]: part.split(" ", 1)[1] if " " in part else ""
        for part in (p.strip() for p in header.split(";"))
        if part
    }


@pytest.mark.parametrize("path", ["/", "/login", "/health", "/lists", "/settings"])
def test_every_response_allows_only_the_apps_own_scripts(client, path):
    policy = _policy(client.get(path, headers=NAVIGATE))
    assert policy["script-src"] == "'self'"
    assert policy["object-src"] == "'none'"
    assert policy["base-uri"] == "'none'"
    assert policy["frame-ancestors"] == "'none'"


INLINE_SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)(?![^>]*application/json)[^>]*>", re.IGNORECASE)
INLINE_HANDLER = re.compile(r"<[a-z][^>]*\son[a-z]+\s*=", re.IGNORECASE)


@pytest.mark.parametrize(
    "path", ["/", "/login", "/lists", "/sources", "/settings", "/settings/devices", "/settings/devices/keys/new", "/settings/bookmarklet",
             "/capture/from-page?url=https%3A%2F%2Fblog.test%2Fpost"]
)
def test_no_page_carries_an_inline_script(client, path):
    page = client.get(path, headers=NAVIGATE).text
    assert not INLINE_SCRIPT.search(page)
    assert not INLINE_HANDLER.search(page)


@pytest.mark.parametrize("kind", ["shortcut", "access"])
def test_the_page_showing_a_new_key_carries_no_inline_script(anonymous, client, kind):
    client.post("/login", data={"password": TEST_PASSWORD})
    page = client.post("/settings/devices/keys", data={"kind": kind}, headers=NAVIGATE).text
    assert not INLINE_SCRIPT.search(page)
    assert not INLINE_HANDLER.search(page)
