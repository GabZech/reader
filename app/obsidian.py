from __future__ import annotations

import base64
import json
import re
from datetime import UTC, datetime
from urllib.parse import quote

import httpx
from lxml.html import fromstring

from app.config import obsidian_github_token

OWNER = "GabZech"
REPO = "news-highlights"
BRANCH = "main"

_UNSAFE_TITLE_CHARS = re.compile(r'[\\/:*?"<>|]')


def _request(method: str, url: str, **kwargs):
    return httpx.request(method, url, timeout=10, **kwargs)


def _export_date(item) -> str:
    for field in ("published_at", "seen_at"):
        try:
            value = item[field]
        except (KeyError, IndexError):
            value = None
        if value:
            try:
                return datetime.fromisoformat(value).strftime("%y-%m-%d")
            except ValueError:
                continue
    return datetime.now(UTC).strftime("%y-%m-%d")


def _sanitize_title(title: str | None, item_id: int) -> str:
    cleaned = _UNSAFE_TITLE_CHARS.sub("", title or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or str(item_id)


def note_path_for_item(item) -> str:
    date = _export_date(item)
    title = _sanitize_title(item["title"], item["id"])
    return f"Highlights/{date} {title}.md"


def build_note_markdown(item, highlights) -> str:
    lines = ["---"]
    lines.append(f"author: {item['author'] or item['source_title'] or ''}")
    if item["published_at"]:
        lines.append(f"published_date: {item['published_at'][:10]}")
    if item["url"]:
        lines.append(f"source: {item['url']}")
    lines.append("---")
    lines.append(f"# {item['title']}")
    lines.append("")
    lines.append("## Highlights")

    current_section = None
    current_subsection = None
    for highlight in highlights:
        section_title = highlight["section_title"]
        subsection_title = highlight["subsection_title"]
        if section_title and section_title != current_section:
            current_section = section_title
            current_subsection = None
            lines.append(f"### {current_section}")
        if subsection_title and subsection_title != current_subsection:
            current_subsection = subsection_title
            lines.append(f"#### {current_subsection}")
        lines.append("")
        lines.extend(_highlight_lines(highlight, item["body_html"]))

    return "\n".join(lines) + "\n"


def _highlight_lines(highlight, body_html) -> list[str]:
    # A highlight spanning a <ul>/<ol> (or several blocks) arrives with each
    # item on its own line - the browser's range.toString() inserts a
    # newline at each block boundary. The raw newlines carry no depth or
    # list-type information though, so reconstruct that from the item's own
    # body_html instead of guessing from the flat text.
    text_lines = [line for line in highlight["text"].split("\n") if line.strip()]
    if not text_lines:
        text_lines = [""]

    try:
        start_block = highlight["start_block"]
        end_block = highlight["end_block"]
    except (KeyError, IndexError):
        start_block = end_block = None
    shapes = (
        _block_range_shapes(body_html, start_block, end_block)
        if start_block is not None
        else None
    )
    if shapes is not None and len(shapes) == len(text_lines) and any(shapes):
        return _shaped_highlight_lines(highlight, text_lines, shapes)

    # Fallback: no reliable shape (missing body_html, or a structure whose
    # line count doesn't line up with what the browser captured, such as a
    # blockquote holding more than one paragraph). Keep the first line as
    # the bullet's own text and nest the rest flat, images included, as a
    # sublist so the structure survives instead of raw newlines breaking
    # the bullet.
    lines = [f"- {text_lines[0]}"]
    lines.extend(f"  - {line}" for line in text_lines[1:])
    lines.extend(f"  - ![]({url})" for url in _image_urls(highlight))
    return lines


def _shaped_highlight_lines(highlight, text_lines, shapes) -> list[str]:
    lines = []
    start = 0
    if shapes[0] is None:
        lines.append(f"- {text_lines[0]}")
        start = 1
    else:
        lines.append("-")
    for index in range(start, len(text_lines)):
        shape = shapes[index]
        line = text_lines[index]
        if shape is None:
            lines.append(f"  - {line}")
        else:
            depth, marker = shape
            lines.append(f"{'  ' * depth}{marker} {line}")
    lines.extend(f"  - ![]({url})" for url in _image_urls(highlight))
    return lines


def _block_range_shapes(
    body_html: str | None, start_block: int | None, end_block: int | None
) -> list[tuple[int, str] | None] | None:
    """One entry per top-level "line" a captured highlight's text would
    carry for the blocks in [start_block, end_block]: None for a plain
    block, or (depth, marker) for each <li> in a <ul>/<ol> block, in
    document order - the same order the browser's range.toString() walks
    when it flattens the same blocks into newline-separated text.
    """
    if not body_html or start_block is None or end_block is None or end_block < start_block:
        return None
    container = fromstring(f"<div>{body_html}</div>")
    blocks = list(container)[start_block : end_block + 1]
    if not blocks:
        return None
    shapes: list[tuple[int, str] | None] = []
    for block in blocks:
        if block.tag in ("ul", "ol"):
            shapes.extend(_list_item_shapes(block, 1))
        else:
            shapes.append(None)
    return shapes


def _list_item_shapes(list_el, depth: int) -> list[tuple[int, str]]:
    is_ordered = list_el.tag == "ol"
    try:
        ordinal = int(list_el.get("start", "1"))
    except ValueError:
        ordinal = 1
    shapes: list[tuple[int, str]] = []
    for item in list_el:
        if item.tag != "li":
            continue
        shapes.append((depth, f"{ordinal}." if is_ordered else "-"))
        if is_ordered:
            ordinal += 1
        for child in item:
            if child.tag in ("ul", "ol"):
                shapes.extend(_list_item_shapes(child, depth + 1))
    return shapes


def _image_urls(highlight) -> list[str]:
    try:
        raw = highlight["image_urls"]
    except (KeyError, IndexError):
        return []
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return []


def _url_for_path(path: str) -> str:
    encoded = "/".join(quote(segment, safe="") for segment in path.split("/"))
    return f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{encoded}"


def _delete_if_exists(headers: dict, path: str) -> None:
    url = _url_for_path(path)
    try:
        existing = _request("GET", url, headers=headers, params={"ref": BRANCH})
    except httpx.HTTPError:
        return
    if existing.status_code != 200:
        return
    sha = existing.json()["sha"]
    try:
        _request(
            "DELETE",
            url,
            headers=headers,
            json={"message": "remove note: renamed", "sha": sha, "branch": BRANCH},
        )
    except httpx.HTTPError:
        pass


def export_note(item, highlights, previous_path: str | None = None) -> dict:
    token = obsidian_github_token()
    if not token:
        return {"exported": False, "reason": "not_configured", "path": None}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    path = note_path_for_item(item)
    url = _url_for_path(path)

    if previous_path and previous_path != path:
        _delete_if_exists(headers, previous_path)

    try:
        existing = _request("GET", url, headers=headers, params={"ref": BRANCH})
    except httpx.HTTPError:
        return {"exported": False, "reason": "unreachable", "path": None}

    if existing.status_code == 200:
        sha = existing.json()["sha"]
    elif existing.status_code == 404:
        sha = None
    else:
        return {"exported": False, "reason": "unreachable", "path": None}

    if not highlights:
        if sha is not None:
            try:
                _request(
                    "DELETE",
                    url,
                    headers=headers,
                    json={
                        "message": f"remove note: {item['title']}",
                        "sha": sha,
                        "branch": BRANCH,
                    },
                )
            except httpx.HTTPError:
                return {"exported": False, "reason": "unreachable", "path": None}
        return {"exported": False, "reason": "no_highlights", "path": None}

    body = {
        "message": f"{'update' if sha is not None else 'add'} note: {item['title']}",
        "content": base64.b64encode(
            build_note_markdown(item, highlights).encode()
        ).decode(),
        "branch": BRANCH,
    }
    if sha is not None:
        body["sha"] = sha

    try:
        response = _request("PUT", url, headers=headers, json=body)
    except httpx.HTTPError:
        return {"exported": False, "reason": "unreachable", "path": None}
    if response.status_code not in (200, 201):
        return {"exported": False, "reason": "unreachable", "path": None}
    return {"exported": True, "path": path}
