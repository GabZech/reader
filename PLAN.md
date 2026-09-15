# Plan: align harness artifacts with the walkinglabs templates

**Status:** proposed, not started. Awaiting client approval.

**Scope:** repo maintenance. The change loop's gates (Preview, live sign-off, deploy) do not apply. Incremental commits and the `AGENTS.md` routing table do.

## Why this file exists, and when it dies

`AGENTS.md` non-negotiable 2 currently reads "No plan files. The chat is the plan; a separate document drifts from what was actually decided." The client has rejected the premise in that second clause: a chat session is not guaranteed to persist, so treating it as the durable record of what was decided is a bet against session loss, not an architecture. This file's own shape argues for that position rather than against it:

- It is a committed working file, not chat-only. If this session had ended after the last commit, the plan would still exist; the equivalent chat-only plan would not.
- It is deleted in the final commit of the change it describes, once that change has actually landed in durable artifacts (code, `docs/roadmap.md`, `docs/decisions.md`), not before. Nothing survives past that point to drift, and nothing before that point depended on chat surviving to get there.

This reopens two things beyond this one file, tracked in section 13 rather than assumed silently: the wording of non-negotiable 2 itself, and the point in the change loop where a not-small change's confirmed plan currently lives only in chat until an agent chooses to write it down. A small change's Shape is deliberately left chat-only (13b), on a token-cost tradeoff the client raised.

## Source material

- Templates: `walkinglabs/learn-harness-engineering`, `docs/en/resources/templates/`, all nine files plus the `index.md` guide.
- Repo side: `AGENTS.md`, `CLAUDE.md`, `HARNESS.md`, `PROGRESS.md`, `init.sh`, `docs/roadmap.md`, `docs/decisions.md`, `docs/architecture.md`, `docs/development.md`, `tests/test_harness_refs.py`, `.claude/skills/2-develop/` (`SKILL.md`, `change-kinds.md`), `.claude/skills/writing-docs/SKILL.md`, `.claude/skills/commits/SKILL.md`.

## Governing split (agreed with the client)

Broad reading for artifacts genuinely absent here: adopt the template's name, location, and structure. Narrow reading where a working artifact already exists and a locked decision shaped it: keep our name and location, align internal structure only. Deviations are labelled and reasoned, never silent.

## Decision summary

| Template | Repo counterpart | Verdict |
| --- | --- | --- |
| `AGENTS.md` | `AGENTS.md` | Extend: adopt four missing sections, keep our structure |
| `CLAUDE.md` | `CLAUDE.md` | **Deviation:** do not adopt, keep the thin adapter |
| `init.sh` | `init.sh` | Extend: adopt three things, keep our reporting |
| `claude-progress.md` | `PROGRESS.md` | Partial: adopt the header block, **deviation** on the session log and the filename |
| `feature_list.json` | `docs/roadmap.md` | **Deviation:** do not add, adopt the two ideas underneath it |
| `session-handoff.md` | none | **Deviation:** do not add, fold its one unique part into `PROGRESS.md` |
| `clean-state-checklist.md` | prose in `AGENTS.md` + Ship | **Deviation:** adopt the format, not a separate file |
| `evaluator-rubric.md` | none | Adopt as a new root file, near-verbatim |
| `quality-document.md` | none | Adopt as a new root file, re-domained for this project |

Net: four files rewritten, two added, one deleted at the end (this one), three templates deliberately not adopted, one adopted as structure rather than a file. Section 13 covers a related but separate finding, outside the nine templates: how this repo records a decision between chat and commit.

---

## 1. `AGENTS.md`

**Template shape:** Startup Workflow (6 numbered steps), Working Rules (5 bullets), Required Artifacts (4 bullets), Definition Of Done (4 bullets), End Of Session (5 numbered steps).

**What we have:** Start of session (3 steps), Which kind of task, Routing table, 15 non-negotiables, Where truth lives, Commands, Chat conduct, End of session (5 bullets).

Ours is richer and project-shaped. Four template elements are genuinely missing.

### 1a. Add a "Required artifacts" section

Nothing currently tells a fresh agent which files are the system of record. The routing table lists skills, not state. Place it directly after "Start of session," before "Which kind of task."

Content, as labelled bullets:

- `PROGRESS.md`: in-flight state and the standard paths. Read at start, updated at every checkpoint, cleared at Ship.
- `docs/roadmap.md`: the feature list. "What's next" is what remains; a line is ticked only by the change that shipped it.
- `docs/decisions.md`: choices expensive to undo, including one dated entry for any plan file archived at a tag once its change ships (client-confirmed convention, 2026-09-11; see that entry, not this file, once `PLAN.md` itself is gone).
- `init.sh`: the standard startup and verification path.
- `HARNESS.md`: how the harness itself is put together. Revisited after any change to how agents work here.
- `evaluator-rubric.md` and `quality-document.md`: post-change review and codebase health (new, see sections 8 and 9).

