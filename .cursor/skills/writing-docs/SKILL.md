---
name: writing-docs
description: >-
  Voice and structure for human-facing living docs under docs/ (vision, metrics,
  personas, journeys, constraints, epics, architecture, development, operations,
  roadmap, and similar). Use when writing or editing those files. Do not use for
  docs/history/ or docs/specs/.
---

# Writing docs

Style for reports and living docs under `docs/` meant for humans. Purpose and consequence before mechanics; stay precise. Prefer scannable structure when the reader must compare many similar units.

## Scope

- **Apply** to human-facing living docs under `docs/` (e.g. product-definition, architecture, development, operations, roadmap, conventions, ui-guidelines)
- **Skip** `docs/history/` and `docs/specs/` (engagement log and feature contracts keep their own shape)

## Voice

- Short prose for purpose, consequence, and narrative framing
- One idea per paragraph or bullet; concrete nouns over jargon stacks
- Presenting order follows the real system or journey flow
- Introduce specialist terms once in plain language, then use the precise name
- Assume systems thinking; do not assume specialist vocabulary; do not dumb down
- Never invent behaviour or blur real constraints
- Prefer **bold** for list labels and for the short topic sentence that states each paragraph’s idea

## Accuracy over prose

When the doc’s job is technical accuracy (user journeys, architecture, constraints, operational procedures, interfaces, acceptance-critical detail):

- Prefer clarity and precision over narrative warmth
- Use a short framing sentence, then let numbered steps, labeled lists, or tables carry the payload
- Do not pad entities, steps, rules, or contracts into story paragraphs

## Lists

- Numbered lists = order or procedure
- Labeled bullets = recurring fields across siblings (same labels, same order, every time)
- Nest concrete deliverables (paths, outputs) under the inventory field; keep the goal as one sentence
- One idea per bullet: the label names the field, the text carries the content
- Do not turn a single idea into a bullet list just to look structured
- Tables are fine when columns help compare peers (e.g. non-goal / rationale)

## Visual

- Prefer journeys and clear structure when explaining systems
- Use a small fixed emoji vocabulary as field or section labels only; same meaning → same icon every time
- When emoji mark consecutive headings or sibling sections, give each a distinct icon from the vocabulary so adjacent labels do not look identical
- Default vocabulary when it fits: 🎯 Goal, ⚡ Problem, 🔭 Vision, 📍 Phase, 📄 Summary / Artifacts, 🏁 Milestone, ❗ Decisions, ⚠️ Open / Caution / Assumptions; ✅/❌ for progress and non-goals under a clear header
- Prefer emoji on subheadings (`##` / `###`), not the document `#` title
- Do not invent a new emoji per bullet, per sentence, or for emphasis
- Narrative framing stays emoji-free unless a milestone or caution needs a signal
- Diagrams only when they clarify a relationship the prose cannot

## Roadmap (`docs/roadmap.md`)

Orient the engagement; do not duplicate vision, metrics, or feature inventory.

### Where We Are

Fixed field order and icons:

1. **📍 Phase** — current phase name and status (e.g. in progress). Do not use 🎯 for phase; 🎯 stays Goal elsewhere
2. **🏁 Milestone** — Prototype / MVP / none set
3. **📄 Summary** — where development stands now and what the next phase is (what is accepted, what this phase is doing, what comes after it). Not the product pitch, not constraints or feature lists. Prefer 1–3 prosaic bullets
4. **❗ Decisions** — durable locks that steer later work, as prosaic bullets (not telegraphic labels). Nest **In** and **Out** sublists when both apply. Pull Out from confirmed non-goals; keep In to who, ownership, cost, must-haves, and hard reliability bets
5. **⚠️ Open** — only what the current phase must still resolve. Do not add a separate Next line

Refresh Summary, Decisions, and Open when a phase gate advances; keep Decisions aligned with accepted vision/non-goals (and later constraints) without pasting those docs.

### Concluded

Under **Concluded**, one ✅ bullet per accepted phase: phase name, links to living-doc results, and the phase history folder when it exists.

## Avoid

- Marketing fluff, academic filler
- One-off or random emoji outside the stable vocabulary
- Bullets where a paragraph would teach better; paragraphs where a catalog would scan better
- Emoji or decoration that replaces precise words
- Claiming something works when it does not
- Em dashes (`—` / `--`); prefer colon `:`
- Suspense: do not hint at something and withhold it
- Naming third-party consumer apps as inspiration, parity targets, or “apps like X” (legal risk if read as copying). Describe the status-quo tool generically (current reading app, existing vendor tool). Named products the client integrates with (e.g. Obsidian as an export target) are fine when factual
- Saving client prompts or verbatim chat dumps into living docs or history
