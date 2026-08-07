# Kickoff clarifying answers

## Status quo (2026-08-06)

**Tools today:** One existing reading app (vendor-hosted).

**Does it break down?** Not fundamentally — it works, but specific frustrations motivate exploring an alternative.

### Pain 1: Data ownership and portability

- User does not own all content stored in the current tool.
- Cannot build a personal knowledge base from that content for later LLM querying.

### Pain 2: Organising sources in smart/query-based lists

- Smart lists are query-driven; adding a new source requires manual work:
  - Find the source ID
  - Copy it
  - Edit the query by hand
- Desired: intuitive UI (e.g. "add to list" button) instead of query editing.
- Concrete example: lists filtered by recency per source type:
  - Weekly newsletters → items from selected sources received in the past week
  - Daily newsletters → items from selected sources received in the past day
  - Adding a new source to either list today = manual ID + query edit

## Motivation and timing (2026-08-06)

- Trigger: AI tooling makes building something like this feel achievable; user wants to try it out.
- Not driven by the current tool failing outright — more by opportunity + existing annoyances (ownership, list UX).

## Who (2026-08-06)

- Solo use only — not building for other readers from the start.

## Non-goals (2026-08-06)

- No automatic local copies of YouTube videos.
- No automatic transcription of YouTube videos.

## Cost constraint (2026-08-06)

- Target: under $5 USD/month for everything (hosting, storage, email ingestion, domain, third-party APIs).
- Reference point: currently pays $5/month for the existing reading app.
- Flexibility: a little over $5/month is acceptable — trade-off for owning the app and the content.

## Desired outcomes (2026-08-06)

- **Easier curated lists** — less friction than the current tool's manual query/source-ID editing (e.g. weekly vs daily newsletter lists).
- **Own all content** — full data ownership for building a personal knowledge base and LLM querying later.
- **Extensibility** — freedom to add features on their own terms, without waiting on a vendor.

## First release — "good enough" (2026-08-06)

### Core reading flow

- **Home screen** to choose which lists to read.
- **In-app reading:** click a link in an item → content opens and is readable in the app (common for daily newsletter links).
  - **Fallback acceptable:** if in-app reading is hard, opening in a browser tab is fine.
- **Separate reading surface:** ideally a dedicated in-app view; hopes for something like private/incognito mode that auto-closes after a session.

### Devices

- Must be usable from **computer** (desktop/laptop), not only phone.

### Highlights → Obsidian

- Highlight full articles or passages; highlights export as **markdown** into the user's **Obsidian vault**.
- Export should include **article metadata as YAML frontmatter** (client can supply sample exports from the current workflow).
- Ability to add **headings before certain highlights** in the export.
  - Today in the current tool: tries via commenting on a highlight — unreliable; wants a better approach.

### Extensibility (repeated)

- Freedom to add features over time without vendor dependency.

## Failure signals (2026-08-06)

Would stay on the current tool / abandon the build if:

- **Reading quality:** article text is badly formatted; websites or newsletters render broken.
- **Ingestion:** articles cannot be read at all because ingestion is blocked or fails.
- **Cost:** running total exceeds **$10 USD/month** (preferred ~$5; some flex OK; $10+ is a hard fail).
- **Reliability:** app is frequently unavailable.
- **Freshness:** newsletters arrive too slowly — especially morning emails; reads 1–2 newsletters every morning on waking and they **must already be there**.
