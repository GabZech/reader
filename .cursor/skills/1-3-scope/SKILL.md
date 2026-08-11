---
name: 1-3-scope
description: >-
  Runs the Scope phase: epics and prototype / MVP / later cuts. Use when
  roadmap says Scope, or after Understand is accepted.
---

# Scope

Turn accepted journeys into buildable epics and decide what belongs in the prototype, the MVP, and later. Decisive only — do not invent new personas or primary journeys here.

## Entry

- Understand is accepted (`docs/product-definition/personas.md`, `journeys.md`, `constraints.md`)

## Artifacts

- `docs/product-definition/epics.md` (one file: epics plus prototype / MVP / later cut)

## Do

**Include:**
- Epics as named capability slices, each traced to at least one journey (and usually a persona)
- Prototype cut: which journeys / epic slices must be clickable in Figma
- MVP cut vs later
- Seed `docs/roadmap.md` “What we are building” from the MVP cut

Do not rewrite personas or invent primary journeys. If something is missing, reopen Understand. Do not choose stack or architecture.

**Human role:** Challenge the cuts; move work between prototype / MVP / later; confirm the first buildable slice is clear.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Prototype; follow writing-docs **Root README** When for this phase. Do not advance without confirmation.
