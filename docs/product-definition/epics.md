# Epics

This file names what the product must be able to do, in the way a reader would describe the work, and which of those abilities belong in the clickable Figma, in the first product, or later. These are not implementation tasks. Limits that apply across paths stay in [constraints](constraints.md).

The clickable Figma is a picture of the solution you can click through, not working software. Its purpose is to find out whether the design is understandable before we build.

The person for every item below is [The Solo Reader](personas.md#the-solo-reader).

## Add a Source to a List

**Capability:** Get a newsletter, feed, or YouTube channel onto the intended list in a few clicks. For lists that only show recent items, choose how far back that source should go (for example last day or last week).

**Journeys:** [Add a Source to a List](journeys.md#add-a-source-to-a-list)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**First product or later:** first product

**Mockup:** yes. What we need to find out: when adding a source to a timed list, can you easily choose that time window, so the list does not fill with every item from the source. Adding a source from a list of all sources is in the Figma too.

## Morning News Pass

**Capability:** Get through the standing morning newsletters on the phone, and send a link to Read later while browsing.

**Journeys:** [Morning News Pass](journeys.md#morning-news-pass)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**First product or later:** first product

**Mockup:** yes. You can click through the morning session in Figma, including sending a link to Read later and removing an item from the list. Those steps are in the Figma so the morning path is a complete story, not because they are the uncertain part of the design.

## Read-Later Pass

**Capability:** Use free time to read articles already saved to Read later. Switch between the library and the archive. See started versus unstarted. Resume where an article left off. Archive it when finished.

**Journeys:** [Read-Later Pass](journeys.md#read-later-pass)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**First product or later:** first product

**Mockup:** yes. You can click through the library session in Figma: open, read, archive, resume unfinished articles, and remove an item from the list.

## Highlight and Land in Obsidian

**Capability:** Keep passages from an article worth saving in the Obsidian vault, in the agreed note format, without a separate export step at the end of the session. Highlight on first open, not only after saving to Read later. A section title applies to the highlights that follow it until the next section title.

**Journeys:** [Park, Highlight, and Land in Obsidian](journeys.md#park-highlight-and-land-in-obsidian)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**First product or later:** first product

**Mockup:** yes. What we need to find out: selecting text highlights it; clicking a highlight lets you add a section title or delete it. The Figma also shows the note arriving in the vault.

## Evening Video Triage

**Capability:** Use evening computer time to watch what looks interesting from favourite channels, without treating the list as a must-watch queue. Full videos only; Shorts filtered out. No local save and no transcription.

**Journeys:** [Evening Video Triage](journeys.md#evening-video-triage)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**First product or later:** later for watching videos inside the app, the evening session, and filtering Shorts. Removing a YouTube item from a list does not wait; it works the same as removing any other list item.

**Mockup:** yes, in part. Favourite channels appears on the home page, and you can remove an item from it like any other list. Watching inside the app, the evening session, and filtering Shorts are not in the Figma.

## Mockup

The Figma is there to find out two things: whether choosing a time window when adding a source to a timed list is obvious, and whether highlighting is obvious (select text to highlight; click a highlight to add a section title or delete it), including the note in the vault.

It also shows the home page and the basic workings of the app: the lists in the picture (News, Read later, Favourite channels), a list of all sources, moving between those parts, and removing any item from the list it is on. A YouTube item is not treated as a special case.

You can click through Morning News Pass and Read-Later Pass so sending a link from the morning session to Read later makes sense as one story. Watching videos inside the app and filtering Shorts are not in the Figma.

The Figma cannot prove that morning newsletters are already in News once the source has sent, that articles you actually read stay readable inside the app, that operating cost stays at or under $10 USD/month, or that adding a newsletter can finish before the first email arrives. We accept those as open risks; they do not change what belongs in the first product.

## First product

The first product has to be usable as a whole: sources land on lists (including YouTube channels), any item can be removed from the list it is on, the morning newsletters can be read and sent to Read later, parked articles can be worked through, and passages land in the vault.

That is **Add a Source to a List**, **Morning News Pass**, **Read-Later Pass**, and **Highlight and Land in Obsidian**, plus removing an item from any list. Leave one of those four out and the first product is not worth using. **Evening Video Triage** waits for watching inside the app, the evening session, and filtering Shorts.

After the Figma, the first thing to build is **Add a Source to a List**. The rest of the first product does not work without it.

## Later

**Evening Video Triage** waits: watching inside the app, the evening computer session, and filtering Shorts. Adding a YouTube channel and removing a video from a list do not wait. More lists later, including lists that mix YouTube with newsletters or RSS, was already agreed; that is not a separate item here.

These stay out, as already agreed: more than one user, saving YouTube videos locally and auto-transcribing them, matching every feature of the current reading app, built-in questioning of your library with an LLM, perfect in-app reading for every site on the web, and going through a publisher paywall without access.
