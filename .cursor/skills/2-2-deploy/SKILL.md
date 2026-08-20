---
name: 2-2-deploy
description: >-
  Runs Feature Development step 2.2 Deploy: put the signed-off local Build on
  the production host, smoke the live path, and bring living docs in line with
  what is now live. Use after Build when the epic is done, when the client asks
  to ship the current signed-off state, or when aligning architecture,
  operations, or roadmap with a shipped increment.
---

# Deploy

Stop building. Release the last signed-off local state to the production host, smoke that it works, and make the living docs match what is actually live. This is the continuous-delivery release: software stayed releasable in Build; going live is an explicit go, not continuous deployment of every change. After deploy, smoke the live path. This is the only time overview docs move for a feature, and the only time later revisions reach production after Foundation's first standup.

## Entry

- Same branch as the open Build
- Either the epic's increment map is done (or leftover risk is explicit), or the client asked to ship
- Ship only signed-off increments; never an unfinished slice
- Read `docs/epics/<epic-slug>/clarifying-answers.md`, `docs/architecture.md`, and `docs/operations.md`

## Artifacts

Update as needed:
- `docs/architecture.md` for structure, data flow, or component boundaries
- `docs/development.md` / `docs/operations.md` when procedures change (commands must have been run)
- `docs/ui-guidelines.md` when visual or interaction rules change
- `docs/roadmap.md` when something ships or priorities shift
- New decision records under `docs/history/decisions/` when the choice is hard to reverse
- `docs/epics/<epic-slug>/`: epic note (what shipped, still open, how to try) plus frozen clarifying-answers when this Deploy closes the epic

## Do

- Deploy per `docs/operations.md`. Do not add product behaviour.
- If hosted: smoke per `docs/operations.md` on the live revision just shipped. Record the result in the epic note, or in clarifying-answers if the epic stays open.
- Align overview docs with what is now live, not with a plan written before Build. Follow writing-docs.
- Mid-epic ship: update living docs that would otherwise lie about production; leave clarifying-answers unfrozen; do not mark the epic complete.
- Epic-complete: fold durable facts from clarifying-answers into living docs (and an ADR when the choice is hard to reverse). Freeze that file. Write the close note: what the client can do now, leftover risk, how to try it (local, and the live URL if hosted). Do not rewrite `docs/history/discovery/` to match this epic.
- Overview docs ship on the same branch as the approved Build.

If smoke fails, return to Build (fix) or roll back per operations.md.

**Human role:** Ask to ship the last signed-off state during Build; confirm the live path and that the overview is accurate; accept when leftover risk is explicit.

## Flow

1. Orient once: no new behaviour; production release, smoke, docs. Name whether this is a mid-epic ship or epic close.
2. Deploy the signed-off revision per `docs/operations.md`.
3. Smoke the intended run path if hosted, or state that local-only still matches `development.md`.
4. Diff living docs against what is now live; draft updates and, if epic-complete, the epic note.
5. Gap check; accept.

### Ready to accept when

- Hosted: the smoke in `operations.md` has been run on the live revision just shipped, or a blocker is explicit
- Overview docs that this ship touched match what is live
- Epic-complete: epic note is honest about shipped vs still open; clarifying-answers are frozen; hard-to-reverse choices that arose are in decision records
- Mid-epic: clarifying-answers stay open; remaining increments are still named

If those are missing, keep writing or fixing the release: do not invent a clean close.

## Gate

After the gap check, ask for explicit accept.

On mid-epic accept: update `docs/roadmap.md` per writing-docs (phase → Build for this epic; refresh Summary / Open for remaining increments). Resume Build. Do not mark the epic complete.

On epic-complete accept: update `docs/roadmap.md` per writing-docs (this epic complete; phase → Build for the next MVP epic named in `epics.md`, or mark **Milestone: MVP** if MVP scope is done; refresh Summary / Decisions / Open). Do not offer a README refresh. Do not mark the epic complete without confirmation.