### 1b. Add a "Definition of done" section

We define "verified" per change kind in `change-kinds.md` and scatter sign-off rules through the non-negotiables, but no single place says when a change is finished. Place it immediately before "End of session."

A change is done only when all of these hold:

1. The behaviour is implemented and matches what Shape said it would be.
2. The verification for every kind the change carries actually ran, per the change-kinds table in `.claude/skills/2-develop/SKILL.md`.
3. Whichever living docs the change made wrong are updated on the branch, before the merge.
4. The client tried it live and said it is good. Nothing else substitutes for this, including a green suite or a passing rubric score.
5. The repo restarts clean from `bash init.sh` and the live host is back on `main`.

**Deviation from the template:** the template's definition of done lets the agent self-certify ("evidence is recorded in `feature_list.json` or `claude-progress.md`"). Point 4 makes the client's live sign-off non-substitutable, which is the actual gate in this repo per `2-develop`'s Gate section and `docs/decisions.md` 2026-09-10.

### 1c. Fold two missing rules into the existing non-negotiables

The list is capped at "at most 15" by `HARNESS.md` and currently sits at exactly 15. Do not grow it. Fold instead:

- **Into rule 7** (never skip, disable, or weaken a test): add "and never start new work on a red baseline: say it was already red rather than silently fixing or working around it." This rule currently lives only inside `init.sh`'s failure messages, which a tool that does not run the script never sees.
- **Into rule 6** (a behaviour or bug change needs a failing test first): add "and the verification bar does not move mid-change: if what counts as proof turns out to be wrong, say so and re-Shape." The template's "do not silently change verification rules during implementation" has no equivalent anywhere in this repo.

### 1d. Add `git log --oneline -5` to "Start of session"

`init.sh` prints unpushed commits but never recent history, so an agent starts blind to what just shipped. Cheapest fix is in `init.sh` itself (see section 3), with `AGENTS.md` step 1 unchanged in wording since it already delegates to the script.

### 1e. Convert "End of session" to a checklist

See section 7.

**Deviations kept:** our routing table, the "Which kind of task" split, the non-negotiables with their short whys, "Where truth lives," and "Chat conduct" have no template equivalent and stay. The template assumes one agent working one priority queue; this repo routes by task type and that is load-bearing.

---

## 2. `CLAUDE.md`

**Template shape:** a complete standalone restatement of the whole manual, reworded for Claude: Operating Loop, Rules, Required Files, Completion Gate, Before You Stop.

**What we have:** a four-line adapter, `@AGENTS.md` plus a fallback instruction for environments where the import does not expand.

### Plan: no change

**Deviation, and the clearest case where the template is worse for us.** Reasons:

- Two files stating the same rules in different words will disagree within weeks. The template has no mechanism to keep them in sync, and neither do we: `tests/test_harness_refs.py` checks that links resolve, not that two prose manuals still agree.
- `HARNESS.md` records the adapter as a deliberate design ("one canonical file any tool can read; `CLAUDE.md` is a thin adapter"). Adopting the template reverses that without a reason that applies here.
- The fallback line still earns its place: `HARNESS.md` records that the `@` import was observed not to expand in a fresh session in this environment.

If the client wants the template's shape anyway, the honest version is to generate `CLAUDE.md` from `AGENTS.md` rather than maintain both by hand. Not proposed now.

---

## 3. `init.sh`

**Template shape:** `set -euo pipefail`, `INSTALL_CMD` / `VERIFY_CMD` / `START_CMD` arrays at the top, prints the working directory, installs, verifies, prints the start command, and `exec`s it when `RUN_START_COMMAND=1`.

**What we have:** a `--quick` flag for the SessionStart hook, install/lint/test with a tailored failure message each, git state, live SHA against `origin/main`, and the `PROGRESS.md` in-flight section. Strictly richer on state reporting, missing the template's run story.

### 3a. Declare the commands as named arrays at the top

Currently `uv sync --locked`, `uv run ruff check`, and `uv run pytest -q` are buried inline across three `if` blocks. Lift them to the top as `INSTALL_CMD`, `LINT_CMD`, `VERIFY_CMD`, `START_CMD`, so the script is editable at a glance and matches the template's legibility intent.

`START_CMD` value: `uv run uvicorn app.main:app --port 8000`.

**Note on that value:** `docs/development.md` documents the run command with `--reload --reload-dir app`, then spends a paragraph explaining that `--reload` is unreliable on Windows in this repo and that running without it is preferred. The script takes the reliable form. Flag this in the commit message so the discrepancy with the doc is deliberate and visible.

### 3b. Print the working directory

One line, before the first section. Satisfies the template's `pwd` step, which `AGENTS.md` otherwise never covers.

