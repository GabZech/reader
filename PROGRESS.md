# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Title box above the text, and the source under the article title** (Visual + Data/schema). Branch `dev/title-box-and-source`. Shape agreed: the Add section title and Add subsection title pages show the Title box and Done button above the highlighted text; the article page (only, not list rows) gets a source-name line directly under the title, with author, date and length staying on the line below it. Feeds, newsletters and YouTube use their source name; a link saved to Read later stores the page's site name in a new optional `items.site_name` column and falls back to the link's host, which is also what articles saved before this show. Leaves alone: list rows, the highlight page, existing data (no backfill). Feedback rounds so far: 0. Live: `main`.

### Planned

1. Title box above the highlighted text on the section and subsection title pages: built and committed, not yet deployed or tried live
2. Source line under the article title, with the `site_name` column: built and committed, not yet deployed or tried live. Migration rehearsed on a copy made before the column existed (rows unchanged, safe to apply twice); the live library could not be copied from a cloud session

Next step: deploy the branch on the client's go, walk both slices through, then Ship (roadmap tick, docs check).

## Blocked

None.
