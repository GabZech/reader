from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse

import feedparser
import httpx

from app.db import delete_items_except_guids, rss_sources, upsert_item

COMMON_FEED_PATHS = (
    "/feed",
    "/rss",
    "/feed.xml",
    "/atom.xml",
    "/index.xml",
    "/rss.xml",
)

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


def parse_feed(xml: str, source_id: str) -> list[dict[str, Any]]:
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
        author = entry.get("author")
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


def fetch_url(url: str, timeout: float = 8.0) -> tuple[str, str]:
    response = httpx.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent": "reader/0.1",
            # Skips Google's EU cookie-consent redirect page, which otherwise
            # replaces the real page (and its feed link) for a YouTube channel URL.
            "Cookie": "SOCS=CAI",
        },
    )
    response.raise_for_status()
    return str(response.url), response.text


def fetch_feed_xml(url: str, timeout: float = 8.0) -> str:
    _final_url, text = fetch_url(url, timeout=timeout)
    return text


def ingest_xml(
    conn,
    xml: str,
    source_id: str,
    limit: int | None = None,
) -> dict:
    entries = parse_feed(xml, source_id)
    feed_total = len(entries)
    ranked = _newest_first(entries)
    kept = ranked if limit is None else ranked[:limit]
    created = 0
    if kept:
        feed_title = kept[0]["feed_title"]
        row = conn.execute(
            "SELECT title, auto_title FROM sources WHERE id = ?", (source_id,)
        ).fetchone()
        if row is not None:
            title = feed_title if row["title"] == row["auto_title"] else row["title"]
            conn.execute(
                "UPDATE sources SET title = ?, auto_title = ? WHERE id = ?",
                (title, feed_title, source_id),
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
    if limit is not None:
        delete_items_except_guids(
            conn, source_id, [entry["guid"] for entry in kept]
        )
    return {
        "created": created,
        "kept": len(kept),
        "feed_total": feed_total,
    }


def ingest_url(
    conn, url: str, source_id: str, limit: int | None = None
) -> dict:
    xml = fetch_feed_xml(url)
    return ingest_xml(conn, xml, source_id, limit=limit)


def ingest_all_sources(conn) -> dict:
    created = 0
    kept = 0
    sources = rss_sources(conn)
    for source in sources:
        result = ingest_url(
            conn, source["feed_url"], source["id"], limit=source["backfill"]
        )
        created += result["created"]
        kept += result["kept"]
    return {"created": created, "kept": kept, "sources": len(sources)}


@dataclass(frozen=True)
class DiscoveredFeed:
    feed_url: str
    title: str
    item_count: int


def source_kind_for(feed_url: str) -> str:
    return "youtube" if "youtube.com/feeds/videos.xml" in feed_url else "rss"


def normalize_user_url(raw: str) -> str | None:
    text = raw.strip()
    if not text:
        return None
    if not re.match(r"^https?://", text, re.I):
        text = "https://" + text
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return text


def discover_feed(url: str) -> DiscoveredFeed | None:
    tried: set[str] = set()
    candidates = [url]
    first = True
    while candidates:
        candidate = candidates.pop(0)
        key = candidate.rstrip("/").lower()
        if key in tried:
            continue
        tried.add(key)
        try:
            final_url, body = fetch_url(candidate)
        except httpx.HTTPError:
            continue
        parsed = feedparser.parse(body)
        if _looks_like_feed(parsed):
            title = parsed.feed.get("title") or "RSS"
            return DiscoveredFeed(
                feed_url=final_url,
                title=str(title),
                item_count=len(parsed.entries),
            )
        if first:
            first = False
            for href in _feed_links(body, final_url):
                candidates.append(href)
            origin = f"{urlparse(final_url).scheme}://{urlparse(final_url).netloc}"
            for path in COMMON_FEED_PATHS:
                candidates.append(urljoin(origin, path))
    return None


def _looks_like_feed(parsed: Any) -> bool:
    return bool(parsed.get("version"))


class _FeedLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "link":
            return
        data = {key.lower(): (value or "") for key, value in attrs}
        rel = data.get("rel", "").lower()
        typ = data.get("type", "").lower()
        href = data.get("href")
        if not href or "alternate" not in rel:
            return
        if "rss" in typ or "atom" in typ or typ in {"application/xml", "text/xml"}:
            self.hrefs.append(href)


def _feed_links(html: str, base_url: str) -> list[str]:
    parser = _FeedLinkParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        return []
    return [urljoin(base_url, href) for href in parser.hrefs]


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
