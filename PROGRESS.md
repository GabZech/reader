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

- **Client to do manually:** force-push `news-highlights` to a clean slate (their own call, once this shipped) — not yet done as of this note.

- **Change:** export images to Obsidian when part of a highlighted text selection. Kinds: behaviour, data/schema. Branch: `dev/export-images-to-obsidian`. Shape: an image is auto-included in a highlight when the selection's block range spans strictly around its top-level block (starts before it, ends after it) — no new tap/click, no JS changes. Leaves alone: any UI to show image presence on the highlight itself; only export is affected.

### Planned

1. Store which images a highlight covers — done. Added `image_urls` column to `highlights`; at save/merge time, walks `body_html`'s top-level blocks strictly between the final `(start_block, end_block)` and collects `<img>` sources (including `recovered-image-row` groups); recomputes fresh from the final unioned range on a merge, never concatenates.
2. Export images into the note — not started. `build_note_markdown` emits an image markdown line under a highlight's bullet for each stored `image_urls` entry.

## Stacked awaiting deploy

None.

## Blocked

None.
