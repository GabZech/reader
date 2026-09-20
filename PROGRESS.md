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

  ### Planned — export trigger rework (client wants at most ~1 commit per article, not one per action)
  - Slice A — Stop exporting on every action, track what's pending instead: done. Added `items.highlights_touched_at` / `items.highlights_exported_at`; add/title/delete highlight actions update "touched" only now. Nothing exports yet (expected, by design, until slice B lands) — 3 new tests prove no export call happens on these actions; full suite (160) and lint pass.
  - Slice B — Archiving or marking as read exports once; deleting never touches the vault: done. 8 new tests cover: archive/mark-read export exactly once when pending, skip when nothing pending, skip a second time once already caught up; delete exports once as a final catch-up when pending then removes local rows, skips export entirely when nothing pending. Full suite (167) and lint pass.
  - Slice C — The day-later safety net: done. A background asyncio task (in `app.main`'s lifespan) runs once at startup and then every 24h, exporting any item touched more than a day ago and not caught up since. `items_due_for_export` in `db.py` is the pure, directly-tested query; 2 new tests cover the query logic and the check picking up only what's actually due. Full suite (169) and lint pass. All 3 slices for this rework are now built; not yet deployed or tried live.
  - Flagged and left as-is per client: local highlight rows are not kept as a permanent record once an item is deleted, only the exported vault file persists.

  ### Planned — merge overlapping highlights (was: reject with 409 and leave a phantom DOM mark)
  - Slice 1 — Server-side merge: not started. Save endpoint accepts which existing highlight ids the new selection overlaps, validates each actually belongs to the item and actually overlaps, validates nothing else is still overlapped, then deletes the old rows and inserts one merged highlight. Section/subsection title carried forward from the earliest merged highlight that had one.
  - Slice 2 — Client-side detection: not started. On a finished selection, check it against the article's known highlights; anything overlapping is sent as a merge, with the combined text read from one DOM range spanning the full union. The overlap-rejection DOM bug noted earlier in `docs/roadmap.md` is superseded by this (overlap merges instead of being rejected), so that roadmap line should be removed once this ships.

## Stacked awaiting deploy

None — `dev/highlight-on-first-open` is the live host right now, holding all 3 slices, awaiting the client's live sign-off before Ship (PR, merge, redeploy `main`).

## Blocked

None.
