# Scope question bank

Clarifying **content** for Scope. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Sole client = the user. Project-agnostic: reuse Understand answers; decide, do not restart.

Epics here are **named capabilities** at a coarser level of detail than user stories. Each traces to at least one accepted journey. Prototype scope, MVP scope, and later wait for the agent’s proposal after these rounds. User stories and acceptance criteria wait for Requirements. Screens wait for Prototype. Stack waits for Foundation.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| What the MVP must achieve | MVP scope | Name which journey outcomes must work or the first product is not worth using |
| What the prototype is for | Prototype scope | Name what the clickable walkthrough must let us learn, and which paths must be walkable for that |
| What cannot stand alone | Epic packaging and both scopes | Name holes: what cannot ship or demo alone, and which journeys are one job vs two |
| What we are still unsure about | Prototype scope; history | Name the riskiest remaining assumptions, and what Prototype should settle vs what we will carry |

Epics and the three scopes are **not** a question cluster. After the rounds above, infer them and confirm (see below).

### 1. What the MVP must achieve

Load-bearing outcomes, not a feature list. Prefer “not worth using without” over “what would you like.”

- Which journey outcomes must work or you would not bother using this?
- What would make a first product feel unfinished in a way that matters (not polish)?
- If only one path could work end to end, which one?

### 2. What the prototype is for

Learning, not a preview of the whole MVP. Focus on what is uncertain or easy to get wrong.

- What do you need to see clickable to know we are on the right track?
- Which parts feel most uncertain, or most likely to go wrong in the design?
- Which paths must be walkable in Figma for that, even if they are not in the MVP?

### 3. What cannot stand alone

Holes and packaging. How the user sees the job, not technical layers.

- Where would it feel broken if one capability shipped without another?
- Do any journeys share a capability so they should be one epic?
- Do any look separate but you treat as one job?

### 4. What we are still unsure about

Reuse Understand unknowns. Prototype tests the riskiest remaining assumptions; do not try to settle everything.

- What are we still assuming that, if wrong, would change the MVP?
- What should the prototype settle vs what we will accept as risk?

Park screen design and deep research design; capture the unknown so Prototype or later phases can use it.

### Epics and scopes (propose, then confirm)

Do not ask the client to invent the epic list or “what to leave out of the MVP.” Near the end, from journeys, constraints, and the rounds above, draft:

- Named epics (user-recognisable capabilities, each linked to at least one journey)
- Prototype scope (paths plus learning purpose)
- MVP scope vs later
- The first piece of the MVP to implement after Prototype

Present that package and ask once whether to confirm or adjust. Fold the confirmed list into `epics.md`.

## Question direction

- Prefer load-bearing outcomes, holes, and uncertainty over feature wish-lists, scoring, or stack.
- Prefer a thin path that still reaches a recognisable result over a pile of disconnected pieces.
- Never solicit MVP exclusions or epic lists with open questions; propose them for confirmation instead.

## Boundaries

- No user stories, acceptance criteria, or story maps in this phase.
- No Figma screens or as-should walkthroughs (Prototype).
- No stack or architecture (Foundation).
- Do not invent primary journeys; if a path is missing, reopen Understand.
- Later is deferred on purpose, not a junk drawer, and is not a Kickoff non-goal.
- Prototype scope is for learning; do not call the Figma work an MVP.

## Boundary with the next phase

After Scope accept, Prototype makes the prototype-scope journeys clickable in Figma and iterates on feedback. Do not design those screens here. If the client volunteers layout or interaction detail early, note it under history and reuse in Prototype.
