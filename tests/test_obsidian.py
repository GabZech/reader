from __future__ import annotations

import base64
import json

from app.obsidian import build_note_markdown, export_note, note_path_for_item


def _item(**overrides):
    base = {
        "id": 42,
        "title": "Subagents on Subagents",
        "author": "Josh Rosen",
        "source_title": "X",
        "published_at": "2026-08-13T00:00:00+00:00",
        "seen_at": None,
        "url": "https://x.com/JoshARosen/status/2087944178558791874",
        "body_html": None,
    }
    base.update(overrides)
    return base


def _highlight(
    text,
    section_title=None,
    subsection_title=None,
    image_urls=None,
    start_block=0,
    end_block=0,
):
    return {
        "text": text,
        "section_title": section_title,
        "subsection_title": subsection_title,
        "image_urls": json.dumps(image_urls) if image_urls else None,
        "start_block": start_block,
        "end_block": end_block,
    }


def test_note_path_uses_published_date_and_title():
    path = note_path_for_item(_item())
    assert path == "Highlights/26-08-13 Subagents on Subagents.md"


def test_note_path_falls_back_to_seen_at_when_no_published_date():
    item = _item(published_at=None, seen_at="2026-09-01T00:00:00+00:00")
    assert note_path_for_item(item) == "Highlights/26-09-01 Subagents on Subagents.md"


def test_note_path_strips_filesystem_unsafe_characters_from_the_title():
    item = _item(title='Ask: "What now?" / How <this> works | really?')
    path = note_path_for_item(item)
    assert path == "Highlights/26-08-13 Ask What now How this works really.md"


def test_note_path_falls_back_to_item_id_when_title_sanitizes_to_nothing():
    item = _item(title='///:::***')
    assert note_path_for_item(item) == "Highlights/26-08-13 42.md"


def test_build_note_markdown_includes_frontmatter_and_title():
    md = build_note_markdown(_item(), [_highlight("First point.")])
    assert "author: Josh Rosen" in md
    assert "published_date: 2026-08-13" in md
    assert "source: https://x.com/JoshARosen/status/2087944178558791874" in md
    assert "# Subagents on Subagents" in md
    assert "## Highlights" in md
    assert "- First point." in md
    assert "## Summary" not in md


def test_build_note_markdown_includes_image_lines_under_the_bullet():
    highlights = [
        _highlight("Text only."),
        _highlight(
            "Spans an image.",
            image_urls=["https://example.test/a.png", "https://example.test/b.png"],
        ),
    ]
    md = build_note_markdown(_item(), highlights)
    lines = [line for line in md.splitlines() if line]
    assert "  - ![](https://example.test/a.png)" not in "\n".join(
        lines[: lines.index("- Spans an image.")]
    )
    idx = lines.index("- Spans an image.")
    assert lines[idx + 1] == "  - ![](https://example.test/a.png)"
    assert lines[idx + 2] == "  - ![](https://example.test/b.png)"


