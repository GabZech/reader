# Docs

This folder is the living record of the product and how we work on it. Read it to see what has been agreed, not to hunt for filenames. History under `docs/history/` and feature contracts under `docs/specs/` keep their own shape. Everything else here follows the writing-docs skill.

## Product Definition

These files settle who the product is for and what it must do, before a stack is chosen.

- **[Vision](product-definition/vision.md).** The problem that motivates a replacement, the direction we are building toward, and what stays out until we explicitly reopen it.
- **[Metrics](product-definition/metrics.md).** How we will tell whether the product is working, including guardrails such as cost and morning reliability.
- **[Personas](product-definition/personas.md).** Who the product is for. Written in Understand.
- **[Journeys](product-definition/journeys.md).** The overall use cases those people already have, and what should change on each path.
- **[Constraints](product-definition/constraints.md).** Cross-cutting limits that steer every later choice (devices, ownership, cost, freshness).
- **[Epics](product-definition/epics.md).** Named capabilities, which belong in the first product, and which wait. After Foundation, the first thing to build is Add a Source to a List.

## Engagement

- **[Roadmap](roadmap.md).** Where the engagement stands now: current phase, milestone, locked decisions, and what this phase still has to resolve.

## System

Written in Foundation after the system package was confirmed. Refresh later when Documentation aligns them with a built feature.

- **[Architecture](architecture.md).** How the running system is put together: parts, data flow, stack, inbound mail and feeds, and the tradeoffs we accepted. The skeleton section says what this slice proved and what the first feature still has to stand up.
- **[Development](development.md).** How to run and test the app on a local machine. Commands in that file have been run.
- **[Operations](operations.md).** Where the app is meant to run in production, how a new version gets there, how the library file is backed up, and what keeping it on should cost.
- **[UI Guidelines](ui-guidelines.md).** The overall look copied from the accepted dummy. Not a design system. Later screens follow this instead of restyling.
- **[Conventions](conventions.md).** Repo writing conventions that are not product behaviour.
