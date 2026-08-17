---
name: 1-3-scope
description: >-
  Runs the Scope phase: epics and mockup / MVP / later scope. Use when
  roadmap says Scope, or after Understand is accepted.
---

# Scope

Turn accepted journeys into named capabilities (epics) and decide mockup scope, MVP scope, and what waits. The mockup is a clickable Figma dummy of the solution, not built software. Decisive only: do not invent new personas or primary journeys here.

## Entry

- Understand is accepted (`docs/product-definition/personas.md`, `journeys.md`, `constraints.md`)

## Artifacts

- `docs/product-definition/epics.md` (one file: epics plus mockup / MVP / later scope)
- `docs/history/discovery/03-scope/` (clarifying answers — never client prompts)

## Do

**Include:**
- Epics as named capabilities, each traced to at least one journey (and usually a persona). Same labels every time: capability, journeys, persona, MVP or later, in mockup scope. Package how the user sees the job, not by technical layer.
- Mockup scope: which journeys or epics must be clickable in Figma, and what that walkthrough is for (learning)
- MVP scope vs later
- Which epic is the natural first piece of the MVP to implement after Mockup
- Refresh `docs/roadmap.md` from those scopes (Milestone, Summary, Decisions, Open). The catalog stays in `epics.md`.

**Clarifying questions:** deliver each ask using the **questioning** skill (`.cursor/skills/questioning/SKILL.md`). **What to ask:** [questionbank.md](questionbank.md). Walk clusters one at a time; skip what Understand or this conversation already answered well.

Do not rewrite personas or invent primary journeys. If a path is missing, reopen Understand. Do not write user stories or acceptance criteria. Do not choose stack or architecture. Do not design Figma screens.

**Human role:** Challenge the scopes; move work between mockup / MVP / later; confirm the first piece of the MVP to implement is clear.

## Clarifying questions

Goal: gather only what epics and mockup / MVP / later scope need. Defer stories to Requirements; defer screens to Mockup; defer stack to Foundation.

### Principles

1. **Reuse Understand.** Deepen what is in or later; do not re-litigate personas, journeys, or constraints unless contradicted. Missing primary path: reopen Understand.
2. **User-recognisable capabilities.** Name epics the way someone would describe the job. Combine journeys into one epic only if they are the same job or a real outcome cannot complete without both. Split if the name would become vague. **Level of detail:** named capabilities, not user stories or tasks.
3. **The clickable mockup is not the MVP.** Mockup scope tests the risky or unclear paths (comprehension, usefulness, core flow). It need not include everything in MVP scope; it may include something later if that is where the uncertainty is. Do not put the whole product in the clickable mockup.
4. **MVP whole enough, not merely small.** The first product must complete a recognisable outcome. Do not leave a load-bearing hole. Do not try to include everything.
5. **Scopes by proposal.** Infer epics and mockup / MVP / later from answers and Understand; confirm or edit. Do not open with laundry lists or scoring workshops.
6. **Stay in Scope.** No stories, no Figma screens, no architecture.

### Flow

1. Orient once (phase purpose and what comes next), then clarifying rounds from [questionbank.md](questionbank.md) via the questioning skill.
2. If answers are vague, ask for one concrete example next.
3. Propose inferred epics plus mockup scope, MVP scope, and later (including the first piece of the MVP to implement); one confirmation ask.
4. Draft `epics.md` when the checklist below is met; present the summary.
5. **Gap check (before accept):** Name one or two thin spots that still belong in Scope (not Mockup/Foundation). One ask: anything to add there or elsewhere in Scope? Incorporate, then continue.
6. One accept ask for Scope.

### Ready to draft artifacts when

- Named epics cover every in-scope primary journey, each a user-recognisable capability (not a story, not a technical layer), with journey links
- MVP scope can complete a recognisable outcome without a load-bearing hole
- Mockup scope has a learning purpose and is narrower than the whole MVP
- Every epic is in MVP scope or later; mockup membership is named where it applies
- The first piece of the MVP to implement after Mockup is named
- Hard constraints from Understand still hold

If those are still missing, keep asking: do not invent them. Epics and scopes are proposed by you, then confirmed.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Mockup; Milestone → Mockup; refresh Summary / Decisions / Open from the scopes; add Scope under Concluded); follow writing-docs **Root README** When for this phase. Do not advance without confirmation.
