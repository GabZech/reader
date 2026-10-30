from __future__ import annotations

import base64
import json
import re
from datetime import UTC, datetime
from urllib.parse import quote, urljoin, urlsplit

import httpx
from lxml.html import fromstring

from app.config import obsidian_github_token

OWNER = "GabZech"
REPO = "news-highlights"
BRANCH = "main"

_PATH_DATE = re.compile(r"Highlights/(\d{2}-\d{2}-\d{2}) ")
KEY_TAG = "#key"
_UNSAFE_TITLE_CHARS = re.compile(r'[\\/:*?"<>|]')
_WHITESPACE = re.compile(r"\s")
_LINK_SCHEMES = ("http", "https", "mailto")


def _request(method: str, url: str, **kwargs):
    return httpx.request(method, url, timeout=10, **kwargs)


def _today() -> str:
    return datetime.now(UTC).strftime("%y-%m-%d")


def _export_date(previous_path: str | None) -> str:
    # The date is the note's first export, which the last path still carries.
    match = _PATH_DATE.match(previous_path or "")
    return match.group(1) if match else _today()


def _sanitize_title(title: str | None, item_id: int) -> str:
    cleaned = _UNSAFE_TITLE_CHARS.sub("", title or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or str(item_id)


def note_path_for_item(item, previous_path: str | None = None) -> str:
    date = _export_date(previous_path)
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
        lines.extend(_highlight_lines(highlight, item["body_html"], item["url"]))

    return "\n".join(lines) + "\n"


def _highlight_lines(highlight, body_html, base_url=None) -> list[str]:
    lines = _plain_highlight_lines(highlight, body_html, base_url)
    if _is_key(highlight) and lines:
        lines[0] = f"{lines[0]} {KEY_TAG}"
    return lines


def _is_key(highlight) -> bool:
    try:
        return bool(highlight["is_key"])
    except (KeyError, IndexError):
        return False


def _mark(line: str, is_key: bool) -> str:
    # Obsidian's ==mark== cannot span lines and breaks on padding inside the
    # marks or on a stray "==" in the text, so those lines stay unmarked.
    stripped = line.strip()
    if not is_key or not stripped or "==" in stripped:
        return line
    return f"=={stripped}=="


def _plain_highlight_lines(highlight, body_html, base_url=None) -> list[str]:
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
    if start_block is not None:
        spans = _link_spans(highlight, body_html, base_url)
        text_lines = _apply_links(text_lines, spans)
    is_key = _is_key(highlight)
    text_lines = [_mark(line, is_key) for line in text_lines]
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
    # the bullet's own text and nest the rest flat as a sublist so the
    # structure survives instead of raw newlines breaking the bullet.
    # Images sit in their own top-level bullets after it.
    image_lines = [f"- ![]({url})" for url in _image_urls(highlight)]
    if not any(line.strip() for line in text_lines) and image_lines:
        return image_lines
    lines = [f"- {text_lines[0]}"]
    lines.extend(f"  - {line}" for line in text_lines[1:])
    return lines + image_lines


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
    lines.extend(f"- ![]({url})" for url in _image_urls(highlight))
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


def _link_spans(highlight, body_html, base_url) -> list[tuple[int, int, str]]:
    """Each link the highlight covers, as (start, end, url) counted in the
    highlight's non-whitespace characters. Offsets are character offsets
    into a block's text, the same ones `app/static/app.js` stores. Counting
    without whitespace keeps the spans valid against the captured text,
    whose newlines at block boundaries the HTML does not carry. Returns no
    spans when the HTML's text no longer matches the captured text.
    """
    if not body_html:
        return []
    start_block, end_block = highlight["start_block"], highlight["end_block"]
    try:
        start_offset, end_offset = highlight["start_offset"], highlight["end_offset"]
    except (KeyError, IndexError):
        start_offset, end_offset = 0, None
    blocks = list(fromstring(f"<div>{body_html}</div>"))[start_block : end_block + 1]
    spans: list[tuple[int, int, str, int]] = []
    selected = []
    pos = 0
    for index, block in enumerate(blocks, start_block):
        lo = start_offset if index == start_block else 0
        hi = end_offset if index == end_block else None
        offset = 0
        for text, href in _text_pieces(block):
            begin, offset = offset, offset + len(text)
            cut = text[max(lo - begin, 0) : None if hi is None else max(hi - begin, 0)]
            compact = _WHITESPACE.sub("", cut)
            selected.append(compact)
            url = _export_href(href, base_url)
            if url and compact:
                last = spans[-1] if spans else None
                if last and last[2] == url and last[1] == pos and last[3] == index:
                    spans[-1] = (last[0], pos + len(compact), url, index)
                else:
                    spans.append((pos, pos + len(compact), url, index))
            pos += len(compact)
    if "".join(selected) != _WHITESPACE.sub("", highlight["text"]):
        return []
    return [(start, end, url) for start, end, url, _ in spans]


def highlights_have_links(item, highlights) -> bool:
    return any(
        _link_spans(highlight, item["body_html"], item["url"]) for highlight in highlights
    )


def _text_pieces(el, href=None):
    # Text in document order with the href of the link it sits in, matching
    # the text nodes the browser's textContent walks (comments carry none).
    if el.tag == "a" and el.get("href"):
        href = el.get("href")
    if isinstance(el.tag, str) and el.text:
        yield el.text, href
    for child in el:
        yield from _text_pieces(child, href)
        if child.tail:
            yield child.tail, href


def _export_href(href: str | None, base_url: str | None) -> str | None:
    # An in-page anchor (a footnote, say) leads nowhere from the note.
    if not href or href.startswith("#"):
        return None
    url = urljoin(base_url or "", href)
    return url if urlsplit(url).scheme in _LINK_SCHEMES else None


def _apply_links(lines: list[str], spans: list[tuple[int, int, str]]) -> list[str]:
    positions = [
        (line_index, char_index)
        for line_index, line in enumerate(lines)
        for char_index, char in enumerate(line)
        if not char.isspace()
    ]
    lines = list(lines)
    # Last span first, so a link added to a line never shifts an earlier one.
    for start, end, url in reversed(spans):
        if end > len(positions):
            continue
        first_line, first_char = positions[start]
        last_line, last_char = positions[end - 1]
        if first_line != last_line:
            continue
        line = lines[first_line]
        label = line[first_char : last_char + 1].replace("[", "\\[").replace("]", "\\]")
        target = url.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
        lines[first_line] = f"{line[:first_char]}[{label}]({target}){line[last_char + 1 :]}"
    return lines


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
    path = note_path_for_item(item, previous_path)
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
