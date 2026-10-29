# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Key highlights.** A "Mark as key" button on the highlight page; a key highlight exports to Obsidian as `- ==text== #key`, so `tag:#key` finds them across the vault. Kinds: behaviour, data/schema (new `is_key` column on `highlights`), visual (button, ★ marker), external system (vault note format). Branch: `dev/key-highlights`.

Shape agreed: explicit mark/unmark routes (never a toggle); merging highlights keeps key; multi-line highlights wrap each line in `==…==` with `#key` once on the first line; image-only gets just the tag; a line containing `==` skips the wrap but keeps the tag. Leaves alone: section titles, copy, delete, Read Later, notes already in the vault. Schema fallback: copy the library off the volume first; the column is additive, so the old app ignores it. Feedback rounds so far: 0. Both pieces built (button as "Mark as key passage" / "Unmark key passage", ★ in the article) and deployed from this branch for trying; waiting on the client's live sign-off. At Ship: tick nothing on the roadmap (no upcoming line), add the key-passage sentence to the roadmap's Highlighting bullet, add the ★ to `docs/ui-guidelines.md` (article line and accent-colour line), clear this entry.

### Planned

1. Mark as key button and export: built, deployed for trying
2. ★ in the article: built, deployed for trying

## Blocked

None.
