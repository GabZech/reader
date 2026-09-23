# Decisions

Choices that are expensive to undo, newest first. Written by Ship when a change produces one; the threshold is a choice a future session might plausibly reverse. Not a changelog: routine changes live in git log and the roadmap's ticked lines.

Each entry: date, title and PR (when one exists), then **Decision**, **Why** (one sentence), **Rejected**, **Revisit when**. The full reasoning and evidence live in the linked PR.

## 2026-09-23: Decision entries are slim, with the full story in the PR

**Decision:** Each entry keeps its Decision, a one-sentence Why, Rejected, and Revisit when, and links the PR that made the choice. Every existing entry was rewritten to this shape once, as a deliberate exception to append-only.

**Why:** PR descriptions already carry the long reasoning, so repeating it here doubled the reading without adding anything the PR lacks.

**Rejected:** Dropping this file for PR descriptions alone: a PR records a change, not the alternatives ruled out or what would reopen a choice, and a superseded PR never points forward. Slimming only new entries: leaves the file half in each shape.

**Revisit when:** A choice needs its reasoning readable without GitHub, e.g. if the repo moves off it.

## 2026-09-23: The vault export fallback runs daily at 5am Brasilia time, with no settle time (#47)

**Decision:** The background export no longer waits for highlights to go untouched for a day, checked every 24 hours from whenever the app started. It runs once a day at 5:00 Brasilia time (UTC−3) and exports every article whose highlights changed since its last export; on startup it exports only what a missed 5am run would have sent. Archive, mark as read, and delete still export immediately, as before.

**Why:** The old timing could leave an edited note stale for up to about 48 hours at unpredictable times, and a fixed early-morning run caps that to about a day in one predictable batch, while keeping the old settle time's purpose of never exporting mid-session.

**Rejected:** A 12-hour settle time with hourly checks (about 13 hours at most): the client preferred one predictable daily run. A real time-zone database lookup: Brasilia has had no daylight saving since 2019, so a fixed offset is exact and avoids a dependency.

**Revisit when:** Brazil reintroduces daylight saving, or the client moves to a time zone that has it.

## 2026-09-23: The live host may stay on a signed-off branch until its PR merges (#45)

**Decision:** Once the client has signed a change off live and its PR is open, the live host stays on that branch when the turn ends; the merge deploys `main`, and `main` is redeployed by hand only if the PR closes unmerged. In every other case (not signed off, paused, scrapped) the host still ends a turn on `main`.

**Why:** Redeploying `main` over a signed-off branch took away the feature the client had just approved until they merged, and spent a deploy to show an older app.

**Rejected:** The strict "always end on `main`" rule: correct only while a branch is unapproved, and it made the gap between sign-off and merge a regression on the live app.

**Revisit when:** A PR can sit open long enough for `main` to move on underneath it, or separate dev and prod apps exist (see 2026-08-20).

## 2026-09-22: Capture keeps trafilatura, with lxml repair around it (#27)

**Decision:** `capture_article` keeps trafilatura as its extraction engine. `lxml` (now a direct dependency) rewrites an image-bearing `<table>` into `<div>`/`<p>` before extraction, working around a trafilatura defect that empties such tables, and afterwards restores any in-article image that did not survive.

**Why:** A direct A/B against Mozilla Readability on 20 real capture URLs found no clear winner, and the repair layer helps whichever engine sits underneath.

**Rejected:** Mozilla Readability: better on the one reported blog, worse on ordinary WordPress sites and empty on JS-shell or paywalled pages; it also adds a Node dependency and thinner metadata. Tuning trafilatura's `favor_recall`: no setting was a strict improvement across the 20 URLs.

**Revisit when:** The safety net is regularly doing the real work rather than trafilatura, or the extractor landscape changes enough to repeat the test.

## 2026-09-21: Squash-merge into `main` is enforced, not just convention (#25)

**Decision:** GitHub repo settings allow only squash-merge for PRs into `main`; merge-commit and rebase-merge are disabled.

**Why:** The client wants `main` to read as one commit per shipped change, and the earlier convention (2026-09-15) had no backstop against picking the wrong merge method.

**Rejected:** Leaving it as convention: relies on remembering the right method every time.

