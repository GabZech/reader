---
name: 1-4-mockup
description: >-
  Runs the Mockup phase: a clickable dummy of the solution before product
  code, with tool choice, setup checks, agent self-review, and feedback
  iteration. Use when roadmap says Mockup, or after Scope is accepted.
---

# Mockup

Make the mockup-scope journeys a clickable dummy before anything is built, then iterate on feedback. This is not built software; Foundation comes after.

## Entry

- Scope is accepted (`docs/product-definition/epics.md` names mockup paths and learning purpose)

## Artifacts

- Clickable dummy in the tool chosen at phase start (HTML folder, Penpot file, or Figma file)
- `docs/product-definition/mockup.md` (tool, how to open, paths walkable, what we learned, what is still open)
- `docs/history/discovery/04-mockup/` (setup notes, feedback rounds: never client prompts)
- HTML only: throwaway pages under `docs/mockup/` (not the product)

## Do

**Include:**
- First ask: which dummy tool. Show all three (HTML, Penpot, Figma), one-line difference each, and a recommendation inferred from **this** project's locked constraints, devices, cost, learning questions, and whether a paid Figma Full/Dev seat already exists. One question; wait.
- Setup for the chosen tool every time the phase starts or resumes: [setup.md](setup.md). Stop until the smoke test passes.
- Self-review: screenshot or export each new or changed screen, critique against the confirmed screen list, fix, then share. Do not present the dummy until that pass is done, or until you state that capture is blocked.
- Clarifying questions via the **questioning** skill. **What to ask:** [questionbank.md](questionbank.md). Skip what Scope or this conversation already answered.
- Screen list and visual approach inferred from Scope mockup paths; confirm, then build; walkthrough; iterate.
- Record tool, open instructions, and learnings in `mockup.md` per writing-docs.

Do not write the product application or choose the product stack. An HTML dummy is throwaway pages. Do not expand mockup scope. Do not rewrite personas or epics unless the dummy contradicts them (then reopen Scope).

**Human role:** Choose the tool; walk the dummy; say what is confusing; accept when the learning purpose is met or remaining risk is explicit.

## Clarifying questions

Goal: gather only what the dummy needs. Defer stories to Requirements; defer stack to Foundation.

### Principles

1. **Reuse Scope.** Walk the locked mockup paths for the locked learning purpose. Reopen Scope only if the dummy contradicts those locks.
2. **Lowest fidelity that answers the question.** Visual finish, click-through, and wording are independent. Match them to what Scope said we must learn.
3. **Pilot before the walkthrough.** Capture, critique, fix; then share.
4. **Simple clicks.** On click → next screen. Dead ends say they are not in this dummy.
5. **Screen list by proposal.** Infer from Scope and the clusters; confirm. Do not ask the client to invent the inventory.
6. **Stay in Mockup.** No stories, no architecture, no product application.

### Flow

1. Orient once (clickable picture, not software; Foundation next).
2. Tool-choice ask (three options, differences, inferred recommendation). Skip only if `mockup.md` already records a tool and this is a resume in that tool.
3. Setup check for the chosen tool. Stop until smoke test passes.
4. Clarifying rounds from [questionbank.md](questionbank.md).
5. Propose screen list + visual approach; one confirm.
6. Build; self-review each screen or small batch; share only after that pass.
7. Client walkthrough and revise until the learning purpose is met or remaining risk is accepted.
8. Draft `mockup.md` and history; gap check; accept.

### Ready to draw when

- Mockup-scope paths and learning purpose are named
- Tool is chosen and setup smoke test passed
- Devices, fidelity, and must-have states are clear
- Screen list is confirmed

### Ready to show the client when

- Those paths are walkable in the dummy
- Agent has visually reviewed the screens, or has said why capture failed
- Dead ends vs linked taps are known

### Ready to accept when

- Client has walked the paths
- `mockup.md` is honest about what the dummy settled vs cannot prove

If those are missing, keep asking or building: do not invent them.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Foundation; refresh Summary / Decisions / Open; add Mockup under Concluded with links to `mockup.md` and history); add `mockup.md` under Product Definition in `docs/README.md`. Do not offer a README refresh. Do not advance without confirmation.
