# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Join sentences the source wrapped, in the Obsidian export** (Bug). Branch `dev/export-wrapped-lines`, stacked on `dev/highlight-export-links` (PR #84, open, not merged by the client's choice).

- Cause: some sources (Vitalik Buterin's site) hard-wrap paragraphs in their HTML, so a highlight's captured text breaks mid-sentence and each line became a nested bullet. Fix: the export rebuilds a highlight's lines from the saved article (one per paragraph or list item, wrapped whitespace collapsed) and falls back to the old line splitting when the article no longer matches. Leaves alone: capture and storage, notes already in the vault.
- Built and tested; not deployed. Open question for the client: re-send past notes broken this way, as was done for links.
- Next step: client decides on the re-send, then deploy for Try, then ship (roadmap line, PR retargeted to `main` once #84 merges).

## Blocked

None.
