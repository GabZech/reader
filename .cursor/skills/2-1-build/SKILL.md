---
name: 2-1-build
description: >-
  Runs Feature Development step 2.1 Build: iterative vertical increments of the
  current epic on the real product, with a short try-and-sign-off loop like
  Mockup. Use when roadmap says Build, after Foundation is accepted, after
  Document of the previous epic, or when implementing an epic.
---

# Build

Make the current epic usable in the real product, one tryable increment at a time. Clarify only what the next slice needs, build it, let the client try it, then the next slice. This is not a SPEC, not throwaway, and not Document.

## Entry

- Foundation is accepted
- Epic chosen from MVP (or later) scope in `docs/product-definition/epics.md`
- Create `docs/specs/<epic-slug>/` if it does not exist

## Artifacts

- Working software on the product (same app as the walking skeleton)
- `docs/specs/<epic-slug>/clarifying-answers.md` (session facts: never client prompts)

## Do

**Include:**
- Work on a branch for this epic. Follow `docs/development.md` when present.
- Clarifying questions via the **questioning** skill. **What to ask:** [questionbank.md](questionbank.md). Skip what earlier phases or this conversation already answered.
- Epic in/out and an ordered increment map inferred from the epic, dummy, and Foundation leftovers; one confirm. Vertical slices the client can try, not layers.
- For the current increment only: fill lived-fact gaps, then build. Run the usual local checks before showing. If the increment must be judged on a hosted or device surface, deploy per `docs/operations.md` and smoke; do not save all shipping for Document.
- After each increment: how to try it; one ask (good, or something needed missing). Iterate until signed off. Do not start the next increment until then.
- Record durable facts in clarifying-answers.

Do not write requirements, design, or task files. Do not reopen Foundation unless the client asks. Do not pull in other epics. Do not restyle. Do not update overview docs or write decision records (Document owns those).

**Human role:** Judge each running increment; say if it is good or something needed is missing; hold work outside this epic; accept Build when every increment is signed off or leftover risk is explicit.

## Clarifying questions

Goal: gather only what the next increment needs. Defer living-doc alignment to Document.

### Principles

1. **Reuse locks.** Journeys, dummy, epics, and Foundation are inputs. Reopen only if this epic cannot honour them.
2. **Increment map by proposal.** Infer ordered tryable slices. Prefer high value and low complexity first unless a leftover joint blocks the rest. Confirm; do not ask the client to invent the backlog.
3. **Clarify the current slice only.** Do not specify the whole epic before the first increment.
4. **Try it, do not specify it.** Behaviour still open is cheaper to settle on a running slice than in a document.
5. **Agent verifies, client judges.** Tests, lint, and build are the agent's loop. Whether the increment is good is the client's.
6. **Stay in Build.** No overview docs, no SPEC trilogy, no next epic.

### Flow

1. Orient once: this epic, real software, one increment at a time. Document is next (living docs and close).
2. Propose in/out, the increment list, and which is first; one confirm.
3. Clarifying rounds from [questionbank.md](questionbank.md) for the current increment only.
4. Build that increment; self-check; deploy if the try-surface needs it; share how to try; one ask. Iterate until good.
5. Name the next increment; repeat from step 3 until the map is done or leftover risk is enough.
6. Gap check; accept Build.

### Ready to build an increment when

- Epic in/out is confirmed
- Increment map is confirmed (it may shrink after trying)
- Gaps for this increment are filled

### Ready to show an increment when

- The slice is tryable end to end
- Local checks have been run, or the agent has said why not
- How to try it is stated, including the live URL when that is the try-surface

### Ready to accept when

- Client has signed off each increment, or remaining risk per increment is explicit
- Clarifying-answers are honest about leftovers Document must record

If those are missing, keep asking or building: do not invent them.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Document for this epic; refresh Summary / Decisions / Open). Do not advance without confirmation. On requested behaviour after a sign-off: stay in Build.
