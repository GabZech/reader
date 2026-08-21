---
name: 1-5-foundation
description: >-
  Runs the Foundation phase: system architecture, stack, operational basics,
  and a walking-skeleton application shell that follows the accepted mockup
  look, with explicit tradeoff review before any product code. Use when
  roadmap says Foundation, or after Mockup is accepted.
---

# Foundation

Design the system once and build a walking skeleton: a tiny, permanent, tested end-to-end slice that links the main parts, follows the accepted mockup look, and is not the first feature.

## Entry

- Mockup is accepted (`docs/vision/mockup.md` records look and remaining risk)
- First MVP epic to implement is named in `docs/vision/epics.md`

## Artifacts

- `docs/architecture.md` (parts, data flow, stack, inbound mechanism, confirmed tradeoffs)
- `docs/development.md` (run, test, local config)
- `docs/operations.md` (host, deploy, backup, cost, intended run path)
- `docs/ui-guidelines.md` (durable look copied from the dummy; not a design system)
- Application skeleton in the repo (production code and tests; not throwaway)
- `docs/history/discovery/05-foundation/` (clarifying answers: never client prompts)

## Do

**Include:**
- Clarifying questions via the **questioning** skill. **What to ask:** [questionbank.md](questionbank.md). Skip what earlier phases or this conversation already answered.
- System package inferred from constraints and the clusters, including tradeoffs actually in tension; one confirm. **No application code until that confirm.**
- Walking skeleton: look, navigation, connected joints, tests, then the intended run path. If the product must be hosted, that path is a first deploy plus smoke test on a real surface (not only local). Compare the running UI to the guidelines before the client judges it.
- Record artifacts per writing-docs.

Do not restyle. Do not build first-epic behaviour. Do not split into many parts unless a confirmed constraint forces it. Do not start a second decision log (`docs/history/decisions/` is Deploy). If the accepted look cannot be built, say so. Live inbound credentials wait for the first epic’s Build unless the skeleton cannot run without them.

**Human role:** Answer lived-fact asks; confirm or edit recommended splits (ownership, operations, inbound) and the system package before any product code; judge the running skeleton (look, and whether this is the right place to hang the first feature); for a hosted product, complete first-time host signup and the smoke on a real device; accept when remaining risk is explicit.

## Clarifying questions

Goal: gather only what architecture, stack, operations, UI guidelines, and the skeleton need. Defer first-epic behaviour to Build.

### Principles

1. **Reuse locks.** Devices, cost, ownership, first epic, and overall look are inputs. Reopen Understand, Scope, or Mockup only if the system cannot honour them.
2. **Few parts.** Prefer one deployable unit. Split only when a confirmed constraint forces it.
3. **System by proposal.** Infer architecture, stack, build-vs-buy, operational split, skeleton joints, and tradeoffs. Do not ask the client to invent the stack, name which jobs can depend on a vendor, or pick from a generic optimisation quiz.
4. **Tradeoffs before code.** Name the forces actually in tension, which way the proposal leans, and what we give up. One confirm. No application code until aligned.
5. **Walking skeleton, not a spike.** Permanent tested code that links the main parts with a tiny end-to-end function. The dummy was the throwaway. The first epic adds the flesh.
6. **Prove the intended run path.** Local run plus tests if the product is local-only. If it must be hosted: first deploy of the skeleton plus smoke test before accept. Missing Docker or a host CLI is work in this phase, not a reason to skip. Later revisions ship during **Deploy** using `operations.md`; this phase is the first standup. Reliability theatre stays out unless who-operates-it demands it.
7. **Stay in Foundation.** No first-epic behaviour, no design system.

### Flow

1. Orient once: real system and a thin walking skeleton, not the first feature. The dummy is the look spec.
2. Clarifying rounds from [questionbank.md](questionbank.md). Decision clusters (operator split, ownership, inbound) are recommend-and-confirm, not open specialist lists.
3. Propose the system package (map, architecture, stack, inbound, skeleton joints, look extraction, tradeoffs); one confirm. Stop if not aligned: revise, do not scaffold.
4. Write the four docs; extract look into UI guidelines. Fold confirmed tradeoffs into `architecture.md`.
5. Set up the toolchain; build the skeleton; local tests. If hosted: first deploy and smoke (client opens the live URL on a target device).
6. Self-review the running UI against the guidelines; share; one ask: does the look match, and is this the right place to hang the first feature. Iterate until good.
7. **Gap check:** recommend one or two remaining thin spots that still belong in Foundation; one confirm (add, skip, or something else). Then accept.

### Ready to scaffold when

- Landscape, operator, ownership, and inbound needs are clear
- System package and tradeoffs are confirmed
- Look is named for the guidelines

### Ready to show the skeleton when

- Tiny end-to-end function links the main parts
- Intended run path is proven: local tests always; hosted deploy plus smoke if it must be hosted. State a blocker only if the host cannot be stood up (refused account, cost, policy), not because the toolchain was not installed
- Agent has compared the running UI to the guidelines and fixed, or has said why it cannot match yet

### Ready to accept when

- Client has judged the running skeleton (look and joints) or remaining risk is explicit
- If hosted: first deploy is live and the smoke test in `operations.md` has been run
- Docs match the running skeleton; look is in the guidelines
- Remaining risk is explicit, including live resources the first feature still has to stand up (credentials, not the host itself)

If those are missing, keep asking or building: do not invent them.

## Gate

After the gap check, ask for explicit accept. On accept: update `docs/roadmap.md` per writing-docs (phase → Plan for the first MVP epic named in `epics.md`; Milestone → MVP; refresh Summary / Decisions / Open; add Foundation under Concluded with links to architecture, development, operations, UI guidelines, and history); move `docs/vision/mockup.md` to `docs/history/discovery/04-mockup/mockup.md` and drop it from Vision in `docs/README.md` (accepted look must already be in `docs/ui-guidelines.md`). Do not offer a README refresh. Do not advance without confirmation.
