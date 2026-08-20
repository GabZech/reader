# Mockup question bank

Clarifying **content** for Mockup. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse Scope; design the dummy, do not restart epic packaging.

The **mockup** is a clickable dummy of the solution, not built software and not the MVP. It has two standing goals: the Scope mockup paths (and named failures) are walkable, and overall look on those paths is compatible with how the client envisions the app. Tool choice (HTML, Penpot, Figma) is the first ask in the phase skill, not a cluster here.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Devices and surfaces | Screen list | Name which device(s) the dummy is walked on, and which is primary |
| Overall look | Visual approach | Name enough visual character that the client can accept or reject the overall UI on the mockup-scope screens |
| Labels and sample content | Screens | Name whether wording should be realistic enough to judge “is this obvious,” vs placeholder |
| States that must exist | Screen list | Name empty, first-use, typical, and error states the walkthrough cannot skip |
| What “clickable” means | Links in the dummy | Name which taps go somewhere vs which are scenery |

The screen inventory is **not** a question cluster. After the rounds above, infer it and confirm (see below).

Setup and self-review are **not** clusters. Feedback rounds are not a cluster: after each shared step, one ask (does this look right, or is something needed on this step missing). When the client says the step is good, the phase skill names the next journey and starts it. Do not batch remaining journeys.

### 1. Devices and surfaces

Reuse Understand constraints and Scope mockup paths.

- Which device is the walkthrough primarily on?
- Does any mockup-scope path need a second surface, or can that wait?

### 2. Overall look

Visual finish, clicks, and words stay independent. The dummy must look real enough to judge overall look on the mockup-scope screens (layout, density, chrome, visual character). It is not a design-system interview and not a polish pass.

- What does the dummy need to show so you can judge whether the overall look is right for the mockup-scope journeys?
- Where should visual finish stay unfinished so we do not chase detail?

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

Do not ask the client to invent the screen inventory or a design system. Near the end, from Scope mockup paths and the rounds above, draft:

- Named screens (or HTML pages) covering those paths, including must-have states
- Which screen is first (entry / shell) and in what order the mockup-scope journeys will be walked (prerequisites first)
- Which taps are linked
- Visual approach: overall look for those screens (coherent layout, density, chrome, and visual character). Scenery and later-scope chrome stay low-finish.

Present that package and ask once whether to confirm or adjust. Then build the first screen only.

After the last signed-off journey, propose what the dummy settled vs what we still carry as risk (journeys and look); confirm; fold into `mockup.md`.

## Question direction

- Prefer learning questions and overall look on in-scope screens over extra screens and visual polish.
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

After Mockup accept, Foundation designs the system once and builds a walking skeleton: architecture, stack, operational basics, and a thin end-to-end slice that follows the accepted look. Tradeoffs are confirmed before product code. Do not choose stack here. If the client volunteers tech preferences, note them under history and reuse in Foundation.
