from __future__ import annotations

import base64

import httpx

from app.config import obsidian_github_token

OWNER = "GabZech"
REPO = "news-highlights"
BRANCH = "main"


def _request(method: str, url: str, **kwargs):
    return httpx.request(method, url, timeout=10, **kwargs)


def note_path_for_item(item_id: int, title: str) -> str:
    return f"Highlights/{item_id}.md"


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

    return "\n".join(lines) + "\n"


def _note_url(item_id: int, title: str) -> str:
    path = note_path_for_item(item_id, title)
    return f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"


def export_note(item, highlights) -> dict:
    token = obsidian_github_token()
    if not token:
        return {"exported": False, "reason": "not_configured"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    url = _note_url(item["id"], item["title"])

    try:
        existing = _request("GET", url, headers=headers, params={"ref": BRANCH})
    except httpx.HTTPError:
        return {"exported": False, "reason": "unreachable"}

    if existing.status_code == 200:
        sha = existing.json()["sha"]
    elif existing.status_code == 404:
        sha = None
    else:
        return {"exported": False, "reason": "unreachable"}

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
                return {"exported": False, "reason": "unreachable"}
        return {"exported": False, "reason": "no_highlights"}

    body = {
        "message": f"update note: {item['title']}",
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
        return {"exported": False, "reason": "unreachable"}
    if response.status_code not in (200, 201):
        return {"exported": False, "reason": "unreachable"}
    return {"exported": True}
