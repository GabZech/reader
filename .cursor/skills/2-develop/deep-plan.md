# Deep plan

Thinking a change through before building it, when the change is big enough that finding out during step 5 would be expensive. No per-epic file: one confirm in chat.

## When

Either of these, without waiting to be asked:

- Frame sized the change as not small: more than a couple of files, a new route, a schema or dependency change, or a data or external-system change
- Reality contradicts what Shape agreed mid-build: an unnamed dependency, a job that turns out to be a different job

Or on an explicit ask to plan it properly, plan it well, think it through first, or deep plan it. Take the ask at its meaning, not its wording.

## Do

Propose, do not quiz. The client confirms or adjusts; they should never have to invent the structure.

1. **Slices.** Split the change into pieces that each work end to end and can be tried alone, in the order they have to be built. A slice that cannot be tried on its own is not a slice.
2. **Per slice:** what it does, what it depends on (an earlier slice, something already in the app, an outside system), what could go wrong that is worth guarding, and how it will be verified.
3. **Failure modes before success paths.** Bad, missing, or duplicate input; a slow or unreachable outside system; a half-finished operation; the same thing done twice.
4. **Reversibility**, only where something is genuinely hard to undo: schema, external setup, deletes. Name the fallback while it is still cheap to think about. Skip the whole point where nothing qualifies.
5. **Depth in proportion.** A three-slice change gets a few sentences per slice. Do not pad.

Then summarise it in chat and ask for one confirm. Write nothing to `docs/` for this: the confirmed summary is the plan, and the tests plus the live app are the record.

## Then

Run the slices through the loop one at a time, each with its own Preview, Build, and Try. Ship them together at the end, or separately when a slice stands on its own.

If a slice turns out to contradict the plan, come back here rather than improvising forward.

## Do not

- Write `plan.md`, `requirements.md`, `design.md`, `tasks.md`, user stories, or acceptance-criteria files
- Ask the client to review a document to approve it: the gate is the conversation
- Re-derive whole-system architecture or reopen Foundation, unless this change cannot honour it
- Pull in work the client did not ask for
