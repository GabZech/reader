---
name: 2-5-review
description: >-
  Runs Feature Development step 2.5 Review: client tries the build against
  acceptance criteria, requests adaptations as needed, and gives final
  acceptance; append notes under docs/specs/<feature-slug>/review/. Use when
  reviewing a built feature, or after Build is ready for Review.
---

# Review

Walk the built software back against the acceptance criteria from Requirements. The agent prepares; the client tries it, requests occasional adaptations, and gives final acceptance.

## Entry

- Build is explicitly ready for Review
- Read `docs/specs/<feature-slug>/requirements.md` and `design.md`

## Artifact

- `docs/specs/<feature-slug>/review/`: append-only notes of what was checked and when

## Do

**Agent prepares:**
- Map changes to requirements acceptance criteria and EARS behaviours
- Summarise deviations from design
- Point at tests run and residual risk
- Run the usual local check suite when practical; call out anything not verified
- Write a dated note under `review/`
- Help the client exercise the feature (how to run it, what to try against the criteria)

**Human role:** Try the software against the acceptance criteria; request adaptations where something is wrong or incomplete (return to Build for those changes); give explicit final acceptance when satisfied. Bugbot and security review subagents are available when asked; they are not mandatory every cycle.

## Gate

Ask for explicit final accept after the client has tried the build. On accept: update `docs/roadmap.md` “Where we are” to Documentation. Do not advance without confirmation. On requested adaptations: return to Build and append a follow-up note when re-reviewed.
