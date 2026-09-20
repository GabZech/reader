# Decisions

Choices that are expensive to undo, newest first. Written by Ship when a change produces one; the threshold is a choice a future session might plausibly reverse. Not a changelog: routine changes live in git log and the roadmap's ticked lines.

Each entry: date and title, then **Decision**, **Why**, **Rejected**, **Revisit when**.

## 2026-09-20: A PR named in `PROGRESS.md` is verified against GitHub, not trusted

**Decision:** `AGENTS.md`'s start-of-session step 2 now requires checking GitHub before trusting any "PR open" line in `PROGRESS.md`; a merged PR's line is cleared immediately as part of resuming, not left for a later session to notice.

**Why:** PR #18 merged on 2026-09-15. `PROGRESS.md` kept calling it open for 5 days across an unknown number of sessions, because `init.sh` is plain bash with no GitHub access — it can only echo the file, never catch that it's now wrong — and nothing else ever re-checked. Writing a better sentence into the file at Ship time does not fix this: the file is committed once and then sits untouched by definition until a PR actually merges, so whatever it says about that PR's status is guaranteed to go stale the moment the merge happens. Only a check at the next read can catch that.

**Rejected:** Wording the in-flight line more carefully (e.g. "open, awaiting merge"): does not solve the actual problem, since no wording self-updates when the PR merges. Automating a post-merge commit back to `main` to clear it: would need a bot writing to `main` outside the PR-gated flow this repo deliberately requires for every other change.

**Revisit when:** `init.sh` or an equivalent gains real GitHub access and can check PR state itself; then this becomes automatic instead of an agent instruction.

## 2026-09-15: Merge to main always goes through a PR, gated separately from sign-off

**Decision:** Ship no longer merges and pushes to `main` directly. It pushes the branch, opens a PR, and merges only when the client merges it themselves or explicitly tells the agent to (a squash-merge, confirmation-gated like `flyctl deploy`). A `PreToolUse` hook now refuses any direct push to `main` outright rather than only asking, and GitHub branch protection on `main` requires a PR before merge.

**Why:** The client's live sign-off answers whether the change is good; it does not separately answer who is allowed to move `main`. Folding both into one gate meant an agent could merge immediately after sign-off with no distinct go-ahead and no review surface. Splitting them gives every merge a PR to point back to, and a hard technical backstop (the hook, plus branch protection) instead of relying on the agent remembering the rule.

**Rejected:** Keeping direct local merge-and-push gated only by sign-off, as before: no PR, no audit trail, and the only thing stopping a stray direct push was a confirmation prompt rather than a refusal.

**Revisit when:** Not expected to.

## 2026-09-15: Chat is not the durable record for a not-small change

**Decision:** For a not-small change, `deep-plan.md`'s confirmed slice list is written into `PROGRESS.md`'s In flight section (under a `### Planned` heading) the moment it's confirmed, not deferred to Pause; each slice's status is kept current there too. `AGENTS.md` non-negotiable 2 is reworded to state this directly rather than naming chat as the plan. A small change's Shape stays chat-only.

**Why:** The client rejected the premise behind the old wording ("the chat is the plan"): a session is not guaranteed to persist, so treating chat as the record of what was decided is a bet against session loss. That risk is worst for a not-small, multi-slice change: the one most likely to span sessions and costliest to reconstruct if the plan is lost. A small change is the opposite, cheap to re-Shape from scratch, so the client separately flagged that a mandatory `PROGRESS.md` write on every Shape would tax the common case for a benefit that rarely applies there.

**Rejected:** Writing every Shape, small changes included, to `PROGRESS.md`: considered first, but the token cost of a write on every single change was judged not worth a benefit that mostly matters for not-small changes. Leaving the old wording as-is: it would keep asserting chat as durable after the client explicitly said not to rely on that.

**Revisit when:** Not expected to.

## 2026-09-11: Archive the harness template-alignment plan at a tag

**Decision:** Tag the commit that added `PLAN.md` (a plan to rewrite this repo's harness artifacts against the templates in `walkinglabs/learn-harness-engineering`) as `archive/harness-template-plan-2026-09`, rather than moving the plan into a `docs/history/`-style folder. The plan itself stays in the working tree, unimplemented pending the client's answers to its open questions, and is deleted per its own commit sequence once the change it describes ships.

**Why:** The reasoning behind several current harness artifacts only makes sense next to the template set that prompted this review; a durable pointer to that comparison is worth keeping without keeping the plan doc live once the change ships. A tag costs nothing to maintain and does not get read, or drift, day to day.

**Rejected:** A `docs/history/`-style folder to hold the plan long-term: retired for exactly this purpose on 2026-09-10, on the record that it sat unconsulted and invited "update history to match code." Recreating it for one plan file would undo that decision without a new reason.

**Revisit when:** Not expected to.

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
