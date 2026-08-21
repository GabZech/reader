# Plan question bank

Clarifying **content** for Plan. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse journeys, dummy, epics, and Foundation; plan this epic, do not restart discovery.

Increments here are **vertical slices**: a thin path the client can try on the local product, cutting across interface and data as needed. Not user stories, not a task list, not a layer (all of one technical part, then all of another).

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Epic choice | Which epic this loop covers | Name the epic after showing the catalog and a recommendation |
| Epic boundary | In/out of this epic | Name what this loop includes vs what waits for another epic |
| Increment map | plan.md increment order | Name every ordered tryable slice for the whole epic and which is first |
| Per-increment shape | plan.md job | Name the job, its reverse, where the result is visible, how the flow ends |
| Dependencies | plan.md dependencies | Name what each increment needs from earlier increments, the skeleton, or outside systems, and the order that forces |
| Failure modes | plan.md failure modes | Name what can go wrong on each increment and what should happen instead |
| Test approach | plan.md test approach | Name what proves each increment works: automated test or manual try |
| Reversibility | plan.md reversibility | Name the fallback for anything on this increment that is hard to undo |
| Open risk | plan.md risk register | List what this epic will carry as explicit remaining risk |

A request to start building is **not** a cluster; it is the Gate. A request to ship is **not** a cluster; it belongs to Deploy.

Epic choice, epic boundary, increment map, and per-increment shape are **propose-and-confirm**, not open lists.

### 1. Epic choice (propose, then confirm)

Show the defined catalog in the message (name, MVP or later, already built or not). A link to `epics.md` is not enough.

- Recommend which loop to start: Scope's named first piece of the MVP if still unbuilt; otherwise remaining MVP work by dependency
- One confirm before in/out or the increment map
- Skip when resuming that epic with a plan already underway (including return from a mid-epic Deploy), not merely because the epic folder exists

### 2. Epic boundary (propose, then confirm)

Infer from the named epic, first-product cut, dummy, and Foundation leftovers.

- What must work or this epic is not usable
- What waits for another epic even if related
- Live resources this epic still has to stand up vs what Foundation already proved

### 3. Increment map (propose, then confirm)

- Ordered vertical slices covering the whole epic, each tryable alone on the local instance
- Which is first: prefer high value and low complexity unless a leftover joint blocks the rest
- Which slices the client should try on a phone or other device (still the local instance)
- Which increments could ship on their own if the client wants a mid-epic Deploy

Building may still shrink or split a slice after trying it; confirm the change there. Do not silently grow the map into another epic.

### 4. Per-increment shape (propose, then confirm)

For each increment, infer the user-recognised job it must finish. Infer from journeys, dummy, Foundation, and what already ships. Show the set; recommend; confirm.

- The job this increment finishes: may be larger than a client's one-line request; still one job, not several
- Reverse of the state change this slice makes
- Where the result is visible; which already-shipped screens must change
- How the flow ends: clear outcome, what happens next, way back or cancel
- What is a different job or another epic and stays out

### 5. Dependencies (propose, then confirm)

- What this increment needs from an earlier increment in this epic
- What it needs from the Foundation skeleton that is not yet stood up (a live credential, a connected joint)
- What it needs from an outside system, and what happens if that system is not ready when this increment is built
- Ordering the map must respect because of these dependencies

### 6. Failure modes and edge cases (propose; ask only the lived facts the client alone knows)

- What happens when input is missing, invalid, duplicate, or already exists
- What "nothing has arrived yet" means when this increment depends on an outside system
- What happens on partial completion (interrupted mid-way) or concurrent use, where this product's use pattern makes that possible
- Which of these the client has an opinion on (a lived fact) vs which the agent should just handle sensibly and only report (propose, do not ask)

### 7. Test approach (propose, then confirm)

- Which behaviour on this increment needs an automated test vs is cheaper to check by trying it locally
- What running check (test, build, screenshot) will tell Build the increment is done, not just "looks done"

### 8. Reversibility (propose; only where something is actually hard to undo)

- For a schema change, external setup, or irreversible delete on this increment: what the fallback is if it ships and turns out wrong
- Skip this cluster entirely for increments with nothing hard to undo; do not manufacture a rollback question for a trivial change

### 9. Open risk

- What this epic will carry as explicit remaining risk into Build and Deploy
- What a later epic must own instead

## Question direction

- Prefer thinking in failure before success: ask what breaks before asking what a good day looks like
- Never solicit the increment map, dependency graph, or failure-mode list as an open exercise; propose them
- Never ask the client to write stories, EARS, requirements, or a design
- Ask reversibility only where something is actually hard to undo

## Boundaries

- No `requirements.md`, `design.md`, or `tasks.md`
- No client review of `plan.md` as a document, except when an item is high-stakes or they ask
- Completeness of the plan for this epic, not code
- No production deploy (Deploy)
- No stack or whole-system redesign (Foundation)
- No other epics

## Boundary with the next phase

Build reads `plan.md` and implements against it, one increment at a time. Build does not redo epic choice, boundary, or the map; it may split or shrink a slice after trying it, with confirm. If Build finds the plan cannot be honoured, it returns here to update `plan.md` and reconfirm, rather than quietly deciding on its own.
