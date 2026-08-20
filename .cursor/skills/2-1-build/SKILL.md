---
name: 2-1-build
description: >-
  Runs Feature Development step 2.1 Build: choose the epic, then iterative
  vertical increments of that epic on a local instance of the real product,
  with a short try-and-sign-off loop like Mockup. Use when roadmap says Build,
  after Foundation is accepted, after Deploy of the previous epic, when
  choosing which epic to build, when implementing an epic, or when returning
  from a mid-epic Deploy.
---

# Build

Make the current epic usable on a local instance of the real product, one tryable increment at a time. Clarify only what the next slice needs, build it, let the client try it locally, then the next slice. Continuous integration: run the usual local checks before showing a slice. Continuous delivery: keep signed-off work releasable, but do not release it here. This is not a SPEC, not throwaway, and not Deploy.

## Entry

- Foundation is accepted
- `docs/vision/epics.md` names the catalog
- Confirm which epic this loop covers before creating `docs/epics/<epic-slug>/`. Skip that confirm when resuming that epic with work already underway (including return from a mid-epic Deploy), not merely because the epic folder exists

## Artifacts

- Working software on the local product (same app as the walking skeleton)
- `docs/epics/<epic-slug>/clarifying-answers.md` (thin session facts for this open Build: in/out, increment map, leftover risk, current-slice gaps, which increments are signed off; never client prompts)

## Do

**Include:**
- Work on a branch for this epic. Follow `docs/development.md` when present.
- Clarifying questions via the **questioning** skill. **What to ask:** [questionbank.md](questionbank.md). Skip what earlier phases or this conversation already answered.
- Which epic this loop covers, then that epic's in/out and increment map; each one confirm. Vertical slices the client can try, not layers.
- For the current increment only: fill lived-fact gaps, then build. Run the usual local checks before showing. How to try is the local run path in `docs/development.md`. Phone or device judgment uses that same local instance, not the production host.
- After each increment: how to try it locally; one ask (good, or something needed missing). Iterate until signed off. Do not start the next increment until then. Record which increments are signed off.
- If the client asks to put the current state live: enter **Deploy** with only signed-off increments. Do not ship an unfinished slice. Do not offer a production push after every increment.
- Record those session facts in clarifying-answers. Do not copy living docs, and do not grow a behaviour spec the running slice can show.

Do not write requirements, design, or task files. Do not reopen Foundation unless the client asks. Do not pull in other epics. Do not restyle. Do not update overview docs or write decision records (Deploy owns those). Do not deploy to the production host.

**Human role:** Confirm which epic this loop covers; judge each running increment locally; say if it is good or something needed is missing; hold work outside this epic; ask to Deploy the last signed-off state at any time; when the map is done, confirm leftover risk so Deploy can ship the epic.

## Clarifying questions

Goal: gather only what the next increment needs. Defer living-doc alignment and production release to Deploy.

### Principles

1. **Reuse locks.** Journeys, dummy, epics, and Foundation are inputs. Reopen only if this epic cannot honour them.
2. **Epic by proposal.** Show the defined catalog and recommend which loop to start. Confirm; do not ask the client to invent the sequence.
3. **Increment map by proposal.** Infer ordered tryable slices. Prefer high value and low complexity first unless a leftover joint blocks the rest. Confirm; do not ask the client to invent the backlog.
4. **Clarify the current slice only.** Do not specify the whole epic before the first increment.
5. **Try it, do not specify it.** Behaviour still open is cheaper to settle on a running slice than in a document. Clarifying-answers hold that slice's gaps, not a spec of the epic.
6. **Agent verifies, client judges.** Tests, lint, and build are continuous integration. Whether the increment is good is the client's.
7. **Stay in Build.** No overview docs, no SPEC trilogy, no next epic, no production deploy.

### Flow

1. Orient once: local instance, one increment at a time; production release is Deploy (when the epic is done, or when the client asks to ship signed-off work). If this loop's epic is not yet confirmed: show defined epics in the message (name, MVP or later, already built or not); recommend which to start (Scope's named first piece if still unbuilt, otherwise remaining MVP work by dependency); one confirm. Do not start in/out until that epic is confirmed. Skip this confirm when resuming that epic with work already underway.
2. Propose in/out, the increment list, and which is first; one confirm.
3. Clarifying rounds from [questionbank.md](questionbank.md) for the current increment only.
4. Build that increment; self-check; share how to try locally; one ask. Iterate until good.
5. Name the next increment; repeat from step 3 until the map is done, leftover risk is enough, or the client asks to Deploy.
6. Enter Deploy per Gate.

### Ready to build an increment when

- Epic for this loop is confirmed
- Epic in/out is confirmed
- Increment map is confirmed (it may shrink after trying)
- Gaps for this increment are filled

### Ready to show an increment when

- The slice is tryable end to end
- Local checks have been run, or the agent has said why not
- How to try it is stated from the local run path

### Ready to enter Deploy when

- The client asked to ship, and at least one increment is signed off: ship only those
- Or the increment map is done (or leftover risk per remaining increment is explicit), and clarifying-answers name leftovers Deploy must record

If those are missing, keep asking or building: do not invent them.

## Gate

When the map is done: after the gap check, ask to enter Deploy for this epic. On that accept: update `docs/roadmap.md` per writing-docs (phase → Deploy for this epic; refresh Summary / Decisions / Open). Do not enter Deploy without confirmation.

When the client asks to Deploy mid-epic: update `docs/roadmap.md` (phase → Deploy; Summary names a mid-epic ship of signed-off increments); enter Deploy. Do not treat that as epic complete.

On requested behaviour after a sign-off: stay in Build unless they asked to Deploy.
