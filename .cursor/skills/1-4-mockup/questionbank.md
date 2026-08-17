# Mockup question bank

Clarifying **content** for Mockup. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse Scope; design the dummy, do not restart epic packaging.

The **mockup** is a clickable dummy of the solution, not built software and not the MVP. Tool choice (HTML, Penpot, Figma) is the first ask in the phase skill, not a cluster here.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Devices and surfaces | Screen list | Name which device(s) the dummy is walked on, and which is primary |
| How finished it should look | Visual approach | Name the lowest visual finish that still answers Scope’s learning questions |
| Labels and sample content | Screens | Name whether wording should be realistic enough to judge “is this obvious,” vs placeholder |
| States that must exist | Screen list | Name empty, first-use, typical, and error states the walkthrough cannot skip |
| What “clickable” means | Links in the dummy | Name which taps go somewhere vs which are scenery |

The screen inventory is **not** a question cluster. After the rounds above, infer it and confirm (see below).

Setup and self-review are **not** clusters. Feedback rounds are not a cluster: the client walks the dummy and says what is confusing.

### 1. Devices and surfaces

Reuse Understand constraints and Scope mockup paths.

- Which device is the walkthrough primarily on?
- Does any mockup-scope path need a second surface, or can that wait?

### 2. How finished it should look

Fidelity is independent for visuals, clicks, and words. Prefer the lowest visual finish that still lets someone judge the learning questions. Polished pictures pull attention to colour and type.

- What would make the dummy look “finished” in a way that would distract from the learning questions?
- Is mid-fidelity (real layout, plausible spacing, little branding) enough?

### 3. Labels and sample content

18F: real content, not lorem, when the question is whether people understand the design.

- Which labels must be realistic or the learning questions cannot be answered?
- Where is placeholder copy acceptable?

### 4. States that must exist

Only states the walkthrough cannot skip. Do not inventory every empty and error screen in the product.

- What does first-use vs a typical filled session look like on the mockup paths?
- Which empty or error states would make the learning questions dishonest if omitted?

### 5. What “clickable” means

Simple On click → next screen. Paid prototype logic (variables, conditionals) is out of scope.

- Which controls on the learning-question screens must actually go somewhere?
- Which chrome is scenery (say so if tapped)?

### Screen list and visual approach (propose, then confirm)

Do not ask the client to invent the screen inventory. Near the end, from Scope mockup paths and the rounds above, draft:

- Named screens (or HTML pages) covering those paths, including must-have states
- Which taps are linked
- Visual approach (usually mid-fidelity, little branding)

Present that package and ask once whether to confirm or adjust. Then build.

After the last walkthrough, propose what the dummy settled vs what we still carry as risk; confirm; fold into `mockup.md`.

## Question direction

- Prefer what the walkthrough must let us learn over visual wish-lists or extra screens.
- Prefer realistic labels where “is it obvious?” is the question.
- Never solicit the screen inventory with an open list; propose it for confirmation instead.

## Boundaries

- No user stories, acceptance criteria, or product stack (Foundation).
- Do not expand mockup scope; if a path is missing from Scope, reopen Scope.
- Do not rewrite as-is journeys; the dummy is the as-should picture.
- Do not call the dummy an MVP or the product.
- HTML dummy: no framework, no product package.json, no backend.
- Later product work is not a Kickoff non-goal; it waits for Foundation and SPECs.

## Boundary with the next phase

After Mockup accept, Foundation designs the system once and builds its skeleton: architecture, stack, application shell, operational basics. Do not choose stack here. If the client volunteers tech preferences, note them under history and reuse in Foundation.