**Revisit when:** The client wants per-commit history preserved on `main`.

## 2026-09-20: Vault export filenames are date + title, not the item id (#23)

**Decision:** A highlight note is `Highlights/YY-MM-DD Article title.md` (published date, else added date, else today; title sanitized, falling back to the item id only if nothing is left). `items.exported_note_path` tracks the last path so a renamed export deletes the old file. Two same-day articles with the same title overwrite each other; this is accepted.

**Why:** The client wants filenames readable and sortable in the vault, and accepted giving up the id-based name's stability to get that.

**Rejected:** Appending an id or hash to guarantee uniqueness: breaks the exact pattern asked for.

**Revisit when:** A real collision happens, or the vault stops being one person's library.

## 2026-09-20: Vault export fires on archive/mark-as-read or a day later, not on every highlight action (#23)

**Decision:** Highlight edits only mark an article as touched. Archiving or marking as read exports once if anything changed; a daily check exports anything touched more than a day ago (timing superseded by the 2026-09-23 entry: daily at 5am Brasilia time, no settle time). Deleting an article never deletes its vault note: unexported highlights export first, then local rows go.

**Why:** Per-action export made one commit per click in `news-highlights`, and the client wants roughly one commit per article.

**Rejected:** Batching per-action exports within a short window: cuts commits per burst, not per reading session.

**Revisit when:** A different vault delivery mechanism replaces per-file GitHub commits.

## 2026-09-20: A PR just awaiting merge is never written into `PROGRESS.md` (#24)

**Decision:** `PROGRESS.md` never records that a PR is open or awaiting merge. A shipped change's in-flight entry is cleared outright in the commit before its PR opens.

**Why:** Any stored PR status goes stale the moment the PR merges, as PR #18 did for five days, while GitHub's PR list cannot.

**Rejected:** Checking a named PR's state before trusting it: still stores the PR as text and fails for any session that skips the check. More careful wording: no wording updates itself. A bot commit to clear it after merge: writes to `main` outside the PR-gated flow.

**Revisit when:** A PR carries real unresolved work beyond the merge click, such as reviewer feedback or a known blocker.

## 2026-09-15: Merge to main always goes through a PR, gated separately from sign-off (#18)

**Decision:** Ship pushes the branch and opens a PR instead of pushing to `main`; the client merges it or explicitly tells the agent to. A `PreToolUse` hook refuses direct pushes to `main`, and branch protection requires a PR.

**Why:** Sign-off says the change is good, not who may move `main`, so merging needs its own go-ahead, an audit trail, and a hard backstop.

**Rejected:** Direct merge gated only by sign-off: no PR, no audit trail, and only a confirmation prompt against a stray push.

**Revisit when:** Not expected to.

## 2026-09-15: Chat is not the durable record for a not-small change

**Decision:** For a not-small change, `deep-plan.md`'s confirmed slice list goes into `PROGRESS.md`'s In flight section (under `### Planned`) as soon as it is confirmed, with each slice's status kept current. A small change's Shape stays chat-only.

**Why:** A session is not guaranteed to persist, and losing the plan costs most on a multi-slice change that spans sessions.

**Rejected:** Writing every Shape to `PROGRESS.md`: a write on every change for a benefit that rarely applies to small ones. Keeping the old "the chat is the plan" wording: the client said not to rely on chat.

**Revisit when:** Not expected to.

## 2026-09-11: Archive the harness template-alignment plan at a tag

