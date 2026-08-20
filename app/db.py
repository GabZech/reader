from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.config import database_path, skeleton_feed_url

LISTS = (
    ("news", "News", 0),
    ("later", "Read later", 1),
    ("fav", "Favourite channels", 2),
)

SKELETON_SOURCE_ID = "skeleton-rss"


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = path or database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def session(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    conn = connect(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS lists (
            slug TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            position INTEGER NOT NULL,
            on_home INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            feed_url TEXT,
            list_slug TEXT REFERENCES lists(slug)
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL REFERENCES sources(id),
            guid TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            url TEXT,
            published_at TEXT,
            body_html TEXT,
            image_url TEXT,
            word_count INTEGER,
            UNIQUE(source_id, guid)
        );
        """
    )
    for slug, name, position in LISTS:
        conn.execute(
            """
            INSERT INTO lists (slug, name, position, on_home)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                position = excluded.position
            """,
            (slug, name, position),
        )
    conn.execute(
        """
        INSERT INTO sources (id, kind, title, feed_url, list_slug)
        VALUES (?, 'rss', 'RSS', ?, 'news')
        ON CONFLICT(id) DO UPDATE SET
            feed_url = excluded.feed_url,
            list_slug = excluded.list_slug
        """,
        (SKELETON_SOURCE_ID, skeleton_feed_url()),
    )


def lists_with_items(conn: sqlite3.Connection, limit_per_list: int | None = None) -> list[dict]:
    rows = conn.execute(
        "SELECT slug, name, position FROM lists WHERE on_home = 1 ORDER BY position"
    ).fetchall()
    result = []
    for row in rows:
        items = items_for_list(conn, row["slug"], limit=limit_per_list)
        result.append(
            {
                "slug": row["slug"],
                "name": row["name"],
                "items": items,
                "count": count_for_list(conn, row["slug"]),
            }
        )
    return result


def all_lists(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT slug, name FROM lists ORDER BY position"
    ).fetchall()
    return [
        {
            "slug": row["slug"],
            "name": row["name"],
            "count": count_for_list(conn, row["slug"]),
        }
        for row in rows
    ]


def count_for_list(conn: sqlite3.Connection, slug: str) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS n
        FROM items
        JOIN sources ON sources.id = items.source_id
        WHERE sources.list_slug = ?
        """,
        (slug,),
    ).fetchone()
    return int(row["n"]) if row else 0


def items_for_list(
    conn: sqlite3.Connection, slug: str, limit: int | None = None
) -> list[sqlite3.Row]:
    sql = """
        SELECT items.*, sources.title AS source_title
        FROM items
        JOIN sources ON sources.id = items.source_id
        WHERE sources.list_slug = ?
        ORDER BY datetime(items.published_at) DESC, items.id DESC
    """
    params: list = [slug]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    return conn.execute(sql, params).fetchall()


def get_list(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM lists WHERE slug = ?", (slug,)).fetchone()


def get_item(conn: sqlite3.Connection, item_id: int) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT items.*, sources.title AS source_title, sources.list_slug
        FROM items
        JOIN sources ON sources.id = items.source_id
        WHERE items.id = ?
        """,
        (item_id,),
    ).fetchone()


def all_sources(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT sources.*, lists.name AS list_name
        FROM sources
        LEFT JOIN lists ON lists.slug = sources.list_slug
        ORDER BY sources.title
        """
    ).fetchall()


def upsert_item(
    conn: sqlite3.Connection,
    *,
    source_id: str,
    guid: str,
    title: str,
    author: str | None,
    url: str | None,
    published_at: str | None,
    body_html: str | None,
    image_url: str | None,
    word_count: int | None,
) -> bool:
    existing = conn.execute(
        "SELECT id FROM items WHERE source_id = ? AND guid = ?",
        (source_id, guid),
    ).fetchone()
    conn.execute(
        """
        INSERT INTO items (
            source_id, guid, title, author, url, published_at,
            body_html, image_url, word_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_id, guid) DO UPDATE SET
            title = excluded.title,
            author = excluded.author,
            url = excluded.url,
            published_at = excluded.published_at,
            body_html = excluded.body_html,
            image_url = excluded.image_url,
            word_count = excluded.word_count
        """,
        (
            source_id,
            guid,
            title,
            author,
            url,
            published_at,
            body_html,
            image_url,
            word_count,
        ),
    )
    return existing is None


def delete_items_except_guids(
    conn: sqlite3.Connection, source_id: str, guids: list[str]
) -> None:
    if not guids:
        conn.execute("DELETE FROM items WHERE source_id = ?", (source_id,))
        return
    placeholders = ",".join("?" * len(guids))
    conn.execute(
        f"DELETE FROM items WHERE source_id = ? AND guid NOT IN ({placeholders})",
        (source_id, *guids),
    )


def format_when(published_at: str | None, now: datetime | None = None) -> str:
    if not published_at:
        return ""
    now = now or datetime.now(timezone.utc)
    try:
        stamp = datetime.fromisoformat(published_at)
    except ValueError:
        return published_at
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    local_now = now.astimezone(stamp.tzinfo)
    delta = local_now.date() - stamp.date()
    if delta.days == 0:
        return "Today"
    if delta.days == 1:
        return "Yesterday"
    return stamp.strftime("%d/%m/%y")


def reading_length(word_count: int | None) -> str:
    if not word_count:
        return ""
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min"
