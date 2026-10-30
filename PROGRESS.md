# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Saved copy first, refresh on open** (Behaviour), branch `dev/cache-first`. Online, pages and articles open from the phone's stored copy; updates come in each time the app is opened (the cog turning), plus right after a change made on this phone. Leaves alone: what is stored, the outbox, the 5-second sync itself.

### Planned

- Slice 1, stored copy first: navigations answer from the stored copy online; a change made here marks pages stale so their next visit fetches fresh; an article opened from its copy still tells the server; one copy per way in (Home, list, source) so Close and buttons stay right. In progress.
- Slice 2, refresh on every open: each open (launch or return) syncs sources, then refreshes every stored page and article, then shows Home; replaces the once-a-minute page refresh. Not started.

## Blocked

None.
