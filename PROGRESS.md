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
- **Bug fix: iPhone Shortcut captures empty article body — ready to ship.** Root cause was not client-side rendering timing (that was a red herring chased first): the Shortcut's **Run JavaScript on Webpage** action had its page field bound to a fixed page instead of the shared one, so `html` silently carried the wrong content regardless of what site was shared or how the script was written. Found via a temporary `?debug=1` diagnostic on `/capture` (deployed to the live host from this branch, then reverted) that showed `html_received_length: 0` even for a trivial `completion("test")` script on an unrelated page. Client fixed the page-field binding on their phone and confirmed live on the real Nexo Jornal link with the plain script (`completion(document.documentElement.outerHTML);`) — no wait-loop needed. `docs/operations.md` updated to the plain script plus a note on checking that page-field binding. No app code changes ship (the debug diagnostic was reverted). Branch `claude/iphone-shortcut-ingestion-bug-6usxrr`, commit `07500b9`, pushed. Live host redeployed back to `main` after the debug branch was tried live. Next: open/update the PR and merge on the client's word.

## Stacked awaiting deploy

None.

## Blocked

None.
