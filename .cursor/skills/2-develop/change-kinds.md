# Change kinds

Procedures behind the table in [SKILL.md](SKILL.md). Open the section for the kinds this change carries; a change carrying several does all of them.

## Behaviour

Write the test before the code, and watch it fail for the right reason: a test that passes before the change proves nothing, and one that fails on an import error proves nothing either.

Cover what the change promises plus the edges that screen already has to survive: empty input, a duplicate, a missing record, something already in the state the change is trying to reach. Skip the test only for a change with no behaviour: pure look, or copy inside existing text.

Run the whole suite, not only the new test, before showing the change and again before merging.

## Bug

Reproduce first, in a test, at the level the bug actually lives. The test must fail **for the reason the client reported**, not for an adjacent reason that happens to be red.

If the reported symptom cannot be reproduced, say so and ask for the conditions rather than fixing what looks broken nearby. A fix without a failing test behind it is a guess.

Keep the test after the fix. It is the regression guard, and it is the reason bugs get their own kind.

## Data / schema

The SQLite library is the one thing in this product that is expensive to get wrong: it lives only on the Fly volume and holds real reading history.

1. Name the fallback in the Shape message: how the library gets back to its current state if the change goes wrong.
2. Copy the library off the volume before anything runs, per `docs/operations.md`. No backup, no migration.
3. Make the migration re-runnable: it must be safe to apply twice, since a deploy can retry.
4. Rehearse on a copy of the real file, not on an empty test database, and check row counts before and after.
5. After shipping, smoke the live path per `docs/operations.md` rather than trusting the deploy log.

A schema change is never small, however few lines it is.

## External system

Mail, feeds, YouTube, the Obsidian vault: anything the product does not control.

1. Write a throwaway probe script that talks to the real system and prints what actually comes back. Keep it out of `app/`.
2. Read the real payload before designing around it. Field names, encodings, date formats, and empty cases are where assumptions break.
3. Save a real response as a fixture and write the tests against that, so the suite does not depend on the outside system being up.
4. Handle the failure modes the probe revealed: unreachable, slow, authenticated but empty, malformed.
5. Credentials go in host environment variables, never the repo. For mail, only the isolated mailbox, never a personal one.
6. Prove it once end to end against the live system before asking for sign-off.
