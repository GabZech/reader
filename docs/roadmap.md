# Roadmap

## Where We Are

**🏁 Next Milestone:** MVP

**📄 Summary:**

- Discovery and Foundation are accepted, and feature work runs the change loop (`.claude/skills/2-develop/`): one change at a time from any epic, previewed when visual, tried on the live app, then merged and shipped
- Manage Lists, Manage Sources, and Read Later's core line (send in, library/archive, resume, delete) are fully built; every list carries Unread/Read with automatic seen tracking
- Newsletters land from the isolated mailbox and RSS, blog, and YouTube sources all work end to end on the live host

**⚠️ Open:**

- The morning-sync timing target for newsletter ingestion is still unmeasured

## What's Next

Grouped by [epic](vision/epics.md). An epic names a capability, not a work order: pick from any group, in any order. Each unticked line is one turn of the change loop.

### Manage Lists

- [x] Create, rename, and delete a list beyond the three that ship

### Manage Sources

- [x] Feed or blog URL onto News, with a recency window
- [x] Choose a list on add, create one during add, or leave the source unlisted
- [x] Existing-source notice, see a source's items, delete a source
- [x] Rename a source's display name
- [x] Add a source to further lists from its own screen; a source can be on several
- [x] YouTube channel onto Favourite channels
- [x] Newsletters land from the isolated mailbox, unlisted, with a red-dot notice

### Bring the Library Over

- [ ] Import sources from the subscriptions export (OPML)
- [ ] Import saved items from the CSV
- [ ] Import saved items from the folder of files

### Read Later

- [x] Send a link to Read later while browsing
- [x] Library and archive
- [ ] Started and unstarted apart on this list as an explicit label (the seen tracking below already carries the signal; resume shipped without adding this label, so it's still open)
- [x] Resume an article where it was left
- [x] Archive a finished article, and remove an item from Read later

### Reading Progress

Not its own epic in [epics](vision/epics.md); tracked here since it is built. Applies to every list except Read later, which uses Library/Archive and Started/Unstarted instead.

- [x] Unread/Read split on every other list, with a Mark as read action on the article page; Home shows unread only
- [x] Automatic seen tracking: an item's row is bold until first opened, everywhere it is listed

### Highlight and Land in Obsidian

- [ ] Highlight passages on first open
- [ ] Section titles that stick to the highlights below them, and deleting a highlight
- [ ] The note arriving in the vault in the agreed format

### Improve UI

Last in the MVP: it needs a full built app to restyle.

- [ ] Revise `ui-guidelines.md` beyond the mockup-era stone and ink look
- [ ] Apply the revised look across every screen already built

### Later

- Evening Video Triage: watching inside the app, the evening session, and filtering Shorts wait. Removing a video from Favourite channels does not wait; it works like removing any other list item

## 📌 Post-MVP Notes

- Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the MVP is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed
- One Fly app serves both trying and living. During a change, the live app briefly runs an unmerged branch against the real library. Splitting into separate dev and prod Fly apps is the real fix; revisit once local testing is viable again
- Once the MVP is up, back up the Fly volume's SQLite library regularly (roughly weekly); sources and articles live only on Fly and are never committed to the repo

## Concluded

- ✅ **Kickoff:** [proposition](vision/proposition.md), [metrics](vision/metrics.md); session log under [history/discovery/01-kickoff](history/discovery/01-kickoff/)
- ✅ **Understand:** [personas](vision/personas.md), [journeys](vision/journeys.md), [constraints](vision/constraints.md); session log under [history/discovery/02-understand](history/discovery/02-understand/)
- ✅ **Scope:** [epics](vision/epics.md); session log under [history/discovery/03-scope](history/discovery/03-scope/)
- ✅ **Mockup:** [mockup](history/discovery/04-mockup/mockup.md); session log under [history/discovery/04-mockup](history/discovery/04-mockup/)
- ✅ **Foundation:** [architecture](architecture.md), [development](development.md), [operations](operations.md), [UI guidelines](ui-guidelines.md); session log under [history/discovery/05-foundation](history/discovery/05-foundation/)
- ✅ **Epic workflow:** replaced by the change loop; working files frozen under [history/epics](history/epics/)
