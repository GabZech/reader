# Scope question bank

Clarifying **content** for Scope. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse Understand answers; decide, do not restart.

Epics here are **named capabilities** at a coarser level of detail than Build increments. Each traces to at least one accepted journey. Increments wait for Build; screens wait for Mockup; stack waits for Foundation.

The **mockup** is a clickable dummy of the solution, not built software. Which tool (HTML, Penpot, Figma) is chosen at Mockup start.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| What the MVP must achieve | MVP scope | Name which journey outcomes must work or the first product is not worth using |
| What the clickable mockup is for | Mockup scope | Name what the clickable walkthrough must let us learn, and which paths must be walkable for that |
| What cannot stand alone | Epic packaging and both scopes | Name what cannot ship or be walked through alone, and which journeys are one job vs two |
| What we are still unsure about | Mockup scope; history | Name the riskiest remaining assumptions, and what the clickable mockup should settle vs what we will carry |

Epics and the three scopes are **not** a question cluster. After the rounds above, infer them and confirm (see below).

### 1. What the MVP must achieve

Outcomes the first product cannot do without, not a feature list. Prefer “not worth using without” over “what would you like.”

- Which journey outcomes must work or the first product is not worth using?
- What would make a first product feel unfinished in a way that matters (not polish)?
- If only one path could work end to end, which one?

### 2. What the clickable mockup is for

Learning, not a preview of the whole MVP. Focus on what is uncertain or easy to get wrong.

- What needs to be clickable to know the solution is on the right track?
- Which parts feel most uncertain, or most likely to go wrong in the design?
- Which paths must be walkable in the dummy for that, even if they are not in the MVP?

### 3. What cannot stand alone

How people doing the job see it, not technical layers.

- Where would it feel broken if one capability shipped without another?
- Do any journeys share a capability so they should be one epic?
- Do any look separate but people treat them as one job?

### 4. What we are still unsure about

Reuse Understand unknowns. The clickable mockup tests the riskiest remaining assumptions; do not try to settle everything.

- What are we still assuming that, if wrong, would change the MVP?
- What should the clickable mockup settle vs what we will accept as risk?

Park screen design and deep research design; capture the unknown so Mockup or later phases can use it.

### Epics and scopes (propose, then confirm)

Do not ask the client to invent the epic list or “what to leave out of the MVP.” Near the end, from journeys, constraints, and the rounds above, draft:

- Named epics (recognisable capabilities, each linked to at least one journey)
- Mockup scope (paths plus learning purpose)
- MVP scope vs later
- The first piece of the MVP to implement after Mockup

Present that package and ask once whether to confirm or adjust. Fold the confirmed list into `epics.md`.

## Question direction

- Prefer outcomes the first product cannot do without, what cannot stand alone, and uncertainty over feature wish-lists, scoring, or stack.
- Prefer a first product that still reaches a recognisable result over disconnected pieces.
- Never solicit MVP exclusions or epic lists with open questions; propose them for confirmation instead.

## Boundaries

- No user stories, acceptance criteria, or story maps in this phase.
- No dummy screens or as-should walkthroughs (Mockup).
- No stack or architecture (Foundation).
- Do not invent primary journeys; if a path is missing, reopen Understand.
- Later is deferred on purpose, and is not a Kickoff non-goal.
- Do not call the clickable dummy a prototype or an MVP.

## Boundary with the next phase

After Scope accept, Mockup makes the mockup-scope journeys a clickable dummy, settles overall look on those paths, and iterates on feedback. Do not design those screens here. If the client volunteers layout or interaction detail early, note it under history and reuse in Mockup.
