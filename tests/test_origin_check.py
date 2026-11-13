"""A form or request sent from another website is refused.

The sign-in cookie is SameSite=Lax, which on fly.dev already keeps other
sites' forms out; on a domain of our own, a sibling subdomain would count as
the same site. So a change sent with another site's Origin is refused before
anything runs. A request with no Origin (the iPhone Shortcut, tools) is let
through to the usual sign-in or key checks.
"""

from __future__ import annotations

import re
import sqlite3

import pytest
from conftest import TEST_PASSWORD
from fastapi.testclient import TestClient

from app.main import app

NAVIGATE = {"Sec-Fetch-Mode": "navigate", "Accept": "text/html"}
CAPTURE = {"url": "https://blog.test/post", "html": "<html><body><p>hi</p></body></html>"}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client


def _lists(tmp_path) -> list[str]:
    conn = sqlite3.connect(tmp_path / "reader.db")
    try:
        return [row[0] for row in conn.execute("SELECT name FROM lists")]
    finally:
        conn.close()


@pytest.mark.parametrize(
    "origin", ["https://evil.test", "https://reader.evil.test", "http://testserver.evil.test", "null"]
)
def test_a_change_from_another_site_is_refused(client, tmp_path, origin):
    client.get("/")
    response = client.post("/lists/add", data={"name": "Planted"}, headers={"Origin": origin})
    assert response.status_code == 403
    assert "Planted" not in _lists(tmp_path)


@pytest.mark.parametrize("headers", [{"Origin": "http://testserver"}, {}])
def test_a_change_from_the_app_itself_or_with_no_origin_goes_through(client, tmp_path, headers):
    client.get("/")
    response = client.post("/lists/add", data={"name": "Mine"}, headers=headers)
    assert response.status_code == 303
    assert "Mine" in _lists(tmp_path)


def test_the_origin_is_compared_with_this_apps_host_and_port(client):
    response = client.post(
        "/lists/add", data={"name": "x"}, headers={"Origin": "http://testserver:8080"}
    )
    assert response.status_code == 403


def test_a_page_read_from_another_site_is_not_refused(client):
    # A link followed from elsewhere is a GET, and changes nothing.
    assert client.get("/", headers={"Origin": "https://evil.test"}).status_code == 200


def test_another_site_cannot_sign_a_browser_in(anonymous, client):
    response = client.post(
        "/login", data={"password": TEST_PASSWORD}, headers={"Origin": "https://evil.test"}
    )
    assert response.status_code == 403
    assert "set-cookie" not in response.headers


def test_the_shortcut_still_saves_with_its_key(anonymous, client):
    client.post("/login", data={"password": TEST_PASSWORD})
    page = client.post("/settings/devices/keys", data={"kind": "shortcut"}, headers=NAVIGATE)
    key = re.search(r"rk_[A-Za-z0-9_-]+", page.text).group(0)
    tool = TestClient(app)
    assert tool.post("/capture", data={**CAPTURE, "key": key}).status_code == 200
    # The old bookmarklet posted the same key from the page being saved.
    from_a_page = tool.post(
        "/capture", data={**CAPTURE, "key": key}, headers={"Origin": "https://blog.test"}
    )
    assert from_a_page.status_code == 403
