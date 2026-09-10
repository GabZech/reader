from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

CHECKED_FILES = (
    [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "README.md", ROOT / "HARNESS.md"]
    + sorted((ROOT / ".claude" / "skills").rglob("*.md"))
    + sorted((ROOT / "docs").rglob("*.md"))
)

# Gitignored paths that legitimately do not exist in a fresh checkout.
ALLOWLIST_PREFIXES = ("preview/",)

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Backticked paths are only checked when they look like a genuine repo-relative
# path (more than one segment); a bare `SKILL.md` or `epics.md` is too often
# informal shorthand for something linked elsewhere in the same doc.
BACKTICK_PATH_RE = re.compile(
    r"`([\w.\-]+(?:/[\w.\-]+)+\.(?:md|py|sh|json|toml|yml|yaml|html|js|css|txt))`"
)


def _references(text: str):
    for match in MD_LINK_RE.finditer(text):
        target = match.group(1)
        if not target.startswith(("http://", "https://", "mailto:")):
            yield "link", target
    for match in BACKTICK_PATH_RE.finditer(text):
        yield "backtick", match.group(1)


def _resolves(target: str, source: Path) -> bool:
    clean = target.split("#", 1)[0].strip()
    if not clean:
        return True
    if any(clean.startswith(prefix) for prefix in ALLOWLIST_PREFIXES):
        return True
    candidates = [(source.parent / clean).resolve(), (ROOT / clean).resolve()]
    return any(c.exists() for c in candidates)


@pytest.mark.parametrize(
    "source", CHECKED_FILES, ids=lambda p: str(p.relative_to(ROOT))
)
def test_references_resolve(source: Path):
    text = source.read_text(encoding="utf-8")
    broken = [
        f"{kind}: {target}"
        for kind, target in _references(text)
        if not _resolves(target, source)
    ]
    assert not broken, f"broken references in {source.relative_to(ROOT)}: {broken}"
