from __future__ import annotations

import tracemalloc
from datetime import UTC, datetime

from app.db import (
    add_source_to_list,
    all_lists,
    connect,
    count_for_list,
    get_item,
    init_db,
    insert_source,
    items_for_list,
    items_for_source,
    lists_with_items,
    upsert_item,
)

# The live machine has 256 MB. Lists and counts once loaded every article's
# full text, so a few overlapping page loads could kill the server, and a page
# that hangs while it restarts shows as a white screen on an iPhone.
BIG_BODY = "<p>" + "x" * 1_500_000 + "</p>"
ARTICLES = 12
LIMIT_MB = 3


def _library(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    insert_source(
        conn, source_id="s", kind="rss", title="Source", feed_url="https://s.test/f", backfill=None
    )
    add_source_to_list(conn, "s", "news", None)
    for n in range(ARTICLES):
        upsert_item(
            conn,
            source_id="s",
            guid=f"g{n}",
            title=f"Title {n}",
            author="Author",
            url=f"https://s.test/{n}",
            published_at=datetime(2026, 8, 20, 12 - n // 4, tzinfo=UTC).isoformat(),
            body_html=BIG_BODY,
            image_url=None,
            word_count=900,
        )
    conn.commit()
    return conn


def _peak_mb(action):
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        result = action()
        return result, tracemalloc.get_traced_memory()[1] / 1_000_000
    finally:
        tracemalloc.stop()


def test_counting_a_list_does_not_load_the_articles(tmp_path):
    conn = _library(tmp_path)
    count, peak = _peak_mb(lambda: count_for_list(conn, "news"))
    assert count == ARTICLES
    assert peak < LIMIT_MB


def test_the_rows_of_a_list_leave_out_the_article_text(tmp_path):
    conn = _library(tmp_path)
    rows, peak = _peak_mb(lambda: items_for_list(conn, "news"))
    assert len(rows) == ARTICLES
    assert peak < LIMIT_MB
    first = rows[0]
    assert first["title"].startswith("Title")
    assert first["source_title"] == "Source"
    assert first["word_count"] == 900
    columns = set(first.keys())
    assert {"seen_at", "progress_index"} <= columns
    assert "body_html" not in columns


def test_home_and_the_lists_page_stay_small(tmp_path):
    conn = _library(tmp_path)
    home, peak_home = _peak_mb(lambda: lists_with_items(conn, limit_per_list=6))
    news = next(section for section in home if section["slug"] == "news")
    assert len(news["items"]) == 6 and news["count"] == ARTICLES
    assert peak_home < LIMIT_MB
    lists, peak_lists = _peak_mb(lambda: all_lists(conn))
    assert next(row for row in lists if row["slug"] == "news")["count"] == ARTICLES
    assert peak_lists < LIMIT_MB


def test_a_source_page_leaves_out_the_article_text(tmp_path):
    conn = _library(tmp_path)
    rows, peak = _peak_mb(lambda: items_for_source(conn, "s"))
    assert len(rows) == ARTICLES
    assert peak < LIMIT_MB


def test_one_article_still_comes_with_its_text(tmp_path):
    conn = _library(tmp_path)
    item_id = items_for_list(conn, "news")[0]["id"]
    assert get_item(conn, item_id)["body_html"] == BIG_BODY
