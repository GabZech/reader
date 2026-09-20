# Agents

One manual for any AI coding tool working in this repo, vendor-neutral. Read it in full before any task.

## Start of session

1. Run `bash init.sh --quick` (or let the SessionStart hook run it for you) for git state, the live version against `origin/main`, and anything in flight.
2. Read `PROGRESS.md`, then check GitHub for open PRs — that list is the record, not a note here, so it can't go stale. If `PROGRESS.md` names anything else in flight, resume that before starting anything new.
3. Once per chat, before the first product change, read `docs/roadmap.md` "Where we are."

## Required artifacts

- **`PROGRESS.md`:** in-flight state and the standard paths. Read at start, updated at every checkpoint, cleared at Ship — never with a note that a PR awaits merge; GitHub's own list is that record.
- **`docs/roadmap.md`:** the feature list. "What's next" is what remains; a line is ticked only by the change that shipped it.
- **`docs/decisions.md`:** choices expensive to undo, including one dated entry for any plan file archived at a tag once its change ships.
- **`init.sh`:** the standard startup and verification path.
- **`HARNESS.md`:** how the harness itself is put together. Revisited after any change to how agents work here.
- **`evaluator-rubric.md` and `quality-document.md`:** a post-change scorecard and a standing snapshot of the codebase's health. Both optional; neither is a merge gate.

## Which kind of task

- **Product change** (a feature, fix, UI tweak, or chore that changes behaviour or what the client sees): the change loop applies.
- **Repo maintenance** (docs, skills, CI, this file): the change loop's gates (Preview, live sign-off, deploy) do not apply, but it still commits incrementally, still merges only through a PR (the client merges it, or explicitly tells the agent to), and still routes anything touched through the table below.

## Branch names

Every branch is `<type>/<kebab-slug>`, `type` matching which kind of task it is: `dev/` for a product change, `maint/` for repo maintenance. E.g. `dev/highlight-export`, `maint/pr-gated-merge`.

## Routing table

| Task | Skill |
| --- | --- |
| Any product change, once Foundation is accepted | `.claude/skills/2-develop/SKILL.md` |
| Any client-facing message: asking something, explaining, or an ask for sign-off | `.claude/skills/questioning/SKILL.md` |
| Editing a living doc under `docs/`, or the root `README.md` | `.claude/skills/writing-docs/SKILL.md` |
| Creating or editing a skill under `.claude/skills/` | `.claude/skills/write-skills/SKILL.md` |
| Committing | `.claude/skills/commits/SKILL.md` |

## Non-negotiables

1. **One change at a time.** Frame and Shape commit to a single change before code; stacking work hides what actually shipped.
2. **No plan files that outlive the change they describe.** For a not-small change, `deep-plan.md`'s confirmed plan is recorded in `PROGRESS.md`'s in-flight section as soon as it is confirmed, not only at Pause, since chat is not assumed to survive a lost session; a small change's Shape stays chat-only, cheap enough to re-Shape from scratch if it is. A working plan file is fine for a change the client asks to see planned in writing, and is deleted once the change ships.
3. **Sign-off gates merge, not commit; merge always goes through a PR.** Commit on the branch as checkpoints pass. Once the client signs off live, Ship opens a PR instead of pushing to `main` directly; the client merges it, or explicitly tells the agent to.
4. **Deploy only on the client's explicit go-ahead.** A screenshot or a walkthrough is not itself permission; one live host holds the real library.
5. **A visual change needs a signed-off mockup screenshot before product code exists.** Iterating a screenshot is cheap; iterating built UI is not.
6. **A behaviour or bug change needs a failing test first.** It proves the change does what it claims, stays on as the regression guard, and the verification bar does not move mid-change: if what counts as proof turns out to be wrong, say so and re-Shape.
7. **Never skip, disable, or weaken a test to get green.** A suite that lies is worse than one that is honestly red, and never start new work on a red baseline: say it was already red rather than silently fixing or working around it.
8. **Commit incrementally, one logical change per commit.** A single end-of-session commit hides which step broke something; format in the `commits` skill.
9. **Never force-push a shared branch, amend or rebase a pushed commit, or skip a hook.** Any of these can erase work someone, or CI, or a deploy, already has.
10. **Ship updates whichever living doc the change made wrong, on the branch, before merge.** Docs drift the moment a change lands without this.
11. **The live host always ends a turn on `main`.** One Fly app serves both trying and living; leaving it on a branch shows the client the wrong thing.
12. **Route every task through the table above before improvising.** The same kind of task handled the same way every time is what makes the rest of this file trustworthy.
13. **A doc or skill edit follows `writing-docs` or `write-skills`.** Both encode a house style that ad hoc edits drift from.
14. **Repo maintenance skips the change loop's gates, never its discipline.** Commit incrementally and route anything it touches through the table above.
15. **This file is read in full, every session, by hand if the tool does not expand `@` imports.** `CLAUDE.md`'s import into this file has not been confirmed to expand in every environment; assume it does not until proven otherwise.

## Where truth lives

Code and tests are behaviour. Living docs under `docs/` are the current agreed picture: keep them true as part of the change that makes one wrong. `docs/decisions.md` records choices that are expensive to undo.

## Commands

- **Health, git, and live-state check:** `bash init.sh` (full) or `bash init.sh --quick` (skips install, lint, and test)
- **Run, test, lint, and local config:** `docs/development.md`

## Chat conduct

- Just before a message that asks for human input (a question, a sign-off ask, a choice to make), mark it with a Markdown horizontal rule (`---` on its own line) followed by a short label in block capitals chosen for that message, so it renders as a real rule rather than wrapping as text on narrow screens:

  ```
  ---

  **SUMMARY**
  ```
- When a message presents a set of items the reader must weigh together, structure it so the set reads clearly and stays visually distinct from surrounding prose.
- A question is not a command: answer it, do not act on it unless asked.
- Narrate progress as it happens: a short update roughly every 5-10 seconds of work (what you just found, what you're doing next), not silence until a task finishes. At the end, briefly summarise what you did and explain what's next.
- Reach for visual structure over dense prose where it clarifies (e.g. tables for comparisons, Mermaid diagrams for workflows/processes/structures, headers and bold to make long answers scannable).

## Definition of done

A change is done only when all of these hold:

1. The behaviour is implemented and matches what Shape said it would be.
2. The verification for every kind the change carries actually ran, per the change-kinds table in `.claude/skills/2-develop/SKILL.md`.
3. Whichever living docs the change made wrong are updated on the branch, before the merge.
4. The client tried it live and said it is good. Nothing else substitutes for this, including a green suite or a passing rubric score.
5. The repo restarts clean from `bash init.sh` and the live host is back on `main`.

## End of session

- [ ] Working tree clean or committed; nothing surprising left staged.
- [ ] `PROGRESS.md` reflects reality: cleared if the turn shipped, updated if it paused mid-change.
- [ ] No half-finished step left undocumented: anything incomplete is in `PROGRESS.md` or committed on a branch, not only in the chat.
- [ ] The next session can start from `bash init.sh` with no manual repair.
- [ ] Recommend `/clear`, or `/compact` if context has grown but continuity still matters.
