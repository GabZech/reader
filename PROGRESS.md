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
- **Swipe gestures on item rows** (visual + behaviour), branch `claude/swipe-gestures-items-g4yteh`. Mockup signed off (throwaway, in `preview/`). Right to left acts at once: Mark as read (Unread tab), Mark as unread (Read tab), Archive (Library), Move to Library (Archive tab). Left to right deletes after a popup (title, "removed from every list, can't be undone", Cancel / Delete). A source's items page: delete only. Replaces the old swipe-left-to-reveal-Delete. Leaves alone: article page buttons, rows at rest, schema. Unread and Move to Library never touch the vault. Failed save: row snaps back with "Couldn't save".

### Planned

1. List pages and a source's items page: both swipes, all four actions (two new routes: unread, unarchive), the popup, live tab counts — built, deployed for live try (725fe6a)
2. Home rows: same swipes, next hidden row moves up — built, deployed for live try (725fe6a)

## Stacked awaiting deploy

None.

## Blocked

None.
