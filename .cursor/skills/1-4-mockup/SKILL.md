---
name: 1-4-mockup
description: >-
  Runs the Mockup phase: a clickable dummy of the solution before product
  code, settling overall look on the mockup-scope journeys, with a guided
  first-screen then journey walkthrough, tool choice, setup checks, and
  agent self-review. Use when roadmap says Mockup, or after Scope is accepted.
---

# Mockup

Make the mockup-scope journeys a clickable dummy, and settle whether the overall look of those journeys is compatible with how the client envisions the app, before anything is built. Then iterate on feedback. This is not built software; Foundation comes after.

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
- Self-review per [setup.md](setup.md). Do not present a first-seen screen without a capture pass, or until you state that capture is blocked.
- Clarifying questions via the **questioning** skill. **What to ask:** [questionbank.md](questionbank.md). Skip what Scope or this conversation already answered.
- Screen list and visual approach inferred from Scope mockup paths; confirm; then a guided walkthrough: first screen, then each mockup-scope journey by name.
- Record tool, open instructions, learnings, and look direction in `mockup.md` per writing-docs.

Do not write the product application or choose the product stack. An HTML dummy is throwaway pages. Do not expand mockup scope: look feedback that adds journeys or later-scope screens reopens Scope; look feedback that changes layout or visual character of existing mockup screens stays here. Do not rewrite personas or epics unless the dummy contradicts them (then reopen Scope).

**Human role:** Choose the tool; judge one step at a time (first screen, then each journey); say whether it looks right and whether anything on that step is missing; say when a step is good enough to move on; hold small visual tweaks and anything outside the agreed journeys; accept when every step is signed off or remaining risk is explicit.

## Clarifying questions

Goal: gather only what the dummy needs. Defer stories to Requirements; defer stack to Foundation.

### Principles

1. **Reuse Scope.** Walk the locked mockup paths for the locked learning purpose. Overall look on those paths is always a Mockup goal, even if Scope did not name it as a learning question. Reopen Scope only if the dummy contradicts those locks.
2. **Fidelity that can be judged.** Visual finish, click-through, and wording are independent. Visual finish must be high enough to judge overall look (layout, density, chrome, visual character) on the mockup-scope screens; it is not a polish pass. Colour and type are part of overall look.
3. **Pilot when the visual risk warrants it.** Capture a first-seen screen before sharing it. Later, capture only if the change could look wrong; skip low-risk edits. Agent decides; do not ask.
4. **Simple clicks.** On click → next screen. Dead ends say they are not in this dummy.
5. **Screen list by proposal.** Infer from Scope and the clusters; confirm. Do not ask the client to invent the inventory.
6. **Stay in Mockup.** No stories, no architecture, no product application. No design system.

### Flow

1. Orient once: clickable picture, not software; Foundation next, and it will build the real shell from what we accept here. Name both goals: walk the agreed journeys and their named failures, and settle whether the overall look of those journeys is compatible. We will show the first screen, then each agreed journey by name, and not move on until you say the current step is good. On each step: say if the overall look is wrong or something needed is missing; hold small visual tweaks and anything outside the agreed journeys.
2. Tool-choice ask (three options, differences, inferred recommendation). Skip only if `mockup.md` already records a tool and this is a resume in that tool.
3. Setup check for the chosen tool. Stop until smoke test passes.
4. Clarifying rounds from [questionbank.md](questionbank.md).
5. Propose screen list + visual approach (overall look for those paths), which screen is first, and journey order (prerequisites first); one confirm.
6. Build only the first screen (entry / shell). Self-review that first-seen screen; share; one ask: does this look right, or is something needed on this screen missing. Iterate until the client says it is good.
7. Explicitly name the next mockup-scope journey, build what that path still needs, self-review first-seen screens, share, and ask the same. Do not start the next journey until the client says the current one is good. Repeat until every mockup-scope journey (with its named failures) is signed off.
8. Draft `mockup.md` and history; gap check; accept.

### Ready to draw when

- Mockup-scope paths and learning purpose are named
- Tool is chosen and setup smoke test passed
- Devices, visual approach, and must-have states are clear
- Screen list is confirmed

### Ready to show a step when

- The current step (first screen, or one journey) is walkable enough to judge
- Agent has captured first-seen or visually risky screens in this step, or has said why capture failed (low-risk follow-ups need no new capture)
- Dead ends vs linked taps for that step are known

### Ready to accept when

- Client has signed off the first screen and each mockup-scope journey (or remaining risk per step is explicit)
- `mockup.md` is honest about what the dummy settled vs cannot prove (journeys and look)

If those are missing, keep asking or building: do not invent them.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Foundation; refresh Summary / Decisions / Open; add Mockup under Concluded with links to `mockup.md` and history); add `mockup.md` under Product Definition in `docs/README.md`. Do not offer a README refresh. Do not advance without confirmation.
