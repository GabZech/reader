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

- **Highlight and Land in Obsidian.** Deep-planned and confirmed, building on branch `dev/highlight-on-first-open`. Client wants all 3 slices stacked, reviewed by screenshot as each lands, and tried live together only once all 3 are built — not deployed slice by slice.

  ### Planned
  - Slice 1 — Highlight on first open: done (signed off from screenshots; not yet live)
  - Slice 2 — Sticky section titles, and deleting a highlight: done (signed off from screenshots; not yet live)
  - Slice 3 — The note lands in the vault: code and tests done (`app/obsidian.py`, `tests/test_obsidian.py`, wired into every highlight-mutating route in `app/main.py`); no UI to screenshot, this one is invisible by design. No summary section for now, per client (deferred to a possible future LLM step, not guessed at). `OBSIDIAN_GITHUB_TOKEN` confirmed set (Deployed) on `reader-skeleton`; about to deploy this branch for the combined live try of all 3 slices.

## Stacked awaiting deploy

- Slices 1, 2, and 3 (Highlight and Land in Obsidian), committed on `dev/highlight-on-first-open`, being deployed now for the combined live try.

## Blocked

None.
