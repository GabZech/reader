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

- **Verify a PR named in `PROGRESS.md` before trusting it.** PR [#18](https://github.com/GabZech/reader/pull/18), which sat here as "open" for 5 days after it actually merged on 2026-09-15 (nothing ever re-checked it), is the proof this was needed. `AGENTS.md`'s start protocol now requires checking GitHub before trusting an open-PR line. This change itself: not started.

## Stacked awaiting deploy

None.

## Blocked

None.
