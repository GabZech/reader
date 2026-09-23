# Decisions

Choices that are expensive to undo, newest first. Written by Ship when a change produces one; the threshold is a choice a future session might plausibly reverse. Not a changelog: routine changes live in git log and the roadmap's ticked lines.

Each entry: date and title, then **Decision**, **Why**, **Rejected**, **Revisit when**.

## 2026-09-23: The live host may stay on a signed-off branch until its PR merges

**Decision:** Once the client has signed a change off live and its PR is open, the live host stays on that branch when the turn ends. The merge deploys `main` automatically; `main` is redeployed by hand only if the PR closes without merging. The host still ends a turn on `main` in every other case: a change not yet signed off, a paused one, or a scrapped one.

**Why:** Redeploying `main` over a signed-off branch took away the feature the client had just approved, until they merged, and spent a deploy to show them an older app. The signed-off branch is what `main` is about to become, so leaving it live shows the client the right thing.

**Rejected:** Keeping the strict "always end on `main`" rule: correct only while a branch is unapproved, and it made the gap between sign-off and merge a regression on the live app.

**Revisit when:** A PR can sit open long enough for `main` to move on underneath it (another change merges first), since the live host would then be missing that change until this one merges; or once separate dev and prod apps exist (see 2026-08-20).

## 2026-09-22: Capture keeps trafilatura, with lxml doing pre/post-extraction repair around it, instead of swapping extraction engines

**Decision:** `capture_article` still uses trafilatura as its extraction engine. Around it, `lxml` (now a direct dependency) does two things: rewrites an image-bearing `<table>` into `<div>`/`<p>` before extraction (works around a confirmed trafilatura defect where mixing an image-only row with a text-only row empties the whole table), and afterwards checks every image in the article's own region against what survived, recovering any that didn't by embedding it directly from its original URL (grouped back into its original table row when it had one).

**Why:** A client-reported article (a personal static blog with hand-written `<table>`-based image layouts) lost every one of its 28 images under trafilatura. Directly ran Mozilla Readability (what most reader apps are built on) against the same 20 real capture URLs already used to validate this fix: no clear winner — it recovers far more of that one article's images, but loses badly on two ordinary WordPress sites trafilatura handles cleanly, and returns nothing at all on JS-shell/paywalled pages trafilatura at least degrades gracefully on. Matches trafilatura's own published benchmark lead over readability-lxml (0.912 vs 0.804 F-score) and public reports that Readwise itself has no single fix either, just ongoing per-site tuning. The safety-net pattern built here is engine-agnostic: it stays useful regardless of which extractor is underneath, or which of its bugs trips on a given site.

**Rejected:** Replacing trafilatura with Mozilla Readability (via a Node/jsdom dependency, or a Python port): rejected on direct A/B evidence across real sites, not benchmark trust alone, plus it would add a Node runtime dependency and lose trafilatura's richer metadata extraction (readability's author/date signals are much thinner). Tuning trafilatura's own flags (`favor_recall` vs balanced mode): tested across all 20 URLs, found no flag setting that was a strict improvement — trades one site's boilerplate for another's dropped images.

**Revisit when:** A future capture failure turns out to be systemic rather than per-site (i.e. the safety net itself is regularly doing the real work instead of trafilatura), or the extraction library landscape changes enough that a direct re-test is worth repeating.

## 2026-09-21: Squash-merge into `main` is enforced, not just convention

**Decision:** GitHub repo settings now allow only squash-merge for PRs into `main`; merge-commit and rebase-merge are disabled (`gh repo edit --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false`). Every PR collapses to one commit on `main`, regardless of how many checkpoint commits it carried on the branch.

**Why:** The client wants `main`'s history to read as one commit per shipped change, not a long trail of in-branch checkpoints. The 2026-09-15 entry on PR-gated merges already named squash-merge as the intended method, but only as a parenthetical; nothing stopped a merge-commit or rebase-merge from going through instead, whether from the GitHub UI or `gh pr merge` with a different flag.

**Rejected:** Leaving it as an unenforced convention: relies on remembering to pick the right merge method every time, with no backstop if someone (or an agent) picks wrong.

