# Roadmap

## Where We Are

**📍 Phase:** Requirements for Add a Source to a List (not started)

**🏁 Milestone:** MVP

**📄 Summary:**

- Foundation accepted: architecture, development, operations, UI guidelines, and a walking skeleton that follows the accepted look, including a live Fly URL
- Requirements is next: user stories and acceptance criteria for adding a source to a list
- The live isolated mailbox remains explicit remaining risk; it is not this phase's stories

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
  - First product completes add-to-list, morning news, Read later, and highlight-to-Obsidian. Any item can be removed from the list it is on, including YouTube items. Watching videos inside the app in the evening, and filtering Shorts, wait
  - Overall look follows the accepted dummy: layout, density, chrome, and quiet type. No icons and no brand colour system
  - One Python web app, SQLite library file, Docker image, PWA cache on the device. Fly.io is the intended host until there is a domain or a machine at home
  - Newsletters: dedicated alias, forward into a separate mailbox used only for this app, IMAP on sync. Never personal-mailbox credentials. Live inbox is part of building Add a Source to a List
  - After Foundation, the first thing to build is adding a source to a list
  - Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the first product is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed
- **Out**
  - Multi-user or shared accounts
  - YouTube local save and auto-transcription
  - Feature-for-feature parity with the current reading app
  - Built-in LLM or RAG querying in the first release
  - Perfect in-app reading for every site on the web
  - Going through a publisher paywall without their access
  - An events list or a separate weekend-events session

**⚠️ Open:**

- User stories and acceptance criteria for Add a Source to a List (Requirements), including how many RSS items to ingest when a feed is first added

## Concluded

- ✅ **Kickoff:** [vision](product-definition/vision.md), [metrics](product-definition/metrics.md); session log under [history/discovery/01-kickoff](history/discovery/01-kickoff/)
- ✅ **Understand:** [personas](product-definition/personas.md), [journeys](product-definition/journeys.md), [constraints](product-definition/constraints.md); session log under [history/discovery/02-understand](history/discovery/02-understand/)
- ✅ **Scope:** [epics](product-definition/epics.md); session log under [history/discovery/03-scope](history/discovery/03-scope/)
- ✅ **Mockup:** [mockup](history/discovery/04-mockup/mockup.md); session log under [history/discovery/04-mockup](history/discovery/04-mockup/)
- ✅ **Foundation:** [architecture](architecture.md), [development](development.md), [operations](operations.md), [UI guidelines](ui-guidelines.md); session log under [history/discovery/05-foundation](history/discovery/05-foundation/)
