---
name: 2-3-deploy
description: >-
  Runs Feature Development step 2.3 Deploy: verify the rollback path, put the
  signed-off local Build on the production host, smoke the live path, and
  bring living docs in line with what is now live. Use after Build when the
  epic is done, when the client asks to ship the current signed-off state, or
  when aligning architecture, operations, or roadmap with a shipped increment.
---

# Deploy

Stop building. Confirm there is a way back, release the last signed-off local state to the production host, smoke that it works, and make the living docs match what is actually live. This is the continuous-delivery release: software stayed releasable in Build; going live is an explicit go, not continuous deployment of every change. This is the only time overview docs move for a feature, and the only time later revisions reach production after Foundation's first standup.

Build may push increments straight to the live host for trial (see Build's Do section). Those trial pushes are not this phase: they carry pre-signoff, possibly unfinished work, have no rollback check or smoke test behind them, and do not touch living docs. Do not treat a trial push as satisfying any Deploy requirement below.

## Entry

- Same branch as the open Build
- Either the epic's increment map is done (or leftover risk is explicit), or the client asked to ship
- Ship only signed-off increments; never an unfinished slice
- Read `docs/epics/<epic-slug>/plan.md`, `clarifying-answers.md`, `docs/architecture.md`, and `docs/operations.md`

## Artifacts

Update as needed:
- `docs/architecture.md` for structure, data flow, or component boundaries
- `docs/development.md` / `docs/operations.md` when procedures change (commands must have been run)
- `docs/ui-guidelines.md` when visual or interaction rules change
- `docs/roadmap.md` when something ships or priorities shift
- New decision records under `docs/history/decisions/` when a choice from Build's logged deviations is hard to reverse
- `docs/epics/<epic-slug>/`: epic note (what shipped vs what was planned, still open, how to try) plus frozen `plan.md` and `clarifying-answers.md` when this Deploy closes the epic

## Do

- Before deploying: confirm the fallback named in `plan.md`'s reversibility notes for what is shipping still holds, proportionate to how this product is hosted and operated. Take any backup that fallback depends on (for example the library file) before a migration runs.
- Deploy per `docs/operations.md`. Do not add product behaviour.
- If hosted: smoke per `docs/operations.md` on the live revision just shipped. Record the result in the epic note, or in `clarifying-answers.md` if the epic stays open.
- If smoke fails: use the confirmed rollback, or return to Build to fix. Do not leave a failed smoke live.
- Align overview docs with what is now live, not with a plan written before Build. Fold any deviations `plan.md` logged during Build into `architecture.md`; write a decision record when one is hard to reverse. Follow writing-docs.
- Mid-epic ship: update living docs that would otherwise lie about production; leave `plan.md` and `clarifying-answers.md` unfrozen; do not mark the epic complete.
- Epic-complete: fold durable facts from `plan.md` and `clarifying-answers.md` into living docs (and an ADR when a choice is hard to reverse). Freeze both files. Write the close note: what shipped against what was planned, leftover risk, how to try it (local, and the live URL if hosted). Do not rewrite `docs/history/discovery/` to match this epic.
- Overview docs ship on the same branch as the approved Build.

**Human role:** Ask to ship the last signed-off state during Build; confirm the rollback path and that the overview is accurate; accept when leftover risk is explicit.

## Flow

1. Orient once: no new behaviour; rollback check, production release, smoke, docs. Name whether this is a mid-epic ship or epic close.
2. Confirm the rollback path for what is shipping; take any backup it depends on.
3. Deploy the signed-off revision per `docs/operations.md`.
4. Smoke the intended run path if hosted, or state that local-only still matches `development.md`.
5. Diff living docs against what is now live; draft updates and, if epic-complete, the epic note.
6. Gap check; accept.

### Ready to accept when

- The rollback path for this ship is named and, if it depends on a backup, that backup was taken
- Hosted: the smoke in `operations.md` has been run on the live revision just shipped, or a blocker is explicit
- Overview docs that this ship touched match what is live
- Epic-complete: epic note is honest about shipped vs planned vs still open; `plan.md` and `clarifying-answers.md` are frozen; hard-to-reverse choices that arose are in decision records
- Mid-epic: `plan.md` and `clarifying-answers.md` stay open; remaining increments are still named

If those are missing, keep writing or fixing the release: do not invent a clean close.

## Gate

After the gap check, ask for explicit accept.

On mid-epic accept: update `docs/roadmap.md` per writing-docs (phase → Build for this epic; refresh Summary / Open for remaining increments). Resume Build. Do not mark the epic complete.

On epic-complete accept: update `docs/roadmap.md` per writing-docs (this epic complete; phase → Plan for the next MVP epic named in `epics.md`, or mark **Milestone: MVP** if MVP scope is done; refresh Summary / Decisions / Open). Do not offer a README refresh. Do not mark the epic complete without confirmation.
