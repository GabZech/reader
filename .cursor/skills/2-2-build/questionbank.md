# Build question bank

Clarifying **content** for Build. Deliver each ask with the questioning skill (`.cursor/skills/questioning/SKILL.md`) — style lives there; this file is only the menu.

Epic choice, boundary, the increment map, dependencies, and failure modes were already decided in **Plan** (`docs/epics/<epic-slug>/plan.md`). Build only fills what is cheaper to settle on a running slice than in a document.

## Question clusters → artifacts

| Cluster | Feeds | Ask until you can… |
| --- | --- | --- |
| Current increment's remaining gaps | clarifying-answers.md | Fill lived facts the plan could not settle: exact wording, spacing, small behaviour only the client would know |
| Deviation from plan | plan.md deviation log | Decide whether a mismatch between the plan and what building revealed needs the client's confirm before continuing |

Trying an increment is **not** a cluster; that ask happens after the slice is built, via the guided walkthrough in the phase skill. A request to ship is **not** a cluster; it enters Deploy from the phase skill.

### 1. Current increment

Ask only what the plan's job, dependencies, and failure-mode entries did not already answer.

- Exact copy, wording, or small display choices cheaper to settle on the running slice than in a document
- A lived fact the plan flagged as open for this increment specifically

### 2. Deviation from plan

When building reveals the plan was wrong or incomplete:

- Name what changed: a dependency, a failure mode, the size of the job
- Propose whether this still fits inside the increment as planned, or needs Plan reconfirmed
- If it only affects this slice's detail: note it in `plan.md` and continue
- If it changes scope, risk, or another increment: stop and ask before continuing

## Question direction

- Prefer the next tryable path over completeness of the epic
- Never re-ask epic choice, boundary, the map, dependencies, or failure modes; they are Plan's
- Never ask the client to write stories, EARS, or a design

## Boundaries

- No `requirements.md`, `design.md`, or `tasks.md`
- No overview-doc rewrites (Deploy)
- No production deploy (Deploy)
- No stack or whole-system redesign (Foundation)
- No other epics

## Boundary with the next phase

Deploy is entered when the increment map is done, or when the client asks to ship the last signed-off state. Deploy verifies the rollback path, puts that revision on the production host, smokes the live path if hosted, and aligns living docs with what is now live. Do not write those docs here. If the client volunteers overview wording early, note it under `clarifying-answers.md` and reuse in Deploy.
