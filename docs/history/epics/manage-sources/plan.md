# Manage sources — plan

Working plan for Build. Confirmed with the client in chat; not a client deliverable. Supersedes the increment detail in [clarifying-answers.md](clarifying-answers.md) as the reference for Build, though that file's notes on increments already tried remain accurate.

## Epic boundary

**In:** add a newsletter, feed, or YouTube channel; choose a list; set a recency window when the list is timed; notice when a source is already there; see items of a source; delete a source; add an existing source to a list from that source's screen; creating a list during add (uses Manage lists); the isolated newsletter mailbox.

**Out:** morning reading, Read later, highlighting, watching videos inside the app, removing a single item from a list, Home Edit, creating/renaming/deleting lists as their own job (Manage lists).

## Increment map

1. RSS or blog feed onto News — signed off
2. Create a new list — signed off, already built (Manage lists dependency)
3. Choose-list-later-or-create-new on add — signed off
4. Existing-source notice, see items, delete — signed off
5. Rename a source's display name — signed off
6. Add an existing source to a list from that source's screen — signed off
7. YouTube channel onto Favourite channels — signed off (2026-08-22)
8. Newsletter auto-detected via the isolated mailbox — current, not started, carries the epic's named open risk

## Per increment

### 1. RSS or blog feed onto News

**Job:** from Sources, paste a feed URL or a blog/Substack page; the app finds the feed, then asks how many items, which list, and (for News) the window.

**Dependencies:** none beyond the skeleton and Manage lists.

**Failure modes:** empty paste stays put; a link with no discoverable feed says so and stays put so another link can be tried; a feed already in Sources does not create a second copy, goes to the existing source instead.

**Test approach:** manual try on the live app (signed off).

**Reversibility:** not applicable, nothing hard to undo.

### 2. Create a new list

**Job:** from Lists via Add list, name a new list; it appears in Lists alongside the others and can be opened. A list's Edit offers rename and delete.

**Dependencies:** none.

**Failure modes:** empty name stays put; a name already used goes to the existing list instead of duplicating; delete returns to Lists and its sources show as not on a list.

**Test approach:** manual try on the live app (signed off).

**Reversibility:** not applicable, nothing hard to undo.

### 3. Choose-list-later-or-create-new on add

**Job:** on the choose-list step of adding a source, all existing lists appear as options, alongside create-new-list and "I'll do this later." "Later" saves the source unlisted; create-new-list reuses increment 2's naming screen, then the new source lands on it.

**Dependencies:** increments 1 and 2.

**Failure modes:** empty name stays put; a name already used resolves to the existing list.

**Test approach:** manual try on the live app (signed off).

**Reversibility:** not applicable, nothing hard to undo.

### 4. Existing-source notice, see items, delete

**Job:** opening a feed already in Sources shows a notice that it's already there, plus see-items and delete for that source. See-items lists that source's own items (not a list's timed window); delete returns to Sources with the source and its items gone, no extra confirm (same pattern as list delete).

**Dependencies:** increment 1 (a source has to exist to revisit).

**Failure modes:** none beyond what increment 1 already covers on entry.

**Test approach:** manual try on the live app (signed off).

**Reversibility:** not applicable, nothing hard to undo.

### 5. Rename a source's display name

**Job:** on the source screen (same screen as see-items, delete, and add-to-list), the name becomes an editable field, defaulting to whatever the app derived from the feed or sender. The new name shows everywhere the source appears: Sources, the source's own screen, and wherever its items are attributed. Purely cosmetic: the app keeps matching this feed or sender by URL/address, not by name, so renaming can't merge or duplicate sources, and two sources can share a display name without conflict.

**Dependencies:** increment 4 (the source screen already exists to add this field to). The app needs to keep the auto-derived name around separately from the display name, so it has something to fall back to.

**Failure modes:** clearing the name and saving resets it to the auto-derived name rather than refusing to save or leaving it blank.

**Test approach:** manual try — rename a source, confirm the new name shows everywhere it's referenced; clear the name and confirm it falls back to the auto-derived one.

**Reversibility:** not applicable, nothing hard to undo; can be renamed again anytime.

### 6. Add an existing source to a list from that source's screen

**Deviation logged 2026-08-21:** originally planned as single-list-per-source (choosing a list moves the source, no duplicates). While building, the client asked for a source to be able to belong to several lists at once. This changed the underlying data model (list membership moved from a column on `sources` to a many-to-many `source_lists` table) and the shape of this increment; confirmed conversationally before building, so treated as a scope update rather than a return to Plan.

**Job:** from a source's own screen, add it to another list using the same picker as increment 3 (existing lists not already joined, or create-new). The screen lists every list the source currently belongs to, each with its own remove control; removing one membership leaves the others untouched. The Sources page shows the single list's name when a source is on exactly one, or a count ("On 2 lists") when on several.

**Dependencies:** increments 3 and 4.

**Failure modes:** the picker excludes lists the source is already on, so there's no path to a duplicate membership.

**Test approach:** manual try — add a source to a second list and confirm both memberships hold independently; remove one and confirm the other survives; confirm the Sources page byline switches from a list name to a count once a source is on more than one.

**Reversibility:** not applicable, nothing hard to undo.

### 7. YouTube channel onto Favourite channels

**Job:** the same add-source entry point from increment 1 also recognizes a channel URL; its items land on Favourite channels. No window ask, since only News is timed.

**Dependencies:** increment 1's URL handling; increment 4's see-items/delete for the source once added.

**Failure modes:** a URL that isn't a channel (single video, playlist) says so and stays put; a private or unavailable channel says so; a channel already added hits the increment 4 notice, not a duplicate.

**Test approach:** manual try with a real public YouTube channel (signed off 2026-08-22, tried on the live app via trial push).

**Reversibility:** not applicable, nothing hard to undo.

### 8. Newsletter auto-detected via the isolated mailbox

**Job:** no manual add step. When mail arrives at the dedicated app-only mailbox from a sender never seen before, the app creates that source on its own, unlisted. The Sources button in the bottom menu shows a red dot whenever at least one such new, not-yet-listed source is waiting; the dot clears when Sources is opened. From there the reader lists it using increment 6's picker, same as any unlisted source. Mail from a sender already known just adds items to the existing source, no new dot.

**Dependencies:** the live isolated mailbox being stood up (Foundation leftover, already the epic's named open risk); increment 6 for listing the new source once it appears; increment 1's list/window choice for News.

**Failure modes:** an unwanted sender auto-creates a source the reader doesn't want, handled the same as any unwanted source: delete it (increment 4). "Forward never set up" and "set up but nothing sent yet" are indistinguishable to the app; both simply show nothing has arrived, no special detection.

**Test approach:** real end-to-end try against the live mailbox: set up the forward, send a real newsletter, sync, confirm timing against the morning-sync target (under 5s typical, 10s ceiling).

**Reversibility:** standing up the live mailbox/alias is externally fiddly to unwind once wired up. Fallback: keep the current reading app's newsletter handling running until this increment is verified live end to end; do not cut over before that.

## Open risk

The live isolated mailbox (setup, IMAP sync reliability, and hitting the morning-sync timing target) is this epic's explicit carried risk into Build and Deploy, as already named in `docs/roadmap.md`.
