# Harness

A mental model for how this repo keeps an AI agent reliable. Revisit this after any change to how agents work here; it should always describe what's actually true, not what's planned. The review this file and `docs/decisions.md` (2026-08-28 onward) are based on is no longer kept as a separate document: its recommendations are all built, and its evidence is now either fixed or superseded below.

Every agent harness needs five things: **Instructions** (what to do), **State** (what's true and what's in progress), **Verification** (proof it worked), **Scope** (do one thing at a time), and **Session lifecycle** (how a work session starts and ends cleanly). Below is where each one lives in this repo today.

| Subsystem | Main artifact today | Status |
| --- | --- | --- |
| Instructions | `AGENTS.md` (vendor-neutral) → `.claude/skills/` | One canonical file any tool can read; `CLAUDE.md` is a thin adapter |
| State | `docs/roadmap.md` (what's built) + `PROGRESS.md` (what's in flight right now) | Both covered |
| Verification | `uv run pytest`, `uv run ruff check`, the harness reference test, and the client's live sign-off | Solid, with a linter and a reference test now |
| Scope | `2-develop`'s one-change-at-a-time rule, Shape names what it leaves alone | Solid |
| Session lifecycle | Start, the six-step loop (with Pause), Ship's clean-state checklist | A real start-of-session check now runs automatically |

## Instructions

Where the rules an agent follows are written down.

