# Roadmap

## Where We Are

**📍 Phase:** Build for Manage sources (in progress)

**🏁 Next Milestone:** MVP

**📄 Summary:**

- Foundation accepted: architecture, development, operations, UI guidelines, and a walking skeleton that follows the accepted look, including a live Fly URL
- Manage sources now has a full increment map at [docs/epics/manage-sources/plan.md](epics/manage-sources/plan.md): finish sign-off on the already-tried RSS/blog-to-News and choose-list increments, then existing-source handling, then add-existing-source-to-list, YouTube channels, and newsletters
- Newsletters are auto-detected, not manually added: mail from a never-seen sender at the isolated mailbox creates its source on its own, unlisted, with a red-dot notice on the Sources button until opened
- A new **Improve UI** epic was added to the MVP catalog, last in build order: it revisits `docs/ui-guidelines.md` beyond the mockup-era look once the rest of the MVP is built
- The live isolated mailbox remains explicit remaining risk within Manage sources

**⚠️ Open:**

- Sign-off still pending on the already-tried RSS/blog-to-News and choose-list increments
- Standing up the live isolated mailbox and proving IMAP sync hits the morning-sync timing target
- Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the MVP is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed

## Concluded

- ✅ **Kickoff:** [proposition](vision/proposition.md), [metrics](vision/metrics.md); session log under [history/discovery/01-kickoff](history/discovery/01-kickoff/)
- ✅ **Understand:** [personas](vision/personas.md), [journeys](vision/journeys.md), [constraints](vision/constraints.md); session log under [history/discovery/02-understand](history/discovery/02-understand/)
- ✅ **Scope:** [epics](vision/epics.md); session log under [history/discovery/03-scope](history/discovery/03-scope/)
- ✅ **Mockup:** [mockup](history/discovery/04-mockup/mockup.md); session log under [history/discovery/04-mockup](history/discovery/04-mockup/)
- ✅ **Foundation:** [architecture](architecture.md), [development](development.md), [operations](operations.md), [UI guidelines](ui-guidelines.md); session log under [history/discovery/05-foundation](history/discovery/05-foundation/)
