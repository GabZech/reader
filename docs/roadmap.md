# Roadmap

## Where we are

**🏁 Next milestone:** MVP

**⚠️ Open:** the morning-sync timing target for newsletter ingestion is still unmeasured.

Discovery and Foundation are accepted, and feature work runs the change loop (`.claude/skills/2-develop/`): one change at a time from any epic, previewed when visual, tried on the live app, then merged and shipped.

### Live features

- **Lists and sources:** lists can be created, renamed, and deleted beyond the three that ship by default. A source (RSS or blog feed, YouTube channel, or newsletter) can be added to any list from its own screen, added to further lists, renamed, and deleted; adding a URL that's already a source shows a notice instead of duplicating it.
- **Bringing content in:** RSS and blog feeds pull in automatically within a recency window when added by URL; YouTube channels are added the same way and land in the Favourite channels list. Newsletters arrive through a private mailbox and sit unlisted with a red-dot notice until sorted onto a list.
- **Read later:** a link can be sent to Read Later while browsing. Saved articles sit in a library, move to an archive once finished, resume from wherever reading was left off, and can be removed outright.
- **Reading progress:** every list except Read Later (which has its own Library/Archive and Started/Unstarted state) splits items into Unread and Read, with a "Mark as read" action on the article and automatic tracking as items are opened, so the Home screen shows only what's unread.
- **Highlighting and Obsidian export:** passages can be highlighted on first opening an article, with section titles that stick to the highlights below them and can be deleted along with them. Highlights land as a note in a private Obsidian vault, in the agreed format, kept to roughly one commit per article via an archive/mark-as-read trigger with a day-later fallback.

### Phases completed

- ✅ **Kickoff:** [proposition](vision/proposition.md), [metrics](vision/metrics.md)
- ✅ **Understand:** [personas](vision/personas.md), [journeys](vision/journeys.md), [constraints](vision/constraints.md)
- ✅ **Scope:** [epics](vision/epics.md)
- ✅ **Mockup:** [mockup pointer](mockup/README.md)
- ✅ **Foundation:** [architecture](architecture.md), [development](development.md), [operations](operations.md), [UI guidelines](ui-guidelines.md)
- ✅ **Epic workflow:** replaced by the change loop; see [decisions](decisions.md) 2026-08-28

Session logs for these phases, and the epic-workflow working files, are frozen at git tag `archive/history-2026-09` (was `docs/history/`; collapsed per [decisions](decisions.md) 2026-09-10).

## What's next

Grouped by [epic](vision/epics.md). An epic names a capability, not a work order: pick from any group, in any order. Each unticked line is one turn of the change loop. An unticked line may carry `(in flight)` while it's the one being worked (matching `PROGRESS.md`'s in-flight entry) or `(blocked: <reason>)` when it can't proceed; both are cleared by Ship. A group moves up into "Where we are" once every line in it is ticked.

### Bring the Library Over

- [ ] Import sources from the subscriptions export (OPML)
- [ ] Import saved items from the CSV
- [ ] Import saved items from the folder of files

### Improve UI

Last in the MVP: it needs a full built app to restyle.

- [ ] Revise `ui-guidelines.md` beyond the mockup-era stone and ink look
- [ ] Apply the revised look across every screen already built

### Later

- Evening Video Triage: watching inside the app, the evening session, and filtering Shorts wait. Removing a video from Favourite channels does not wait; it works like removing any other list item

### 📌 Deferred to post-MVP

Choices explicitly put off until after the MVP, each with a real trigger to revisit. Removed once acted on.

- Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the MVP is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed
- One Fly app serves both trying and living. During a change, the live app briefly runs an unmerged branch against the real library. Splitting into separate dev and prod Fly apps is the real fix; revisit once local testing is viable again
- Once the MVP is up, back up the Fly volume's SQLite library regularly (roughly weekly); sources and articles live only on Fly and are never committed to the repo
- The service worker only caches a GET after it succeeds once, and every write (highlight, mark read, archive, progress, sync) is fire-and-forget with no retry. On an unstable connection this reads as the app silently not saving. Revisit once the MVP is in daily use on real mobile networks, with two pieces: queue a failed write (in IndexedDB) and replay it when the connection returns, showing a visible "will sync" state instead of swallowing the error; and pre-cache an article's page as soon as it lands on Read later, not only after it has been opened once, so a saved article is readable offline even on a first attempt
- No visible offline/connectivity state anywhere in the app; a failed action and a slow one currently look the same to the reader. A small persistent indicator (online/offline, syncing) would make the queued-write behaviour above legible instead of mysterious. Bundle with the note above rather than building alone
