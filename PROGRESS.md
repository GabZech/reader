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

**Return to the highlight, and resume early.** Kinds: behaviour, bug. Branch: `claude/highlight-scroll-position-egtd4c` (the cloud session's designated branch, in place of a `dev/` name).

Shape agreed: the Close links on the highlight and title pages, and the redirect after saving a title, go to `/items/{id}#highlight-{id}`. The article scrolls to that highlight (centred) as soon as highlights are drawn. Resuming the saved reading spot no longer waits for `load`: it jumps when the text is ready, then corrects once after `load`, unless the user has touched the page (wheel, touch, key, pointer) since. A highlight marker beats the saved spot; a missing highlight falls back to it. Leaves alone: delete-redirect, progress saving, schema, page looks, list/source back-links.

### Planned

- Slice 1: back links and title redirect carry the marker (tests in `tests/test_app.py`): in progress
- Slice 2: early jump, highlight target, user-scroll guard (browser tests in `tests/test_highlight_browser.py`): not started

Feedback rounds: 0. Next step: build, then deploy the branch for a live try.

## Stacked awaiting deploy

None.

## Blocked

None.
