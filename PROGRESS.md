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

- **Change:** outline images a highlight covers, so a selection across an image shows it was included. Kinds: visual, bug. Branch: `claude/image-selection-feedback-3l9eft`. Shape: images a highlight covers (the same ones stored and exported) get a 4px outline in the highlight colour, on select and on reload; mockup signed off. Leaves alone: tapping an outlined image does not open the highlight detail. Feedback round 1: a selection that starts or ends on an image must include it — done: an image-only boundary block now counts as covered; a boundary that merely touches one moves onto the neighbouring text. Tested in `tests/test_highlight_browser.py` (first browser tests, Playwright dev dependency). Next: client tries round 1 live.
- **Also open:** `maint/hook-command-guards` (hooks check the command itself, since `if` filters run the hook for unparsable commands) is pushed; PR awaits the client's go-ahead. Next product change after this one: a `§` marker before highlights that carry a section or subsection title (client liked the idea; mockup not yet made).

## Stacked awaiting deploy

None.

## Blocked

None.
