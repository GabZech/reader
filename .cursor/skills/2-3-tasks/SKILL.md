---
name: 2-3-tasks
description: >-
  Runs Feature Development step 2.3 Tasks: ordered implementation steps in
  docs/specs/<feature-slug>/tasks.md. Use when writing tasks.md, or after
  Design is accepted.
---

# Tasks

Break the accepted design into implementation steps small enough to execute and check off.

## Entry

- Design for this feature is accepted
- Read `requirements.md` and `design.md` under `docs/specs/<feature-slug>/`

## Artifact

- `docs/specs/<feature-slug>/tasks.md`

## Do

**Include:**
- Discrete, ordered, trackable tasks
- Clear descriptions and expected outcomes
- Dependencies between tasks
- Optional vs required tasks

Tasks must implement only the accepted requirements and design. No coding yet.

**Human role:** Review the breakdown; adjust priorities; mark optional tasks; confirm when ready for Build.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Build. Do not start Build without confirmation.
