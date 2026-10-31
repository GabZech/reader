# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Show why a page fetch failed in Diagnostics** (Behaviour). Branch `dev/show-page-fetch-failures`. Live, the empty Vitalik posts are still blank after the full-text change (#89) and the app logs nothing about page fetches, so the cause is unknown. Agreed: record one line per page fetch the sync makes (post address, outcome such as filled, unreachable with the error, HTTP status, no text, and time taken) in memory, newest 100, shown as a "Page fetches" section on Diagnostics and as `page_fetches` in its JSON; recording must never fail a sync. Leaves alone: what is fetched and kept, sync speed. Deployed to live; the sync showed the real cause: Vitalik's feed (served from vitalik.eth.limo) links every post to the vitalik.ca apex, which has no DNS record, so the fetch failed instantly with ConnectError. Fix agreed and built: when a post's own host cannot be reached and the feed came from a different host, fetch the same path from the feed's host (and use it first for the rest of that sync); the Diagnostics line shows the error text and the host used. Leaves alone: the stored link ("Open original" still points at the dead host). Next: deploy, open Home with the browser, check the post. Feedback rounds: 0.

### Planned

- Slice 1: record and show page fetches in Diagnostics: live, worked
- Slice 2: fetch from the feed's host when a post's own host is dead: built, tests pass, checked against the real feed, awaiting Try

## Blocked

None.
