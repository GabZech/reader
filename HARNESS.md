# Harness

A mental model for how this repo keeps an AI agent reliable. Revisit this after any change to how agents work here — it should always describe what's actually true, not what's planned.

Every agent harness needs five things: **Instructions** (what to do), **State** (what's true and what's in progress), **Verification** (proof it worked), **Scope** (do one thing at a time), and **Session lifecycle** (how a work session starts and ends cleanly). Below is where each one lives in this repo today.

For the fuller analysis this is based on, and the improvements still to come, see [harness-plan.md](harness-plan.md).

| Subsystem | Main artifact today | Status |
| --- | --- | --- |
| Instructions | `CLAUDE.md` → `.cursor/rules/` → `.cursor/skills/` | Works, but tool-specific (see below) |
| State | `docs/roadmap.md` + living docs under `docs/` | Good for "what's built"; nothing yet for "what's in progress right now" |
| Verification | `uv run pytest` + the client's live sign-off | Solid; no linter yet |
| Scope | `2-develop`'s one-change-at-a-time rule | Solid |
| Session lifecycle | The six-step change loop, start to finish | No formal start-of-session check yet |

## Instructions

Where the rules an agent follows are written down.

- **[CLAUDE.md](CLAUDE.md)** is the front door: every session is supposed to read it first. Today it mostly points elsewhere rather than holding rules itself.
- **`.cursor/rules/*.mdc`** are the always-on guardrails: [engagement.mdc](.cursor/rules/engagement.mdc) (when the change loop applies), [chats.mdc](.cursor/rules/chats.mdc) (how to talk to the client), [commits.mdc](.cursor/rules/commits.mdc) (how to commit).
- **`.cursor/skills/*/SKILL.md`** are the workflow instructions, read only when the task matches. The one that matters most day to day is [2-develop](.cursor/skills/2-develop/SKILL.md): the actual change loop (Frame, Shape, Preview, Build, Try, Ship). [questioning](.cursor/skills/questioning/SKILL.md) governs how to talk to you; [writing-docs](.cursor/skills/writing-docs/SKILL.md) and [write-skills](.cursor/skills/write-skills/SKILL.md) govern editing docs and skills.

**Known gap:** this whole setup is written for Cursor's auto-triggering, but you're using Claude Code, which doesn't auto-trigger `.cursor/` files — `CLAUDE.md` has to explicitly say "go read these" for it to work. It works, but it's tied to one vendor. The plan proposes a single vendor-neutral `AGENTS.md` that any tool can read.

## State

Where "what's true right now" and "what's still in progress" live.

- **[docs/roadmap.md](docs/roadmap.md)**, "What's Next," is the closest thing to a feature list: a checkbox per capability, grouped by epic, ticked only when shipped.
- **Living docs under `docs/`** (architecture, development, operations, ui-guidelines, and `vision/`) are the current agreed picture of the product. They're supposed to be corrected every time a change makes one of them wrong — that discipline occasionally lapses, which is why part of this session's work was a truth pass over them.
- **`docs/history/`** is a frozen log of how discovery and early epics went. It's not consulted day to day.

**Known gap:** there's no record of *in-flight* state — what branch is mid-change, what was agreed in Shape, what's committed but not yet deployed. Right now that only lives in the conversation and in git, which is lost across a `/clear` or a new session. The plan proposes a small `PROGRESS.md` snapshot for this.

## Verification

How an agent proves a change actually works, instead of just claiming it does.

- **`uv run pytest`**: 102 tests, about 20 seconds, run locally before every change is shown and in CI ([test.yml](.github/workflows/test.yml)) on every push and pull request.
- **[change-kinds.md](.cursor/skills/2-develop/change-kinds.md)** spells out what "verified" means per kind of change: a bug needs a test that reproduces the report, a schema change needs a backup and a rehearsal on a copy of the real data, an external-system change needs a probe against the real thing.
- **The client's live sign-off** is the real gate, and it's a stronger check than most automated harnesses have: the client actually tries the change on the live app before it merges, not just on a report of test results.

**Known gap:** no linter or type-checker yet, so a whole class of small bugs (unused imports, obvious type mismatches) isn't caught mechanically.

## Scope

Keeping an agent working on one thing at a time instead of sprawling.

- **`2-develop`'s Frame step** names the change and sizes it before anything else happens.
- **Shape** states what will change and how it'll be verified, and stops for a confirm on anything not small.
- **[deep-plan.md](.cursor/skills/2-develop/deep-plan.md)** breaks a bigger change into slices that each work end to end and get tried one at a time, rather than one giant change landing all at once.
- **The "Do not" list** in `2-develop` explicitly rules out scope creep: restyling, widening the change beyond what was asked, pulling in unrequested work.

This is one of the strongest parts of the current setup.

## Session lifecycle

How a work session starts, runs, and ends in a state the next session can pick up cleanly.

- **Start:** currently informal — there's no automated check of git state, test health, or what's live before work begins.
- **Work:** the six-step loop in `2-develop` — Frame, Shape, Preview, Build, Try, Ship.
- **End:** `Ship` is the strongest part of this — it ticks the roadmap, updates whichever living doc the change made wrong, commits docs before merging, merges to main, redeploys, and recommends `/clear` for a fresh session.
- **Deploy gate:** just hardened. CI now only auto-deploys a push to `main`; trying a branch live requires a manual trigger. `git push` and `flyctl deploy` now ask for confirmation ([.claude/settings.json](.claude/settings.json)) instead of running unattended.

**Known gap:** no start-of-session health check. The plan proposes an `init.sh` that reports test status, git state, and what's actually live, so a session starts knowing where things stand instead of assuming.

## What's proposed but not built yet

Phase 1 of the plan (making the rules internally consistent and the docs true) is done as of this file. Phases 2 to 4 — a vendor-neutral `AGENTS.md`, the `PROGRESS.md` snapshot, `init.sh`, moving skills so Claude Code triggers them natively, and collapsing `docs/history/` into `docs/decisions.md` — are proposed in [harness-plan.md](harness-plan.md) but not yet done. Update this file's "Known gap" notes as each phase lands.
