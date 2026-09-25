# Progress

Snapshot of in-flight state, overwritten each time, not appended. Git log is
already the session log. Update this at every change-loop checkpoint commit;
clear it at Ship. A small change's Shape stays chat-only; a not-small
change's deep-plan output lives here instead, under In flight's
`### Planned` heading, since chat is not assumed to survive a lost session.

## Current verified state

- **Repository root:** `/home/user/reader`
- **Standard startup path:** `bash init.sh`
- **Standard verification path:** `uv run ruff check` then `uv run pytest`
- **Focused debug command:** `uv run pytest tests/test_app.py -k <name>`
- **Run the app:** `RUN_START_COMMAND=1 bash init.sh` (without `--quick`), or see `docs/development.md`
- **Highest-priority unfinished item:** none chosen yet. Epics in `docs/roadmap.md` do not impose an order; this names what was actually picked, not a computed priority
- **Current blocker:** none

## Live now

Run `bash init.sh` for the current live SHA against `origin/main`.

## In flight

- **Queued, not started:** commit message `add note:` for a new file, `update note:` for an existing one — awaiting client go-ahead.

- **Change:** preserve full list nesting depth and ordered/unordered list type when a highlight spans a list, on export. Kind: behaviour. Branch: `claude/highlights-export-formatting-3swqvt`. Builds on the already-shipped flat sublist fix (commit `26a1efd`).
  Shape: server-only — reconstruct structure from `item['body_html']` + the highlight's stored block range at export time (same pattern as `images_in_block_range`); no changes to `app.js`, the save path, or the schema. Falls back to today's shipped flat behaviour whenever the HTML-derived shape doesn't cleanly line up with the captured text (missing `body_html`, or an edge case like list-items-containing-paragraphs).
  ### Planned
  - [ ] Slice 1: shape extraction — pure function walking `body_html`'s blocks in a highlight's range, returning per-line `None` (plain) or `(depth, marker)` for each `<li>` (nesting depth, `-`/`N.` marker honoring `<ol start>`). Verified with unit tests only (flat list, nested list, ordered list, mixed nesting, plain paragraphs, missing `body_html`, list-of-paragraphs edge case).
  - [ ] Slice 2: wire into `build_note_markdown` — use shapes to indent/mark each line when they align with the captured text; fall back to the flat rendering otherwise. Verified with unit tests plus a rendered screenshot.

## Stacked awaiting deploy

None.

## Blocked

None.
