from __future__ import annotations

import base64

from app.obsidian import build_note_markdown, export_note, note_path_for_item


def _item(**overrides):
    base = {
        "id": 42,
        "title": "Subagents on Subagents",
        "author": "Josh Rosen",
        "source_title": "X",
        "published_at": "2026-08-13T00:00:00+00:00",
        "url": "https://x.com/JoshARosen/status/2087944178558791874",
    }
    base.update(overrides)
    return base


def _highlight(text, section_title=None, subsection_title=None):
    return {
        "text": text,
        "section_title": section_title,
        "subsection_title": subsection_title,
    }


def test_note_path_is_stable_per_item():
    path = note_path_for_item(42, "Subagents on Subagents: How Many Layers?")
    assert path == "Highlights/42.md"
    assert note_path_for_item(42, "A totally different title") == path


def test_build_note_markdown_includes_frontmatter_and_title():
    md = build_note_markdown(_item(), [_highlight("First point.")])
    assert "author: Josh Rosen" in md
    assert "published_date: 2026-08-13" in md
    assert "source: https://x.com/JoshARosen/status/2087944178558791874" in md
    assert "# Subagents on Subagents" in md
    assert "## Highlights" in md
    assert "- First point." in md
    assert "## Summary" not in md


def test_build_note_markdown_groups_by_sticky_section_title():
    highlights = [
        _highlight("Untitled first."),
        _highlight("Under section A.", section_title="Section A"),
        _highlight("Still under section A."),
        _highlight("Under subsection.", subsection_title="Sub one"),
        _highlight("Under section B.", section_title="Section B"),
    ]
    md = build_note_markdown(_item(), highlights)
    lines = [line for line in md.splitlines() if line]
    assert lines.index("### Section A") < lines.index("- Under section A.")
    assert lines.index("- Under section A.") < lines.index("- Still under section A.")
    assert lines.index("#### Sub one") < lines.index("- Under subsection.")
    assert lines.index("### Section B") > lines.index("#### Sub one")
    # A new section resets any active subsection heading.
    assert "#### Sub one" not in lines[lines.index("### Section B") :]


def test_export_note_creates_when_no_existing_file(monkeypatch):
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if method == "GET":
            return _FakeResponse(404, {})
        if method == "PUT":
            return _FakeResponse(201, {"content": {"sha": "abc123"}})
        raise AssertionError(f"unexpected method {method}")

    monkeypatch.setenv("OBSIDIAN_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr("app.obsidian._request", fake_request)

    result = export_note(_item(), [_highlight("Some text.")])
    assert result == {"exported": True}

    methods = [call[0] for call in calls]
    assert methods == ["GET", "PUT"]
    put_kwargs = calls[1][2]
    assert "sha" not in put_kwargs["json"]
    decoded = base64.b64decode(put_kwargs["json"]["content"]).decode()
    assert "Some text." in decoded


def test_export_note_updates_with_existing_sha(monkeypatch):
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if method == "GET":
            return _FakeResponse(200, {"sha": "existing-sha"})
        if method == "PUT":
            return _FakeResponse(200, {"content": {"sha": "new-sha"}})
        raise AssertionError(f"unexpected method {method}")

    monkeypatch.setenv("OBSIDIAN_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr("app.obsidian._request", fake_request)

    result = export_note(_item(), [_highlight("Some text.")])
    assert result == {"exported": True}
    assert calls[1][2]["json"]["sha"] == "existing-sha"


def test_export_note_deletes_when_no_highlights_left(monkeypatch):
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if method == "GET":
            return _FakeResponse(200, {"sha": "existing-sha"})
        if method == "DELETE":
            return _FakeResponse(200, {})
        raise AssertionError(f"unexpected method {method}")

    monkeypatch.setenv("OBSIDIAN_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr("app.obsidian._request", fake_request)

    result = export_note(_item(), [])
    assert result == {"exported": False, "reason": "no_highlights"}
    methods = [call[0] for call in calls]
    assert methods == ["GET", "DELETE"]


def test_export_note_without_a_token_does_not_call_out(monkeypatch):
    monkeypatch.delenv("OBSIDIAN_GITHUB_TOKEN", raising=False)

    def fake_request(method, url, **kwargs):
        raise AssertionError("should not be called without a token")

    monkeypatch.setattr("app.obsidian._request", fake_request)

    result = export_note(_item(), [_highlight("Some text.")])
    assert result == {"exported": False, "reason": "not_configured"}


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload
