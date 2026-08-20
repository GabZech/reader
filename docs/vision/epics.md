# Epics

This file names what the product must be able to do, in the way a reader would describe the work, and which of those abilities belong in the clickable dummy, in the MVP, or later. These are not implementation tasks. Limits that apply across paths stay in [constraints](constraints.md).

The clickable dummy is HTML pages you can click through, not working software. Its purpose is to find out whether the design is understandable before we build. It lives under `docs/mockup/`.

The person for every item below is [The Solo Reader](personas.md#the-solo-reader).

Epics are listed in the order you need them: setup and lists before sources, sources before import and reading sessions.

## Manage lists

**Capability:** Create a list, rename it, and delete it, besides the three that are already there (News, Read later, Favourite channels).

**Done when:** You can add a list, change its name, and remove a list you no longer want. Sources that were on a deleted list show as not on a list.

**In / out:**
- **In:** create, rename, and delete a list
- **Out:** which lists appear on Home and in what order (Home Edit); putting sources on lists; removing a single item from a list

**Depends on:** News, Read later, and Favourite channels are already there.

**Journeys:** [Add a Source to a List](journeys.md#add-a-source-to-a-list)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** in part. The dummy shows those lists, and a list’s Edit for rename and delete. Creating a list, and Home Edit, are not the uncertain part of that picture.

## Manage sources

**Capability:** Get a newsletter, feed, or YouTube channel onto the intended list, change that membership, see its items, and delete the source. For lists that only show recent items, choose how far back that source should go (for example last day or last week).

**Done when:** A source is on the intended list with the right window, you can see its items, and you can take the source out.

**In / out:**
- **In:** add a newsletter, feed, or YouTube channel; choose a list; set a recency window when the list is timed; notice when a source is already there; see items of this source; delete the source; add an existing source to a list from that source’s screen. Creating a list during add uses **Manage lists**. Isolated mailbox for newsletters.
- **Out:** morning reading, Read later, highlighting, watching videos inside the app, removing a single item from a list, Home Edit, creating or renaming or deleting lists as their own job

**Depends on:** [Manage lists](#manage-lists)

**Journeys:** [Add a Source to a List](journeys.md#add-a-source-to-a-list)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. What we need to find out: when adding a source to a timed list, can you easily choose that time window, so the list does not fill with every item from the source. The dummy also shows the list of all sources, see items, add to a list, and delete source.

## Bring the Library Over

**Capability:** Move the existing library into this product: import sources from a subscriptions export (OPML), and import items from a CSV and from a folder of files.

**Done when:** The sources that matter are on lists here, and the saved items are in this library, without rebuilding by hand.

**In / out:**
- **In:** import sources from that subscriptions export; import items from the CSV and from the folder of files
- **Out:** adding sources by hand (that is [Manage sources](#manage-sources))

**Depends on:** [Manage sources](#manage-sources)

**Journeys:** [Bring the Library Over](journeys.md#bring-the-library-over)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP. Adding sources by hand in **Manage sources** does not wait. Importing the existing library is also in the MVP, so switching off the current reading app does not mean rebuilding by hand.

**Mockup:** no. The dummy does not cover this import. It was not an uncertainty for the clickable picture.

## Morning News Pass

**Capability:** Get through the standing morning newsletters on the phone, and send a link to Read later while browsing.

**Done when:** You can get through those newsletters on the phone and send a link to Read later. You can remove an item from News.

**In / out:**
- **In:** open and read the morning newsletters; send a link to Read later; remove an item from News
- **Out:** adding sources; highlighting and the vault note; watching videos

**Depends on:** [Manage sources](#manage-sources)

**Journeys:** [Morning News Pass](journeys.md#morning-news-pass)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. You can click through the morning session in the dummy, including sending a link to Read later and removing an item from the list. Those steps are in the dummy so the morning path is a complete story, not because they are the uncertain part of the design.

## Read-Later Pass

**Capability:** Use free time to read articles already saved to Read later. Switch between the library and the archive. See started versus unstarted. Resume where an article left off. Archive it when finished.

**Done when:** You can work through parked articles: library and archive, started and unstarted, resume, archive. You can remove an item from Read later.

**In / out:**
- **In:** library and archive; started and unstarted; resume; archive; remove an item from this list
- **Out:** sending a link here from News (that is [Morning News Pass](#morning-news-pass)); highlighting and the vault note

**Depends on:** [Morning News Pass](#morning-news-pass)

**Journeys:** [Read-Later Pass](journeys.md#read-later-pass)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. You can click through the library session in the dummy: open, read, archive, resume unfinished articles, and remove an item from the list.

## Highlight and Land in Obsidian

**Capability:** Keep passages from an article worth saving in the Obsidian vault, in the agreed note format, without a separate export step at the end of the session. Highlight on first open, not only after saving to Read later. A section title applies to the highlights that follow it until the next section title.

**Done when:** You can highlight on first open, add or remove a section title, delete a highlight, and the note is in the vault in the agreed format.

**In / out:**
- **In:** highlight on first open; sticky section titles; delete a highlight; note arriving in the vault in the agreed format
- **Out:** parking an article on Read later; the reading session around the article

**Depends on:** [Morning News Pass](#morning-news-pass) or [Read-Later Pass](#read-later-pass) (an article is open)

**Journeys:** [Park, Highlight, and Land in Obsidian](journeys.md#park-highlight-and-land-in-obsidian)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** MVP

**Mockup:** yes. What we need to find out: selecting text highlights it; tapping a highlight lets you add a section title or delete it. The dummy does not show the note arriving in the vault.

## Evening Video Triage

**Capability:** Use evening computer time to watch what looks interesting from favourite channels, without treating the list as a must-watch queue. Full videos only; Shorts filtered out. No local save and no transcription.

**Done when:** You can use evening computer time to watch full videos from favourite channels inside the app, skip Shorts, and leave the list as a browse rather than a must-watch queue.

**In / out:**
- **In (later):** watching inside the app; the evening session; filtering Shorts
- **Out of this wait:** adding a YouTube channel ([Manage sources](#manage-sources)); removing a YouTube item from a list (same as removing any other list item)

**Depends on:** [Manage sources](#manage-sources)

**Journeys:** [Evening Video Triage](journeys.md#evening-video-triage)

**Persona:** [The Solo Reader](personas.md#the-solo-reader)

**MVP or later:** later for watching videos inside the app, the evening session, and filtering Shorts. Removing a YouTube item from a list does not wait; it works the same as removing any other list item.

**Mockup:** yes, in part. Favourite channels appears on the home page, and you can remove an item from it like any other list. Watching inside the app, the evening session, and filtering Shorts are not in the dummy.

## Mockup

The HTML dummy is there to find out two things: whether choosing a time window when adding a source to a timed list is obvious, and whether highlighting is obvious (select text to highlight; tap a highlight to add a section title or delete it).

It also shows the home page and the basic workings of the app: the lists in the picture (News, Read later, Favourite channels), a list of all sources, moving between those parts, and removing any item from the list it is on. A YouTube item is not treated as a special case. A list’s Edit can rename or delete that list. Home Edit (which lists appear, and in what order) is in the dummy; it is not in **Manage lists**.

You can click through Morning News Pass and Read-Later Pass so sending a link from the morning session to Read later makes sense as one story. Watching videos inside the app and filtering Shorts are not in the dummy. The dummy does not show the highlight note arriving in the vault.

The dummy cannot prove that morning newsletters are already in News once the source has sent, that articles you actually read stay readable inside the app, that operating cost stays at or under $10 USD/month, or that adding a newsletter can finish before the first email arrives. We accept those as open risks; they do not change what belongs in the MVP.

## MVP

The MVP has to be usable as a whole: you can manage lists besides the three that are already there, sources land on lists (including YouTube channels) and can be removed, the existing library can be brought over, any item can be removed from the list it is on, the morning newsletters can be read and sent to Read later, parked articles can be worked through, and passages land in the vault.

That is **Manage lists**, **Manage sources**, **Bring the Library Over**, **Morning News Pass**, **Read-Later Pass**, and **Highlight and Land in Obsidian**, plus removing an item from any list. Leave one of those out and the MVP is not worth using. **Evening Video Triage** waits for watching inside the app, the evening session, and filtering Shorts.

The first thing to build is **Manage lists**, then **Manage sources**. The rest of the MVP does not work without those.

## Later

**Evening Video Triage** waits: watching inside the app, the evening computer session, and filtering Shorts. Adding a YouTube channel and removing a video from a list do not wait.

These stay out, as already agreed: more than one user, saving YouTube videos locally and auto-transcribing them, matching every feature of the current reading app, built-in questioning of your library with an LLM, perfect in-app reading for every site on the web, and going through a publisher paywall without access.
