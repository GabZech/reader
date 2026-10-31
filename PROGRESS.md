# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Fetch full text for feed items that come without it** (Bug + Behaviour + External system). Branch `dev/fetch-full-text-for-empty-feed-items`. Vitalik Buterin's feed ships every post with an empty description, so the post opened blank. Agreed: after a source's feed is read, fetch the linked page for every item with no text at all (newest first, no cap per sync at the client's request, retried each sync until a page gives text); clean it with the same extraction Read later uses; skip YouTube; never fail the sync; keep stored text when the feed refresh brings none. An item with any text in the feed, however short, is left alone (the client chose this over a 50-word teaser rule). Leaves alone: schema, feed parsing, Read later capture behaviour, the look. Feedback rounds: 0.

### Planned

- Slice 1: sync fills in the article text (shared extraction, fetch after feed read, feed refresh keeps longer stored text): built, tests pass, awaiting Try
- Slice 2: the phone picks up the new text (article version includes text length): built, tests pass, awaiting Try

## Blocked

None.
