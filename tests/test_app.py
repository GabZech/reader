from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.ingest import ingest_xml
from app.main import app

FIXTURE = Path(__file__).parent / "fixtures" / "feed.xml"


def test_home_shell(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "Home" in response.text
    assert "News" in response.text
    assert "Read later" in response.text
    assert "Favourite channels" in response.text
    assert "Lists" in response.text
    assert "Sources" in response.text


def test_sync_then_item_is_readable(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    xml = FIXTURE.read_text(encoding="utf-8")
    monkeypatch.setattr(
        "app.main.ingest_url",
        lambda conn, url: ingest_xml(conn, xml),
    )
    with TestClient(app) as client:
        synced = client.post("/sync")
        assert synced.status_code == 200
        assert synced.json()["created"] == 2
        assert synced.json()["kept"] == 2
        home = client.get("/")
        assert "First fixture item" in home.text
        news = client.get("/lists/news")
        assert "Second fixture item" in news.text
        item = client.get("/items/1")
        assert item.status_code == 200
        assert "Hello from the fixture feed" in item.text
        sources = client.get("/sources")
        assert "Fixture news" in sources.text
