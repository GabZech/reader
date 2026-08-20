# Build question bank

Clarifying **content** for Build. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse journeys, dummy, epics, and Foundation; build this epic, do not restart discovery.

Increments here are **vertical slices**: a thin path the client can try on the local product, cutting across interface and data as needed. Not user stories, not a task list, not a layer (all of one technical part, then all of another).

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Epic choice | Which epic this loop covers | Name the epic after showing the catalog and a recommendation |
| Epic boundary | In/out of this epic | Name what this loop includes vs what waits for another epic |
| Increment map | Build order | Name ordered tryable slices and which is first |
| Slice analysis | This increment’s real shape | Name the job, its reverse, where the result is visible, how the flow ends, and identifying corrections |
| Current increment | Remaining gaps | Fill only lived facts that analysis could not settle |
| Open unknowns | Clarifying-answers; Deploy | List leftover risk this epic will not settle |

Trying an increment is **not** a cluster. That ask lives in the phase skill after the slice is running. A request to ship is **not** a cluster; it enters Deploy from the phase skill.

Epic choice, epic boundary, increment map, and slice analysis are **propose-and-confirm**, not open lists.

### 1. Epic choice (propose, then confirm)

Show the defined catalog in the message (name, MVP or later, Depends on, already built or not). A link to `epics.md` is not enough.

- Recommend which loop to start: Scope's named first piece of the MVP if still unbuilt and its Depends on is satisfied; otherwise remaining MVP work by Depends on
- One confirm before in/out or increment map
- Skip when resuming that epic with work already underway (including return from a mid-epic Deploy), not merely because the epic folder exists

### 2. Epic boundary (propose, then confirm)

Infer from the named epic's In/out, Done when, and Depends on, plus dummy and Foundation leftovers. If those fields are missing, propose start/change/stop in or out now.

- What must work or this epic is not usable
- What waits for another epic even if related
- Live resources this epic still has to stand up vs what Foundation already proved
- If a missing reverse is a different job, reopen Scope rather than stretching this loop

### 3. Increment map (propose, then confirm)

- Ordered vertical slices, each tryable alone on the local instance
- Which is first: prefer high value and low complexity unless a leftover joint blocks the rest
- Which slices the client should try on a phone or other device (still the local instance)

After an increment is tried, the map may shrink or split; confirm the change. Do not silently grow into another epic.

### 4. Slice analysis (propose, then confirm)

When a slice is named (map or client request), infer the user-recognised job it must finish. Infer from journeys, dummy, Foundation, and what already ships. Show the set; recommend; one confirm. Do not ask the client to invent this inventory.

- The job this increment finishes: may be larger than the named ask; still one job, not several
- Reverse of the state change this slice makes
- Where the result is visible; which already-shipped screens must change
- How the flow ends: clear outcome, what happens next, way back or cancel
- Corrections to identifying details the user supplied on this slice
- What is a different job or another epic and stays out

### 5. Current increment

Ask only lived facts this slice still needs after slice analysis. How something enters, waits, counts, empty states, duplicates. Do not pre-ask the rest of the map.

- What happens when the input is missing, invalid, or already exists, if that can happen on this slice
- What “nothing has arrived yet” means if this slice depends on an outside system

### 6. Open unknowns

- What this epic will carry as explicit remaining risk into Deploy
- What a later epic must own

## Question direction

- Prefer the next tryable path over completeness of the epic
- Never solicit which epic to build, the increment inventory, or slice companions as an open list; propose them
- Never start coding from the wording of a client ask or map item until slice analysis is confirmed
- Never ask the client to write stories, EARS, or a design

## Boundaries

- No `requirements.md`, `design.md`, or `tasks.md`
- Completeness of this job, not a spec of the epic
- No overview-doc rewrites (Deploy)
- No production deploy (Deploy)
- No stack or whole-system redesign (Foundation)
- No other epics

## Boundary with the next phase

Deploy is entered when the increment map is done, or when the client asks to ship the last signed-off state. Deploy puts that revision on the production host, smokes the live path if hosted, and aligns living docs with what is now live. Do not write those docs here. If the client volunteers overview wording early, note it under clarifying-answers and reuse in Deploy.