def test_build_note_markdown_turns_a_captured_list_into_a_sublist():
    # A highlight spanning a <ul>/<ol> arrives with each item on its own
    # line (the browser's range.toString() inserts a newline at each block
    # boundary) - those should become an indented sublist, not a garbled
    # single bullet with raw newlines in it.
    highlight = _highlight("\nMinimum viable\nMaximum necessary\n")
    md = build_note_markdown(_item(), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("- Minimum viable")
    assert lines[idx + 1] == "  - Maximum necessary"
    assert "\nMinimum viable\nMaximum necessary\n" not in md


def test_build_note_markdown_nests_images_after_multiline_text():
    highlight = _highlight(
        "Lead-in text.\nSecond line.",
        image_urls=["https://example.test/a.png"],
    )
    md = build_note_markdown(_item(), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("- Lead-in text.")
    assert lines[idx + 1] == "  - Second line."
    assert lines[idx + 2] == "  - ![](https://example.test/a.png)"


def test_build_note_markdown_preserves_nested_unordered_sublist_depth():
    body_html = (
        "<ul>\n<li>Outer one\n<ul>\n<li>Inner a</li>\n<li>Inner b</li>\n</ul>\n</li>\n"
        "<li>Outer two</li>\n</ul>"
    )
    highlight = _highlight(
        "\nOuter one\n\nInner a\nInner b\n\n\nOuter two\n",
        start_block=0,
        end_block=0,
    )
    md = build_note_markdown(_item(body_html=body_html), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("-")
    assert lines[idx + 1 : idx + 5] == [
        "  - Outer one",
        "    - Inner a",
        "    - Inner b",
        "  - Outer two",
    ]


def test_build_note_markdown_renders_an_ordered_list_with_its_own_numbering():
    body_html = '<ol start="3">\n<li>Third step</li>\n<li>Fourth step</li>\n</ol>'
    highlight = _highlight("\nThird step\nFourth step\n", start_block=0, end_block=0)
    md = build_note_markdown(_item(body_html=body_html), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("-")
    assert lines[idx + 1 : idx + 3] == ["  3. Third step", "  4. Fourth step"]


def test_build_note_markdown_mixes_ordered_and_nested_unordered_markers():
    body_html = (
        "<ol>\n<li>Step one\n<ul>\n<li>Detail a</li>\n<li>Detail b</li>\n</ul>\n</li>\n"
        "<li>Step two</li>\n</ol>"
    )
    highlight = _highlight(
        "\nStep one\n\nDetail a\nDetail b\n\n\nStep two\n",
        start_block=0,
        end_block=0,
    )
    md = build_note_markdown(_item(body_html=body_html), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("-")
    assert lines[idx + 1 : idx + 5] == [
        "  1. Step one",
        "    - Detail a",
        "    - Detail b",
        "  2. Step two",
    ]


def test_build_note_markdown_nests_a_bare_bullet_when_the_highlight_starts_inside_the_list():
    body_html = "<ul>\n<li>Bullet one</li>\n<li>Bullet two</li>\n</ul>"
    highlight = _highlight("\nBullet one\nBullet two\n", start_block=0, end_block=0)
    md = build_note_markdown(_item(body_html=body_html), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("-")
    assert lines[idx + 1 : idx + 3] == ["  - Bullet one", "  - Bullet two"]


def test_build_note_markdown_keeps_lead_in_text_before_a_captured_list():
    body_html = "<p>Notes:</p>\n<ul>\n<li>Bullet one</li>\n<li>Bullet two</li>\n</ul>"
    highlight = _highlight(
        "Notes:\n\nBullet one\nBullet two\n", start_block=0, end_block=1
    )
    md = build_note_markdown(_item(body_html=body_html), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("- Notes:")
    assert lines[idx + 1 : idx + 3] == ["  - Bullet one", "  - Bullet two"]


def test_build_note_markdown_falls_back_when_shape_and_text_line_counts_disagree():
    # A single top-level blockquote block holding two paragraphs captures as
    # two text lines but only counts as one (non-list) shape entry - the
    # mismatch must fall back to the flat rendering rather than guess.
    body_html = "<blockquote>\n<p>Quoted first</p>\n<p>Quoted second</p>\n</blockquote>"
    highlight = _highlight(
        "\nQuoted first\nQuoted second\n", start_block=0, end_block=0
    )
    md = build_note_markdown(_item(body_html=body_html), [highlight])
    lines = [line for line in md.splitlines() if line]
    idx = lines.index("- Quoted first")
    assert lines[idx + 1] == "  - Quoted second"


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

    item = _item()
    result = export_note(item, [_highlight("Some text.")])
    assert result == {"exported": True, "path": note_path_for_item(item)}

    methods = [call[0] for call in calls]
    assert methods == ["GET", "PUT"]
    put_kwargs = calls[1][2]
    assert "sha" not in put_kwargs["json"]
    assert put_kwargs["json"]["message"] == f"add note: {item['title']}"
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

    item = _item()
    result = export_note(item, [_highlight("Some text.")])
    assert result == {"exported": True, "path": note_path_for_item(item)}
    assert calls[1][2]["json"]["sha"] == "existing-sha"
    assert calls[1][2]["json"]["message"] == f"update note: {item['title']}"


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
    assert result == {"exported": False, "reason": "no_highlights", "path": None}
    methods = [call[0] for call in calls]
    assert methods == ["GET", "DELETE"]


def test_export_note_without_a_token_does_not_call_out(monkeypatch):
    monkeypatch.delenv("OBSIDIAN_GITHUB_TOKEN", raising=False)

    def fake_request(method, url, **kwargs):
        raise AssertionError("should not be called without a token")

    monkeypatch.setattr("app.obsidian._request", fake_request)

    result = export_note(_item(), [_highlight("Some text.")])
    assert result == {"exported": False, "reason": "not_configured", "path": None}


def test_export_note_deletes_the_old_file_when_the_path_changed(monkeypatch):
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if method == "GET" and "old-name.md" in url:
            return _FakeResponse(200, {"sha": "old-sha"})
        if method == "DELETE" and "old-name.md" in url:
            return _FakeResponse(200, {})
        if method == "GET":
            return _FakeResponse(404, {})
        if method == "PUT":
            return _FakeResponse(201, {"content": {"sha": "new-sha"}})
        raise AssertionError(f"unexpected {method} {url}")

    monkeypatch.setenv("OBSIDIAN_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr("app.obsidian._request", fake_request)

    item = _item()
    result = export_note(
        item, [_highlight("Some text.")], previous_path="Highlights/old-name.md"
    )
    assert result == {"exported": True, "path": note_path_for_item(item)}

    deletes = [(m, u) for m, u, _ in calls if m == "DELETE"]
    assert len(deletes) == 1
    assert "old-name.md" in deletes[0][1]
    puts = [(m, u) for m, u, _ in calls if m == "PUT"]
    assert len(puts) == 1
    assert "old-name.md" not in puts[0][1]


def test_export_note_does_not_delete_when_the_path_is_unchanged(monkeypatch):
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if method == "GET":
            return _FakeResponse(404, {})
        if method == "PUT":
            return _FakeResponse(201, {"content": {"sha": "new-sha"}})
        raise AssertionError(f"unexpected {method} {url}")

    monkeypatch.setenv("OBSIDIAN_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr("app.obsidian._request", fake_request)

    item = _item()
    result = export_note(
        item, [_highlight("Some text.")], previous_path=note_path_for_item(item)
    )
    assert result == {"exported": True, "path": note_path_for_item(item)}
    methods = [call[0] for call in calls]
    assert "DELETE" not in methods


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload
