# Harness improvement plan

Written 2026-09-10. Compares this repo's agent harness against [Harness Engineering: Quick Actionable Guide](https://dev.to/truongpx396/harness-engineering-quick-actionable-guide-2b93) and proposes concrete changes. Repo maintenance, not product work: the change loop does not apply, but every skill edit follows `write-skills` and every commit follows the commits rule. Delete this file once the plan is executed.

## Your four ideas, in short

| Idea | Verdict |
| --- | --- |
| Collapse `docs/history/` into one `decisions.md` | **Yes, with two rescues.** The decisions folder has never been used and the raw logs are mostly superseded. One file in history is actually a live spec, and the mockup pointer has to survive (see 4.1, 4.2) |
| `init.sh` | **Yes, adapted.** It should report git and live-host state too, not only install and test, because the loop's own rules depend on that state (2.5) |
| `AGENTS.md` | **Yes, as the canonical vendor-neutral manual.** `CLAUDE.md` becomes a thin adapter. The bigger win is that the auto-loaded file finally carries the rules instead of routing to them (2.1) |
| `agents-progress.md` | **Yes, narrower than the article.** A snapshot of in-flight state, overwritten each time, not an appended session log. Git log is already the log (2.4) |

## 1. What the article argues (compressed)

- **Five subsystems.** Instructions, State, Verification, Scope, and Session lifecycle. Reliability comes from all five, not from better prompts
- **Minimal harness.** An operating manual (`AGENTS.md`), a health script (`init.sh`), a machine-readable feature list, and a progress file for session memory. `DECISIONS.md` and per-task "sprint contracts" come next
- **Instruction hygiene.** Keep the main file short (roughly 50 to 200 lines, at most about 15 hard rules), put critical rules at the top or bottom, route to topic docs, give each rule a why, and delete stale rules
- **Execution discipline.** One feature at a time, a start phase that checks the environment and reads state, and no "done" without verification evidence. Every session ends clean and resumable
- **Mechanical over instructional.** Checks that pass or fail beat rules the agent has to remember

The article's success-rate numbers (20% to 100%, and so on) are single-source claims. Treat them as motivation, not evidence.

## 2. Where this repo stands

| Subsystem | Already strong | Gaps |
| --- | --- | --- |
| Instructions | Short skills (2-develop is 63 non-blank lines), direct positive rules, and progressive disclosure via linked reference files | Nothing auto-loaded holds a rule: `CLAUDE.md` routes to `.cursor/` files that must be read by hand. The setup is tied to one vendor. One rule is said in five places. `writing-docs` runs to about 210 lines. Rules carry no why |
| State | The roadmap checklist is a real feature list, and only Ship can tick it | No record of an in-flight change. The roadmap Summary has grown into a changelog |
| Verification | TDD per change kind, 102 tests in 22s, and a human live sign-off as the evaluator (stronger than anything the article proposes) | pytest only: no lint. pytest ships in the production image. Nothing catches stale paths in docs or skills |
| Scope | WIP=1 is explicit, Frame and Shape act as a sprint contract, and deep-plan slices work | "Several can stack up before one deploy", with nothing committed, reopens WIP>1. Shape never says what it will leave alone |
| Lifecycle | Ship is thorough: doc check, merge, redeploy, `/clear` | No start check (health, git state, what's live). No pause protocol. "Live is back on main" can't be verified |

## 3. Findings (evidence)

1. **The commit rules contradict each other and can't be followed in cloud sessions.** [commits.mdc:10](.cursor/rules/commits.mdc#L10) says to commit each logical change as soon as it's done. [2-develop:84](.cursor/skills/2-develop/SKILL.md#L84) forbids committing before live sign-off and says to deploy from the working tree. Commit `782d2b2` records that cloud sessions can't reach Fly's builder, so the only deploy path there is a git push, which needs a commit.
2. **The deploy gate is only an instruction, and it failed twice in one session** (commit `568bf71`). Meanwhile `.claude/settings.local.json` pre-approves `flyctl deploy *`, and [test.yml:20-23](.github/workflows/test.yml#L20-L23) deploys on a push to any branch. Pushing a branch to back it up therefore deploys it onto the real library.
3. **Two deploy paths are described inconsistently.** The Try step "pushes the branch to the live host per operations.md". [operations.md:15](docs/operations.md#L15) still credits "Build's trial pushes", a phase that no longer exists.
4. **Living docs have drifted.**
   - [operations.md:50](docs/operations.md#L50) says the app doesn't read the mail credentials. It has since increment 8.
   - [development.md:56](docs/development.md#L56) and [architecture.md:19,39,48](docs/architecture.md#L19) still describe mail as "later". The Skeleton to-do list includes features that are already built.
   - [development.md:47](docs/development.md#L47) says CI "should" run the tests. It already does.
   - [docs/README.md:16](docs/README.md#L16) still names the "first piece of the MVP".
   - [roadmap.md:56](docs/roadmap.md#L56) says "once resume lands", but resume has shipped.
   - [README.md:19](README.md#L19) writes "`Docs/`".

   Ship only checks docs the *current* change made wrong, so drift left by earlier changes persists.
5. **Decision records are never written.** `docs/history/decisions/` is still an empty `.gitkeep` after three weeks. In that time several hard-to-undo choices landed: the uv migration (`a9777d3`), CI deploys (`782d2b2`), many-to-many list membership (`783f81b`), and two process rules. `docs/history/plans/` is an empty orphan that the history README doesn't list.
6. **A living spec is filed as history.** [export-example-obsidian.md](docs/history/discovery/02-understand/export-example-obsidian.md) is linked from [constraints.md:11](docs/vision/constraints.md#L11) and [journeys.md:85](docs/vision/journeys.md#L85) as the settled vault format for the unbuilt Highlight epic.
7. **The roadmap Summary is a changelog.** It has 8 bullets ([roadmap.md:9-16](docs/roadmap.md#L9-L16)) where `writing-docs` allows 2 to 4, because every Ship appends one.
8. **The entry point is a chain of "go read X".** `CLAUDE.md` holds only routing, and its `@` imports don't appear to expand in this setup (hence the "read via the Read tool" workaround). Skills in `.cursor/` never trigger in Claude Code without manual routing.
9. **One rule is duplicated.** "Where truth lives / don't rewrite history" appears in `engagement.mdc:31`, `docs/README.md:5`, `history/README.md:3`, `writing-docs` (twice), and `create-phase-skill`.
10. **Discovery machinery sits dormant.** The 1-1 to 1-5 skills, their question banks, `create-phase-skill`, and the discovery doc shapes in `writing-docs` come to about 900 lines. [1-5-foundation Gate](.cursor/skills/1-5-foundation/SKILL.md#L85) still routes to a "Plan" phase that no longer exists. The upstream template repo looks like an older shape (`product-definition/`, `specs/`), so these evolved versions may exist only here.
11. **Agent memory has gone stale.** Two Claude memories cite `.cursor/skills/2-2-build/SKILL.md` and "Plan/Build phases", both gone. Both rules are now codified in the repo. The VS Code timer quirk is a repo fact that lives only in one vendor's memory.
12. **The live version can't be observed.** [/health](app/main.py#L1179) returns only `{"ok": true}`, so neither agent nor client can check which commit is live.

## 4. Recommendations

Four phases, ordered by value and risk. Each phase is its own branch.

### Phase 1: Make the rules true and consistent

Small edits that fix what is already wrong. Findings 1 to 4 and 11.

**1.1 One commit and deploy story.** Edit `2-develop/SKILL.md`, `docs/operations.md`, and the commits rule so they say the same thing:

- **Sign-off gates merge, not commit.** Commit on the branch at every checkpoint (tests green, plus the local screenshot or change description shown). Keep `--no-ff` merges to main as today. Drop "Do not commit before sign-off" and "deploying straight from the working tree"
- **Deploying is one explicit act, done only on the client's go-ahead.** Locally that's `flyctl deploy` from the committed branch. In the cloud it's the manual CI trigger (1.2)
- **The Try step names both paths once**, pointing at `operations.md` for the commands. Remove the reference to "Build's trial pushes"

**1.2 Enforce the deploy gate mechanically.** Two changes:

- **CI deploys automatically only from `main`.** A branch trial deploy goes through `workflow_dispatch` (`gh workflow run test.yml --ref <branch>`). Pushing a branch becomes a safe backup
- **A committed `.claude/settings.json`** with `ask` rules for `Bash(git push *)`, `Bash(flyctl deploy *)`, and `Bash(gh workflow run *)`. The client's permission prompt becomes the deploy gate, and it applies in cloud sessions too because the file is committed. Remove `flyctl deploy` from the local allow list

**1.3 A doc-truth pass** over every item in finding 4, one commit per doc. Also correct `README.md`'s "`Docs/`".

**1.4 Memory hygiene.**

- **Delete** the two feedback memories now codified in the repo (client-facing tone, walkthrough before sign-off)
- **Move** the VS Code timer quirk into `docs/development.md` as one sentence, then delete that memory
- **Keep** the AskUserQuestion formatting memory: it's about tool behaviour, not the repo

### Phase 2: Vendor-neutral entry and session lifecycle

Findings 7 to 9, plus the missing start and pause protocol.

**2.1 `AGENTS.md` at the root, around 100 lines, as the canonical manual.** It replaces `engagement.mdc`, `chats.mdc`, and the routing in `CLAUDE.md`. Critical material goes at the top and bottom, per the article:

1. **Start of session** (top): run `./init.sh`, read `PROGRESS.md`, and resume anything in flight before starting new work
2. **Which kind of task:** product change or repo maintenance
3. **Routing table:** task → skill path. For example: product change → `2-develop`, asking the client → `questioning`, editing living docs → `writing-docs`, editing skills → `write-skills`, committing → `commits`. This table is the vendor-neutral trigger mechanism: any tool that reads `AGENTS.md` works, wherever the skills live
4. **Non-negotiables:** at most 15, each with a short why. Longer rationale links to `docs/decisions.md`
5. **Where truth lives:** stated once, here only (fixes finding 9)
6. **Commands:** init, test, lint, run, each a pointer to `docs/development.md`
7. **Chat conduct:** the two rules from `chats.mdc`
8. **End of session** (bottom): the clean-state checklist from 2.6

**2.2 `CLAUDE.md` becomes an adapter:** `@AGENTS.md` plus one fallback line ("read `AGENTS.md` in full before any task"). Keep the fallback until a fresh session confirms the import expands (check with `/memory`).

**2.3 Move skills to `.claude/skills/`** with `git mv`, so Claude Code discovers them natively (auto-triggering plus `/2-develop` as a slash command). The `SKILL.md` format is the open Agent Skills standard, so switching vendor means moving one folder and updating the routing-table paths. Also:

- **Turn `commits.mdc` into a `commits` skill** ("Use when creating a git commit")
- **Delete `.cursor/rules/` and `.cursor/skills/`**
- **Keep the `.cursor/` lines in `.gitignore`.** They're harmless and useful if you go back

**2.4 `PROGRESS.md` at the root: a snapshot, at most 30 lines, overwritten not appended.** Fields:

- **Live now:** what's deployed (from `/health`, see 3.3)
- **In flight:** the change, its kinds, its branch, what Shape agreed (including what it will leave alone), feedback rounds so far, and the next step
- **Stacked awaiting deploy:** changes committed on the branch but not yet tried live
- **Blocked:** anything waiting on the client or an outside system

Update it with every checkpoint commit and clear it at Ship. It's committed, so it survives `/clear`, compaction, and cloud-sandbox teardown. That covers the case where branches diverged after a context clear (see the manage-sources clarifying-answers). It isn't a plan document: "no plan files" still holds for anything the client reviews.

**2.5 `init.sh` at the root, in bash.** Bash runs in Git Bash on Windows, in Linux cloud sandboxes, and on macOS. The script:

1. Runs `uv sync --locked`, then `uv run ruff check`, then `uv run pytest -q`, and exits non-zero if the baseline is red ("it was red before I touched it" must be said, not silently fixed)
2. Prints git state: branch, dirty files, unpushed commits, and any other local branch (an unfinished change)
3. Prints the live version from `/health` next to `origin/main`
4. Prints the in-flight section of `PROGRESS.md`

A `--quick` flag skips step 1 for hooks.

**2.6 Lifecycle steps in 2-develop.**

- **Start** (before Frame): the `AGENTS.md` start protocol
- **Pause** (new, for leaving mid-change): commit on the branch, update `PROGRESS.md`, and say what's live
- **Ship** gains the rest of the clean-state checklist: clear `PROGRESS.md`, empty `preview/`, free port 8000, and confirm live equals main with `init.sh --quick`

**2.7 A SessionStart hook** in `.claude/settings.json` that runs `bash init.sh --quick`, so state arrives in context without the agent having to remember. Other tools fall back to the start protocol in `AGENTS.md`.

**2.8 Trim the roadmap Summary** back to 2 to 4 bullets describing state. In the 2-develop Artifacts line: Ship updates the Summary only when the product's overall state changes, never one bullet per change. Git log and the ticks already carry that history.

**2.9 Add "and what it will leave alone" to Shape.** This is the article's sprint-contract exclusions, as a single phrase.

### Phase 3: Verification and observability

Findings 4 and 12, plus pipeline depth.

**3.1 Lint and dev dependencies.**

- **In `pyproject.toml`,** move pytest into `[dependency-groups] dev` and add ruff there
- **In the `Dockerfile`,** add `--no-dev` to `uv sync` so test tooling leaves the image
- **CI** runs `uv run ruff check` before pytest

Start with ruff's default rules and fix findings in one `fix lint:` commit. Defer `ruff format` (it would rewrite every file) and type checking (about 2,800 mostly unannotated lines; revisit if type bugs show up).

**3.2 A harness reference test.** `tests/test_harness_refs.py` asserts that relative markdown links and backticked repo paths in `AGENTS.md`, the skills, and `docs/` all resolve, with an allowlist for gitignored paths such as `preview/`. It would have caught `2-2-build` and `conventions.md`, and it runs in CI with the rest of the suite. This is the mechanical answer to finding 4's kind of drift. It checks references, not facts, so the Ship doc check remains.

**3.3 `/health` returns the build version.**

- **`Dockerfile`** gets `ARG GIT_SHA`, exposed as an environment variable
- **CI** passes `--build-arg GIT_SHA=$GITHUB_SHA`; a local deploy passes `git rev-parse --short HEAD`

`init.sh` compares the result against `origin/main`. That turns "don't leave live on a branch" into something checkable.

**3.4 Optional: an independent review for not-small changes** before Try (`/code-review` in Claude Code, or any reviewer agent elsewhere). This is the article's split between execution and verification. The client's live sign-off stays the only gate.

### Phase 4: Simplify the records

Findings 5, 6, and 10.

**4.1 `docs/decisions.md`: living and append-only, newest first.** Each entry has a date and title, then Decision, Why, Rejected, and Revisit-when. Backfill only choices no living doc records yet:

- The change loop replacing the epic workflow
- The uv migration
- CI deploys, and why (cloud sandboxes can't reach Fly's builder)
- Deploy only on the client's say-so (two premature pushes)
- Sign-off gates merge, not commit (from 1.1)
- One Fly app for both trying and living (a cost choice, revisit after MVP)
- Newsletter handling: Message-ID dedup, and `\Seen` rather than archive
- History collapsed into this file

In 2-develop, replace the `history/decisions/` artifact with this file. The threshold drops to "a choice a future session might plausibly reverse".

**4.2 Collapse `docs/history/`.**

1. Tag the last commit that contains it (`archive/history-2026-09`) and push the tag
2. Move `export-example-obsidian.md` to `docs/vision/obsidian-export-example.md` and fix its two links
3. Fold the mockup pointer (how to open it, paths walkable, what we learned) into [docs/mockup/README.md](docs/mockup/README.md). Keep the dummy itself: it's still the look spec for the unbuilt Highlight screens
4. Delete the rest. Point the roadmap's Concluded links at the living docs, plus one line naming the tag
5. Remove every "don't rewrite history" rule (finding 9), since nothing is left to protect

**4.3 Split `writing-docs`** to under about 100 lines. Keep voice, lists, the roadmap shape, and the system-doc shapes. Drop the discovery-era shapes (README-when, epics, mockup) together with 4.4.

**4.4 Retire the discovery skills** (1-1 to 1-5, the banks, `create-phase-skill`). First copy these versions to `GabZech/template-spec-workflow`, since upstream looks older. Then delete them here and drop the greenfield branch from `AGENTS.md`. Skip this item if you want to keep evolving the template from inside this repo.

## 5. Deliberately not adopting

- **`feature_list.json`.** The roadmap's What's Next already is the list of (behaviour, state) pairs. It's client-facing, and only Ship can tick it. A second list would drift from it
- **An appended session log.** A snapshot plus git log carries the same information without rotting, which is exactly what happened to the roadmap Summary
- **Sprint-contract files and evaluator rubrics.** The Shape message and deep-plan confirm are the contract, and the client's live sign-off is a stronger evaluator than a rubric. "No plan files" is a deliberate choice that works
- **Pre-commit hooks that run the suite.** 22 seconds on every commit adds friction. CI and `init.sh` cover it
- **Type checking now.** Deferred (see 3.1)

## 6. Target layout

```text
AGENTS.md                 canonical manual, vendor-neutral
CLAUDE.md                 adapter: @AGENTS.md
PROGRESS.md               in-flight snapshot
init.sh                   health + git + live state
.claude/settings.json     adapter: ask-gates on push/deploy, SessionStart hook
.claude/skills/           2-develop (+ change-kinds, deep-plan, preview), questioning,
                          writing-docs, write-skills, commits
docs/decisions.md         decision log (replaces docs/history/)
docs/vision/obsidian-export-example.md
docs/mockup/              accepted dummy + README pointer
docs/…                    other living docs unchanged
```

## 7. Sequencing and verification

| Phase | Done when |
| --- | --- |
| 1 | A grep for the finding-4 phrases returns nothing. On a throwaway branch: a branch push doesn't deploy, a manual dispatch does, a merge to main does, and `git push` raises a permission prompt |
| 2 | In a fresh session, `/memory` shows `AGENTS.md` loaded and skills show up natively. `init.sh` runs green in Git Bash and in a cloud session. A dry-run pause, then `/clear`, then a new session resumes from `PROGRESS.md` |
| 3 | CI is green with ruff. The built image has no pytest. `/health` shows the SHA after a deploy. The reference test fails when a bad path is introduced |
| 4 | The reference test is green after the moves. The tag exists on origin. No link points into `docs/history/` |

## 8. Verify before relying

- **`CLAUDE.md` `@` imports.** They don't appear to expand here today, so keep the fallback line until they do
- **`ask` rules in cloud sessions,** and under whatever permission mode you normally run
- **`gh` authentication in cloud sessions** for `workflow_dispatch`. If it's unavailable, trigger trial deploys on a push to a `try/*` branch instead
- **Where the next vendor looks for skills,** at the time you switch. The routing table in `AGENTS.md` works regardless
