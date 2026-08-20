# Foundation question bank

Clarifying **content** for Foundation. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Pick and adapt; do not read as a script. Reuse Understand constraints, Scope’s first MVP epic, and Mockup look; design the system, do not restart discovery.

A **walking skeleton** is a tiny, permanent, tested end-to-end slice that links the main architectural parts. It is not the first feature and not a throwaway dummy.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Landscape | Architecture, stack, operations | Name existing systems, data, accounts, cost ceiling, and languages or hosts already in play |
| Where it has to run | Architecture, stack | Name the surfaces it must run on, and whether it must work offline, on a local network, or only with internet |
| Who operates it | Operations, stack | Name who deploys and keeps it running, how much of that work is acceptable, and how much hosting control they can handle |
| What must stay in your hands | Architecture, stack | Name which data and jobs cannot live only in a vendor |
| How the outside world gets in | Architecture, operations | Name inbound paths the first product needs at “this must work,” not vendor choice |

Setup, toolchain, skeleton joints, and tradeoffs are **not** clusters. After the rounds above, infer the system package and confirm (see below). Tests, config, and a smoke test on the intended run path are checks the agent runs after that confirm.

### 1. Landscape

Reuse Kickoff, Understand, and any tech notes already in history.

- What systems, data stores, or accounts already exist that the new system must work with or could reuse?
- What is already paid for, and what is the cost ceiling for keeping this on?
- Are any languages, hosts, or stores already in play that a later change would be expensive?

### 2. Where it has to run

Reuse Understand devices and Mockup surfaces. Ask only what is still open.

- Which surfaces must the real app run on, and which is primary?
- Must it work without internet, on a local network, or only when hosted?

### 3. Who operates it

Hosting control must match who will actually keep it running.

- Who deploys and maintains it day to day?
- How much operational work is acceptable (updates, backups, incidents)?
- How much hosting control can they handle: a managed platform, or running their own machines?

### 4. What must stay in your hands

GOV.UK: keep full control of data you store. Infer from ownership constraints; confirm gaps.

- Which data must remain in client-controlled, exportable form?
- Which jobs must not depend on a vendor remaining available or cheap?

### 5. How the outside world gets in

Name the path at “this must work.” Do not pick the vendor here.

- What inbound paths does the first product need (mail, feeds, files, APIs, webhooks)?
- Which of those must already work for the skeleton to be honest, vs waiting for the first feature?

Park feature behaviour and story split; capture the unknown so Requirements can use it.

### System package and tradeoffs (propose, then confirm)

Do not ask the client to invent the stack or pick from a generic optimisation quiz. Near the end, from constraints and the rounds above, draft:

- Component map: what we build, what we attach as a vendor resource, what we reuse
- Architecture and stack (few parts; delay splits)
- How inbound paths work (the mechanism). Live credentials wait for the first feature unless the skeleton cannot run without them
- Skeleton joints: the tiny end-to-end function that connects those parts, and whether Foundation must prove a hosted deploy or local run is enough
- UI guidelines extracted from the accepted dummy: copy, do not redesign
- **Tradeoffs actually in tension:** each names what we optimize for, what we give up, and why that follows from the locks. Omit axes that are not in tension

Present that package and ask once whether to confirm or adjust. **No application code until confirmed.** If not aligned, revise the package; do not scaffold.

After the client judges the running skeleton, propose what Foundation settled vs what the first feature still has to prove; confirm; fold into the four docs.

When inferring tradeoffs, consider these tensions only if they apply (do not dump the list):

- Control vs convenience (own vs vendor)
- Who-operates burden vs hosting control
- Cost vs capability
- Ability to change later (open formats, less lock-in) vs delivery speed
- Compatibility with existing surfaces, data, and tools vs a clean new stack
- Local or offline use vs hosted availability
- Few parts vs splitting for scale or isolation

## Question direction

- Prefer landscape, operator, ownership, and inbound need over language preference, vendor shopping, or a speed-vs-control quiz.
- Prefer a simple whole that can evolve over premature splits.
- Never solicit the stack, component map, or tradeoff axes with an open list; propose them for confirmation instead.

## Boundaries

- No user stories, acceptance criteria, or feature SPEC (Requirements).
- Do not restyle or invent a design system (look is copied from Mockup into UI guidelines).
- Do not expand MVP scope or reopen epic packaging unless the system cannot honour Scope.
- Do not write decision records under `docs/history/decisions/` (Documentation owns those).
- Reliability theatre (many environments, 24/7 ops) stays out unless who-operates-it demands it.
- The dummy stays throwaway; the skeleton is production code.

## Boundary with the next phase

After Foundation accept, Requirements writes stories and acceptance criteria for the first MVP epic named in Scope. Do not write that SPEC here. If the client volunteers story-level detail early, note it under history and reuse in Requirements.
