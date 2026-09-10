---
name: writing-docs
description: >-
  Voice and structure for human-facing living docs under docs/ (vision, roadmap, decisions, architecture, development, operations, ui-guidelines, and similar) and the product root README.
  Use when writing or editing those files.
---

# Writing docs

Style for reports and living docs under `docs/` meant for humans. Purpose and consequence before mechanics; stay precise. Prefer scannable structure when the reader must compare many similar units.

## Voice

- Short prose for purpose, consequence, and narrative framing; one idea per paragraph or bullet; concrete nouns over jargon stacks
- Presenting order follows the real system or journey flow. Introduce a specialist term once in plain language, then use the precise name
- Assume systems thinking; do not assume specialist vocabulary; do not dumb down. Never invent behaviour or blur real constraints
- Prefer **bold** for list labels and for the short topic sentence that states each paragraph's idea
- Where the doc's job is technical accuracy (journeys, architecture, constraints, operations, interfaces): prefer clarity over narrative warmth, a short framing sentence then numbered steps or labeled lists, no padding entities or rules into story paragraphs

## Lists

- Numbered = order or procedure; labeled bullets = recurring fields across siblings (same labels, same order, every time)
- Nest concrete deliverables (paths, outputs) under the inventory field; keep the goal as one sentence
- One idea per bullet: the label names the field, the text carries the content. Do not turn a single idea into a list just to look structured
- Tables are fine when columns help compare peers

## Visual

- A small fixed emoji vocabulary as field or section labels only, same meaning → same icon every time: 🎯 Goal, 🔭 Vision, 📄 Summary, ❗ Decisions, ⚠️ Open / Caution, 📌 Post-MVP Notes, ✅/❌ progress and non-goals
- Distinct icons on adjacent sibling headings so labels do not look identical; emoji on subheadings, never the document `#` title; never one per bullet or sentence; narrative prose stays emoji-free unless a milestone or caution needs a signal

## Root README (`README.md`)

Product front door, not a second copy of the proposition or a feature inventory.

1. **Title:** product or working name
2. **Overview:** short prosaic pitch, problem and consequence first, then direction. Sentences, not a capability inventory
3. **How we work:** why structure beats jumping to code, then the change loop's steps in running sentences with what each is for
4. Optional short pointers into `docs/`

The change loop's Ship step owns keeping this current; no standing refresh ask outside that.

## Roadmap (`docs/roadmap.md`)

Orient the reader; do not duplicate vision or a full feature inventory.

- **Where We Are:** 🏁 Milestone (MVP / none set); 📄 Summary, 2-4 prosaic bullets on what is accepted, built, and how feature work runs, not the pitch or a feature inventory; ⚠️ Open, only genuinely unresolved risk right now (a provisional MVP-boundary choice goes in Post-MVP Notes instead)
- **What's Next:** remaining work grouped by epic from `docs/vision/epics.md`, epics-need-epics order. `###` group heading, then `[x]`/`[ ]` lines, one per turn of the change loop, named the way the reader would. Tick a line as part of shipping the change that earned it. Close with **Later** for deferred capabilities
- **Post-MVP Notes:** choices explicitly deferred to after MVP, each with a real MVP-boundary trigger to revisit; not a parking lot. Remove once acted on
- **Concluded:** one ✅ bullet per accepted phase or milestone, linking its living-doc results

## Decisions (`docs/decisions.md`)

Living, append-only, newest first. One entry per choice expensive to undo: date and title, then **Decision**, **Why**, **Rejected**, **Revisit when**. Written by Ship when a change produces one. Threshold: a choice a future session might plausibly reverse, not a design detail already implied by the code.

## System docs

Same labeled-field shape; refresh as part of any change that makes one wrong.

- **Architecture:** Purpose (one paragraph); ❗ Tradeoffs (what we optimize for, give up, and why); Parts (named components, data flow); Stack (current choices, not rejects); Outside connections (mechanism level, no live credentials); ⚠️ Skeleton (proved vs still to stand up). No vendor tutorials or a second decision log; that's `docs/decisions.md`
- **Development:** Purpose; Prerequisites; Run; Test (what CI uses); Local config (variable names, not secret values). Commands here must have been run
- **Operations:** Purpose; Where it runs; Deploy; Config and secrets (secrets stay out of the repo); Backup and data control; Cost against the ceiling; Smoke test
- **UI Guidelines:** Purpose (durable look the real UI follows, not a design system); Layout, density, chrome; Type and colour only if the look uses them; Surfaces; Out of scope (later screens wait for the change that builds them). Do not restyle on the strength of this doc alone

## Avoid

- Marketing fluff, academic filler, suspense that hints then withholds
- One-off or random emoji outside the stable vocabulary; decoration that replaces precise words
- Bullets where a paragraph would teach better; paragraphs where a catalog would scan better
- Claiming something works when it does not
- Em dashes (`—` / `--`); prefer colon `:`
- Naming third-party consumer apps as inspiration or parity targets (legal risk if read as copying); describe the status-quo tool generically. Named products the client integrates with (e.g. Obsidian as an export target) are fine when factual
- Saving client prompts or verbatim chat dumps into living docs
