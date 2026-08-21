---
name: 2-1-plan
description: >-
  Runs Feature Development step 2.1 Plan: choose the epic, map its increments,
  and work out dependencies, failure modes, test approach, and reversibility
  for each before any code is written. Use when roadmap says Plan, after
  Foundation is accepted, after Deploy of the previous epic, when choosing
  which epic to build next, or when a plan needs revisiting mid-epic.
---

# Plan

Turn the next epic into a plan the agent can build from without guessing: which increments, in what order, what each depends on, what can go wrong, and how each will be verified. Confirmed conversationally with the client, then written once as `plan.md` for the agent to build against. Not a spec: thin enough for a simple epic, no requirements/design/tasks trilogy, no user stories.

## Entry

- Foundation is accepted, or the previous epic's Deploy is done (or the client asked to ship mid-epic)
- `docs/vision/epics.md` names the catalog
- Confirm which epic this loop covers before creating `docs/epics/<epic-slug>/`. Skip that confirm when resuming an epic whose plan already exists (including return from a mid-epic Deploy) and only the next stretch of increments needs planning
- Or Build found a deviation from `plan.md` significant enough to need reconfirming

## Artifacts

- `docs/epics/<epic-slug>/plan.md`: the epic's increment map plus, per increment, its job, dependencies, failure modes, test approach, and reversibility. Agent-facing working memory, not a client deliverable: write it after the client has confirmed it in chat, not the other way round.

## Do

**Include:**
- Clarifying questions via the **questioning** skill. **What to ask:** [questionbank.md](questionbank.md). Skip what earlier phases or this conversation already answered.
- Which epic this loop covers, then that epic's in/out; each one confirm, in chat.
- Increment map for the whole epic: ordered vertical slices, each tryable alone; one confirm.
- Per increment: the job, its dependencies (on earlier increments, the Foundation skeleton, or outside systems), failure modes and edge cases worth guarding, how it will be verified (automated test vs. manual try), and, for anything hard to undo, the fallback if it ships wrong. Propose from journeys, dummy, epics, architecture, and Foundation; confirm.
- Depth proportional to the epic: a small epic gets a few sentences per increment; a risky or multi-part one gets more. Do not pad a simple epic to look thorough.
- Write `plan.md` once the client has confirmed the map and per-increment shape in chat.

**Exclude:**
- Writing code, tests, or touching the running app
- `requirements.md`, `design.md`, `tasks.md`, user stories, acceptance-criteria files
- Asking the client to open and review `plan.md` line by line. The gate is a conversational summary (scope, order, key risks), per questioning. Point them at the file itself only when an item is high-stakes (hard to reverse, or conflicts with a locked decision) or they ask to see it
- Pulling in another epic, restyling, or reopening Foundation unless this epic cannot honour it

**Human role:** Confirm which epic this loop covers; confirm epic in/out; confirm the increment map and each increment's dependencies, failure modes, and test approach as they're proposed; open `plan.md` only on request or when an item is flagged high-stakes; give the go-ahead to start building.

## Clarifying questions

Goal: work out how this epic will be built before any of it is. Defer trying it to Build; defer production release to Deploy.

### Principles

1. **Reuse locks.** Journeys, dummy, epics, and Foundation are inputs. Reopen only if this epic cannot honour them.
2. **Propose, don't quiz.** Epic choice, boundary, increment map, and each increment's shape are inferred and shown for confirm, never an open list the client must invent.
3. **Think in failure, not just success.** For each increment, name what could go wrong (bad, missing, or duplicate input; a slow or down outside system; partial completion; concurrent use) before it's built, not after a bug report.
4. **Name how it will be checked.** Decide the test approach per increment while planning, so Build has a check to run instead of "looks done."
5. **Flag what's hard to undo.** Schema changes, external setup, irreversible deletes: name the fallback now, while it's cheap to think about. Skip this cluster entirely where nothing on the increment is hard to undo.
6. **The gate is a conversation.** Summarize the plan in chat for confirm; do not make the client review a document to approve it. Reserve the document itself for high-stakes items or an explicit request.
7. **Stay in Plan.** No code, no whole-system redesign, no other epics.

### Flow

1. Orient once: this plans the epic before building it; trying it and shipping it are later phases. If the epic for this loop is not yet confirmed: show the defined catalog in the message (name, MVP or later, already built or not), recommend which to start, one confirm.
2. Propose in/out for this epic; one confirm.
3. Propose the increment map for the whole epic; one confirm.
4. Per increment, propose job, dependencies, failure modes, test approach, and reversibility; confirm each, or a batch when several increments are simple and similar.
5. Name the risk register: what stays open and carries into Build and Deploy.
6. Summarize the full plan in chat; write `plan.md`.
7. Gap check; ask to start building.

### Ready to write plan.md when

- Epic and its in/out are confirmed
- Increment map covers the epic and is confirmed
- Every increment has a confirmed job, dependencies, failure modes, test approach, and reversibility note (or an explicit "not applicable")
- Open risk for this epic is named

If those are missing, keep asking: do not invent them.

## Gate

After the gap check, summarize the plan in chat and ask to start building. On accept: write or update `plan.md`; update `docs/roadmap.md` per writing-docs (phase → Build for this epic; refresh Summary / Decisions / Open). Do not start Build without confirmation.
