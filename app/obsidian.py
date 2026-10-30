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
_BLOCK_TAGS = frozenset(
    {
        "address", "article", "aside", "blockquote", "dd", "details", "div", "dl",
        "dt", "fieldset", "figcaption", "figure", "footer", "h1", "h2", "h3", "h4",
        "h5", "h6", "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section",
        "table", "tr", "ul",
    }
)


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
    selection = (
        _dom_selection(highlight, body_html, base_url) if start_block is not None else None
    )
    shapes = None
    if selection:
        text_lines, shapes, spans = selection
        text_lines = _apply_links(text_lines, spans)
    is_key = _is_key(highlight)
    text_lines = [_mark(line, is_key) for line in text_lines]
    if shapes is None and start_block is not None:
        shapes = _block_range_shapes(body_html, start_block, end_block)
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
            shapes.extend(shape for _, shape in _list_items(block, 1))
        else:
            shapes.append(None)
    return shapes


def _list_items(list_el, depth: int):
    """Each <li> of a list, nested ones included, with its (depth, marker)."""
    is_ordered = list_el.tag == "ol"
    try:
        ordinal = int(list_el.get("start", "1"))
    except ValueError:
        ordinal = 1
    for item in list_el:
        if item.tag != "li":
            continue
        yield item, (depth, f"{ordinal}." if is_ordered else "-")
        if is_ordered:
            ordinal += 1
        for child in item:
            if child.tag in ("ul", "ol"):
                yield from _list_items(child, depth + 1)


def _dom_selection(highlight, body_html, base_url):
    """The highlight rebuilt from the article's saved HTML: (lines, shapes,
    links), or None when the HTML no longer matches the captured text.

    A line is one paragraph, or one list item, with the whitespace the
    source wrapped it in collapsed to single spaces. Offsets are character
    offsets into a block's text, the same ones `app/static/app.js` stores.
    The captured text cannot give the lines on its own: it breaks wherever
    the source did, mid-sentence included. Links are (start, end, url)
    counted in non-whitespace characters over all the lines, which is how
    `_apply_links` finds them again after the lines are cleaned up.
    """
    if not body_html:
        return None
    start_block, end_block = highlight["start_block"], highlight["end_block"]
    try:
        start_offset, end_offset = highlight["start_offset"], highlight["end_offset"]
    except (KeyError, IndexError):
        start_offset, end_offset = 0, None
    blocks = list(fromstring(f"<div>{body_html}</div>"))[start_block : end_block + 1]
    if not blocks:
        return None
    lines: dict[tuple[int, int], list[str]] = {}
    line_shapes: dict[tuple[int, int], tuple[int, str] | None] = {}
    spans: list[tuple[int, int, str, tuple[int, int]]] = []
    selected = []
    pos = 0
    for index, block in enumerate(blocks, start_block):
        lo = start_offset if index == start_block else 0
        hi = end_offset if index == end_block else None
        shapes, pieces = _line_pieces(block)
        offset = 0
        for text, href, line in pieces:
            begin, offset = offset, offset + len(text)
            cut = text[max(lo - begin, 0) : None if hi is None else max(hi - begin, 0)]
            compact = _WHITESPACE.sub("", cut)
            selected.append(compact)
            if line is None:
                continue
            key = (index, line)
            lines.setdefault(key, []).append(cut)
            line_shapes[key] = shapes[line]
            url = _export_href(href, base_url)
            if url and compact:
                last = spans[-1] if spans else None
                if last and last[2] == url and last[1] == pos and last[3] == key:
                    spans[-1] = (last[0], pos + len(compact), url, key)
                else:
                    spans.append((pos, pos + len(compact), url, key))
            pos += len(compact)
    if "".join(selected) != _WHITESPACE.sub("", highlight["text"]):
        return None
    texts, shapes = [], []
    for key, parts in lines.items():
        text = re.sub(r"\s+", " ", "".join(parts)).strip()
        if text:
            texts.append(text)
            shapes.append(line_shapes[key])
    if not texts:
        return None
    return texts, shapes, [(start, end, url) for start, end, url, _ in spans]


def highlights_have_links(item, highlights) -> bool:
    for highlight in highlights:
        selection = _dom_selection(highlight, item["body_html"], item["url"])
        if selection and selection[2]:
            return True
    return False


def highlights_export_differently(item, highlights) -> bool:
    """Whether a note written from the captured text alone, which breaks
    wherever the source wrapped a line, would read differently from one
    rebuilt from the article now.
    """
    for highlight in highlights:
        selection = _dom_selection(highlight, item["body_html"], item["url"])
        if not selection:
            continue
        captured = [
            re.sub(r"\s+", " ", line).strip()
            for line in highlight["text"].split("\n")
            if line.strip()
        ]
        if captured != selection[0]:
            return True
    return False


def _line_pieces(block):
    """A block's shape per line and its text pieces in document order, each
    with the href of the link it sits in and the line it belongs to (None
    for whitespace between a list's items). A plain block is one line; a
    list has a line per item, a nested item's text staying on its own line.
    """
    is_list = block.tag in ("ul", "ol")
    if is_list:
        items = list(_list_items(block, 1))
        line_of = {item: number for number, (item, _) in enumerate(items)}
        shapes = [shape for _, shape in items]
        first_line = None
    else:
        line_of, shapes, first_line = {}, [None], 0

    def fresh_line():
        shapes.append(None)
        return len(shapes) - 1

    def starts_line(el):
        # Inside a plain block, a paragraph (or the like) nested in it is a
        # line of its own; inside a list, an item's text stays on its line.
        return not is_list and el is not block and el.tag in _BLOCK_TAGS

    def walk(el, line, href):
        line = line_of.get(el, line)
        if starts_line(el):
            line = fresh_line()
        if el.tag == "a" and el.get("href"):
            href = el.get("href")
        if isinstance(el.tag, str) and el.text:
            yield el.text, href, line
        for child in el:
            yield from walk(child, line, href)
            if starts_line(child):
                line = fresh_line()
            if child.tail:
                yield child.tail, href, line

    return shapes, list(walk(block, first_line, None))


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
