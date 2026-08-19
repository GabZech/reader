# Roadmap

## Where We Are

**📍 Phase:** Foundation (not started)

**🏁 Milestone:** Mockup

**📄 Summary:**

- Mockup accepted: the clickable dummy and overall look are locked in [mockup](product-definition/mockup.md)
- Foundation is next: stack, architecture, operational basics, and an application shell that follows that look
- After Foundation, the first feature to build is adding a source to a list

**❗ Decisions:**

- **In**
  - Built for one person only; not a shared or multi-user product
  - Full ownership of ingested content and highlights in client-controlled formats
  - Obsidian export matches the settled markdown sample (frontmatter, title, summary, highlights, section headings)
  - Morning newsletters must already be in the News list by the phone pass, once the source has sent
  - Phone for morning News (usually home Wi-Fi unless away). Other reading, including Read later, mostly on the phone and sometimes on the computer. Computer primary only for Favourite channels
  - Operating cost about $5 USD/month preferred, $10 USD/month hard ceiling, including any store or developer fees
  - List membership cannot stay as manual author-name or feed-ID query editing. The lists in the picture now are News, Read later, and Favourite channels. More lists may mix types later
  - In-app extraction of the sources actually read must be consistently readable; the browser is a rare escape, not the normal path
  - First product completes add-to-list, morning news, Read later, and highlight-to-Obsidian. Any item can be removed from the list it is on, including YouTube items. Watching videos inside the app in the evening, and filtering Shorts, wait
  - Overall look follows the accepted dummy: layout, density, chrome, and quiet type. No icons and no brand colour system
  - How inbound email works is chosen in Foundation. Standing up the live inbox is part of building Add a Source to a List
  - After Foundation, the first thing to build is adding a source to a list
- **Out**
  - Multi-user or shared accounts
  - YouTube local save and auto-transcription
  - Feature-for-feature parity with the current reading app
  - Built-in LLM or RAG querying in the first release
  - Perfect in-app reading for every site on the web
  - Going through a publisher paywall without their access
  - An events list or a separate weekend-events session

**⚠️ Open:**

- Stack, architecture, application shell, and operational basics, including how email is received (Foundation)

## Concluded

- ✅ **Kickoff:** [vision](product-definition/vision.md), [metrics](product-definition/metrics.md); session log under [history/discovery/01-kickoff](history/discovery/01-kickoff/)
- ✅ **Understand:** [personas](product-definition/personas.md), [journeys](product-definition/journeys.md), [constraints](product-definition/constraints.md); session log under [history/discovery/02-understand](history/discovery/02-understand/)
- ✅ **Scope:** [epics](product-definition/epics.md); session log under [history/discovery/03-scope](history/discovery/03-scope/)
- ✅ **Mockup:** [mockup](product-definition/mockup.md); session log under [history/discovery/04-mockup](history/discovery/04-mockup/)
