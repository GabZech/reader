from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.db import (
    connect,
    format_when,
    init_db,
    insert_source,
    item_in_window,
    items_for_list,
)
from app.ingest import ingest_xml, parse_feed

FIXTURE = Path(__file__).parent / "fixtures" / "feed.xml"
SOURCE_ID = "fixture-rss"


def _source(conn, window: str | None = "week") -> None:
    insert_source(
        conn,
        source_id=SOURCE_ID,
        kind="rss",
        title="RSS",
        feed_url="https://example.test/feed.xml",
        list_slug="news",
        window=window,
        backfill=None,
    )


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
        conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=timezone.utc)
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
            conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=timezone.utc)
        )
    ]
    assert titles == ["Item 7", "Item 6", "Item 5", "Item 4", "Item 3"]


def test_item_in_window_day_and_week():
    now = datetime(2026, 8, 20, 12, tzinfo=timezone.utc)
    assert item_in_window("day", "2026-08-20T08:00:00+00:00", now)
    assert not item_in_window("day", "2026-08-19T08:00:00+00:00", now)
    assert item_in_window("week", "2026-08-14T08:00:00+00:00", now)
    assert not item_in_window("week", "2026-08-12T08:00:00+00:00", now)
    assert item_in_window(None, "2026-01-01T00:00:00+00:00", now)


def test_format_when_today_and_date():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
    assert format_when("2026-08-20T08:00:00+00:00", now) == "Today"
    assert format_when("2026-08-19T08:00:00+00:00", now) == "Yesterday"
    assert format_when("2026-08-17T08:00:00+00:00", now) == "17/08/26"