### 3c. Print the start command, and run it under `RUN_START_COMMAND=1`

Today an agent that wants to run the app has to go read `docs/development.md`. Adopt the template's block verbatim in behaviour: print the command, and `exec` it when the environment variable is set. Place it last, after the `PROGRESS.md` section, so `--quick` output still ends on in-flight state.

Guard: skip the launch under `--quick`, since the SessionStart hook must return rather than block on a server.

### 3d. Print recent history

Add `git log --oneline -5` to the git state section (section 1d's real implementation).

### Deviations

- **Keep `set -uo pipefail`, not the template's `set -euo pipefail`.** Ours deliberately omits `-e`: each command's exit status is checked so the script can print a tailored message telling the agent what to say to the client ("say it was already red; do not silently fix a baseline you did not touch"). Under `-e` the script aborts before that message prints, which is a real loss of instruction.
- **Keep `--quick`, the git state block, the live-vs-`origin/main` block, and the `PROGRESS.md` block.** None have template equivalents. The live comparison in particular is what makes non-negotiable 11 checkable rather than assumed.

### Verification for this file

Run `bash init.sh --quick` and `bash init.sh` both, and `RUN_START_COMMAND=1 bash init.sh` far enough to confirm it binds port 8000, then stop it and free the port per `docs/development.md`.

---

## 4. `PROGRESS.md`

**Template shape (`claude-progress.md`):** a "Current Verified State" block (repository root, standard startup path, standard verification path, highest-priority unfinished feature, current blocker) plus an appended "Session Log" with one numbered entry per session.

**What we have:** an overwritten snapshot: Live now, In flight, Stacked awaiting deploy, Blocked.

### 4a. Adopt "Current verified state"

The real gap. Our file never states the standard startup path, the standard verification path, or what to work on next, so an agent has to open `AGENTS.md` and `docs/development.md` to orient. Add as the first section, above "Live now":

- **Repository root:** `/home/user/reader` (or wherever checked out)
- **Standard startup path:** `bash init.sh`
- **Standard verification path:** `uv run ruff check` then `uv run pytest`
- **Focused debug command:** `uv run pytest tests/test_app.py -k <name>`
- **Run the app:** `RUN_START_COMMAND=1 bash init.sh`, or see `docs/development.md`
- **Highest-priority unfinished item:** the next line the client picks from `docs/roadmap.md` "What's next". Epics do not impose an order; this names what was actually chosen, or "none chosen yet".
- **Current blocker:** none, or what.

The "Focused debug command" and "Run the app" lines are the `session-handoff.md` Commands block folded in (see section 6).

**Deviation on the "highest-priority" wording:** the template assumes a strict priority queue. `docs/roadmap.md` says the opposite in as many words: "An epic names a capability, not a work order: pick from any group, in any order." The field is kept because orientation is useful, but reworded to record the client's choice rather than to imply a computed priority.

### 4b. Keep the existing four sections

Live now, In flight, Stacked awaiting deploy, Blocked. All four are referenced by `2-develop`'s Pause step and by `init.sh`'s `awk` extraction.

### 4c. Do not add a session log

**Deviation.** The template appends a numbered entry per session. Ours is overwritten by design, on grounds stated in the file itself and in `HARNESS.md`: git log is already the session log, and `docs/decisions.md` already holds the durable choices. A third overlapping record of what happened would rot faster than either, and `docs/decisions.md` 2026-09-10 records exactly that failure mode for `docs/history/`, which sat unconsulted for three weeks.

### 4d. Keep the filename

**Deviation.** Renaming to `claude-progress.md` would break `init.sh` (two references), the SessionStart hook path in `.claude/settings.json`, `AGENTS.md`, `HARNESS.md`, `2-develop/SKILL.md` (two references), and any reader of the current file, in exchange for matching a name the template's own header calls "a historical course convention, not a Claude Code requirement." Explicitly agreed with the client under the governing split.

### Constraint to respect

`init.sh` extracts the in-flight section with `awk '/^## In flight/{flag=1; next} /^## /{flag=0} flag'`. The new section is added **above** In flight and must not itself be named with a heading that changes that match. Re-run `bash init.sh --quick` after the edit and confirm the in-flight print is unchanged.

---

## 5. `feature_list.json` and `docs/roadmap.md`

**Template shape:** JSON. Per feature: `id`, `priority` (integer, lower is higher), `area`, `title`, `user_visible_behavior`, `status` (`not_started` / `in_progress` / `blocked` / `passing`), `verification` (array of steps), `evidence` (array), `notes`. Plus `rules.single_active_feature` and a status legend.

**What we have:** markdown checkboxes in `docs/roadmap.md`, grouped by epic, with an explicit statement that order is the client's to choose.

### Plan: do not add the JSON file

**Deviation, and the one I feel strongest about.** Three reasons:

1. **It encodes an ordering this project rejected.** The template is built on a strict priority queue: an integer per feature, and a startup step that says "choose the highest-priority unfinished feature." `docs/roadmap.md` states the opposite as a rule, not an accident: "An epic names a capability, not a work order: pick from any group, in any order." Adopting the JSON would either contradict that or fill `priority` with meaningless integers.
2. **It creates a second feature list.** Ship already ticks the roadmap. Nothing but discipline would keep JSON and markdown agreeing, and `tests/test_harness_refs.py` cannot check semantic agreement. This is the `docs/history/` failure again.
3. **Its completion model cannot express our gate.** `status: "passing"` means the agent ran verification and recorded evidence. In this repo the gate is the client trying it live. A feature marked `passing` that the client has not signed off would be false in the format's own terms, and the schema has no field for the gate that actually decides.

### What to adopt instead

**A status vocabulary on the roadmap.** Today a line is ticked or unticked, so a blocked or in-flight item is indistinguishable from one never started. Add two inline markers, used sparingly and only where true:

- `- [ ] (in flight)` for the line currently being worked, matching `PROGRESS.md`'s in-flight entry.
- `- [ ] (blocked: <one clause>)` where work cannot continue.

Rules: at most one `(in flight)` line at a time, enforced by non-negotiable 1. Both markers are cleared by Ship. Add a one-sentence note under the "What's next" intro explaining the two markers, and mirror it in `writing-docs`' Roadmap section so the convention is where doc edits are governed.

**The "highest-priority unfinished feature" pointer** lands in `PROGRESS.md`'s new header block (section 4a), not in JSON.

**The `verification` field is already better covered** by the change-kinds table in `.claude/skills/2-develop/SKILL.md` and the procedures in `change-kinds.md`, which are per kind of change rather than retyped per feature.

### Scope guard

`docs/roadmap.md` is a client-facing living doc governed by `writing-docs`. This change touches only the two markers and one explanatory sentence. Do not restructure "Where we are," do not reword existing lines, do not retro-fit `user_visible_behavior` sentences onto the 14 already-ticked lines.

---

## 6. `session-handoff.md`

**Template shape:** Verified Now, Changed This Session, Broken Or Unverified, Next Best Step, Commands (startup, verification, focused debug).

### Plan: do not add the file

**Deviation.** Field-by-field, it is `PROGRESS.md` with different headings:

| Template section | Already covered by |
| --- | --- |
| Verified Now | `PROGRESS.md` Live now, plus `init.sh`'s live-vs-`origin/main` check |
| Changed This Session | git log, which `init.sh` will now print (section 3d) |
| Broken Or Unverified | `PROGRESS.md` Blocked |
| Next Best Step | `PROGRESS.md` In flight, plus the new Current verified state block |
| Commands | nothing: the one real gap |

The guide itself calls the file optional and aimed at long sessions with several active areas. This repo forbids that shape by non-negotiable 1.

**Adopt the Commands block only**, into `PROGRESS.md`'s Current verified state (section 4a).

Section 13b strengthens this further for not-small changes: once deep-plan's confirmed plan lands in `PROGRESS.md` at confirm time rather than only at Pause, there is even less a separate handoff file would capture that `PROGRESS.md` does not already hold, live, before any pause is even declared.

---

## 7. `clean-state-checklist.md`

**Template shape:** six checkboxes in a standalone root file.

**What we have:** the same content as prose, in two places: `AGENTS.md` "End of session" (5 bullets) and `2-develop`'s Ship step (clear `PROGRESS.md`, empty `preview/`, free port 8000, confirm live equals main).

### Plan: adopt the format, split by who needs it, not one file

**Deviation.** A third copy of end-of-session rules is the drift risk this repo keeps hitting. The template's six items are not actually one kind of thing, though: some apply to every session regardless of task kind, some only apply once a product change ships. Splitting them by audience, rather than forcing them into one file, avoids both a third copy and a checklist that repo maintenance has no reason to open.

**`AGENTS.md` "End of session" becomes the generic checklist**, as real checkboxes, since every session, maintenance included, needs these and has no reason to consult `2-develop` (which gates on "any product change"):

- [ ] Working tree clean or committed; nothing surprising left staged.
- [ ] `PROGRESS.md` reflects reality: cleared if the turn shipped, updated if it paused mid-change.
- [ ] No half-finished step left undocumented: anything incomplete is in `PROGRESS.md` or committed on a branch, not only in the chat. *(new, from the template)*
- [ ] The next session can start from `bash init.sh` with no manual repair. *(new, from the template)*
- [ ] Recommend `/clear`, or `/compact` if context has grown but continuity still matters.

**`2-develop`'s Ship step becomes the product-specific checklist**, turning its existing prose into real checkboxes rather than restating them a second time in `AGENTS.md`:

- [ ] `docs/roadmap.md` reflects what actually passed: no line ticked that the client has not signed off live, no stale `(in flight)` or `(blocked)` marker. *(new, from the template)*
- [ ] `preview/` empty, port 8000 free.
- [ ] The live host is back on `main` (`bash init.sh --quick` confirms it).

One canonical copy of each half, each where the session that needs it will actually look.

**Confirmed 2026-09-15:** the split stands, no standalone `clean-state-checklist.md`.

---

## 8. `evaluator-rubric.md` (new file, repo root)

**Template shape:** a 6-row table scored 0-2 (Correctness, Verification, Scope discipline, Reliability, Maintainability, Handoff readiness), a Verdict (Accept / Revise / Block), and Required Follow-Up (missing evidence, required fixes, next review trigger).

**What we have:** nothing. `HARNESS.md` records that an independent review pass before Try was considered and left optional, on the grounds that the client's live sign-off already outperforms most automated review gates.

### Plan: adopt near-verbatim, at repo root

Root matches both the template and our own convention for harness artifacts (`HARNESS.md`, `PROGRESS.md` are root; `docs/` is for client-facing living docs).

Take the template's six categories and table shape unchanged. Add these project-specific pieces:

- **A framing paragraph** stating what it is for and, critically, what it is not: the rubric grades a session's output, it does not gate a merge. Only the client's live sign-off does. Without this line the rubric becomes a way to self-approve past the real gate, which is the exact failure `docs/decisions.md` 2026-09-10 ("Deploy only on the client's explicit go-ahead") was written to stop.
- **Bind the Verification row to `change-kinds.md`**, so "did the required checks run" means the row of the change-kinds table for each kind the change carried, not a vague impression.
- **Bind the Scope discipline row to Shape**, which already records what the change would leave alone. That makes the row checkable against a written statement rather than a memory.
- **The tuning warning from the guide**, in the file itself: agents are poor self-judges out of the box and will talk themselves into approving. Plan for three to five rounds of scoring a completed change, comparing against the client's own judgement, and tightening whichever row diverged. Record each tightening so the alignment work is visible.
- **When to run it:** after Ship, on a not-small change. Not on every typo fix. Explicitly optional, consistent with `HARNESS.md`'s existing position on review passes.

**Deviation from the template's placement in the workflow:** the guide positions the rubric "after implementation and before final acceptance," which in this repo would put it before the client's sign-off and risk reading as a gate. Ours runs after Ship, as a retrospective on the session, not a checkpoint in the loop.

---

## 9. `quality-document.md` (new file, repo root)

**Template shape:** grading scale A to D; a Product Domains table (Domain, Grade, Verification, Agent Legibility, Test Stability, Key Gaps, Last Updated); an Architectural Layers table (Layer, Grade, Boundary Enforcement, Agent Legibility, Key Gaps, Last Updated); a Change History section. Plus a harness-simplification loop described in the guide.

**What we have:** nothing. `HARNESS.md` describes the harness, not the codebase's health.

### Plan: adopt the structure, replace the example content

The template's domains and layers are from an Electron document app (Main Process, Preload, Renderer, Services). We are Python and FastAPI. Substitute real ones.

**Product domains**, taken from the epic groups in `docs/roadmap.md` so the two documents agree on what the product is made of:

| Domain | Source of truth for its state |
| --- | --- |
| Manage Lists | roadmap group, fully ticked |
| Manage Sources | roadmap group, fully ticked |
| Bring the Library Over | roadmap group, nothing ticked |
| Read Later | roadmap group, one line open |
| Reading Progress | roadmap group, fully ticked |
| Highlight and Land in Obsidian | roadmap group, nothing ticked |
| Improve UI | roadmap group, nothing ticked, gated on a full built app |

**Architectural layers**, taken from the real module layout rather than invented:

| Layer | Files | What "boundary enforcement" means here |
| --- | --- | --- |
| Routes and request handling | `app/main.py` (1343 lines) | Does it hold logic that belongs in `db.py` or `ingest.py` |
| Data access | `app/db.py` (714 lines) | Is SQL confined here |
| Ingest | `app/ingest.py` (602 lines) | Feed, YouTube, and capture paths kept separable |
| Mail | `app/mail.py` (140 lines) | IMAP confined here; isolated mailbox only |
| Config | `app/config.py` (43 lines) | Environment reads confined here |
| Templates and static | `app/templates/` (22 templates), `app/static/` | Presentation only; PWA cache registration |

**Grade the layers in this change.** The client authorized the first grading pass as part of this work (2026-09-15), rather than deferring it. Populate the structure, the domain and layer rows, and the criteria, then actually grade each one by reading the relevant code and the roadmap, not by guessing from file sizes alone: `app/main.py` at 1343 lines is a real signal for the Routes layer's grade, but the grade itself still has to name what specifically is or isn't a boundary problem, not just cite the line count.

**Adopt the harness-simplification loop** from the guide, in the file:

1. Take a snapshot.
2. Remove one harness component.
3. Re-run the suite and the standard verification path.
4. Take another snapshot.
5. If grades did not drop, the component was overhead. If they did, restore it.

This is worth capturing because the repo already reasons this way and has no written method for it: `docs/decisions.md` 2026-09-10 deleted roughly 900 lines of dormant discovery skills on precisely this argument, and `HARNESS.md` frames every harness component as an assumption about what the model cannot do.

**Cross-reference guard:** the domain table duplicates the epic names from `docs/roadmap.md`. To keep that from drifting, the file states that the roadmap is the source of truth for which domains exist and what is built, and that this file only grades them.

---

## Cross-cutting work

### 10. `tests/test_harness_refs.py`

`CHECKED_FILES` is currently `[AGENTS.md, CLAUDE.md, README.md, HARNESS.md]` plus every `.md` under `.claude/skills/` and `docs/`. The two new root files would not be checked, and neither is `PROGRESS.md` today.

**Add `PROGRESS.md`, `evaluator-rubric.md`, and `quality-document.md` to `CHECKED_FILES`.** All three will carry backticked repo-relative paths that the regex picks up, so the guard is worth having. This is a behaviour change to a test, so per non-negotiable 6 it gets the check that it fails for the right reason: confirm the expanded list actually parametrises to three more cases before relying on it.

`PLAN.md` itself is deliberately not added: it is deleted at the end of the change.

### 11. `HARNESS.md`

Every section above changes what is true about the harness, so non-negotiable 10 requires updating it on the same branch, and the client asked directly that nothing from this change go unmentioned so `HARNESS.md` stays a complete map. Walking every subsystem in its existing table, not just the two new files:

- **Instructions:** the `AGENTS.md` description gains a line for its new Required Artifacts and Definition of Done sections (1a, 1b), and for non-negotiables 6 and 7 each gaining a clause (1c). Non-negotiable 2's reworded text (13a: no plan files that outlive the change; a not-small change's plan lives in `PROGRESS.md`, not chat) replaces the current "No plan files" description wherever `HARNESS.md` paraphrases it. The archived-plan convention (13d: one dated `docs/decisions.md` entry per archived plan, naming its tag) gets its own line next to the existing discovery-skills and template-plan tag examples, stated as the standing rule those two instances follow, not left implicit. `2-develop`'s description notes that deep-plan's confirmed plan now writes to `PROGRESS.md` at confirm time for a not-small change (13b), and that Pause is correspondingly smaller for those.
- **State:** `PROGRESS.md`'s description gains its new Current verified state block (4a) and, for not-small changes, the deep-plan plan and per-slice status it now carries (13b, 13e). `docs/roadmap.md`'s description notes the `(in flight)` / `(blocked)` inline markers (section 5). `docs/decisions.md`'s description notes the archived-plan convention (13d) as a stated pattern, not only shown through examples.
- **Verification:** a new **Review** row (or an expanded Verification row), naming `evaluator-rubric.md` and `quality-document.md`, their status as new and, per the client's 2026-09-15 direction, actually graded rather than left blank (section 9). Notes that the "considered and left optional" review question now has concrete artifacts behind it, position unchanged: still optional, still not a gate.
- **Scope:** one line noting deep-plan's output is now durable (13b) rather than chat-only, since Scope already covers Frame/Shape/deep-plan.
- **Session lifecycle:** Start gains `git log --oneline -5` (1d, 3d). Work notes deep-plan writing to `PROGRESS.md` at confirm time for not-small changes. End notes the checklist split (section 7): `AGENTS.md` holds the generic half, Ship's own steps hold the product-specific half, rather than one shared list. The subsystem table's own Status column is refreshed wherever an edit above changes what was true when it was last written (for example, State's "Both covered" note).

Keep `HARNESS.md` describing what is actually true after the other commits land, not what this plan intends: write this commit last, and check it against the real state of each edited file rather than against this plan's wording.

### 12. Voice

`writing-docs` governs `docs/` and the root `README.md`. The new root harness files are not under `docs/`, but there is no nearer house style, so follow it: bold labels on list items, one idea per bullet, tables where columns compare peers, no em dashes, and no emoji outside the fixed vocabulary. `AGENTS.md` and `PROGRESS.md` keep their existing plainer register.

---

## 13. Beyond the nine templates: chat is not a durable record

None of the nine walkinglabs templates raised this; it surfaced from reviewing why `PLAN.md` was being treated as an exception to non-negotiable 2 rather than an instance of the right pattern. The client's position, stated directly: a chat session is not guaranteed to persist, so nothing that must survive past this conversation should depend on chat being the record of what was decided. That reaches two places already live in this repo.

### 13a. `AGENTS.md` non-negotiable 2

**Current wording:** "No plan files. The chat is the plan; a separate document drifts from what was actually decided."

**Problem:** the second clause names chat itself as the durable record for the period between Frame/Shape and the next commit. If the session ends before that commit lands (disconnect, crash, a context limit that drops the working turn), nothing survives, not because a plan file was missing, but because the one place the decision lived was never treated as something that could vanish.

**Proposed rewording:** "No plan files that outlive the change they describe. For a not-small change, `deep-plan.md`'s confirmed slice list is recorded in `PROGRESS.md`'s in-flight section as soon as it is confirmed, not only at Pause; that is the durable record, not the chat. A small change's Shape stays chat-only: cheap enough to re-Shape from scratch if a session is lost, not worth a mandatory write on every single one. A working plan file is fine for a change the client asks to see planned in writing, deleted once the change ships (see `docs/decisions.md` 2026-08-28 and the entry section 13c adds)."

This keeps what non-negotiable 2 was actually protecting against, a plan document that quietly drifts from what shipped, while dropping the part that assumed chat persistence, and without taxing every small change for a benefit that mostly applies to bigger ones (see 13b's client-flagged token-cost concern, 2026-09-15).

### 13b. `2-develop`'s deep-plan and Pause steps, not-small changes only

**Current mechanics:** for a small change, Shape is "one message" in chat. For a not-small change, `deep-plan.md` produces a confirmed slice list instead, explicitly written nowhere durable: "Write nothing to `docs/` for this: the confirmed summary is the plan." Either way, nothing survives until Pause (leaving mid-change) or Ship (on completion). A session that ends between that confirm and either of those loses the plan entirely: what will change, what could break, how it will be verified, what it leaves alone, or, for a not-small change, the whole slice breakdown.

**Proposed change, narrowed to not-small changes (client concern, 2026-09-15):** deep-plan's confirmed slice list is written into `PROGRESS.md`'s in-flight section the moment it is confirmed in chat, not deferred to Pause. Pause becomes a smaller step for these: it already has the plan on file, and only adds the branch name, feedback rounds so far, and the next step.

**Small changes are deliberately left out.** The client flagged that a mandatory `PROGRESS.md` edit on every Shape adds a real, recurring token cost for a benefit that only pays off in the rare case a session dies mid-change, and a small change is by definition cheap to re-Shape from chat memory if that happens. Not-small changes are the opposite: rarer, higher-stakes if the plan is lost, and the write lands next to work already happening (deep-plan's own confirm, plus a commit at each slice's Try per 13e) rather than as pure added overhead. So this section, and the non-negotiable 2 rewording in 13a, apply only where deep-plan already applies.

**Confirmed 2026-09-15:** a new "Planned" subsection under "In flight," holding the confirmed slice list plus, per 13e, each slice's status. Ships in this same maintenance change, not a separate turn. This is a small follow-on edit to `2-develop/SKILL.md` and `PROGRESS.md`'s own header comment, alongside the template-alignment work in sections 1 through 9, since both land in the same branch. It does not disturb the `awk` extraction `init.sh` runs against `PROGRESS.md` (section 4, Constraint to respect): "Planned" nests inside the existing `## In flight` heading rather than adding a new one.

### 13e. Per-slice status for a not-small change

**Problem 13b alone misses:** deep-plan's slices "run one at a time... each with its own Preview, Build, and Try." A session can die between slice 2 and slice 3 of a change that is otherwise mid-flight. Writing the slice list once, at confirm time, is not enough by itself: without also recording which slice is done and which is next, a resumed session has the plan but not its progress against it, and would have to infer position from the branch's commits and the live app instead of `PROGRESS.md`.

**Proposed change:** the same in-flight entry that holds the confirmed slice list (13b) also carries a per-slice status line (done / in progress / not started), updated at each slice's own Try, alongside the per-change fields Pause already writes: branch, feedback rounds so far, next step.

**Scope:** applies only to not-small changes. A small change's Shape has no slices to track; 13b alone covers it.

### 13c. A new decision, not an edit to the old one

`docs/decisions.md` is append-only, newest first; the 2026-08-28 entry ("The change loop replaces the epic-based workflow") is not edited to match this. A new entry records the reversal instead, dated when 13a and 13b actually ship: title along the lines of "Chat is not treated as a durable record for a not-small change; deep-plan's confirmed plan is written to `PROGRESS.md` at confirm time," with **Rejected** naming the 2026-08-28 wording it supersedes and naming the token-cost reasoning for why small changes stay chat-only.

### 13d. Archived plan files each get one dated entry, as a standing convention

The client confirmed this beyond the one instance: every plan file that gets committed then deleted at ship, this one included, gets exactly one dated entry in `docs/decisions.md` naming the tag it was archived at, rather than a live folder of saved plans (the `docs/history/` shape retired 2026-09-10, for sitting unconsulted and drifting). This is now the standing mechanism non-negotiable 2's reworded text (13a) points to, not a one-off explained only in this plan; the `docs/decisions.md` bullet added to `AGENTS.md`'s Required Artifacts (section 1a) states it directly so a future session does not have to reconstruct the convention from two examples.

---

## Commit sequence

One logical change per commit, per the `commits` skill, format `action scope: description`, all on `claude/readme-folder-tree-review-5tacpb`.

1. `update init.sh: name the commands, print cwd and recent log, add the start command` (section 3)
2. `update progress: add the current verified state and commands block` (section 4)
3. `update agents: required artifacts, definition of done, and a real end-of-session checklist` (sections 1a, 1b, 1c, 1e)
4. `update develop: split the clean-state checklist, Ship gets the product-specific half` (section 7)
5. `add evaluator rubric: a post-change scorecard that is not a gate` (section 8)
6. `add quality document: domain and layer health, first pass graded` (section 9)
7. `update roadmap: in-flight and blocked markers` plus the mirrored note in `writing-docs` (section 5)
8. `update harness refs test: check progress, rubric, and quality document` (section 10)
9. `update agents: non-negotiable 2 no longer names chat as the durable record` (section 13a)
10. `update develop: write deep-plan's confirmed plan, and per-slice status, to PROGRESS.md at confirm time for not-small changes` (sections 13b, 13e)
11. `add decision: chat is not the record for a not-small change, deep-plan writes to PROGRESS.md at confirm time` (section 13c)
12. `update harness: record every change above, written last against the real state of each file` (section 11)
13. `remove plan: the change is shipped` (this file)

Commits 1 to 12 each leave the repo working. Run `uv run ruff check` and `uv run pytest` before each. `HARNESS.md` (commit 12) comes after every content change, including 13a-13c, per section 11's own instruction to write it last.

## Acceptance criteria

- `bash init.sh` and `bash init.sh --quick` both run clean; the in-flight extraction still prints correctly after the `PROGRESS.md` edit.
- `RUN_START_COMMAND=1 bash init.sh` serves the app on 8000, and `--quick` does not launch it.
- `uv run pytest` green, including three new parametrised cases in `test_harness_refs.py`.
- `uv run ruff check` clean.
- `AGENTS.md` still has at most 15 non-negotiables.
- Every new backticked path and markdown link in the new and edited files resolves.
- `HARNESS.md` describes the repo as it is after commits 1 to 11, with nothing aspirational.
- No `feature_list.json`, no `session-handoff.md`, no `clean-state-checklist.md`, and `CLAUDE.md` unchanged.
- `AGENTS.md` non-negotiable 2 no longer states or implies that chat is the durable record between Shape and the next commit.
- `deep-plan.md`'s confirm step writes its output to `PROGRESS.md` at confirm time, not only at Pause, for not-small changes. A small change's Shape stays chat-only, by deliberate choice, not oversight.
- A not-small change's in-flight entry in `PROGRESS.md` shows per-slice status, updated at each slice's Try.
- `PLAN.md` deleted.

## Risks

- **`AGENTS.md` growth.** It is already long and it is read in full every session. The additions are roughly 25 lines. If it starts to feel bloated, the right cut is the "Commands" section, which duplicates `docs/development.md`, not the new definition of done.
- **Two review artifacts nobody uses.** The rubric and the quality document are optional by design, and optional harness machinery is what this repo deleted 900 lines of in September. Mitigation: the quality document's own simplification loop is the check. If neither file has been touched in a few months, that is evidence to remove them, and the file says so.
- **Roadmap markers going stale.** An `(in flight)` marker left behind after Ship is worse than no marker. Mitigated by the new checklist item in section 7 and by Ship already clearing `PROGRESS.md`.
- **The start command diverging from `docs/development.md`.** Deliberate, explained in section 3a, flagged in the commit message.

## Open questions for the client

All resolved as of 2026-09-15. Kept for the record rather than deleted, since each answer shaped a section above.

1. ~~`clean-state-checklist.md`: fold into `AGENTS.md`, or a standalone file?~~ Split by audience instead (section 7): generic half in `AGENTS.md`, Ship-specific half in `2-develop`. No standalone file.
2. ~~Should the first grading pass on `quality-document.md` happen in this change, or as its own turn?~~ This change, per section 9.
3. ~~Does "no plan files" stay a non-negotiable after this?~~ No: chat is not treated as a durable record for a not-small change (section 13).
4. ~~Sections 13b/13e's `PROGRESS.md` format, and whether 13a-13e ship now or separately?~~ A "Planned" subsection under "In flight," carrying deep-plan's confirmed slice list and per-slice status; ships in this same maintenance change.
