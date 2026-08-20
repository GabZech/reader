from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any

import feedparser
import httpx

from app.db import SKELETON_SOURCE_ID, delete_items_except_guids, upsert_item

SKELETON_FEED_LIMIT = 5

ALLOWED_TAGS = {
    "p",
    "a",
    "br",
    "em",
    "strong",
    "code",
    "pre",
    "ul",
    "ol",
    "li",
    "h2",
    "h3",
    "blockquote",
    "img",
    "figure",
    "figcaption",
}


class _Sanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._out: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ALLOWED_TAGS:
            return
        if tag == "br":
            self._out.append("<br>")
            return
        if tag == "img":
            src = _attr(attrs, "src")
            alt = _attr(attrs, "alt") or ""
            if src:
                self._out.append(f'<img src="{_esc(src)}" alt="{_esc(alt)}">')
            return
        if tag == "a":
            href = _attr(attrs, "href")
            if href:
                self._out.append(f'<a href="{_esc(href)}" rel="noreferrer">')
            else:
                self._out.append("<a>")
            return
        self._out.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if tag not in ALLOWED_TAGS or tag in {"br", "img"}:
            return
        self._out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self._out.append(_esc(data))

    def result(self) -> str:
        return "".join(self._out)


def _attr(attrs: list[tuple[str, str | None]], name: str) -> str | None:
    for key, value in attrs:
        if key == name:
            return value
    return None


def _esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sanitize_html(raw: str | None) -> str:
    if not raw:
        return ""
    parser = _Sanitizer()
    parser.feed(raw)
    parser.close()
    return parser.result()


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    words = [part for part in text.split() if part]
    return len(words)


def parse_feed(xml: str, source_id: str = SKELETON_SOURCE_ID) -> list[dict[str, Any]]:
    parsed = feedparser.parse(xml)
    feed_title = parsed.feed.get("title") or "RSS"
    entries = []
    for entry in parsed.entries:
        guid = entry.get("id") or entry.get("link") or entry.get("title")
        if not guid:
            continue
        html = entry.get("summary") or entry.get("description") or ""
        body = sanitize_html(html)
        image = _entry_image(entry)
        published = _entry_published(entry)
        author = entry.get("author") or feed_title
        entries.append(
            {
                "source_id": source_id,
                "guid": str(guid),
                "title": entry.get("title") or "(untitled)",
                "author": author,
                "url": entry.get("link"),
                "published_at": published,
                "body_html": body,
                "image_url": image,
                "word_count": word_count(body),
                "feed_title": feed_title,
            }
        )
    return entries


def _newest_first(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(entry: dict[str, Any]) -> str:
        return entry.get("published_at") or ""

    return sorted(entries, key=key, reverse=True)


def fetch_feed_xml(url: str, timeout: float = 8.0) -> str:
    response = httpx.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "reader-skeleton/0.1"},
    )
    response.raise_for_status()
    return response.text


def ingest_xml(
    conn,
    xml: str,
    source_id: str = SKELETON_SOURCE_ID,
    limit: int = SKELETON_FEED_LIMIT,
) -> dict:
    entries = parse_feed(xml, source_id)
    feed_total = len(entries)
    kept = _newest_first(entries)[:limit]
    created = 0
    if kept:
        feed_title = kept[0]["feed_title"]
        conn.execute(
            "UPDATE sources SET title = ? WHERE id = ?",
            (feed_title, source_id),
        )
    for entry in kept:
        is_new = upsert_item(
            conn,
            source_id=entry["source_id"],
            guid=entry["guid"],
            title=entry["title"],
            author=entry["author"],
            url=entry["url"],
            published_at=entry["published_at"],
            body_html=entry["body_html"],
            image_url=entry["image_url"],
            word_count=entry["word_count"],
        )
        if is_new:
            created += 1
    delete_items_except_guids(
        conn, source_id, [entry["guid"] for entry in kept]
    )
    return {
        "created": created,
        "kept": len(kept),
        "feed_total": feed_total,
    }


def ingest_url(conn, url: str, source_id: str = SKELETON_SOURCE_ID) -> dict:
    xml = fetch_feed_xml(url)
    return ingest_xml(conn, xml, source_id)


def _entry_published(entry: Any) -> str | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    from datetime import datetime, timezone

    try:
        stamp = datetime(*parsed[:6], tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
    return stamp.isoformat()


def _entry_image(entry: Any) -> str | None:
    media = entry.get("media_thumbnail") or entry.get("media_content")
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]
    for enclosure in entry.get("enclosures") or []:
        href = enclosure.get("href")
        typ = enclosure.get("type") or ""
        if href and typ.startswith("image/"):
            return href
    return None
