---
name: 2-1-requirements
description: >-
  Runs Feature Development step 2.1 Requirements: user stories and acceptance
  criteria in docs/specs/<feature-slug>/requirements.md. Use when starting a
  SPEC, writing requirements.md, or after Foundation proposes the next feature.
---

# Requirements

State what the feature must do before any design or code.

## Entry

- Foundation is accepted
- Feature chosen from MVP (or later) scope in `docs/product-definition/epics.md`
- Create `docs/specs/<feature-slug>/` if it does not exist

## Artifact

- `docs/specs/<feature-slug>/requirements.md`

## Do

**Include:**
- User stories with testable acceptance criteria
- System behaviours in EARS format (WHEN…THE SYSTEM SHALL…)
- Functional requirements
- Edge cases and error handling

Do not implement code. Do not write design or tasks yet.

**Human role:** Review completeness; iterate on stories and criteria; add missing scenarios; confirm when requirements meet their needs.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Design for this feature. Do not advance without confirmation.
