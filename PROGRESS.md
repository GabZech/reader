# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Offline reading and highlighting** (behaviour + visual), branch `dev/offline-reading`. Read Later articles readable offline without being opened first; highlights and highlight edits (section and subsection titles, key passage, delete) made offline are kept on the device and sent once back online. Leaves alone: archive, mark as read and swipe moves offline (stay deferred in the roadmap). Feedback rounds: 1 (first try on the iPhone: nothing opened offline; the download ask reached the older worker, and a renamed cache wiped stored pages; fixed). 2 (Read Later and Home opened offline but articles did not: the download was cut short before reaching them; now runs four at once, articles first, and Home’s cog turns while it runs, at the client’s ask).

### Planned

1. Download ahead: Read Later article pages (and images, within a storage cap) cached whenever the app opens online; articles looked up by item number alone when offline; cached copy refreshed after a highlight save; Home and every list page refreshed too. Done: signed off on the iPhone (Read Later and its articles open in airplane mode; cog turns while downloading)
2. Offline highlights: drawn at once, queued in IndexedDB, replayed when back online; reading position via the same queue; the server returns the existing highlight for an identical span so a replay never duplicates. Built and deployed, awaiting the iPhone try (reading position kept in localStorage, not IndexedDB: written as the page goes away)
3. Offline highlight page: any highlight's page built on the device from the article's data; section/subsection title, key and delete work offline and queue after the highlight they belong to (temporary id mapped to the real one); an edit to a highlight gone from the server is dropped. Built and committed, not deployed: one browser test failed once in six repeat runs, not yet identified
4. Sync indicator: unsynced highlights look distinct; a small offline / waiting-to-sync indicator. Mockup first. Not started

## Blocked

None.
