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
- **Highest-priority unfinished item:** the title marker, in flight below. Epics in `docs/roadmap.md` do not impose an order; this names what was actually picked, not a computed priority
- **Current blocker:** none

## Live now

Run `bash init.sh` for the current live SHA against `origin/main`.

## In flight

- **Client to do manually:** force-push `news-highlights` to a clean slate (their own call, once this shipped) — not yet done as of this note.

- **Change:** a small yellow `§` just before any highlight that carries a section or subsection title. Kinds: visual, behaviour. Branch: `dev/highlight-title-marker`, stacked on `claude/image-selection-feedback-3l9eft` (PR #37) for its browser-test tooling. Shape: `has_title` in `highlights_json` and the save response; an empty `span.hl-title-marker` before the highlight's first mark, its `§` drawn by CSS so block offsets stay put; kept through a merge; tapping it opens the highlight. Mockup signed off (`--title-marker`: `#fbbf24` dark, `#b45309` light). Built and tested (`tests/test_highlight_title_marker.py`). Leaves alone: no distinction between section and subsection. Next: client says whether to deploy for a live try.

## Stacked awaiting deploy

None.

## Blocked

None.
