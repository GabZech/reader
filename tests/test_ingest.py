from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.db import (
    add_source_to_list,
    connect,
    format_when,
    init_db,
    insert_source,
    is_item_in_list,
    item_in_window,
    items_for_list,
)
from app.ingest import capture_article, ingest_xml, parse_feed

FIXTURE = Path(__file__).parent / "fixtures" / "feed.xml"
CAPTURE_FIXTURES = Path(__file__).parent / "fixtures" / "capture"
SOURCE_ID = "fixture-rss"


def _source(conn, window: str | None = "week") -> None:
    insert_source(
        conn,
        source_id=SOURCE_ID,
        kind="rss",
        title="RSS",
        feed_url="https://example.test/feed.xml",
        backfill=None,
    )
    add_source_to_list(conn, SOURCE_ID, "news", window)


def test_parse_feed_reads_items():
    entries = parse_feed(FIXTURE.read_text(encoding="utf-8"), SOURCE_ID)
    assert [entry["title"] for entry in entries] == [
        "First fixture item",
        "Second fixture item",
    ]
    assert "Hello from the fixture feed" in entries[0]["body_html"]


def test_ingest_xml_stores_news_items(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    _source(conn)
    result = ingest_xml(conn, FIXTURE.read_text(encoding="utf-8"), SOURCE_ID)
    conn.commit()
    assert result["created"] == 2
    assert result["kept"] == 2
    assert result["feed_total"] == 2
    items = items_for_list(
        conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=UTC)
    )
    assert [row["title"] for row in items] == [
        "First fixture item",
        "Second fixture item",
    ]
    again = ingest_xml(conn, FIXTURE.read_text(encoding="utf-8"), SOURCE_ID)
    assert again["created"] == 0


def test_ingest_xml_keeps_only_latest_five_when_limited(tmp_path):
    items_xml = "\n".join(
        f"""
        <item>
          <title>Item {n}</title>
          <link>https://example.test/news/{n}</link>
          <guid>https://example.test/news/{n}</guid>
          <pubDate>Wed, {n:02d} Aug 2026 08:00:00 +0000</pubDate>
          <description>&lt;p&gt;Body {n}&lt;/p&gt;</description>
        </item>
        """
        for n in range(1, 8)
    )
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0"><channel>
      <title>Many</title>
      {items_xml}
    </channel></rss>"""
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    _source(conn, window=None)
    result = ingest_xml(conn, xml, SOURCE_ID, limit=5)
    conn.commit()
    assert result["feed_total"] == 7
    assert result["kept"] == 5
    titles = [
        row["title"]
        for row in items_for_list(
            conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=UTC)
        )
    ]
    assert titles == ["Item 7", "Item 6", "Item 5", "Item 4", "Item 3"]


def test_item_in_window_day_and_week():
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    assert item_in_window("day", "2026-08-20T08:00:00+00:00", now)
    assert not item_in_window("day", "2026-08-19T08:00:00+00:00", now)
    assert item_in_window("week", "2026-08-14T08:00:00+00:00", now)
    assert not item_in_window("week", "2026-08-12T08:00:00+00:00", now)
    assert item_in_window(None, "2026-01-01T00:00:00+00:00", now)


def test_format_when_today_and_date():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
    assert format_when("2026-08-20T08:00:00+00:00", now) == "Today"
    assert format_when("2026-08-19T08:00:00+00:00", now) == "Yesterday"
    assert format_when("2026-08-17T08:00:00+00:00", now) == "17/08/26"


def _capture_fixture(name: str) -> str:
    return (CAPTURE_FIXTURES / name).read_text(encoding="utf-8")


def test_capture_article_cleans_a_real_page_and_adds_it_to_read_later(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
    item_id, title = capture_article(conn, url, html=_capture_fixture("blog.html"))
    conn.commit()
    assert "Hiten Shah" in title
    assert is_item_in_list(conn, item_id, "later")
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["url"] == url
    assert "skill library" in item["body_html"]
    assert item["word_count"] > 0


def test_capture_article_falls_back_to_a_server_fetch_when_given_no_html(
    monkeypatch, tmp_path
):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://dataproducts.substack.com/p/the-shift-left-manifesto-v2"
    monkeypatch.setattr(
        "app.ingest.fetch_url", lambda u, timeout=8.0: (u, _capture_fixture("substack.html"))
    )
    item_id, title = capture_article(conn, url)
    conn.commit()
    assert "Shift Left" in title
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["word_count"] > 0


def test_capture_article_still_saves_a_link_it_cannot_clean(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.nexojornal.com.br/colunistas/2026/09/02/paywalled"
    item_id, title = capture_article(conn, url, html=_capture_fixture("paywalled.html"))
    conn.commit()
    assert title and title != url
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert not item["body_html"]
    assert is_item_in_list(conn, item_id, "later")


def test_capture_article_does_not_crash_on_a_javascript_only_page(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/seanlinehan/status/2091955290552078418/"
    item_id, title = capture_article(conn, url, html=_capture_fixture("js_shell.html"))
    conn.commit()
    assert title
    assert is_item_in_list(conn, item_id, "later")


def test_capture_article_is_idempotent_per_url(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
    first_id, _ = capture_article(conn, url, html=_capture_fixture("blog.html"))
    second_id, _ = capture_article(conn, url, html=_capture_fixture("blog.html"))
    conn.commit()
    assert first_id == second_id
    count = conn.execute("SELECT COUNT(*) AS n FROM items WHERE url = ?", (url,)).fetchone()
    assert count["n"] == 1
