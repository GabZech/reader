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
- **Current blocker:** `harness/pr-gated-merge` is pushed and needs a PR opened; `gh` is unauthenticated in this environment (see Blocked)

## Live now

Run `bash init.sh` for the current live SHA against `origin/main`.

## In flight

None.

## Stacked awaiting deploy

None.

## Blocked

- **Repo maintenance: merge to main only through a gated PR.** Branch `harness/pr-gated-merge` is pushed (commits `c107c9b`, `05b7d5e`: AGENTS.md, HARNESS.md, docs/decisions.md, `.claude/settings.json`, `.claude/skills/2-develop/SKILL.md`), tests and lint pass. Blocked on: (1) opening the PR — `gh` is not authenticated in this environment (`gh auth login` needed), or open it by hand at https://github.com/GabZech/reader/pull/new/harness/pr-gated-merge; (2) GitHub branch protection on `main` (require PR before merge) — client asked for this too, not yet configured, also needs `gh` auth or the GitHub web UI. Once the PR exists, merge it yourself or tell the agent to (squash).
