# Understand question bank

Clarifying **content** for Understand. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse Kickoff answers; deepen, do not restart.

Journeys here are **overall use cases** at discovery level of detail: named end-to-end scenarios with actor, goal, trigger, steps today, outcome, costly edges, and **Wanted**. User stories and acceptance criteria wait for Requirements.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Persona depth | Personas | Name who is in focus, their goals, contexts, and what success or failure looks like for them |
| Situations and rhythm | Personas, journeys | Say when, where, and how often the work happens, and what starts or ends a session |
| Journey inventory | Journeys | List the primary end-to-end scenarios by name, in chronological order of occurrence (use-case level of detail) |
| Journey walkthrough | Journeys | Narrate each primary journey: trigger → steps today → outcome, friction, and **Wanted** if they volunteer a change |
| Edges and recovery | Journeys | Name costly failure, empty, late, or wrong cases and what people do then |
| Cross-cutting constraints | Constraints | Separate hard vs soft limits that are not one journey |
| Open unknowns | History notes; later phases | List what still blocks honest mockup / MVP / later scope |

### 1. Persona depth

Kickoff “who” stays headline-level; deepen situation and goals here. Prefer roles and contexts over demographic portraits.

- Who is trying to get this done day to day?
- What are they trying to achieve, in their words?
- What does a good outcome look like for them? A bad one?
- What skills, access, or support needs shape how they work (devices, connectivity, assistance)?
- Who else is affected but is not the primary actor (operators, buyers, bystanders)? Ask only if Kickoff left that thin.

### 2. Situations and rhythm

- Walk through a typical time when this problem shows up.
- Where are they, and what device or channel are they on?
- How often does this happen, and what starts or ends the session?
- What else competes for attention in that moment?

### 3. Journey inventory (overall use cases)

Name distinct goals worth following end to end. Stop at scenario level of detail; do not split into user stories.

- What distinct goals would we need to follow end to end to cover the vision?
- Which of those are central vs occasional?
- For each, who is the actor and what kicks it off?
- In what order do these typically occur, including setup before the sessions it enables?

### 4. Journey walkthrough (per primary journey)

Prefer critical incidents and chronological follow-ups over generic funnel templates. Walk primary journeys in the chronological order from the inventory. Current-state first; do not design the to-be path here. If they volunteer what should change, record it as **Wanted** on that journey; do not rewrite the steps.

- Tell me about the last time this was done.
- What were the steps from trigger to done?
- Which tools, people, or channels sat on the path?
- Where did it feel smooth? Where did it stall or need a workaround?
- What were they thinking or worrying about at the sticky points?

### 5. Edges and recovery

- Tell me about a time it went wrong or almost failed.
- What do people do when information is missing, late, wrong, or incomplete?
- Which rare cases still matter because the cost of failure is high?

### 6. Cross-cutting constraints

Do not open with “what are your constraints?” Near the end, infer hard vs soft **limits** from prior answers and Kickoff (legal, contractual, policy, safety, legacy systems, processes, data ownership and retention, privacy, cost, reliability, integrations, must-nots). Present a short list and ask once whether to confirm or adjust. Probe only thin spots. Do not file product wishes here; those belong as **Wanted** on the journey they would change.

- What rules or obligations cannot be bent?
- What existing systems, formats, or processes must be lived with for now?
- What data ownership, retention, or privacy expectations apply?
- What cost, reliability, or operating limits would make the effort not worth it?
- What must the solution never do?

Mark which limits are fixed (hard) vs changeable (soft). Soft constraints are candidates to change later, not silent workarounds to bake in.

### 7. Open unknowns

- What are we still assuming about users or behaviour that we have not seen in a concrete example?
- What would we need to learn before Scope can set mockup, MVP, and later honestly?

Park deep research design; capture the unknown so Scope or later phases can use it.

## Question direction

- Prefer past and present behaviour, concrete situations, and critical incidents over hypotheticals, feature wish-lists, or opinions of the idea.
- Prefer current-state journeys before to-be design.
- Prefer outcome and friction detail over delivery tasks, stack, or story breakdowns.
- Never solicit constraint laundry lists with open exclusion questions; propose inferred constraints for confirmation instead.

## Boundaries

- No user stories, acceptance criteria, or story maps in this phase.
- No epic packaging and no mockup / MVP / later scope (Scope owns those).
- No stack or architecture (Foundation).
- Do not invent primary journeys the client did not recognise; if Scope needs a missing path, reopen Understand.
- Personas stay qualitative: goals, context, motivations. Approaches and steps live on journeys.

## Boundary with the next phase

After Understand accept, Scope turns accepted journeys into epics and decides mockup / MVP / later. Do not pre-assign those scopes here. If the client volunteers scope preferences early, note them under history and reuse in Scope.
