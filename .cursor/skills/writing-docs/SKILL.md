---
name: writing-docs
description: >-
  Voice and structure for human-facing living docs under docs/ (vision, metrics,
  personas, journeys, constraints, epics, mockup, architecture, development,
  operations, roadmap, and similar) and the product root README. Use when
  writing or editing those files. Do not use for docs/history/ or docs/epics/.
---

# Writing docs

Style for reports and living docs under `docs/` meant for humans. Purpose and consequence before mechanics; stay precise. Prefer scannable structure when the reader must compare many similar units.

## Scope

- **Apply** to human-facing living docs under `docs/` (e.g. vision, architecture, development, operations, roadmap, conventions, ui-guidelines) and the product root `README.md`
- **Skip** `docs/history/` and `docs/epics/` (engagement log and epic notes keep their own shape; history stays frozen after the phase accepts)

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

## Root README (`README.md`)

Product front door after Kickoff; not a second copy of the proposition or the full template manual.

### Shape

1. **Title** — product or working name
2. **Overview** — short prosaic pitch: problem and consequence first, then direction. Write in sentences, not a capability or feature inventory. Refresh when discovery locks change what a newcomer should know. Do not paste the full proposition, personas, or epic lists
3. **How we work** — why before how: open with why structure beats jumping to code, then the two stages in short prose (discovery and foundation once; feature development repeats as Build then Deploy per epic). Name discovery phases in running sentences with their goals; do not use telegraphic bullet or arrow lists. No artifact inventories. Point to the template for discovery and foundation detail: [GabZech/template-spec-workflow](https://github.com/GabZech/template-spec-workflow). This repo’s feature loop is Build then Deploy, not that template’s SPEC stairs. Build is local try-and-sign-off with continuous integration before each slice is shown. Deploy is the continuous-delivery release: production host, smoke, living docs; not continuous deployment of every change.
4. Optional short pointers into `docs/` when useful; omit template “How to Start” once the product is underway

### When

- **Kickoff (required):** on accept, replace the template README with this shape
- **Understand (optional):** after phase accept, one questioning-skill ask whether to refresh Overview (and only then edit). Keep How we work stable unless the engagement model itself changes
- **Scope, Mockup, and Foundation:** do not offer this ask
- **Feature development:** do not offer this ask; Deploy owns living-doc alignment for features

## Roadmap (`docs/roadmap.md`)

Orient the engagement; do not duplicate vision, metrics, or feature inventory.

### Where We Are

Fixed field order and icons:

1. **📍 Phase** — current phase name and status (e.g. in progress). Do not use 🎯 for phase; 🎯 stays Goal elsewhere
2. **🏁 Milestone** — Mockup / MVP / none set
3. **📄 Summary** — where development stands now and what the next phase is (what is accepted, what this phase is doing, what comes after it). Not the product pitch, not constraints or feature lists. Prefer 1–3 prosaic bullets
4. **❗ Decisions** — durable locks that steer later work, as prosaic bullets (not telegraphic labels). Nest **In** and **Out** sublists when both apply. Pull Out from confirmed non-goals; keep In to who, ownership, cost, must-haves, and hard reliability bets
5. **⚠️ Open** — only what the current phase must still resolve. Do not add a separate Next line

Refresh Summary, Decisions, and Open when a phase gate advances; keep Decisions aligned with accepted proposition and non-goals (and later constraints) without pasting those docs.

### Concluded

Under **Concluded**, one ✅ bullet per accepted phase: phase name, links to living-doc results, and the phase history folder when it exists.

## Mockup (`docs/vision/mockup.md`)

Thin pointer to the clickable dummy. Write during Mockup once the dummy is walkable; refresh on accept. The dummy itself is not this file (HTML lives under `docs/mockup/`; Penpot/Figma stay in that tool). Keep this file under vision until Foundation is accepted; Foundation then moves it to `docs/history/discovery/04-mockup/`.

### Shape

1. **Purpose** — journey learning purpose from Scope, and that the dummy settles overall look on those paths
2. **Tool** — HTML, Penpot, or Figma
3. **How to open** — local URL or share link; enough to walk it without a repo scavenger hunt
4. **Paths walkable** — labeled list matching mockup-scope
5. **What we learned** — include overall look that was accepted
6. **Still open** — unproven journey questions and look-risk carried into Foundation

Do not paste screens, rewrite journeys, or treat the dummy as the product.

## Architecture (`docs/architecture.md`)

Whole-system shape. Write during Foundation after the system package is confirmed; refresh when Deploy aligns it with a later ship. Do not put an epic’s increment design here.

### Shape

1. **Purpose:** what the running system is, in one short paragraph
2. **❗ Tradeoffs:** what we optimize for, what we give up, and why (the confirmed Foundation package). Omit axes that were not in tension
3. **Parts:** named components and how data moves between them. Prefer few parts
4. **Stack:** languages, frameworks, stores, hosts: current choices, not a catalogue of rejects
5. **Outside connections:** inbound and outbound paths at mechanism level (not live credentials)
6. **⚠️ Skeleton:** what the walking skeleton proved vs what the first feature still has to stand up

Do not paste epic notes, vendor tutorials, or a second decision log. Hard-to-reverse choices that arise later go under `docs/history/decisions/` in Deploy.

## Development (`docs/development.md`)

How to run and change the skeleton locally. Commands in this file must have been run.

### Shape

1. **Purpose:** what a developer needs this file for
2. **Prerequisites:** toolchain and versions
3. **Run:** how to start the skeleton locally
4. **Test:** how to run the checks continuous integration will use, when those exist
5. **Local config:** what varies on a machine (names of variables, not secret values)

## Operations (`docs/operations.md`)

How the system is hosted, deployed, and kept on. Proportionate to who operates it and the cost ceiling.

### Shape

1. **Purpose:** what operating this system involves
2. **Where it runs:** intended run path (local-only or hosted)
3. **Deploy:** how a new version reaches that path
4. **Config and secrets:** how they are injected; secrets stay out of the repo
5. **Backup and data control:** how client-controlled data is kept and exported
6. **Cost:** what keeping it on is expected to cost, against the ceiling
7. **Smoke test:** the fast check that the intended run path still works

## UI Guidelines (`docs/ui-guidelines.md`)

Durable look copied from the accepted dummy. Foundation must write this before moving `mockup.md` to history. Not a design system.

### Shape

1. **Purpose:** overall look the real UI must follow
2. **Layout, density, chrome:** structure of screens and scaffolding
3. **Type:** and colour only if the accepted look uses it
4. **Surfaces:** devices or widths the shell must honour
5. **Out of scope:** feature interactions and later-scope screens wait for that epic’s Build

Do not restyle. Do not paste the dummy.

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
- Rewriting `docs/history/` to match later code or living docs