- **[AGENTS.md](AGENTS.md)** is the front door and the canonical manual: any tool that reads it gets the start protocol, a routing table to every skill, at most 15 non-negotiables (each with a short why), where truth lives, and the end-of-session checklist, all in one file rather than a chain of pointers.
- **[CLAUDE.md](CLAUDE.md)** is a thin adapter: `@AGENTS.md` plus a fallback line. This repo's own `@` import has not been observed to expand (a fresh session in this environment received the raw `@AGENTS.md` text, unexpanded), so the fallback line still matters; a session that confirms expansion working can drop it.
- **`.claude/skills/*/SKILL.md`** are the workflow instructions. Claude Code discovers these natively now (a fresh session's own skill listing shows them without any routing rule pointing at them), and `.cursor/` is gone. The one that matters most day to day is [2-develop](.claude/skills/2-develop/SKILL.md): the change loop (Start, Frame, Shape, Preview, Build, Try, Pause, Ship). [questioning](.claude/skills/questioning/SKILL.md) governs how to talk to the client; [writing-docs](.claude/skills/writing-docs/SKILL.md), [write-skills](.claude/skills/write-skills/SKILL.md), and [commits](.claude/skills/commits/SKILL.md) govern editing docs, skills, and committing.

The discovery-phase skills (Kickoff through Foundation, and their question banks) are retired: Foundation has been accepted for weeks and feature work runs the change loop, so about 900 lines of dormant, phase-specific machinery were deleted rather than kept live. They are not lost: the git tag `archive/discovery-skills-2026-09` points at the last commit that had them, kept specifically so a future template repo can be generated from this one without re-writing them from scratch (see `docs/decisions.md` 2026-09-10).

A review of this file's own artifacts against an external template set ([`walkinglabs/learn-harness-engineering`](https://github.com/walkinglabs/learn-harness-engineering)) is preserved the same way: at git tag `archive/harness-template-plan-2026-09` ([`PLAN.md` at that tag](https://github.com/GabZech/reader/blob/archive/harness-template-plan-2026-09/PLAN.md)), logged in `docs/decisions.md` 2026-09-11. It explains, artifact by artifact, why several of the rows in the table above are shaped the way they are, and which parts of the template set this repo deliberately did not adopt.

## State

Where "what's true right now" and "what's still in progress" live.

- **[docs/roadmap.md](docs/roadmap.md)**, "What's Next," is the feature list: a checkbox per capability, grouped by epic, ticked only when shipped. Its "Where we are" Summary is now trimmed to 2-4 bullets describing current state, not a per-change changelog.
- **[PROGRESS.md](PROGRESS.md)** is the in-flight snapshot: overwritten, not appended, covering what's live, what's mid-change, what's committed but not yet deployed, and what's blocked. `init.sh` prints it at session start. Currently empty: no product change is in flight.
- **Living docs under `docs/`** (architecture, development, operations, ui-guidelines, vision/) are the current agreed picture, kept true as part of whichever change makes one wrong.
- **[docs/decisions.md](docs/decisions.md)** is the decision log: dated entries for choices expensive to undo, newest first, written by Ship. Backfilled with the eight choices already made that no living doc recorded. Replaces `docs/history/decisions/`, which sat as an empty `.gitkeep` for three weeks.
- **`docs/history/`** is gone. It was a frozen log nobody consulted day to day; the one durable file it held (the Obsidian export sample) moved to `docs/vision/`, the mockup pointer folded into `docs/mockup/README.md`, and the rest is preserved at the git tag `archive/history-2026-09` rather than as a folder to maintain.

## Verification

How an agent proves a change actually works, instead of just claiming it does.

- **`uv run pytest`**: 130 tests, run locally before every change is shown and in CI ([test.yml](.github/workflows/test.yml)) on every push and pull request.
- **`uv run ruff check`**: runs in CI before the tests. `pytest` and `ruff` are dev-only dependencies (`[dependency-groups] dev`); the deployed image installs with `--no-dev`, so neither ships in production.
- **[tests/test_harness_refs.py](tests/test_harness_refs.py)** asserts that markdown links and multi-segment backticked paths across `AGENTS.md`, `.claude/skills/`, and `docs/` all resolve. It runs with the rest of the suite and would have caught the two stale-path findings that motivated it.
- **[change-kinds.md](.claude/skills/2-develop/change-kinds.md)** spells out what "verified" means per kind of change.
- **The client's live sign-off** is the real gate: the client actually tries the change on the live app before it merges, not just a report of test results.
- **`/health`** returns `{"ok": true, "sha": "<short git sha>"}` (`"dev"` outside a built image), so "live is back on main" is a comparison `init.sh` makes automatically, not an assumption.

An independent review pass (e.g. `/code-review`) before Try for a not-small change was considered and left optional, per the plan this file no longer separately keeps: the client's live sign-off already outperforms most automated review gates, and requiring a second reviewer step for every not-small change would add friction the evidence did not clearly justify.

## Scope

Keeping an agent working on one thing at a time instead of sprawling.

- **`2-develop`'s Frame step** names the change and sizes it before anything else happens.
- **Shape** states what will change, what could break, how it'll be verified, and now also what it will leave alone, so the exclusions are on record before code starts.
- **[deep-plan.md](.claude/skills/2-develop/deep-plan.md)** breaks a bigger change into slices that each work end to end and get tried one at a time.
- **The "Do not" list** in `2-develop` rules out scope creep: restyling, widening the change beyond what was asked, pulling in unrequested work.

Still one of the strongest parts of this setup.

## Session lifecycle

How a work session starts, runs, and ends in a state the next session can pick up cleanly.

- **Start:** `bash init.sh --quick` runs automatically via a `SessionStart` hook in [.claude/settings.json](.claude/settings.json), printing git state, the live SHA against `origin/main`, and `PROGRESS.md`'s in-flight section without the agent having to remember to ask. `AGENTS.md`'s own start protocol is the fallback for tools that don't run the hook. `init.sh` (no flag) also runs `uv sync`, `ruff check`, and `pytest`, failing loudly rather than silently working around a red baseline.
- **Work:** the change loop in `2-develop`: Frame, Shape, Preview, Build, Try, Ship, with a new Pause step for leaving mid-change (commit, update `PROGRESS.md`, say what's live).
- **End:** `Ship` ticks the roadmap, updates whichever living doc the change made wrong, merges to main, redeploys, and now also runs the rest of the clean-state checklist: clear `PROGRESS.md`, empty `preview/`, free port 8000, confirm live equals main with `init.sh --quick`.
- **Deploy gate:** CI auto-deploys only a push to `main`; trying a branch live is a manual `workflow_dispatch`. `git push`, `flyctl deploy`, and `gh workflow run` ask for confirmation ([.claude/settings.json](.claude/settings.json)).

**Verified in this environment:** the GitHub CLI (`gh`) is not installed in a Claude Code cloud session, confirmed by direct check; the branch trial-deploy path documented in `docs/operations.md` now names the GitHub MCP server's workflow-trigger tool as the cloud-session mechanism instead, since it reaches this repo without `gh`. `CLAUDE.md`'s `@AGENTS.md` import did not expand in this session (see Instructions above). The `.claude/settings.json` ask-gates on `git push`/`flyctl deploy`/`gh workflow run` were exercised for real by this session's own branch push; see that push's outcome in git history and the session record rather than here, since a static doc can't keep this current across environments.
