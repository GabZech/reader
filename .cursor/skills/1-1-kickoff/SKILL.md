---
name: 1-1-kickoff
description: >-
  Runs the Kickoff phase: capture the idea, explain the engagement, clarify,
  then write problem statement, vision, non-goals, and success metrics. Use when
  roadmap says Kickoff, on a greenfield first prompt, or after copying this
  template for a new product.
---

# Kickoff

Capture the product idea, set how the engagement runs, clarify what matters, and lock the problem statement, vision, non-goals, and success measures.

## Entry

- Greenfield product, empty or Kickoff-stage roadmap, or first prompt after copying the template

## Artifacts

- `docs/roadmap.md` (initialised with where we are)
- `docs/product-definition/vision.md`
- `docs/product-definition/metrics.md`
- `README.md` (product overview + concise workflow; replaces the template manual)
- `docs/history/discovery/01-kickoff/` (engagement explanation, clarifying answers — never client prompts)

## Do

**Include:**
- Restate the client’s idea once, briefly, then explain the workflow in a few sentences
- Clarifying questions from this skill (see below); deliver each ask using the **questioning** skill (`.cursor/skills/questioning/SKILL.md`)
- Problem statement, product vision, and explicit non-goals in `vision.md`
- How success will be measured in `metrics.md`
- Initialise `docs/roadmap.md` per the **Roadmap** section in the writing-docs skill (`.cursor/skills/writing-docs/SKILL.md`)

**Do not** save client prompts (verbatim chat messages or “initial prompt” dumps) under `docs/` or elsewhere in the repo. Capture durable facts in clarifying answers and living docs only.

Do not write personas, journeys, epics, or stack choices yet.

**Human role:** Answer clarifying questions; confirm or edit proposed non-goals; add anything still missing when prompted; challenge the drafts; accept when Kickoff is complete.

## Clarifying questions

Goal: gather only what `vision.md` and `metrics.md` need. Defer deep user/journey detail to Understand; defer stack to Foundation.

**Style:** follow `.cursor/skills/questioning/SKILL.md` (one question per message; short acknowledge or none — never long parrot-restates).

**What to ask:** use the menu in [questionbank.md](questionbank.md). Walk clusters one question at a time; skip what the client already answered well in conversation.

### Principles (Kickoff substance)

1. **Problem before solution.** If the client pitches a feature or stack, extract the underlying problem, who it hurts, and why it matters. Do not put solutions in the problem statement.
2. **Past and present over hypotheticals.** Prefer what happens today, workarounds, and concrete examples over “would you use…” or opinion of the idea.
3. **Outcomes over outputs.** Success metrics measure changed behaviour or value, not “shipped X.”
4. **Non-goals by proposal.** Do not ask open “what should we leave out?” questions. Near the end of clarifying, infer likely non-goals from prior answers (adjacent problems, audiences, tempting extras, hard must-nots if signaled) and propose a short list for confirmation or edit.
5. **Assumptions on the table.** Surface what is believed but unproven; note what later discovery must learn or prove.
6. **Stay in Kickoff scope.** High-level “who” and “why” yes; full personas, journeys, epic cuts, and architecture no.

### Flow

1. Brief idea restatement + short workflow explanation (not a questioning turn).
2. Clarifying rounds from [questionbank.md](questionbank.md), one question per message via the questioning skill — skip the non-goals cluster; do not solicit exclusions.
3. If answers are vague, ask for one concrete example next.
4. Propose inferred non-goals; one confirmation ask (accept, edit, or reject items).
5. Draft vision + metrics when “enough to draft” is met; present the summary.
6. **Gap check (before accept):** From this conversation, name one or two topic categories the client might still want in Kickoff (gaps or thin spots that still belong in vision/metrics — not Understand/Foundation work). One ask: anything to add in those areas (or elsewhere in Kickoff)? Incorporate answers, then continue.
7. One accept ask for Kickoff.

### Enough to draft when

- One primary problem (not a laundry list of unrelated issues)
- Clear enough “who is hurt / who benefits” for a vision — not full personas
- Why it matters now (trigger or cost of inaction)
- Non-goals confirmed (or adjusted) from the agent’s proposal
- Measurable signals of success, or explicit placeholders to baseline later

If problem, who, why-now, or metrics are still missing, keep asking — do not invent them. Non-goals are proposed by you, then confirmed.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Understand; refresh Summary / Decisions / Open; add Kickoff under Concluded); rewrite `README.md` per writing-docs **Root README**. Do not advance without confirmation.
