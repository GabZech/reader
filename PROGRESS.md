# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Key highlights.** A "Mark as key" button on the highlight page; a key highlight exports to Obsidian as `- ==text== #key`, so `tag:#key` finds them across the vault. Kinds: behaviour, data/schema (new `is_key` column on `highlights`), visual (button, ★ marker), external system (vault note format). Branch: `dev/key-highlights`.

Shape agreed: explicit mark/unmark routes (never a toggle); merging highlights keeps key; multi-line highlights wrap each line in `==…==` with `#key` once on the first line; image-only gets just the tag; a line containing `==` skips the wrap but keeps the tag. Leaves alone: section titles, copy, delete, Read Later, notes already in the vault. Schema fallback: copy the library off the volume first; the column is additive, so the old app ignores it. Feedback rounds so far: 0.

### Planned

1. Mark as key button and export: not started
2. ★ in the article: not started

## Blocked

None.
