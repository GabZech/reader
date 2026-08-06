---
name: 2-4-build
description: >-
  Runs Feature Development step 2.4 Build: implement approved tasks on a
  feature branch. Use when implementing a SPEC, or after Tasks are accepted.
---

# Build

Implement the approved tasks, and only those, on a feature branch.

## Entry

- Requirements, Design, and Tasks are all accepted
- Work from `docs/specs/<feature-slug>/tasks.md`
- Follow local setup in `docs/development.md` when present

## Artifacts

- Working software on the feature branch (approved tasks implemented)
- Optional small annotations on SPEC files if tasks reveal corrections

## Do

- Execute approved `tasks.md` on the feature branch
- Keep the branch green with the same checks continuous integration runs when those exist
- Annotate `requirements.md`, `design.md`, or `tasks.md` only for small corrections revealed by implementation

**Do not** during Build:
- Update overview docs (`docs/architecture.md`, `docs/development.md`, `docs/operations.md`, `docs/roadmap.md`)
- Add decision records under `docs/history/decisions/` (those land in Documentation)
- Implement work outside the approved task list

**Human role:** Confirm when Build is ready for Review.

## Gate

Build may proceed task-by-task after Tasks are approved. Finishing Build still needs an explicit “ready for Review.” On that confirm: update `docs/roadmap.md` “Where we are” to Review.
