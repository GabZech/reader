"""The server fetches pages only from the public internet.

A save key, or a feed, could otherwise point the server at addresses only it
can reach (itself, Fly's private network, a cloud metadata address) and read
what comes back. Every hop of a redirect is checked the same way.
"""

from __future__ import annotations

import http.server
import threading

import httpx
import pytest
from fastapi.testclient import TestClient

from app import ingest
from app.main import app

PUBLIC = "93.184.215.14"


@pytest.fixture
def resolve(monkeypatch):
    """Names resolve to what the test says, never through real DNS."""
    table: dict[str, list[str]] = {}

    def addresses(host: str) -> list[str]:
        return table.get(host, [PUBLIC])

    monkeypatch.setattr(ingest, "_addresses", addresses)
    return table


@pytest.fixture
def served(monkeypatch):
    """Answers fetches without a network; records what was asked."""
    asked: list[str] = []
    routes: dict[str, httpx.Response] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        asked.append(str(request.url))
        return routes.get(str(request.url), httpx.Response(200, text="<html>ok</html>"))

    monkeypatch.setattr(ingest, "_TRANSPORT", httpx.MockTransport(handler))
    return asked, routes


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://localhost/",
        "http://[::1]/",
        "http://10.0.0.5/",
        "http://192.168.1.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[fdaa::3]:4280/",
        "http://[::ffff:127.0.0.1]/",
        "http://0.0.0.0/",
    ],
)
def test_a_private_or_internal_address_is_refused_before_any_request(url, resolve, served):
    resolve["localhost"] = ["127.0.0.1"]
    asked, _routes = served
    with pytest.raises(ingest.BlockedAddress):
        ingest.fetch_url(url)
    assert asked == []


def test_a_name_that_resolves_to_a_private_address_is_refused(resolve, served):
    resolve["sneaky.test"] = [PUBLIC, "10.1.2.3"]
    with pytest.raises(ingest.BlockedAddress):
        ingest.fetch_url("https://sneaky.test/")
    assert served[0] == []


def test_a_redirect_to_a_private_address_is_refused(resolve, served):
    asked, routes = served
    routes["https://public.test/go"] = httpx.Response(
        302, headers={"Location": "http://169.254.169.254/latest/meta-data/"}
    )
    with pytest.raises(ingest.BlockedAddress):
        ingest.fetch_url("https://public.test/go")
    assert asked == ["https://public.test/go"]


def test_a_redirect_to_another_scheme_is_refused(resolve, served):
    _asked, routes = served
    routes["https://public.test/go"] = httpx.Response(302, headers={"Location": "file:///etc/passwd"})
    with pytest.raises(ingest.BlockedAddress):
        ingest.fetch_url("https://public.test/go")


def test_a_public_redirect_is_followed(resolve, served):
    asked, routes = served
    routes["https://public.test/old"] = httpx.Response(301, headers={"Location": "/new"})
    final_url, text = ingest.fetch_url("https://public.test/old")
    assert final_url == "https://public.test/new"
    assert text == "<html>ok</html>"
    assert asked == ["https://public.test/old", "https://public.test/new"]


def test_endless_redirects_stop(resolve, served):
    _asked, routes = served
    routes["https://public.test/loop"] = httpx.Response(302, headers={"Location": "/loop"})
    with pytest.raises(httpx.TooManyRedirects):
        ingest.fetch_url("https://public.test/loop")


def test_a_refused_address_counts_as_unreachable():
    # Every caller already treats an unreachable host as skippable.
    assert issubclass(ingest.BlockedAddress, httpx.TransportError)


def test_capture_cannot_read_a_server_on_the_host_itself(monkeypatch, tmp_path):
    hits: list[str] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            hits.append(self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><head><title>internal secret</title></head></html>")

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    try:
        with TestClient(app) as client:
            response = client.post(
                "/capture", data={"url": f"http://127.0.0.1:{server.server_address[1]}/"}
            )
    finally:
        server.shutdown()
    assert response.status_code >= 400
    assert "internal secret" not in response.text
    assert hits == []
