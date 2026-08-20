from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.db import connect, format_when, init_db, items_for_list
from app.ingest import ingest_xml, parse_feed

FIXTURE = Path(__file__).parent / "fixtures" / "feed.xml"


def test_parse_feed_reads_items():
    entries = parse_feed(FIXTURE.read_text(encoding="utf-8"))
    assert [entry["title"] for entry in entries] == [
        "First fixture item",
        "Second fixture item",
    ]
    assert "Hello from the fixture feed" in entries[0]["body_html"]


def test_ingest_xml_stores_news_items(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    result = ingest_xml(conn, FIXTURE.read_text(encoding="utf-8"))
    conn.commit()
    assert result["created"] == 2
    assert result["kept"] == 2
    assert result["feed_total"] == 2
    items = items_for_list(conn, "news")
    assert [row["title"] for row in items] == [
        "First fixture item",
        "Second fixture item",
    ]
    again = ingest_xml(conn, FIXTURE.read_text(encoding="utf-8"))
    assert again["created"] == 0


def test_ingest_xml_keeps_only_latest_five(tmp_path):
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
    result = ingest_xml(conn, xml)
    conn.commit()
    assert result["feed_total"] == 7
    assert result["kept"] == 5
    titles = [row["title"] for row in items_for_list(conn, "news")]
    assert titles == ["Item 7", "Item 6", "Item 5", "Item 4", "Item 3"]


def test_format_when_today_and_date():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
    assert format_when("2026-08-20T08:00:00+00:00", now) == "Today"
    assert format_when("2026-08-19T08:00:00+00:00", now) == "Yesterday"
    assert format_when("2026-08-17T08:00:00+00:00", now) == "17/08/26"
