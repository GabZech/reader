from __future__ import annotations

import json

import pytest
from test_app import _client

from app import diag


@pytest.fixture(autouse=True)
def _fresh_log():
    diag.reset()
    yield
    diag.reset()


def _event(seq: int, name: str = "start", path: str = "/", detail: str = "", launch: str = "abc"):
    return {"s": seq, "t": 1_800_000_000_000 + seq, "e": name, "p": path, "d": detail, "n": "n1", "l": launch}


def _snapshot(client) -> dict:
    return client.get("/diagnostics?format=json").json()


def test_events_from_the_phone_are_kept_and_listed(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        sent = [_event(1, "start", "/sources"), _event(2, "tap", "/", "/")]
        response = client.post("/diag", content=json.dumps(sent))
        assert response.status_code == 200
        events = _snapshot(client)["events"]
        assert [(e["e"], e["p"]) for e in events] == [("start", "/sources"), ("tap", "/")]


def test_the_same_event_sent_twice_is_kept_once(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        body = json.dumps([_event(1), _event(2)])
        client.post("/diag", content=body)
        client.post("/diag", content=body)
        assert len(_snapshot(client)["events"]) == 2


def test_garbage_and_oversized_posts_are_refused(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        assert client.post("/diag", content="not json").status_code == 400
        assert client.post("/diag", content=json.dumps({"s": 1})).status_code == 400
        assert client.post("/diag", content="[" + "0," * 40_000 + "0]").status_code == 413
        assert _snapshot(client)["events"] == []


def test_odd_fields_are_cleaned_not_trusted(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        nasty = {"s": 5, "t": 1, "e": "x" * 500, "p": "/<b>", "d": "y" * 500, "n": 7, "l": None, "extra": "no"}
        client.post("/diag", content=json.dumps([nasty, "junk", 3]))
        (event,) = _snapshot(client)["events"]
        assert len(event["e"]) <= 40 and len(event["d"]) <= 200
        assert "extra" not in event


def test_only_the_newest_events_are_kept(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        for start in range(0, diag.MAX_EVENTS + 100, 50):
            batch = [_event(n) for n in range(start + 1, start + 51)]
            client.post("/diag", content=json.dumps(batch))
        events = _snapshot(client)["events"]
        assert len(events) == diag.MAX_EVENTS
        assert events[-1]["s"] == diag.MAX_EVENTS + 100


def test_page_requests_are_logged_with_status_and_time(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.get("/lists")
        client.get("/nope")
        client.get("/static/styles.css")
        client.get("/health")
        client.post("/diag", content="[]")
        seen = {(r["path"], r["status"]) for r in _snapshot(client)["requests"]}
        assert ("/lists", 200) in seen
        assert ("/nope", 404) in seen
        assert all(not path.startswith("/static") for path, _ in seen)
        assert all(path not in ("/health", "/diag", "/diagnostics") for path, _ in seen)
        timed = next(r for r in _snapshot(client)["requests"] if r["path"] == "/lists")
        assert isinstance(timed["ms"], int) and timed["ms"] >= 0


def test_the_server_reports_when_it_started(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        data = _snapshot(client)
        assert data["started_at"].endswith("Z")
        assert data["uptime_s"] >= 0


def test_the_diagnostics_page_opens_and_settings_links_to_it(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.post("/diag", content=json.dumps([_event(1, "check", "/", "fcp=1")]))
        page = client.get("/diagnostics")
        assert page.status_code == 200
        assert "Diagnostics" in page.text and "check" in page.text
        assert 'href="/diagnostics"' in client.get("/settings").text
