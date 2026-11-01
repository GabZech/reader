# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Read later in the article's top bar** (kinds: visual + behaviour), branch `dev/read-later-in-top-bar`. Live is on `main`; nothing deployed from this branch yet. Feedback rounds: 0.

Shape agreed:

- Top bar keeps Close, then Original · Read later · Mark read (shortened labels). Once saved, "Read later" reads "Saved".
- Bottom row: Delete on the left, Archive on the right; Archive only for a saved article.
- Opened from the Read later list: bar is Close · Original; bottom row is Delete | Archive.
- Read later pressed on an article opened from a list also marks it read in that list (it leaves Home and Unread, stays under Read). Opened from a source's own page there is no list, so it is only saved.
- The page stays put after Read later (no reload, online or offline), so the bar does not change under the reader.
- "Saved" is only a label: once saved there is no undo from the article (asked for, then dropped).
- Leaves alone: Mark read, Open original, Archive and Delete behaviour, the offline queue's ordering, swipe actions, wording outside the bar.

### Planned

1. Layout: bar labels and Read later in the bar, bottom row Delete | Archive. Not started.
2. Read later also marks read in the origin list, page stays put. Not started.

Signed-off mockups are in `preview/` (gitignored): `u-news`, `u-news-saved`, `u-later-list`.

## Blocked

None.
