from __future__ import annotations

import base64
import json
import re
from datetime import UTC, datetime
from urllib.parse import quote

import httpx

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
        lines.append(f"- {highlight['text']}")
        for url in _image_urls(highlight):
            lines.append(f"![]({url})")

    return "\n".join(lines) + "\n"


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
