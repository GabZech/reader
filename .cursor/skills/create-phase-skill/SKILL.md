---
name: create-phase-skill
description: >-
  Creates or upgrades a project-agnostic discovery or feature phase skill and
  its question bank: brainstorm with the client first, research and review,
  then write files. Use when authoring a phase skill, adding questionbank.md,
  or repeating the Kickoff/Understand skill-creation workflow for Scope,
  Prototype, Foundation, or later phases.
---

# Create phase skill

Build or upgrade a **project-agnostic** phase skill (and optional question bank) with the client. Do not jump to files or web research on the first turn.

Authoring craft (succinct copy, split style vs content, SKILL.md shape) lives in the **write-skills** skill (`.cursor/skills/write-skills/SKILL.md`). This skill owns the **engagement sequence** only.

## When

- Client asks to create or improve a phase skill / question bank
- A phase skill lacks clarifying guidance that Kickoff or Understand already have
- Preparing Scope, Prototype, Foundation, or a later phase the same way

## Sequence (mandatory order)

### 1. Brainstorm and propose — no research, no files

Propose, in conversation:

- Phase strategy (what this phase locks; what it must not do)
- Artifact list and level of detail (e.g. journeys = overall use cases; stories later)
- Question clusters → which artifact each feeds → “ask until you can…” exits
- Boundaries with the previous and next phase
- What to propose-for-confirm vs ask open (mirror Kickoff non-goals / Understand constraints)

Keep the proposal **idea-agnostic**: any product, not the current client’s domain. Wait for alignment or edits before step 2.

### 2. Research and infer — still no repo writes

After the client agrees on structure:

- Research **high-quality** sources (e.g. NN/g, GOV.UK Service Manual, established design-kit / service-design guidance). Prefer primary practice guides over listicles.
- Infer accurate, agnostic questions and tighten strategy from that evidence.
- Present the revised cluster menu and key source-backed practices for client review.
- Do not create or edit skill files until the client approves the content.

### 3. Create or update files

On explicit go-ahead:

- Add or update `.cursor/skills/<phase>/SKILL.md` (Entry, Artifacts, Do, clarifying flow, ready-to-draft-artifacts, Gate)
- Add or update `.cursor/skills/<phase>/questionbank.md` when the phase needs a clarifying menu; link it from the phase skill like Kickoff/Understand
- Follow **write-skills** and **questioning** (style stays in questioning; menu content stays in the bank)
- Match house patterns already used in `1-1-kickoff` and `1-2-understand`
- Do not embed the current product’s domain into the skill or bank

### 4. Close the loop

Summarize what was added or changed and which phase to run next (or resume). Do not start that phase’s clarifying rounds unless the client asks to continue into product work.

## Defaults

| Topic | Default |
| --- | --- |
| Agnosticism | Skills and banks apply to any idea; product facts stay in `docs/` |
| Question banks | Progressive disclosure: long menus in `questionbank.md`, not in `SKILL.md` |
| Delivery style | Never duplicate questioning skill rules inside the bank |
| Scopes and stack | Discovery banks stay descriptive until Scope (prototype / MVP / later) or Foundation (stack) |
| User stories | Not in discovery banks; Requirements owns story + AC level of detail |
| Client prompts | Never save verbatim chat into skills or `docs/` |

## Anti-patterns

- Researching or writing files before the client has seen a structure proposal
- Encoding the current product’s personas, journeys, or stack into the phase skill
- Turning the bank into a rigid script instead of a pick-and-adapt menu
- Soliciting open “what should we leave out?” lists when the phase should propose non-goals, constraints, or scopes for confirm/edit
