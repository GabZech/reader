---
name: 2-2-document
description: >-
  Runs Feature Development step 2.2 Document: bring overview docs in line with
  the accepted Build, write a short epic note, and smoke the live path when
  hosted. Use after Build is accepted, or when aligning architecture,
  operations, or roadmap with a finished epic.
---

# Document

Stop building. Make the living docs match the product as it actually is, record what this epic shipped and what is still open, and confirm the live path agrees. This is the only time overview docs move for a feature.

## Entry

- Build for this epic is accepted
- Still on the same branch as that Build
- Read `docs/specs/<epic-slug>/clarifying-answers.md`, `docs/architecture.md`, and `docs/operations.md`

## Artifacts

Update as needed:
- `docs/architecture.md` for structure, data flow, or component boundaries
- `docs/development.md` / `docs/operations.md` when procedures change (commands must have been run)
- `docs/ui-guidelines.md` when visual or interaction rules change
- `docs/roadmap.md` when something ships or priorities shift
- New decision records under `docs/history/decisions/` when the choice is hard to reverse
- `docs/specs/<epic-slug>/`: short epic note (what shipped, still open, how to try) plus frozen clarifying-answers

## Do

- Align overview docs with the running software, not with a plan written before Build. Follow writing-docs.
- Epic note: what the client can do now, leftover risk, how to try it (local, and the live URL if hosted).
- If hosted: smoke per `docs/operations.md` on the live revision that contains this epic; record the result in the epic note. If Build already deployed the last increment, do not invent a second host path; confirm that revision and smoke it.
- Overview docs ship on the same branch as the approved Build.

Do not add product behaviour. If smoke fails, return to Build (fix) or roll back per operations.md.

**Human role:** Confirm the overview is accurate; accept when leftover risk is explicit.

## Flow

1. Orient once: no new behaviour; docs and close.
2. Diff living docs against what was built; draft updates and the epic note.
3. Smoke the intended run path if hosted, or state that local-only still matches `development.md`.
4. Gap check: anything the docs still get wrong.
5. Accept.

### Ready to accept when

- Overview docs that this epic touched match reality
- Epic note is honest about shipped vs still open
- Hosted: the smoke in `operations.md` has been run on the live revision, or a blocker is explicit
- Hard-to-reverse choices that arose are in decision records

If those are missing, keep writing: do not invent a clean close.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (this epic complete; phase → Build for the next MVP epic named in `epics.md`, or mark **Milestone: MVP** if MVP scope is done; refresh Summary / Decisions / Open). Do not offer a README refresh. Do not mark the epic complete without confirmation.
