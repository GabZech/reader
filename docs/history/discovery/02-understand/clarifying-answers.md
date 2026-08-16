# Understand clarifying answers

## Morning and other sessions (2026-08-16)

**Morning (typical):** Opens the current reading app, goes to the "News" list, and reads two newsletters. If time remains, may read a third.

**Morning sources (last session named):** A traditional newspaper newsletter and an AI news newsletter.

**Deferral:** If a newsletter contains an article worth a detailed read and there is not time in the moment, the item is sent to a "read later" list and read at another time.

**Other times of day:** The reader is also used outside the morning session. Lists are chosen by moment, not only by recency.

**Thematic lists (examples given):**
- Favourite YouTube channels — opened when the goal is entertainment
- An "events" list of newsletters about things going on in town — may be read before the weekend. Interaction is the same as a newsletter list (digest, overlay, close, continue).

**Devices:** Morning News is on the phone, usually on home Wi-Fi unless the reader is not at home. Computer use is usual in the evening, when there is free time, for watching videos or reading the "read later" list.

**In-app reading (morning):** Reading usually stays inside the app. Newsletters are summaries of articles. If an item looks interesting, it opens in an overlay; after reading, Close returns to the newsletter to continue. For a newspaper article link, the overlay shows the full original page, not extracted text. The original design is valued because it matches how the author published it.

**Volunteered preference (not current-state):** A toggle on the overlay: original page vs an ingested distraction-free view (ads and irrelevant chrome removed).

**Highlighting (today):** Happens when an article is very interesting. The article is added to the "read later" list and highlighted there, not on first open from the newsletter.

**Volunteered preference (not current-state):** Being able to highlight on the original article page after opening the link, so the read-later round-trip is not required just to highlight.

**Obsidian (today):** After highlighting, nothing is done in the reading app. Highlights sync in the background through Readwise, then appear in the Obsidian vault the next time Obsidian is opened. The export step itself is considered fine. The format is static and pre-defined. Sample: [export-example-obsidian.md](export-example-obsidian.md).

**Export format (from sample):** YAML frontmatter with `author`, `published_date`, `source`, `last_highlighted_date`; then `#` title, `## Summary` as a blockquote, `## Highlights`, `###` section headings, and bullet highlights (with bold used inside the text).

**Section titles (today):** `###` headings are added manually while highlighting by attaching a note to a highlight, which exports as a subtitle.

**Volunteered preference (not current-state):** An explicit "section title" on a highlight that applies to following highlights until the next section title, instead of a note-on-highlight workaround.

## Adding sources to lists (2026-08-16)

**Newsletter (today):** Sign up, wait until the first email arrives, copy the author name, open the list query, and manually add an `if author=x` clause.

**RSS (today):** Paste the blog or Substack link; it is added automatically as a feed source and shows up as an individual source in the sources list.

**Timed lists (today):** Some lists only show content from the last day or last week, with the window varying by newsletter frequency. Adding a source into that kind of list is part of the same manual query pain.

**Volunteered preference (not current-state):** A list of all sources, addable to lists in a few clicks. When adding to a timed list, choose the list and a per-source recency window (for example: add to list X, only show entries from the last week for this source).

## YouTube list (2026-08-16)

**Today:** Browse the latest items. If one looks interesting, click and watch. If it is not worth watching, delete it without opening. If unsure or it might be for later, leave it untouched. Watching stays inside the reading app.

Note: This is watching via the current app's lists. That is separate from the Kickoff non-goal of local video save and auto-transcription.

## Edges (2026-08-16)

**Article open (today):** Often cannot access an article because it is behind a paywall. Other frequent failures: wrong formatting, and missing content such as images.

**Recovery (today):** Try reopening the app. Then either leave the item, or, if it is worth reading and the failure was formatting, add it to the save-for-later list, which usually fixes the error.

**Paywall (today):** No path through. The item is left. Hits are always sites the reader does not subscribe to. They have only one newspaper subscription. Even for that subscribed paper, the overlay does not always work. Last recovery named: sign in again in the overlay.

**Morning freshness (today):** The two newsletters are always in the News list if the app is opened after the source has sent them.

**Volunteered preference (not current-state):** Store the login for subscribed sources so it is not necessary to sign in again each time.

**Not taken as a product goal:** Circumventing a publisher paywall without an account at the source.

## Constraints (confirmed, 2026-08-16)

Confirmed from Kickoff plus Understand answers. Client moved click-to-add sources and extraction quality to hard. Overlay original-page default and distraction-free toggle stay soft. Living docs: [personas](../../../product-definition/personas.md), [journeys](../../../product-definition/journeys.md), [constraints](../../../product-definition/constraints.md).

**Hard**
- Solo personal tool; not shared or multi-user.
- Full ownership of ingested content and highlights in client-controlled, exportable formats.
- Obsidian export must match the settled sample: YAML frontmatter (`author`, `published_date`, `source`, `last_highlighted_date`), title, summary, highlights, `###` section headings.
- Morning newsletters must already be in the News list by the morning phone pass, once the source has sent.
- Usable on phone (morning News) and computer (evening read-later and video).
- Operating cost at or under $10 USD/month (about $5 preferred), including hosting, ingestion, and any store or developer fees.
- Must not: YouTube local save or auto-transcription; built-in LLM/RAG in the first release; unauthorised paywall circumvention; chasing feature-for-feature parity with the current app.
- Source inventory with click-to-add to lists, including a per-source recency window for timed lists. Manual author-name / feed-ID query editing is not an acceptable standing workflow.
- In-app extraction of newsletters, RSS, and other source content must be consistently readable (layout and images). Opening in the browser should be rare, not a standing workaround. This is not a promise of perfection for every site on the web.

**Soft (limits that remain in constraints.md):**
- Avoid a paid Apple Developer / App Store path if that would blow the monthly cost ceiling.
- Readwise as the sync hop is current-state, not required, as long as the vault format still lands.

Path-specific wishes (highlight on first open, sticky section titles, overlay toggle, persist login, click-to-add UI) moved to **Wanted** on the matching journey.

## Gap check (2026-08-16)

**Lists:** The named set (News, read-later, YouTube channels, events) is enough for now. Other lists will be added later, including lists that mix YouTube videos with newsletter or RSS sources. A list is a moment grouping, not a single media type.

**Morning connectivity:** Usually home Wi-Fi, unless not at home.

## Doc split (2026-08-16)

Personas hold who/why; journeys hold as-is steps plus **Wanted** (what should differ on that path). Constraints hold cross-cutting limits only, not product wishes. Split lives in the Understand skill.

## Accept (2026-08-16)

Understand accepted. Scope is next but not started in this session.