**Decision:** The commit that added `PLAN.md` (a plan to align this repo's harness with the templates in `walkinglabs/learn-harness-engineering`) is tagged `archive/harness-template-plan-2026-09`; the plan file itself is deleted once its change ships.

**Why:** Several harness artifacts only make sense next to that comparison, and a tag keeps it reachable at no upkeep cost.

**Rejected:** A `docs/history/`-style folder: retired on 2026-09-10 for exactly this purpose, with no new reason to bring it back.

**Revisit when:** Not expected to.

## 2026-09-10: Archive the discovery-phase skills at a tag instead of a template repo

**Decision:** The last commit with the retired discovery skills (Kickoff through Foundation, `create-phase-skill`, and their question banks) is tagged `archive/discovery-skills-2026-09`, rather than copied into `GabZech/template-spec-workflow`.

**Why:** A future template repo generated from `reader` can pull the skills from the tag without committing now to that repo's shape.

**Rejected:** Pushing them into the template repo now: premature before that task is asked for. Keeping them live here: 900 lines of dormant machinery was the original problem.

**Revisit when:** The client asks for a template repo generated from `reader`; the tag is then the source.

## 2026-09-10: Collapse `docs/history/` into this file

**Decision:** `docs/history/` is retired. The Obsidian export sample moved under `docs/vision/`, the mockup pointer folded into `docs/mockup/README.md`, and the rest is tagged `archive/history-2026-09` and deleted.

**Why:** Nobody consulted it day to day: its decisions folder sat empty for three weeks while real decisions landed elsewhere, and it invited "update history to match code."

**Rejected:** Keeping it alongside this file: two places to check for the same kind of fact.

**Revisit when:** Never, by design; the tag preserves the record.

## 2026-09-10: Sign-off gates merge, not commit

**Decision:** Commit checkpoints on the branch as soon as checks pass. Only the client's live sign-off gates the merge to `main`.

**Why:** "Do not commit before sign-off" could not be followed in a cloud session, which can only reach the live host through a pushed commit.

**Rejected:** Deploying from an uncommitted working tree: not a concept in a cloud session.

**Revisit when:** Not expected to.

## 2026-09-10: Deploy only on the client's explicit go-ahead

**Decision:** A screenshot or local walkthrough is never itself permission to deploy; deploy only after the client's reply says to.

**Why:** The gap between "here's what changed" and an actual "yes, deploy" let a premature push happen twice in one session.

**Rejected:** Trusting agent judgement on when a change is ready to go live.

**Revisit when:** Not expected to.

## 2026-09-09: CI deploys on push to `main`

**Decision:** A GitHub Actions job deploys after tests pass on a push to `main`, using a `FLY_API_TOKEN` repository secret. Trying a branch live uses the same job on manual dispatch.

**Why:** A cloud session's egress proxy cannot carry Fly's gRPC deploy handshake, and GitHub-hosted runners are not behind it.

**Rejected:** Running `flyctl deploy` from a cloud session: fails at the network layer, beyond this repo's reach.

**Revisit when:** Fly offers a deploy path over plain HTTPS, or the hosting choice is revisited.

## 2026-09-09: Migrate to `uv` for Python dependencies

**Decision:** `pyproject.toml` plus `uv.lock` replace `requirements.txt`; Dockerfile and CI install through `uv`.

**Why:** One tool gives a locked, reproducible install across local, CI, and production.

**Rejected:** Plain `pip` with an unpinned `requirements.txt`: no lockfile, so environments could silently drift.

**Revisit when:** Not expected to.

## 2026-08-28: The change loop replaces the epic-based workflow

**Decision:** Feature work runs the six-step change loop (`.claude/skills/2-develop/`) instead of per-epic plan and clarifying-answers files.

**Why:** The epic workflow's files drifted from what shipped, while the change loop verifies each change live.

**Rejected:** Keeping per-epic plan files as a parallel record: "no plan files" is deliberate.

**Revisit when:** Not expected to.

## 2026-08-24: Newsletter dedup by Message-ID; mark IMAP `\Seen`, never archive

**Decision:** A synced message's identity is its `Message-ID` header. After ingest the IMAP message is marked `\Seen` for tidiness only, never deleted or archived.

**Why:** The client asked for no archiving, and `Message-ID` dedup keeps ingest correct whatever the mailbox's read flags say.

**Rejected:** Using IMAP `UNSEEN` as the record of what is ingested: conflates tidiness with dedup and breaks if anything else touches the mailbox.

**Revisit when:** The mailbox needs cleanup for size or cost.

## 2026-08-20: One Fly app serves both trying and living

**Decision:** Trial deploys and real production traffic share one Fly app and host.

**Why:** A second always-on machine would roughly double hosting cost against a $10 ceiling with little headroom.

**Rejected:** A second Fly app now: does not fit the MVP budget.

**Revisit when:** The MVP ships and the cost ceiling is reopened; until then a change briefly runs live against the real library during Try, an accepted risk (see `docs/roadmap.md` Post-MVP Notes).
