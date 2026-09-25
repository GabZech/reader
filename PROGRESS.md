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

- **Highlight a standalone image on double-click/tap.** Branch `claude/image-highlight-double-click-1jvixs`. Kinds: behaviour + bug-adjacent (server rejects a single-image-block highlight the client already knows how to render). Scope: only images that are their own top-level block (the normal case here); an image sharing a block with real text is left alone. Client confirmed the plan and said "Build and deploy."

  ### Planned
  1. Done — Server accepts a single-image-block highlight: taught `images_in_block_range` the `start_block == end_block` image-only case; loosened the add-highlight endpoint so empty text is allowed when the range resolves to at least one image. Verified by pytest.
  2. Done — Client double-click/tap to save: `dblclick` handler on the article body saves a zero-width single-block highlight for an unhighlighted image; an already-highlighted image jumps to its detail page instead of re-saving. Verified by a browser test.
  3. Done — Mobile double-tap reliability: `touch-action: manipulation` on article-body images so double-tap isn't eaten by browser zoom.

  All three slices built, tested (292 passed) and tried locally (screenshot: double-click outlines the image, no text selection). Deploying next; awaiting client's live sign-off before merge.

## Stacked awaiting deploy

None.

## Blocked

None.
