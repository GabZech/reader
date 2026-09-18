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

- **Repo maintenance: merge to main only through a gated PR, plus `dev/`/`maint/` branch-naming convention.** PR [#18](https://github.com/GabZech/reader/pull/18) (branch `maint/pr-gated-merge`) is open, tests and lint pass. GitHub branch protection on `main` is live (PR required; `enforce_admins` is off so the client can still push small increments to `main` directly, per their preference). Nothing is blocking it: waiting only on the client's merge decision — they merge it, or tell the agent to squash-merge.

- **Highlight and Land in Obsidian.** Deep-planned and confirmed, building on branch `dev/highlight-on-first-open`, now deployed there (live SHA `b318c3d`) for the combined live try.

  ### Planned
  - Slice 1 — Highlight on first open: done (signed off from screenshots). Client tried it live on a real iPhone and reported highlighting didn't work: native selection-handle dragging never fires `mouseup`, which is what the code relied on. Fixed by also listening for `selectionchange` (debounced 400ms), verified with a Playwright script that reproduces the handle-drag pattern (no synthetic `mouseup`) and confirmed the highlight is created and survives a reload. Redeployed; awaiting the client trying it again on their phone.
  - Slice 2 — Sticky section titles, and deleting a highlight: done (signed off from screenshots; not yet tried live by the client)
  - Slice 3 — The note lands in the vault: done. Proven end to end against the real system while deployed: creating a highlight on a live test article produced a real commit in `GabZech/news-highlights` (`Highlights/<item_id>.md`); deleting the last highlight produced a real removal commit. Two real bugs found and fixed in the process (`sqlite3.Row` has no `.get()`; the export call wasn't isolated from the routes it rides on). Test data cleaned up from both the live library and the real repo afterward. Not yet tried live by the client.

## Stacked awaiting deploy

None — `dev/highlight-on-first-open` is the live host right now, holding all 3 slices, awaiting the client's live sign-off before Ship (PR, merge, redeploy `main`).

## Blocked

None.
