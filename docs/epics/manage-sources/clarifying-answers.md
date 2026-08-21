# Add a Source to a List — clarifying answers

Session facts for this epic. Not client prompts.

## Epic (2026-08-20)

This loop covers **Manage sources**: add a source to a list, see its items, and delete it. Living epic name waits for Deploy.

## In / out (2026-08-20)

**In**

- A new RSS or blog feed, YouTube channel, or newsletter gets onto the intended list
- News asks last day or last week on its own screen after the list
- An RSS or blog feed shows how many items it currently has, then the reader chooses all of them, the last 5, only the latest one, or an exact count, before ingest
- YouTube is a public channel feed whose items show on Favourite channels; watching inside the app waits
- Isolated mailbox is live: dedicated alias, forward into a mailbox used only for this app, IMAP on sync. Never personal-mailbox credentials
- Sources shows each source and which list it is on, including the window (for example News (<24h))
- A feed already in Sources opens that source and says it is already there
- See items of this source, and delete source

**Out**

- Morning pass (unseen/seen, send to Read later, mark as seen)
- Read later library, archive, and resume
- Highlighting and vault notes
- Watching videos in the app, the evening session, and filtering Shorts
- Cleaning up the linked article when an item is opened
- Home Edit, removing an item from a list
- Adding an existing source to a list from the source screen
- Renaming the repo, the Fly URL, and the home-screen logo

## Step map (2026-08-20)

1. Add an RSS or blog feed to News (tried; not signed off)
2. Create a new list (signed off)
3. Choose-list: I’ll do this later and create new list (tried; not signed off)
4. Existing source: already-there notice, see items, delete (current)
5. Add an existing source to a list from the source screen
6. Add a YouTube channel to Favourite channels
7. Add a newsletter to News through the isolated mailbox

Judge steps on the live app.

## Increment 1 — RSS or blog to News (2026-08-20)

New RSS or blog enters from Sources via Add source. Paste a feed URL or a blog or Substack page; the app finds the feed; then how many items, list, and window.

Empty paste stays put. A link with no feed says so and stays so another link can be tried. A feed already in Sources does not create a second copy; go to the source that is already there.

Tried on the live app. Choose-list later and create is the current step.

## Increment — Create a new list (2026-08-20)

Signed off. Standalone from add-source. Home Edit waits.

Door is Lists via Add list. Empty name stays put. A name already used does not create a second list; go to the one that is already there. After creating, Lists shows the new list with the others and it can be opened. It does not appear on Home.

A list’s Edit opens rename and delete: name field, Done, and Delete list. Empty stays put. A name already used stays on Edit. The list URL does not change. Delete list returns to Lists; sources that were on it show as not on a list.

## Increment — Choose-list later and create (2026-08-20)

Tried; not signed off. All lists appear on choose-list. Create new list sits with those options. A gap, then I’ll do this later.

I’ll do this later saves the source with no list. Create new list uses the same name screen; after Continue the source goes on that list (News still asks the window). Empty name stays put. A name already used is that existing list.

## Build sign-off (2026-08-21)

Increments 1 (RSS/blog to News), 3 (choose-list-later-or-create-new), and 4 (existing-source notice, see items, delete) signed off after a guided walkthrough on a local instance with real feeds (Hacker News, Lobsters, xkcd). All matched `plan.md`.

Increment 5 (rename a source's display name) signed off. Editable field lives inline on the source screen, next to Save name; a "Saved." message shows underneath the button after a successful save (small UX addition, not in the original plan text). While building this, found and fixed two pre-existing bugs that would have silently undone any rename: `ingest_xml` was resetting `sources.title` back to the feed-provided title on every sync, and `parse_feed` was baking the source's title into `items.author` for entries with no author, freezing the old name on already-ingested items. Both fixed in `app/ingest.py`; the source's originally auto-derived name is now tracked separately in `sources.auto_title` so a rename can be told apart from the feed's own title and an empty-name save can fall back to it.

Next: increment 6, add an existing source to a list from that source's screen.

## Increment — Existing source notice, see items, delete (2026-08-20)

Current. A feed already in Sources still opens that source; the page says it is already there.

Source screen: See items of this source, and Delete source. Add source to list from this screen waits.

See items lists that source’s items (not the list window). Open an item; Close returns to See items. Delete source returns to Sources; the source and its items are gone. No extra confirm, same as Delete list.
