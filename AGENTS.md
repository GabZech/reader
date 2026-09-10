# Agents

One manual for any AI coding tool working in this repo, vendor-neutral. Read it in full before any task.

## Start of session

1. Run `bash init.sh --quick` (or let the SessionStart hook run it for you) for git state, the live version against `origin/main`, and anything in flight.
2. Read `PROGRESS.md`. If it names something in flight, resume that before starting anything new.
3. Once per chat, before the first product change, read `docs/roadmap.md` "Where we are."

## Which kind of task

- **Product change** (a feature, fix, UI tweak, or chore that changes behaviour or what the client sees): the change loop applies.
- **Repo maintenance** (docs, skills, CI, this file): the change loop's gates (Preview, live sign-off, deploy) do not apply, but still commit incrementally and still route anything touched through the table below.

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
2. **No plan files.** The chat is the plan; a separate document drifts from what was actually decided.
3. **Sign-off gates merge, not commit.** Commit on the branch as checkpoints pass; only the client's live sign-off allows a merge to `main`.
4. **Deploy only on the client's explicit go-ahead.** A screenshot or a walkthrough is not itself permission; one live host holds the real library.
5. **A visual change needs a signed-off mockup screenshot before product code exists.** Iterating a screenshot is cheap; iterating built UI is not.
6. **A behaviour or bug change needs a failing test first.** It proves the change does what it claims, and stays on as the regression guard.
7. **Never skip, disable, or weaken a test to get green.** A suite that lies is worse than one that is honestly red.
8. **Commit incrementally, one logical change per commit.** A single end-of-session commit hides which step broke something; format in the `commits` skill.
9. **Never force-push a shared branch, amend or rebase a pushed commit, or skip a hook.** Any of these can erase work someone, or CI, or a deploy, already has.
10. **Ship updates whichever living doc the change made wrong, on the branch, before merge.** Docs drift the moment a change lands without this.
11. **The live host always ends a turn on `main`.** One Fly app serves both trying and living; leaving it on a branch shows the client the wrong thing.
12. **Route every task through the table above before improvising.** The same kind of task handled the same way every time is what makes the rest of this file trustworthy.
13. **A doc or skill edit follows `writing-docs` or `write-skills`.** Both encode a house style that ad hoc edits drift from.
14. **Repo maintenance skips the change loop's gates, never its discipline.** Commit incrementally and route anything it touches through the table above.
15. **This file is read in full, every session, by hand if the tool does not expand `@` imports.** `CLAUDE.md`'s import into this file has not been confirmed to expand in every environment; assume it does not until proven otherwise.

## Where truth lives

Code and tests are behaviour. Living docs under `docs/` (not `history/`) are the current agreed picture: keep them true as part of the change that makes one wrong. `docs/history/` is how we got here; do not refresh it to match later code.

## Commands

- **Health, git, and live-state check:** `bash init.sh` (full) or `bash init.sh --quick` (skips install, lint, and test)
- **Run, test, lint, and local config:** `docs/development.md`

## Chat conduct

- When a message presents a set of items the reader must weigh together, structure it so the set reads clearly and stays visually distinct from surrounding prose.
- A question is not a command: answer it, do not act on it unless asked.

## End of session

- Working tree clean or committed; nothing surprising left staged.
- `PROGRESS.md` reflects reality: cleared if the turn shipped, updated if it paused mid-change.
- `preview/` empty, port 8000 free.
- If a product change shipped: the live host is back on `main` (`bash init.sh --quick` confirms it).
- Recommend `/clear` for a fresh session, or `/compact` if context has grown but continuity still matters.
