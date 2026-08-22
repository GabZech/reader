# Roadmap

## Where We Are

**📍 Phase:** Plan for Manage sources (in progress; full re-plan, epic renamed from "Add a Source to a List")

**🏁 Milestone:** MVP

**📄 Summary:**

- Foundation accepted: architecture, development, operations, UI guidelines, and a walking skeleton that follows the accepted look, including a live Fly URL
- The epic previously tracked as "Add a Source to a List" is renamed **Manage sources** to match `docs/vision/epics.md`; some increments (RSS/blog to News, list membership, existing-source notice/see items/delete) already run but are being re-planned as part of this epic's full increment map, not discarded
- A new **Improve UI** epic was added to the MVP catalog, last in build order: it revisits `docs/ui-guidelines.md` beyond the mockup-era look once the rest of the MVP is built
- The live isolated mailbox remains explicit remaining risk within Manage sources

**❗ Decisions:**

- **In**
  - Built for one person only; not a shared or multi-user product
  - Full ownership of ingested content and highlights in client-controlled formats
  - Obsidian export matches the settled markdown sample (frontmatter, title, summary, highlights, section headings)
  - Morning newsletters must be in the News list after a typical-morning sync on open (target under 5 seconds, 10 seconds ceiling), once the source has sent; they stay readable if the connection then drops. First sync and backlog may take longer
  - Phone for morning News (usually home Wi-Fi unless away). Other reading, including Read later, mostly on the phone and sometimes on the computer. Computer primary only for Favourite channels
  - Operating cost about $5 USD/month preferred, $10 USD/month hard ceiling, including any store or developer fees
  - List membership cannot stay as manual author-name or feed-ID query editing. The lists in the picture now are News, Read later, and Favourite channels. More lists may mix types later
  - In-app extraction of the sources actually read must be consistently readable; the browser is a rare escape, not the normal path
  - The MVP completes add-to-list, bringing the existing library over (subscriptions export, saved-item CSV, folder of files), morning news, Read later, and highlight-to-Obsidian. Any item can be removed from the list it is on, including YouTube items. Watching videos inside the app in the evening, and filtering Shorts, wait. Adding sources by hand does not wait.
  - Overall look follows the accepted dummy for now: layout, density, chrome, and quiet type. The no-icons / no-brand-colour rule is a mockup-era guideline, not an MVP lock: the new **Improve UI** epic (last in the MVP) revisits `docs/ui-guidelines.md` once the rest of the MVP is built, and may introduce icons and colour
  - One Python web app, SQLite library file, Docker image, PWA cache on the device. Fly.io is the intended host until there is a domain or a machine at home
  - Newsletters: dedicated alias, forward into a separate mailbox used only for this app, IMAP on sync. Never personal-mailbox credentials. Live inbox is part of building Add a Source to a List
  - After Foundation, the first thing to build is adding a source to a list
  - Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the MVP is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed
  - Once the MVP is up, back up the Fly volume's SQLite library regularly (roughly weekly); sources and articles live only on Fly and are never committed to the repo
- **Out**
  - Multi-user or shared accounts
  - YouTube local save and auto-transcription
  - Feature-for-feature parity with the current reading app
  - Built-in LLM or RAG querying in the first release
  - Perfect in-app reading for every site on the web
  - Going through a publisher paywall without their access
  - An events list or a separate weekend-events session

**⚠️ Open:**

- How Add a Source to a List is split into tryable increments, including how a new source enters and the isolated mailbox
- Once the MVP is up, set up regular (e.g. weekly) backups of the Fly SQLite data volume

## Concluded

- ✅ **Kickoff:** [proposition](vision/proposition.md), [metrics](vision/metrics.md); session log under [history/discovery/01-kickoff](history/discovery/01-kickoff/)
- ✅ **Understand:** [personas](vision/personas.md), [journeys](vision/journeys.md), [constraints](vision/constraints.md); session log under [history/discovery/02-understand](history/discovery/02-understand/)
- ✅ **Scope:** [epics](vision/epics.md); session log under [history/discovery/03-scope](history/discovery/03-scope/)
- ✅ **Mockup:** [mockup](history/discovery/04-mockup/mockup.md); session log under [history/discovery/04-mockup](history/discovery/04-mockup/)
- ✅ **Foundation:** [architecture](architecture.md), [development](development.md), [operations](operations.md), [UI guidelines](ui-guidelines.md); session log under [history/discovery/05-foundation](history/discovery/05-foundation/)
