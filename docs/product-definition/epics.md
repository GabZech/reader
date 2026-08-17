# Epics

Named capabilities at the grain of a job, traced to accepted [journeys](journeys.md). They are not user stories. Mockup / first-product / later cuts live here. The clickable dummy is a Figma walkthrough of the solution, not built software. Cross-cutting limits stay in [constraints](constraints.md).

The actor for every epic is [The Solo Reader](personas.md#the-solo-reader).

## Add a Source to a List

**Capability:** Get a newsletter, feed, or YouTube channel onto the intended list in a few clicks, including a per-source recency window on timed lists.

**Journeys:** [Add a Source to a List](journeys.md#add-a-source-to-a-list)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. The learning cut is choosing a recency window when adding a source to a timed list, so the list does not flood with every item. Click-to-add from a source inventory is walkable with it.

## Morning News Pass

**Capability:** Get through the standing morning newsletters on the phone, and park a link to Read later while browsing.

**Journeys:** [Morning News Pass](journeys.md#morning-news-pass)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. The morning session is walkable, including parking a link to Read later. That coupling is in the dummy so the core path is a complete story, not because it is the uncertain design.

## Read-Later Pass

**Capability:** Use free time to read parked articles: library versus archive, started versus unstarted, resume where an item left off, archive when done.

**Journeys:** [Read-Later Pass](journeys.md#read-later-pass)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. The library session is walkable: open, read, archive, resume unfinished items.

## Highlight and Land in Obsidian

**Capability:** Keep passages from an article worth saving in the vault, in the settled markdown format, without a manual export step at the end of the session. Highlight on first open, not only after parking. Sticky section titles apply to following highlights until the next title.

**Journeys:** [Park, Highlight, and Land in Obsidian](journeys.md#park-highlight-and-land-in-obsidian)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. The learning cut is select-to-highlight and click-for-section-title-or-delete, with the vault note as the landing.

## Evening Video Triage

**Capability:** Use evening computer time to watch what looks interesting from favourite channels, without treating the list as a must-watch queue. Full videos only; Shorts filtered out. No local save and no transcription.

**Journeys:** [Evening Video Triage](journeys.md#evening-video-triage)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** later

**Mockup:** no

## Mockup scope

The dummy’s job is learning: whether adding a source to a timed list with a recency window is obvious, and whether highlighting (select to mark; click for a section title or delete) is obvious, with the vault note as the landing.

Morning News Pass and Read-Later Pass are walkable in the same dummy so parking from the morning pass is real. Evening Video Triage is not in the walkthrough.

Morning freshness, in-app extraction quality, the $10 USD/month cost ceiling, and waiting for a newsletter’s first email are carried as risk. The dummy will not settle them.

## First product (MVP)

The first product completes a recognisable loop: sources land on lists, the morning newsletters can be read and parked, parked articles can be worked through, and passages land in the vault.

That is **Add a Source to a List**, **Morning News Pass**, **Read-Later Pass**, and **Highlight and Land in Obsidian** together. Omitting any of those four leaves the loop unfinished. **Evening Video Triage** waits.

After Mockup, the first piece to implement is **Add a Source to a List**. The other first-product capabilities do not work without it.

## Later

**Evening Video Triage** waits: browse favourite channels, watch or discard, filter Shorts. Adding mixed-type lists later still stands from Understand; it is not a separate epic yet.

Kickoff non-goals stay out: multi-user, YouTube local save and auto-transcription, feature-for-feature parity, built-in LLM or RAG querying, perfect in-app reading for every site, going through a publisher paywall without access.
