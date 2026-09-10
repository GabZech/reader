# Decisions

Choices that are expensive to undo, newest first. Written by Ship when a change produces one; the threshold is a choice a future session might plausibly reverse. Not a changelog: routine changes live in git log and the roadmap's ticked lines.

Each entry: date and title, then **Decision**, **Why**, **Rejected**, **Revisit when**.

## 2026-09-10: Archive the discovery-phase skills at a tag instead of a template repo

**Decision:** Tag the last commit that had the retired discovery skills (Kickoff through Foundation, `create-phase-skill`, and their question banks) as `archive/discovery-skills-2026-09`, rather than copying them into `GabZech/template-spec-workflow` now.

**Why:** The client expects to ask an agent to generate a template repo from `reader` itself at some point in the future; a tag on this repo is enough for that generation to pull the skills back out, without committing now to a separate template repo's shape or conventions.

**Rejected:** Pushing them into `GabZech/template-spec-workflow` immediately: premature while the actual "generate a template from this repo" task, and its shape, has not been asked for yet. Keeping them live in `.claude/skills/` here: they are dormant now that Foundation is accepted, and leaving 900 lines of unused machinery in place was the original problem.

**Revisit when:** The client asks for a template repo generated from `reader`. At that point the tag is the source, not this repo's live `.claude/skills/`.

## 2026-09-10: Collapse `docs/history/` into this file

**Decision:** Retire `docs/history/` as a working folder. The one durable spec it held (the Obsidian export sample) moved under `docs/vision/`; the mockup pointer folded into `docs/mockup/README.md`; the rest is tagged (`archive/history-2026-09`) and deleted.

**Why:** `docs/history/decisions/` sat empty for three weeks while several hard-to-undo choices landed undocumented elsewhere; `docs/history/epics/` froze working files from a workflow the change loop already replaced. Neither was consulted day to day, and both invited "update history to match code," which the rules explicitly forbade.

**Rejected:** Keeping history and adding this file alongside it: two places to check for the same kind of fact.

**Revisit when:** Never, by design. The tag preserves the record if it is ever needed.

## 2026-09-10: Sign-off gates merge, not commit

**Decision:** Commit checkpoints on the branch as soon as checks pass. Only the client's live sign-off gates the merge to `main`.

**Why:** The previous wording ("do not commit before sign-off," "deploy from the working tree") could not be followed in a cloud session, which has no working tree to deploy from and can only reach the live host through a pushed commit.

**Rejected:** Deploying straight from an uncommitted working tree: it does not exist as a concept in a cloud session and was already being worked around inconsistently.

**Revisit when:** Not expected to.

## 2026-09-10: Deploy only on the client's explicit go-ahead

**Decision:** Showing a screenshot or a local walkthrough is never itself permission to deploy. Deploy only after the client's reply says to.

**Why:** The gap between "here's what changed" and an actual "yes, deploy" let a premature push happen twice in one session before this was codified.

**Rejected:** Trusting agent judgement on when a change looks ready enough to go live automatically.

**Revisit when:** Not expected to.

## 2026-09-09: CI deploys on push to `main`

**Decision:** A GitHub Actions job deploys automatically after tests pass on a push to `main`, using a `FLY_API_TOKEN` repository secret. Trying a branch live goes through the same job on manual dispatch instead of deploying every push.

**Why:** A cloud agent session's own network cannot reach Fly's remote builder: the deploy goes over gRPC, and the sandbox's egress proxy cannot carry that handshake. GitHub-hosted runners are not behind that proxy.

**Rejected:** Running `flyctl deploy` from inside a cloud session directly: it fails at the network layer, not something a workaround in this repo can fix.

**Revisit when:** If Fly ever exposes a deploy path that works over plain HTTPS, or the hosting choice itself is revisited.

## 2026-09-09: Migrate to `uv` for Python dependencies

**Decision:** Replace `requirements.txt` with `pyproject.toml` plus `uv.lock`; Dockerfile and CI install through `uv`.

**Why:** A locked, reproducible install with one tool for the venv and the dependency graph, matching `docs/development.md`'s single-command run story.

**Rejected:** Staying on plain `pip` and an unpinned `requirements.txt`: no lockfile meant CI, local, and production could silently drift apart.

**Revisit when:** Not expected to.

## 2026-08-28: The change loop replaces the epic-based workflow

**Decision:** Feature work runs the six-step change loop (`.claude/skills/2-develop/`) instead of per-epic plan and clarifying-answers files.

**Why:** The epic workflow's working files (`docs/history/epics/`) required upkeep that drifted from what actually shipped; the change loop verifies each change live instead of against a written plan.

**Rejected:** Keeping per-epic plan files as a parallel record: "no plan files" is deliberate, per section 5 of the harness review this file's own history section came from.

**Revisit when:** Not expected to.

## 2026-08-24: Newsletter dedup by Message-ID; mark IMAP `\Seen`, never archive

**Decision:** A synced message's identity is its `Message-ID` header, independent of the mailbox's own read state. After ingest, mark the IMAP message `\Seen` for mailbox tidiness only; never delete or archive it from the mailbox.

**Why:** The client asked for no archiving of the isolated mailbox. Marking `\Seen` is cosmetic and reversible; `Message-ID` dedup means a mis-marked or re-synced message is never ingested twice regardless of that flag.

**Rejected:** Using the IMAP `UNSEEN` search result as the source of truth for what is already ingested: it would conflate mailbox tidiness with dedup and break if anything else touches the mailbox.

**Revisit when:** If the isolated mailbox ever needs cleanup for size or cost, revisit whether old, already-ingested mail can be archived without changing the dedup story.

## 2026-08-20: One Fly app serves both trying and living

**Decision:** Trial deploys and the real production traffic share a single Fly app and host, rather than separate dev and prod apps.

**Why:** A second always-on machine would roughly double the monthly hosting cost against a $10 ceiling that already has little headroom.

**Rejected:** Standing up a second Fly app now: the cost does not fit the MVP-stage budget.

**Revisit when:** Once the MVP ships and the cost ceiling is reopened. Until then, a change briefly runs live against the real library during Try, which is a known, accepted risk (see `docs/roadmap.md` Post-MVP Notes).
