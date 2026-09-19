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
- **Bug fix: iPhone Shortcut captures empty article body on client-rendered sites.** Diagnosed: Nexo Jornal (and similarly built sites) render the article body client-side after page load; the Shortcut's `completion(document.documentElement.outerHTML)` fires before that render finishes, so `/capture` gets an empty shell and saves the item with a correct title but no body. Confirmed by fetching the article server-side (`<div id="__next">` is empty in the raw response) and by manually hydrating the real article content into the DOM, where `trafilatura` extracts it cleanly - so the extraction code itself is fine. Fix is documented in `docs/operations.md`'s Shortcut recipe (a poll-for-content script with a 5s ceiling), committed on branch `claude/iphone-shortcut-ingestion-bug-6usxrr` and pushed. No app code changed. Waiting on the client to manually replace the "Run JavaScript on Webpage" action in their existing Shortcut with the new script, then confirm the Nexo Jornal link captures with a body before this is considered done.

## Stacked awaiting deploy

None.

## Blocked

None.
