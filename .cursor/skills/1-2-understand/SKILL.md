---
name: 1-2-understand
description: >-
  Runs the Understand phase: personas, journeys (overall use cases), and
  cross-cutting constraints. Use when roadmap says Understand, or after
  Kickoff is accepted.
---

# Understand

Build a shared picture of who the product is for, what they try to do end to end, and the constraints that shape those paths. Descriptive only — no epics and no mockup / MVP / later scope.

## Entry

- Kickoff is accepted (`docs/vision/proposition.md` and `docs/vision/metrics.md`)

## Artifacts

- `docs/vision/personas.md`
- `docs/vision/journeys.md` (named overall use cases at discovery level of detail)
- `docs/vision/constraints.md`
- `docs/history/discovery/02-understand/` (clarifying answers — never client prompts)

## Do

**Include:**
- Personas: who is in focus, goals, context. Goals link to the named journeys that pursue them. Do not retell journey steps or paste constraints.
- Journeys: as-is overall use cases. Same labels every time: actor, goal, trigger, steps today, outcome, costly edges, **Wanted**. Actor links to the persona. Related journeys link to each other. **Wanted** is what should differ on that path (or “None named”), not a redesigned walkthrough. Do not retell the persona portrait. List journeys in chronological order of occurrence for the actor: setup and prerequisites before the sessions they enable, then typical time-of-use. If later journeys assume a durable object already exists, include a setup or maintenance journey for how it comes into being and how it is retired, or record that it is assumed to already exist. Do not invent a sequence for parallel paths.
- Constraints: cross-cutting hard vs soft **limits** (cost, ownership, must-nots, quality bars). Not a parking lot for product wishes.
- Open questions that still block a clear picture of users or journeys

**Clarifying questions:** deliver each ask using the **questioning** skill (`.cursor/skills/questioning/SKILL.md`). **What to ask:** [questionbank.md](questionbank.md). Walk clusters one at a time; skip what Kickoff or this conversation already answered well.

Do not write epics. Do not assign mockup / MVP / later. Do not invent stack or architecture. Do not write user stories or acceptance criteria.

**Human role:** Confirm personas and journeys feel right; add missing users or paths; challenge weak constraints; check **Wanted** is a short change note, not a to-be redesign; accept when the picture is good enough to scope.

## Clarifying questions

Goal: gather only what personas, journeys, and constraints need. Defer epics and mockup / MVP / later scope to Scope; defer increment behaviour to Build; defer stack to Foundation.

### Principles

1. **Reuse Kickoff.** Deepen who, outcomes, and assumptions; do not re-litigate vision or metrics unless contradicted.
2. **Past and present over hypotheticals.** Critical incidents and concrete situations over “would you use…” or feature opinions.
3. **Current-state journeys.** Map how goals are achieved today. Put path-specific desired changes as **Wanted** on that journey. Put cross-cutting limits in constraints. Do not rewrite journeys as the new app. As-should paths wait for Mockup.
4. **Use-case level of detail, not Build steps.** Name end-to-end scenarios; stop before splitting into tryable Build steps.
5. **Constraints by proposal.** Infer hard vs soft limits from answers and Kickoff; confirm or edit — do not open with a laundry-list ask.
6. **Stay in Understand scope.** No epics, mockup / MVP / later, or architecture.

### Flow

1. Orient once (phase purpose and what comes next), then clarifying rounds from [questionbank.md](questionbank.md) via the questioning skill.
2. If answers are vague, ask for one concrete example or “last time” next.
3. After primary journeys are clear, propose inferred constraints (limits only); one confirmation ask.
4. Draft personas, journeys, and constraints when the checklist below is met; present the summary.
5. **Gap check (before accept):** Recommend one or two remaining thin spots that still belong in Understand (not Scope/Mockup/Foundation). One confirm (add, skip, or something else). Incorporate, then continue.
6. One accept ask for Understand.

### Ready to draft artifacts when

- At least one grounded persona (goals and context, not demographics alone), with goals linking to journeys rather than retelling them
- A named set of primary journeys covering the vision’s outcomes, each naming the persona as actor with a link
- Durable objects that later sessions assume already exist have a setup or maintenance journey, or an explicit assumed-to-exist note
- Each primary journey narratable end to end (trigger, steps today, outcome, main friction), with **Wanted** where a change was named
- Costly edges called out where they matter
- Cross-cutting **limits** confirmed (or adjusted) from the agent’s proposal, with hard vs soft clear enough to steer Scope. Product wishes are not filed as constraints.
- Open unknowns listed when they still block honest mockup / MVP / later scope

If persona, primary journeys, or constraints are still missing, keep asking — do not invent them.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Scope; refresh Summary / Decisions / Open; add Understand under Concluded); follow writing-docs **Root README** When for this phase. Do not advance without confirmation.
