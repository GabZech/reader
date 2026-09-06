---
name: 2-develop
description: >-
  Runs the change loop for feature work: frame, shape, preview the look, build,
  try on the live app, ship. One change at a time, from any epic, signed off
  live before it merges. Use for any product change after Foundation is
  accepted: a feature, a fix, a UI tweak, a chore. Also use when asked to plan
  something properly, plan it well, think it through first, or deep plan it
  before building.
---

# Develop

One change at a time, from chat direction to live and merged. A change belongs to whatever part of the product the client names: epics group work in the roadmap, they do not gate it.

Client-facing voice follows the **questioning** skill.

## Entry

- Foundation is accepted
- Any product change: feature, fix, UI tweak, chore
- Once per chat, read `docs/roadmap.md` "Where we are" before the first change

## Artifacts

- Working software, merged to main and live
- Living docs, updated only where this change made them wrong
- `docs/roadmap.md`: "Where we are", and the ticked line under "What's next"
- `docs/conventions.md`: a how-to-build preference the client stated that outlives this change
- `docs/history/decisions/`: a decision record, only when the choice is expensive to undo

## The loop

### 1. Frame

Restate the change in a sentence or two. Name its kinds; a change can carry several, and every kind it carries applies. Then size it: **not small** if it touches more than a couple of files, adds a route, changes the schema or a dependency, or is a data or external-system change. Not small goes to [deep-plan.md](deep-plan.md) before step 2, as does any explicit ask to plan it properly.

### 2. Shape

Before any code, one message: what will change, what could break, how it will be verified. Small: say it and keep going. Not small: stop for one confirm. No plan file.

### 3. Preview

A change to what the client sees needs a screenshot of the intended look, signed off before product code exists. Iterate the mockup, never the app. Mechanics: [preview.md](preview.md). Skip only when producing the mockup would cost more than building and deploying the change outright.

### 4. Build

A branch per change. Behaviour: write the failing test first. Then the code, then `python -m pytest` and the local checks in `docs/development.md`. Read the diff against what Shape said and close gaps before the client sees it.

### 5. Try

Deploy the branch to the live host per `docs/operations.md`, then a short walkthrough in prose: what to open first, what to try next, which failure mode is worth checking on this change. One ask: good, or what is missing.

- Never ask for sign-off without the walkthrough in the same message
- Never paste curl output, route lists, or test logs in place of the walkthrough
- Two rounds of fixes that do not land mean the approach is wrong, not the details: back to Shape
- "Scrap this" is a clean outcome: delete the branch, redeploy main

### 6. Ship

Merge to main, then redeploy from main. One live host holds the real library, so the turn is not closed until what is live is main again; the same redeploy clears an abandoned branch. Then update the living docs this change made wrong, tick the roadmap line, and write a convention or a decision record if this change produced one. Recommend a fresh chat, and a `/compact` if context has grown.

If a shipped change breaks the live app: revert the merge, redeploy main.

## Change kinds

| Kind | Before code | Proof |
| --- | --- | --- |
| Visual | Signed-off screenshot mockup | The client's eye on the live app; no test |
| Behaviour | A failing test for the new behaviour | That test green, suite green |
| Bug | A test that fails for the reported reason | Same test green; it stays as the regression guard |
| Data / schema | Named fallback; library copied off the volume | Migration clean on a copy; smoke on live |
| External system | A probe proving the real connection and payload | Test against the captured payload, plus one live run |
| Chore / copy | Nothing | Checks pass; visible on the live app |

Procedures for the middle four: [change-kinds.md](change-kinds.md).

## Do not

- Write code before Shape, or product code for a visual change before its mockup is signed off
- Merge before the client has signed off on the live app
- Leave the live host on a branch once the turn is over
- Skip, disable, or weaken a test to get green
- Create per-epic plan or clarifying-answers files
- Restyle, or widen the change beyond what was asked

## Gate

The client trying it live and saying it is good. That is the only gate that closes a turn.
