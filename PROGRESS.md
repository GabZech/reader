# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Keep links in the Obsidian export, and re-send past notes** (Bug + Data / external system). Branch `dev/highlight-export-links`.

- Shape agreed: links inside a highlight export as `[text](url)` (partial selection links only the selected words; relative links resolved against the article URL; in-page `#` links stay plain). Past vault notes whose highlights cover a link are re-sent once on the first startup after deploy, which overwrites any hand edits in those notes (client accepted). Leaves alone: bold/italics in the export, highlight capture and storage, notes without links, notes for deleted items.
- Feedback rounds: 0. Not deployed yet: the client asked to hold the deploy.
- Next step: deploy the branch for Try when the client says so, then check a few past notes in the vault gained their links.

### Planned

1. Links survive the export: done (built, not yet tried live)
2. One-time re-send of past notes with links: done (built, not yet tried live)

## Blocked

None.
