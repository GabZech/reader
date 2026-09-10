# Docs

This folder is the living record of the product and how we work on it. Read it to see what has been agreed, not to hunt for filenames.

**Where truth lives.** The running app and its tests are behaviour. The living files below are the current agreed picture. History under `docs/history/` is how we got here; do not update it to match later code. Feature work keeps no separate working record: the conversation is the plan, and these files plus git history are what survives it. Everything here follows the writing-docs skill.

## Vision

These files settle who the product is for and what it must do, before a stack is chosen.

- **[Proposition](vision/proposition.md).** The problem that motivates a replacement, the direction we are building toward, and what stays out until we explicitly reopen it.
- **[Metrics](vision/metrics.md).** How we will tell whether the product is working, including guardrails such as cost and morning reliability.
- **[Personas](vision/personas.md).** Who the product is for. Written in Understand.
- **[Journeys](vision/journeys.md).** The overall use cases those people already have, and what should change on each path.
- **[Constraints](vision/constraints.md).** Cross-cutting limits that steer every later choice (devices, ownership, cost, freshness).
- **[Epics](vision/epics.md).** Named capabilities, which belong in the MVP, and which wait. First piece of the MVP is Manage lists, then Manage sources.

## Engagement

- **[Roadmap](roadmap.md).** Where the product stands now: what is built, what is next grouped by epic, and what is still open.

## System

Written in Foundation after the system package was confirmed. Refreshed as part of any change that makes one of them wrong.

- **[Architecture](architecture.md).** How the running system is put together: parts, data flow, stack, inbound mail and feeds, and the tradeoffs we accepted. The skeleton section says what this slice proved and what the first feature still has to stand up.
- **[Development](development.md).** How to run and test the app on a local machine. Commands in that file have been run.
- **[Operations](operations.md).** Where the app is meant to run in production, how a new version gets there, how the library file is backed up, and what keeping it on should cost.
- **[UI Guidelines](ui-guidelines.md).** The overall look copied from the accepted dummy. Not a design system. Later screens follow this instead of restyling.
