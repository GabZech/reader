---
name: 2-6-documentation
description: >-
  Runs Feature Development step 2.6 Documentation: bring overview docs in line
  with reality on the same feature branch. Use after Review is accepted, or when
  updating architecture, roadmap, development, or operations for a feature.
---

# Documentation

Bring permanent documentation back in line with reality, on the same branch as the code. This is the single place overview docs move.

## Entry

- Review is accepted
- Still on the feature branch that holds the approved Build

## Artifacts

Update as needed:
- `docs/architecture.md` for structure, data flow, or component boundaries
- `docs/roadmap.md` when something ships or priorities shift
- `docs/development.md` / `docs/operations.md` when procedures change (commands must have been run)
- `docs/ui-guidelines.md` when visual or interaction rules change
- New decision records under `docs/history/decisions/` when the choice is hard to reverse
- Archived plans under `docs/history/plans/` when an implementation plan closes
- `docs/specs/<feature-slug>/`: freeze after this phase is accepted (no further SPEC edits except gate notes later)

## Do

- Align overview docs with what was actually built
- Record significant technical choices as decision records under `docs/history/decisions/`
- Archive any implementation plan under `docs/history/plans/` with an outcome note when this cycle closes a plan

Overview docs ship on the same feature branch / squash merge as the approved Build: not mid-Build, and not in a later orphan commit after Deploy.

**Human role:** Confirm the overview is accurate before Deploy.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Deploy. Do not advance without confirmation.
