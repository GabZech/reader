# Reader

## Overview

Reader is a personal reading hub for one person. It brings newsletters, feeds, and saved articles into one place you control, so daily reading stays simple and the material remains yours to organise, highlight, and keep.

The product is built for a solo reader who wants full ownership of their corpus, light-touch curated lists, and an easy path from highlights into an Obsidian vault. It is not a shared or multi-user app.

## How we work

Left alone, an agent will start coding from the first prompt. At that point neither side usually understands the product well enough, so work drifts. This repo uses a SPEC-driven workflow (from [template-spec-workflow](https://github.com/GabZech/template-spec-workflow)) to slow that impulse: agree what matters, then build only what was accepted. Every step ends with an explicit client accept before the next begins.

### 1. Product discovery and foundation

The first stage runs once. Its job is to turn a rough idea into a shared picture of the product, and only then scaffold the system that will hold features.

**Kickoff** locks the problem, vision, non-goals, and how success will be measured. **Understand** deepens that into who the product is for, what they try to do end to end, and the constraints that shape those paths. **Scope** packages those journeys into epics and decides what belongs in the prototype, the MVP, and later. **Prototype** makes the priority journeys clickable in Figma so the flow can be challenged before product code exists. **Foundation** then designs the system once and builds its skeleton: architecture, stack, application shell, and operational basics.

### 2. Feature development

After that, work repeats one feature at a time. Before code, the feature is pinned down in requirements, design, and tasks. Only then is it built, reviewed against the agreed criteria, documented, deployed, and watched in the live environment.

For the full playbook, see the [template workflow overview](https://github.com/GabZech/template-spec-workflow#workflow-overview).

## Docs

Living product definition and engagement status live under [`docs/`](docs/README.md). Start with [`docs/roadmap.md`](docs/roadmap.md) for where we are.
