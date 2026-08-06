---
name: 2-2-design
description: >-
  Runs Feature Development step 2.2 Design: how the feature fits the existing
  architecture in docs/specs/<feature-slug>/design.md. Use when writing
  design.md, or after Requirements are accepted.
---

# Design

Explain how this feature fits the architecture that already exists.

## Entry

- Requirements for this feature are accepted
- Read `docs/architecture.md` and the accepted `requirements.md`

## Artifact

- `docs/specs/<feature-slug>/design.md`

## Do

**Include:**
- How the feature maps onto existing components and boundaries
- Sequence or interaction diagrams where they clarify behaviour
- Data models and interfaces touched or added
- Error handling approach
- Testing strategy for this feature

**Do not:**
- Propose a new stack or whole-system redesign (Foundation only)
- Reopen Foundation unless the client explicitly asks

If the feature cannot fit the current architecture, stop and ask whether to reopen Foundation.

**Human role:** Review the approach; iterate on fit and interfaces; confirm the design is feasible within the existing system.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Tasks. Do not advance without confirmation.