**Revisit when:** The client wants per-commit granularity preserved on `main` for some future need.

## 2026-09-20: Vault export filenames are date + title, not the item id

**Decision:** A highlight note's filename in `news-highlights` is `Highlights/YY-MM-DD Article title.md` (date from published date, falling back to when the article was added, then to today; title sanitized for filesystem-unsafe characters, falling back to the item id only if sanitizing leaves nothing). `items.exported_note_path` tracks the last-written path so a later export whose computed name differs deletes the old file first, instead of leaving a stale duplicate. Two articles with the same title on the same day silently overwrite each other's note; this is accepted, not guarded against.

**Why:** The client wants filenames readable and sortable in the vault itself, not opaque ids. The original id-based naming was chosen specifically for stability (the filename could never change), which this deliberately gives up: a title or date correction can now change the filename. Guarding the collision case would mean departing from the exact pattern asked for, for a personal single-user library where it should be rare.

**Rejected:** Appending a disambiguator (id or hash) to guarantee uniqueness: rejected because it breaks the exact pattern requested and the client accepted the collision risk explicitly.

**Revisit when:** A real collision actually happens, or the vault stops being a single person's personal library.

## 2026-09-20: Vault export fires on archive/mark-as-read or a day later, not on every highlight action

**Decision:** Saving a highlight, setting a title, or deleting a highlight no longer exports to the vault immediately; it just records that the article's highlights were touched. Archiving (Read later) or marking as read (every other list) exports once, only if something changed since the last export. A background check once a day exports anything touched more than a day ago and never caught up otherwise. Deleting an article never deletes its note from the vault: any still-unexported highlights export once as a final catch-up first, then local highlight rows are removed — the vault file is the durable copy, not the local database.

**Why:** The old design exported on every single highlight-related click, producing one commit per action in `news-highlights` (a session of highlighting could be seven commits for one article). The client wants roughly one commit per article. Archiving/marking as read is the natural "I'm done with this one" signal already in the app; the day-later fallback exists specifically for breaking off a reading session before reaching that signal.

**Rejected:** Keeping per-action export and only reducing frequency (e.g. batching within a short window): rejected because it does not address the client's actual goal of a article getting materially fewer commits across a whole reading session, only within a single burst of edits.

**Revisit when:** Not expected to, short of a different vault delivery mechanism replacing per-file GitHub commits entirely.

## 2026-09-20: A PR just awaiting merge is never written into `PROGRESS.md`

**Decision:** `PROGRESS.md` never records "PR #N open, awaiting merge" as text, not even briefly. `PROGRESS.md`'s in-flight entry for a shipped change is cleared outright in the same commit that precedes opening its PR (already 2-develop's Ship step, from an earlier fix); this decision closes the gap that let an agent satisfy "cleared" by writing a "PR open" note back in, which is exactly what happened. No corresponding check was added at session start: the client just checks GitHub, or asks, when a PR's status actually matters to them.

**Why:** PR #18 merged on 2026-09-15. `PROGRESS.md` kept calling it open for 5 days across an unknown number of sessions, because `init.sh` is plain bash with no GitHub access — it can only echo the file, never catch that it's now wrong — and nothing else ever re-checked. Any text stored about a PR's status is frozen the moment it's committed and is guaranteed to go stale the instant the PR merges after that, no matter how it's worded ("open", "awaiting merge", a PR number). The number is also not known until after the PR exists, so a "last commit before the PR" literally cannot name it. The only way this stops going stale is to never store it: GitHub's PR list is the record, and it can't lie, since a merged PR simply stops appearing in it.

**Rejected:** Checking whether a named PR has merged before trusting it (this decision's own first draft): still requires storing the PR's identity as text, and still leaves a session that skips the check exposed. Wording the in-flight line more carefully: no wording self-updates. Automating a post-merge commit back to `main` to clear it: would need a bot writing to `main` outside the PR-gated flow this repo deliberately requires for every other change.

**Revisit when:** A PR develops real unresolved work beyond waiting on the merge click (reviewer feedback, a known blocker) — that's worth a `PROGRESS.md` line again, since GitHub's PR list won't hand over that context for free.

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
