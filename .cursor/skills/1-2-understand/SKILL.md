---
name: 1-2-understand
description: >-
  Runs the Understand phase: personas, journeys, and cross-cutting constraints.
  Use when roadmap says Understand, or after Kickoff is accepted.
---

# Understand

Build a shared picture of who the product is for, what they are trying to do, and the constraints that shape those journeys. Descriptive only — no epics and no prototype / MVP / later cuts.

## Entry

- Kickoff is accepted (`docs/product-definition/vision.md` and `docs/product-definition/metrics.md`)

## Artifacts

- `docs/product-definition/personas.md`
- `docs/product-definition/journeys.md`
- `docs/product-definition/constraints.md`

## Do

**Include:**
- Personas: who uses the product, goals, context
- Journeys: what they are trying to do end to end, including detail and edge cases that belong on a journey
- Constraints: cross-cutting rules and limits (compliance, data, offline, integrations, must-nots) that do not sit cleanly on one journey
- Open questions that still block a clear picture of users or journeys

Do not write epics. Do not assign prototype / MVP / later. Do not invent stack or architecture.

**Human role:** Confirm personas and journeys feel right; add missing users or paths; challenge weak constraints; accept when the picture is good enough to scope.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Scope. Do not advance without confirmation.
