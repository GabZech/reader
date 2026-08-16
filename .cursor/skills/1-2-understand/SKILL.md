---
name: 1-2-understand
description: >-
  Runs the Understand phase: personas, journeys (overall use cases), and
  cross-cutting constraints. Use when roadmap says Understand, or after
  Kickoff is accepted.
---

# Understand

Build a shared picture of who the product is for, what they try to do end to end, and the constraints that shape those paths. Descriptive only — no epics and no prototype / MVP / later cuts.

## Entry

- Kickoff is accepted (`docs/product-definition/vision.md` and `docs/product-definition/metrics.md`)

## Artifacts

- `docs/product-definition/personas.md`
- `docs/product-definition/journeys.md` (named overall use cases at discovery grain)
- `docs/product-definition/constraints.md`
- `docs/history/discovery/02-understand/` (clarifying answers — never client prompts)

## Do

**Include:**
- Personas: who is in focus, goals, context. Goals link to the named journeys that pursue them. Do not retell journey steps or paste constraints.
- Journeys: as-is overall use cases. Same labels every time: actor, goal, trigger, steps today, outcome, costly edges, **Wanted**. Actor links to the persona. Related journeys link to each other. **Wanted** is what should differ on that path (or “None named”), not a redesigned walkthrough. Do not retell the persona portrait.
- Constraints: cross-cutting hard vs soft **limits** (cost, ownership, must-nots, quality bars). Not a parking lot for product wishes.
- Open questions that still block a clear picture of users or journeys

**Clarifying questions:** deliver each ask using the **questioning** skill (`.cursor/skills/questioning/SKILL.md`). **What to ask:** [questionbank.md](questionbank.md). Walk clusters one at a time; skip what Kickoff or this conversation already answered well.

Do not write epics. Do not assign prototype / MVP / later. Do not invent stack or architecture. Do not write user stories or acceptance criteria.

**Human role:** Confirm personas and journeys feel right; add missing users or paths; challenge weak constraints; check **Wanted** is a short change note, not a to-be redesign; accept when the picture is good enough to scope.

## Clarifying questions

Goal: gather only what personas, journeys, and constraints need. Defer epic cuts to Scope; defer stories to Requirements; defer stack to Foundation.

### Principles

1. **Reuse Kickoff.** Deepen who, outcomes, and assumptions; do not re-litigate vision or metrics unless contradicted.
2. **Past and present over hypotheticals.** Critical incidents and concrete situations over “would you use…” or feature opinions.
3. **Current-state journeys.** Map how goals are achieved today. Put path-specific desired changes as **Wanted** on that journey. Put cross-cutting limits in constraints. Do not rewrite journeys as the new app. As-should paths wait for Prototype.
4. **Use-case grain, not stories.** Name end-to-end scenarios; stop before user-story split and acceptance criteria.
5. **Constraints by proposal.** Infer hard vs soft limits from answers and Kickoff; confirm or edit — do not open with a laundry-list ask.
6. **Stay in Understand scope.** No epics, MVP cuts, or architecture.

### Flow

1. Orient once (phase purpose and what comes next), then clarifying rounds from [questionbank.md](questionbank.md) via the questioning skill.
2. If answers are vague, ask for one concrete example or “last time” next.
3. After primary journeys are clear, propose inferred constraints (limits only); one confirmation ask.
4. Draft personas, journeys, and constraints when the checklist below is met; present the summary.
5. **Gap check (before accept):** Name one or two thin spots that still belong in Understand (not Scope/Foundation). One ask: anything to add there or elsewhere in Understand? Incorporate, then continue.
6. One accept ask for Understand.

### Ready to draft artifacts when

- At least one grounded persona (goals and context, not demographics alone), with goals linking to journeys rather than retelling them
- A named set of primary journeys covering the vision’s outcomes, each naming the persona as actor with a link
- Each primary journey narratable end to end (trigger, steps today, outcome, main friction), with **Wanted** where a change was named
- Costly edges called out where they matter
- Cross-cutting **limits** confirmed (or adjusted) from the agent’s proposal, with hard vs soft clear enough to steer Scope. Product wishes are not filed as constraints.
- Open unknowns listed when they still block an honest cut

If persona, primary journeys, or constraints are still missing, keep asking — do not invent them.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Scope; refresh Summary / Decisions / Open; add Understand under Concluded); follow writing-docs **Root README** When for this phase. Do not advance without confirmation.
