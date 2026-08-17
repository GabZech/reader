# Kickoff question bank

Clarifying **content** for Kickoff. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Motivation & timing | Problem, vision | Say why this work exists and why now |
| Who & impact | Problem, vision | Name who is affected and how (high level) |
| Problem / opportunity | Problem statement | Write one focused problem without a solution inside it |
| Status quo | Problem, vision | Describe today’s workaround and what already works |
| Desired outcomes | Vision, metrics | Separate outcomes for people affected from commissioning-side outcomes |
| Success measures | Metrics | Name outcome signals, not delivery tasks |
| Assumptions & unknowns | History notes; later phases | List what must be learned or proved next |

Non-goals are **not** a question cluster. After the rounds above, infer them and confirm (see below).

### 1. Motivation and timing

- Why are we doing this work?
- What are we trying to decide or enable?
- What triggered this now (event, pain spike, deadline, opportunity)?
- What happens if we do nothing for six months?

### 2. Who and impact (Kickoff-depth only)

- Who feels this problem day to day?
- Who else is affected (operators, buyers, bystanders)?
- How does the problem show up for them (time, money, risk, frustration, missed opportunity)?

Defer detailed persona traits, contexts, and edge cases to Understand. Do not ask who is out of focus — infer that later for the non-goals proposal.

### 3. Problem / opportunity (5 Ws)

Aim for a brief problem statement: background, people affected, impact if unsolved. Opportunity framing is fine (“gap between today and desired state”).

- What is going wrong (or what opportunity is underserved)?
- Where does this problem show up?
- When does it typically occur?
- Why does it matter to the people affected?
- Why does it matter to whoever is commissioning this?

Avoid embedding “so we will build X” in the problem itself.

If the conversation starts from a solution, pick **one** of: What job is that meant to do? What fails today without it? How do people cope now?

### 4. Status quo and alternatives

- How is this handled today (tools, spreadsheets, people, ignoring it)?
- What has already been tried?
- What worked a little from those attempts?
- What else has been considered, including doing nothing?

Prefer specific past behaviour over opinions of the idea.

### 5. Desired outcomes

- If this succeeds, what is different for the people affected, in concrete terms?
- What outcomes does the commissioning side need (revenue, time saved, risk reduced, learning)?
- What would “good enough for a first release” feel like?
- How does that differ from the long-term ambition?

### 6. Success measures

Write metrics that would still count as a win if achieved by a different implementation.

- How will we know the problem got better?
- What would we measure (behaviour, time, error rate, completion, retention, cost)?
- Do we have a baseline today?
- If not, should the first metric be “establish baseline for X”?
- What would count as failure or “wrong problem”?

Avoid vanity or output metrics.

### 7. Assumptions and what to learn

- What are we assuming is true about users, demand, or feasibility?
- What do we need to learn or prove before we invest heavily?
- What difficulties or rabbit holes do you already foresee?

Park deep research design for later phases; capture the unknowns so Understand / Scope can use them.

### Non-goals (propose, then confirm)

Do not ask the client to invent exclusions or “what to leave out.” Near the end, from everything already said, draft a short list of likely non-goals: adjacent problems, audiences not in focus, tempting extras, and any hard must-nots the answers already imply. Present that list and ask once whether to confirm or adjust. Fold the confirmed list into `vision.md`.

## Question direction

- Prefer past and present behaviour, concrete situations, and outcomes over hypotheticals, feature wish-lists, or opinions of the idea.
- Prefer outcome measures over delivery or stack choices (stack waits for Foundation).
- Never solicit non-goals with open exclusion questions; propose them for confirmation instead.

## Boundaries

- Keep the problem statement free of solutions; if several unrelated problems appear, pick a primary focus and park the rest as proposed non-goals.
- Kickoff “who” stays headline-level; personas and journeys belong in Understand.
- Architecture waits for Foundation.
- Metrics track changed outcomes, not shipping volume.
- Treat compliments and vague enthusiasm as weak signal; push for costs, workarounds, and specifics (questioning skill).
- Confirmed non-goals required before drafting.

## Boundary with the next phase

After Kickoff accept, Understand deepens personas, journeys, and cross-cutting constraints. Do not write those artifacts here. If the client volunteers journey detail early, note it under history and reuse in Understand.
