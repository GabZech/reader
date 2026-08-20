# Build question bank

Clarifying **content** for Build. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse journeys, dummy, epics, and Foundation; build this epic, do not restart discovery.

Increments here are **vertical slices**: a thin path the client can try on the real product, cutting across interface and data as needed. Not user stories, not a task list, not a layer (all of one technical part, then all of another).

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Epic boundary | In/out of this epic | Name what this loop includes vs what waits for another epic |
| Increment map | Build order | Name ordered tryable slices and which is first |
| Current increment | That slice | Fill only the gaps that slice needs |
| Open unknowns | Clarifying-answers; Document | List leftover risk this epic will not settle |

Trying an increment is **not** a cluster. That ask lives in the phase skill after the slice is running.

Epic boundary and increment map are **propose-and-confirm**, not open lists.

### 1. Epic boundary (propose, then confirm)

Infer from the named epic, first-product cut, dummy, and Foundation leftovers.

- What must work or this epic is not usable
- What waits for another epic even if related
- Live resources this epic still has to stand up vs what Foundation already proved

### 2. Increment map (propose, then confirm)

- Ordered vertical slices, each tryable alone
- Which is first: prefer high value and low complexity unless a leftover joint blocks the rest
- Which slices need the hosted or device surface to judge

After an increment is tried, the map may shrink or split; confirm the change. Do not silently grow into another epic.

### 3. Current increment

Ask only what this slice still needs. Lived facts: how something enters, waits, counts, empty states, duplicates. Do not pre-ask the rest of the map.

- What the client must be able to do when this slice is done
- What happens when the input is missing, invalid, or already exists, if that can happen on this slice
- What “nothing has arrived yet” means if this slice depends on an outside system

### 4. Open unknowns

- What this epic will carry as explicit remaining risk into Document
- What a later epic must own

## Question direction

- Prefer the next tryable path over completeness of the epic
- Never solicit the increment inventory with an open list; propose it
- Never ask the client to write stories, EARS, or a design

## Boundaries

- No `requirements.md`, `design.md`, or `tasks.md`
- No overview-doc rewrites (Document)
- No stack or whole-system redesign (Foundation)
- No other epics

## Boundary with the next phase

After Build accept, Document aligns living docs with what shipped, records leftover risk, and smokes the live path if hosted. Do not write those docs here. If the client volunteers overview wording early, note it under clarifying-answers and reuse in Document.
