---
name: 2-2-build
description: >-
  Runs Feature Development step 2.2 Build: implement an epic's planned
  increments one vertical slice at a time on a local instance of the real
  product, verified against the plan, with a short try-and-sign-off loop like
  Mockup. Use when roadmap says Build, after an epic's Plan is accepted, after
  Deploy of the previous epic, or when returning from a mid-epic Deploy.
---

# Build

Build the current epic's planned increments, one tryable slice at a time, against `docs/epics/<epic-slug>/plan.md`. Do not re-derive what Plan already settled; build what it named, verify against the failure modes and test approach it named, then let the client try it. Continuous integration: run the usual local checks and the tests the plan called for before showing a slice. Continuous delivery: keep signed-off work releasable, but do not release it here. This is not a spec, not throwaway, and not Deploy.

## Entry

- This epic's Plan is accepted: `docs/epics/<epic-slug>/plan.md` names the increment map
- Resume directly, no re-confirm, when this epic's Build is already underway, including return from a mid-epic Deploy

## Artifacts

- Working software, tried locally or via a trial push to the live host (see Do)
- `docs/epics/<epic-slug>/clarifying-answers.md`: lived facts this increment needed that the plan could not settle upfront, and which increments are signed off
- Deviations from `plan.md` discovered while building, logged in that file

## Do

**Include:**
- Work on a branch for this epic. Follow `docs/development.md` when present.
- Take the next increment from `plan.md`'s map. Re-read its job, dependencies, failure modes, and test approach before coding it.
- Clarifying questions via the **questioning** skill, only for lived facts the plan left open. **What to ask:** [questionbank.md](questionbank.md).
- Build the increment; write automated tests for the failure modes and edge cases the plan named for it, plus whatever the plan said would prove it done; run the usual local checks.
- Before showing the increment, check the diff against the plan: does it do the named job, honour the named dependencies, handle the named failure modes. Fix gaps found this way before the client sees them.
- Once local checks pass, push the increment to the live host as a **trial push** (`flyctl deploy --remote-only --ha=false` per `docs/operations.md`) so it can be tried there. A trial push is not a release: no rollback check, no smoke ceremony, no living-doc update, no `docs/roadmap.md` phase change. It carries pre-signoff, possibly unfinished work and is expected to be overwritten by the next increment's trial push.
- Show the increment with a short guided walkthrough: what to try first, then next, and which of the plan's failure modes are worth checking on this slice. Not "it's done, test everything." Write this in plain prose per the questioning skill's voice and its "presenting a set" pattern; never paste raw verification (curl output, route lists, test-runner logs, tool-call narration) into chat as a stand-in for the walkthrough. Do this every time a slice is shown, including small follow-up fixes within an increment, not just the first showing.
- One ask per showing: good, or something needed missing. Iterate until signed off. Record which increments are signed off. Never ask for sign-off without the guided walkthrough immediately before it in the same message.
- Once an increment is signed off, before starting the next one: recommend a `/compact` if context has grown enough to matter. Signed-off state lives in `plan.md` and `clarifying-answers.md`, not in the chat history, so nothing is lost by compacting there. This is a recommendation only — the agent cannot run `/compact` itself.
- If the client asks to put the current signed-off state live as a real release: enter **Deploy**. Do not ship an unfinished slice through Deploy. A trial push (above) is not this and does not by itself satisfy Deploy's rollback, smoke, or doc-alignment requirements.
- If reality contradicts the plan (an unnamed dependency, a failure mode that does not hold, a job that turns out bigger or different): log the deviation in `plan.md`. Pause and return to **Plan** to reconfirm when the deviation changes scope, risk, or another increment; otherwise note it and continue.

Do not write requirements, design, or task files. Do not redo epic choice, boundary, or map confirms; those are Plan's. Do not reopen Foundation unless the client asks. Do not pull in other epics. Do not restyle. Do not update overview docs or write decision records (Deploy owns those). Do not deploy to the production host.

**Human role:** Judge each running increment via the guided walkthrough; say if it is good or something needed is missing; confirm any material deviation from the plan; hold work outside this epic; ask to Deploy the last signed-off state at any time; when the map is done, confirm leftover risk so Deploy can ship the epic.

## Clarifying questions

Goal: fill only what `plan.md` left open for the current increment. Epic choice, boundary, the map, dependencies, and failure modes were already decided in Plan; do not re-ask them.

**What to ask:** [questionbank.md](questionbank.md).

### Ready to build an increment when

- The increment's entry in `plan.md` is current: no unresolved deviation carried from an earlier slice
- Remaining lived-fact gaps for this increment are filled

### Ready to show an increment when

- The slice is tryable end to end, on the live host if local trial is not available (trial push done)
- Tests for the plan's named failure modes exist and pass; local checks have been run, or the agent has said why not
- The diff has been checked against the plan's job, dependencies, and failure modes
- A short guided walkthrough is ready: what to try, in what order, what to watch for

### Ready to enter Deploy when

- The client asked to ship, and at least one increment is signed off: ship only those
- Or the increment map is done (or leftover risk per remaining increment is explicit), and `clarifying-answers.md` / `plan.md` name leftovers Deploy must record

If those are missing, keep asking or building: do not invent them.

## Gate

When the map is done: after the gap check, ask to enter Deploy for this epic. On that accept: update `docs/roadmap.md` per writing-docs (phase → Deploy for this epic; refresh Summary / Decisions / Open). Do not enter Deploy without confirmation.

When the client asks to Deploy mid-epic: update `docs/roadmap.md` (phase → Deploy; Summary names a mid-epic ship of signed-off increments); enter Deploy. Do not treat that as epic complete.

On requested behaviour after a sign-off: stay in Build unless they asked to Deploy. If it is not on the map, return to Plan.
