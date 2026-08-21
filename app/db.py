from __future__ import annotations

import hashlib
import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from app.config import database_path

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
            ON CONFLICT(slug) DO NOTHING
            """,
            (slug, name, position),
        )
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(sources)")}
    if "window" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN window TEXT")
    if "backfill" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN backfill INTEGER")
    if "auto_title" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN auto_title TEXT")
        conn.execute("UPDATE sources SET auto_title = title WHERE auto_title IS NULL")
    conn.execute("DELETE FROM items WHERE source_id = ?", (SKELETON_SOURCE_ID,))
    conn.execute("DELETE FROM sources WHERE id = ?", (SKELETON_SOURCE_ID,))


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


def count_for_list(
    conn: sqlite3.Connection, slug: str, now: datetime | None = None
) -> int:
    return len(_visible_items(conn, slug, now))


def items_for_list(
    conn: sqlite3.Connection,
    slug: str,
    limit: int | None = None,
    now: datetime | None = None,
) -> list[sqlite3.Row]:
    rows = _visible_items(conn, slug, now)
    if limit is not None:
        return rows[:limit]
    return rows


def _visible_items(
    conn: sqlite3.Connection, slug: str, now: datetime | None = None
) -> list[sqlite3.Row]:
    now = now or datetime.now(timezone.utc)
    rows = conn.execute(
        """
        SELECT items.*, sources.title AS source_title, sources.window AS window
        FROM items
        JOIN sources ON sources.id = items.source_id
        WHERE sources.list_slug = ?
        ORDER BY datetime(items.published_at) DESC, items.id DESC
        """,
        (slug,),
    ).fetchall()
    return [row for row in rows if item_in_window(row["window"], row["published_at"], now)]


def item_in_window(
    window: str | None, published_at: str | None, now: datetime
) -> bool:
    if not window:
        return True
    if not published_at:
        return True
    try:
        stamp = datetime.fromisoformat(published_at)
    except ValueError:
        return True
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    delta = now.astimezone(stamp.tzinfo) - stamp
    if window == "day":
        return delta <= timedelta(hours=24)
    if window == "week":
        return delta <= timedelta(days=7)
    return True


def get_list(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM lists WHERE slug = ?", (slug,)).fetchone()


def find_list_by_name(conn: sqlite3.Connection, name: str) -> sqlite3.Row | None:
    key = name.strip().casefold()
    if not key:
        return None
    for row in conn.execute("SELECT * FROM lists").fetchall():
        if row["name"].casefold() == key:
            return row
    return None


def list_slug_for(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return slug or "list"


def insert_list(conn: sqlite3.Connection, name: str) -> str:
    title = name.strip()
    slug = list_slug_for(title)
    base = slug
    n = 2
    while get_list(conn, slug) is not None:
        slug = f"{base}-{n}"
        n += 1
    position_row = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM lists"
    ).fetchone()
    conn.execute(
        """
        INSERT INTO lists (slug, name, position, on_home)
        VALUES (?, ?, ?, 0)
        """,
        (slug, title, int(position_row["next_pos"])),
    )
    return slug


def rename_list(conn: sqlite3.Connection, slug: str, name: str) -> None:
    conn.execute(
        "UPDATE lists SET name = ? WHERE slug = ?",
        (name.strip(), slug),
    )


def delete_list(conn: sqlite3.Connection, slug: str) -> None:
    conn.execute(
        "UPDATE sources SET list_slug = NULL WHERE list_slug = ?",
        (slug,),
    )
    conn.execute("DELETE FROM lists WHERE slug = ?", (slug,))


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


def rss_sources(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT * FROM sources
        WHERE kind = 'rss' AND feed_url IS NOT NULL AND feed_url != ''
        ORDER BY title
        """
    ).fetchall()


def get_source(conn: sqlite3.Connection, source_id: str) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT sources.*, lists.name AS list_name
        FROM sources
        LEFT JOIN lists ON lists.slug = sources.list_slug
        WHERE sources.id = ?
        """,
        (source_id,),
    ).fetchone()


def normalize_feed_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    path = parsed.path.rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme.lower()}://{host}{path}{query}"


def source_id_for(feed_url: str) -> str:
    return hashlib.sha256(normalize_feed_url(feed_url).encode()).hexdigest()[:16]


def find_source_by_feed_url(
    conn: sqlite3.Connection, feed_url: str
) -> sqlite3.Row | None:
    key = normalize_feed_url(feed_url)
    for row in all_sources(conn):
        if row["feed_url"] and normalize_feed_url(row["feed_url"]) == key:
            return row
    return None


def insert_source(
    conn: sqlite3.Connection,
    *,
    source_id: str,
    kind: str,
    title: str,
    feed_url: str | None,
    list_slug: str | None,
    window: str | None,
    backfill: int | None,
    auto_title: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO sources (id, kind, title, feed_url, list_slug, window, backfill, auto_title)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (source_id, kind, title, feed_url, list_slug, window, backfill, auto_title or title),
    )


def items_for_source(conn: sqlite3.Connection, source_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT items.*, sources.title AS source_title
        FROM items
        JOIN sources ON sources.id = items.source_id
        WHERE items.source_id = ?
        ORDER BY datetime(items.published_at) DESC, items.id DESC
        """,
        (source_id,),
    ).fetchall()


def delete_source(conn: sqlite3.Connection, source_id: str) -> None:
    conn.execute("DELETE FROM items WHERE source_id = ?", (source_id,))
    conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))


def rename_source(conn: sqlite3.Connection, source_id: str, name: str) -> None:
    source = get_source(conn, source_id)
    if source is None:
        return
    title = name.strip() or source["auto_title"] or source["title"]
    conn.execute("UPDATE sources SET title = ? WHERE id = ?", (title, source_id))


def source_byline(source: sqlite3.Row) -> str:
    kind = "RSS" if source["kind"] == "rss" else source["kind"]
    if not source["list_slug"]:
        return f"{kind} · Not on a list"
    if source["list_slug"] == "news":
        if source["window"] == "day":
            return f"{kind} · News (<24h)"
        if source["window"] == "week":
            return f"{kind} · News (<7days)"
        return f"{kind} · News"
    name = source["list_name"] or source["list_slug"]
    return f"{kind} · {name}"


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
