# Roadmap

Feature development is currently underway.

## Where we are

### 🔭 Discovery

Before any code was written, a discovery phase mapped out who this app is for and what it needs to do, producing:

- [proposition](vision/proposition.md) and [metrics](vision/metrics.md): the problem this solves and how success is measured
- [personas](vision/personas.md), [journeys](vision/journeys.md), and [constraints](vision/constraints.md): who uses it, how, and the limits to design within
- [epics](vision/epics.md): the capabilities scoped in for the MVP
- [mockup](mockup/README.md): a clickable mockup of the app, built before the real thing
- [architecture](architecture.md), [development](development.md), [operations](operations.md), and [UI guidelines](ui-guidelines.md): the technical foundation the app is built on

Session logs from this phase, and the working files from an earlier per-epic way of running feature work (since replaced by the change loop; see [decisions](decisions.md) 2026-08-28), are frozen at git tag `archive/history-2026-09` (was `docs/history/`; collapsed per [decisions](decisions.md) 2026-09-10).

### ✅ Live features

- **Lists and sources:** lists can be created, renamed, and deleted beyond the three that ship by default. A source (RSS or blog feed, YouTube channel, or newsletter) can be added to any list from its own screen, added to further lists, renamed, and deleted; adding a URL that's already a source shows a notice instead of duplicating it.
- **Bringing content in:** RSS and blog feeds pull in automatically within a recency window when added by URL; YouTube channels are added the same way and land in the Favourite channels list. Newsletters arrive through a private mailbox and sit unlisted with a red-dot notice until sorted onto a list.
- **Read later:** a link can be sent to Read Later while browsing. Saved articles sit in a library, move to an archive once finished (and back again if that was a mistake), resume from wherever reading was left off, and can be removed outright.
- **Reading progress:** every list except Read Later (which has its own Library/Archive and Started/Unstarted state) splits items into Unread and Read, with a "Mark as read" action on the article and automatic tracking as items are opened, so the Home screen shows only what's unread. Swiping a row right to left moves it straight to the other tab (read or unread, archive or library, on Home too), and swiping left to right deletes it after a confirmation.
- **Highlighting and Obsidian export:** passages can be highlighted on first opening an article, including any image the selection covers, which gets an outline in the highlight colour and travels into the export, with section titles that stick to the highlights below them and can be deleted along with them; a highlight carrying a title shows a small `§` before it in the article. Highlights land as a note in a private Obsidian vault, in the agreed format, kept to roughly one commit per article via an archive/mark-as-read trigger with a daily 5am (Brasilia time) fallback.

## What's next

### 🎯 Upcoming features


#### Improve UI


- [ ] Revise `ui-guidelines.md` beyond the mockup-era stone and ink look
- [ ] Apply the revised look across every screen already built

### 📌 Deferred to later

Choices explicitly put off for later, each with a real trigger to revisit. Removed once acted on.

- Bring the Library Over: importing sources from the subscriptions export (OPML), and saved items from the CSV and from the folder of files, so switching off the current reading app doesn't mean rebuilding by hand. Revisit when ready to actually switch off the current reading app
- Evening Video Triage: watching inside the app, the evening session, and filtering Shorts wait. Removing a video from Favourite channels does not wait; it works like removing any other list item
- Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the MVP is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed
- One Fly app serves both trying and living. During a change, the live app briefly runs an unmerged branch against the real library. Splitting into separate dev and prod Fly apps is the real fix; revisit once local testing is viable again
- Once the MVP is up, back up the Fly volume's SQLite library regularly (roughly weekly); sources and articles live only on Fly and are never committed to the repo
- The service worker only caches a GET after it succeeds once, and every write (highlight, mark read, archive, progress, sync) is fire-and-forget with no retry. On an unstable connection this reads as the app silently not saving. Revisit once the MVP is in daily use on real mobile networks, with two pieces: queue a failed write (in IndexedDB) and replay it when the connection returns, showing a visible "will sync" state instead of swallowing the error; and pre-cache an article's page as soon as it lands on Read later, not only after it has been opened once, so a saved article is readable offline even on a first attempt
- No visible offline/connectivity state anywhere in the app; a failed action and a slow one currently look the same to the reader. A small persistent indicator (online/offline, syncing) would make the queued-write behaviour above legible instead of mysterious. Bundle with the note above rather than building alone
