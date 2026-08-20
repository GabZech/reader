# Journeys

These are current-state overall use cases at discovery grain. They are not user stories and not mockup / MVP scope. The actor is [The Solo Reader](personas.md#the-solo-reader).

**Steps today** are as-is. **Wanted** is what should differ on that path, not a full as-should walkthrough. As-should journeys wait for Mockup. Cross-cutting limits live in [constraints](constraints.md).

The lists in the picture now are **News**, **Read later**, and **Favourite channels**. More lists will be added later, including lists that mix YouTube videos with newsletter or RSS sources.

## Add a Source to a List

**Actor:** [The Solo Reader](personas.md#the-solo-reader)

**Goal:** Get a new newsletter, feed, or YouTube channel onto the right list, including lists that only show the last day or last week.

**Trigger:** A new source should appear in News, Favourite channels, a timed list, or another list.

**Steps today:**
1. Newsletter: sign up, wait for the first email, copy the author name, open the list query, add an `if author=x` clause by hand.
2. RSS / blog / Substack: paste the link; it is added as a feed source and appears as an individual source in the sources list. Membership in a specific list can still need query work, especially for timed windows.
3. YouTube channel: paste the channel weblink; it is added as a source.

**Outcome:** The source’s items start showing in the intended list, with a recency window that matches how often that source publishes.

**Costly edges:** Newsletter onboarding cannot finish until the first email arrives. Author name and feed ID hunting plus query edits are the standing pain.

**Wanted:** A list of all sources, addable to lists in a few clicks. When adding to a timed list, choose the list and a per-source recency window (for example last week for this source).

## Morning News Pass

**Actor:** [The Solo Reader](personas.md#the-solo-reader)

**Goal:** Get through the standing morning newsletters on the phone before the day takes over.

**Trigger:** Waking / the morning reading slot.

**Steps today:**
1. Open the current reading app on the phone, usually on home Wi-Fi (not when away from home).
2. Open the News list.
3. Read two newsletters (last named: a traditional newspaper newsletter and an AI news newsletter). If time remains, maybe a third.
4. Each newsletter is a summary of articles. Interesting items open in an overlay; Close returns to the newsletter.
5. A newspaper article link opens the full original page in that overlay, not extracted text.
6. If an article needs a detailed read and there is no time, send it to Read later (continues in [Read-Later Pass](#read-later-pass)).

**Outcome:** The morning pair (sometimes a third) has been seen. Some items may be parked for later. The session ends when time runs out or the intended newsletters are done.

**Costly edges:** Overlay often hits a paywall on sites the reader does not subscribe to: the item is left. Formatting can be wrong or images missing: reopen the app, then leave the item, or add it to save-later if it is worth reading and the failure was formatting (that usually repairs it). For the one subscribed newspaper, the overlay does not always stay signed in: recovery last named is signing in again there. Newsletters are present if the app is opened after the source has sent.

**Wanted:** Keep the overlay as the original page by default, with an optional toggle to a distraction-free ingested view (ads and extra chrome removed). Persist login for the one subscribed newspaper so signing in again is not routine.

## Read-Later Pass

**Actor:** [The Solo Reader](personas.md#the-solo-reader)

**Goal:** Use free time to read interesting articles already saved to Read later.

**Trigger:** Having time and wanting to read something from that list.

**Steps today:**
1. Open Read later (mostly on the phone; sometimes on the computer).
2. The library is articles saved to Read later that have not been archived yet. Open an article, then read and highlight (highlighting continues in [Park, Highlight, and Land in Obsidian](#park-highlight-and-land-in-obsidian)).
3. When finished with an article, archive it. It leaves the library but stays saved separately. Re-access is from the Obsidian note, not from the archive.
4. If the session stops mid-article, the item stays in the library marked seen, and reopen resumes where it left off.

**Outcome:** Some items read, highlighted, and archived; unfinished ones remain in the library; the vault has the notes. The session ends when the reader has had enough or has to do something else.

**Costly edges:** None named for resume. Same overlay failures as [Morning News Pass](#morning-news-pass) when an article itself fails to open or format.

**Wanted:** On this list, a toggle between library and archive, not unseen versus seen (the split other lists use). Library stays the not-yet-archived saved articles. Started / unstarted instead of seen. Keep resume on reopen.

## Park, Highlight, and Land in Obsidian

**Actor:** [The Solo Reader](personas.md#the-solo-reader)

**Goal:** Keep passages from an article that is worth saving, in the vault, without a manual export step at the end of the reading session.

**Trigger:** An article is judged very interesting, usually during [Morning News Pass](#morning-news-pass) or [Read-Later Pass](#read-later-pass).

**Steps today:**
1. Add the article to Read later (this is also how highlighting is reached today; first-open highlight is not the current path).
2. Open it from Read later during [Read-Later Pass](#read-later-pass) and highlight there.
3. Attach a note to a highlight when a `###` section heading is needed; that note exports as a subtitle.
4. Do nothing else in the reading app. Readwise syncs in the background.
5. The next time Obsidian is opened, the note is in the vault.

**Outcome:** A markdown note matching the settled export format: YAML frontmatter (`author`, `published_date`, `source`, `last_highlighted_date`), title, summary, and highlights. Sample: [export-example-obsidian.md](../history/discovery/02-understand/export-example-obsidian.md).

**Costly edges:** The export pipe itself is considered fine. The awkward part is assigning section titles while highlighting (note-on-highlight workaround). Highlighting currently requires the Read later round-trip.

**Wanted:** Highlight on the original article on first open, without parking on Read later only to highlight. Sticky section titles: a section title applies to following highlights until the next section title, instead of a note on a single highlight.

## Evening Video Triage

**Actor:** [The Solo Reader](personas.md#the-solo-reader)

**Goal:** Use free evening time to watch what looks interesting from favourite channels, without treating the list as a must-watch queue.

**Trigger:** Entertainment, opening Favourite channels. This session is primarily on the computer.

**Steps today:**
1. Browse the latest items.
2. If interesting, click and watch inside the reading app.
3. If not worth watching, delete without opening.
4. If unsure or maybe later, leave the item untouched.

**Outcome:** Some videos watched, some discarded, some still sitting. No local save and no transcription.

**Costly edges:** None named beyond the Kickoff non-goal of local video save and auto-transcription, which stays out. See [constraints](constraints.md).

**Wanted:** Show only full videos. Filter out Shorts.

## Bring the Library Over

**Actor:** [The Solo Reader](personas.md#the-solo-reader)

**Goal:** Move sources and saved items out of the current reading app so this product can be used without rebuilding the library by hand.

**Trigger:** Switching away from the current reading app, or wanting this product to start from the library already collected there.

**Steps today:**
1. Sources and saved items live in the current reading app.
2. Leaving it means adding each source again, and losing parked or saved items unless they are copied out by some other means.
3. The current app can export subscriptions (an OPML file), a table of items (a CSV file), and a folder of saved files.

**Outcome:** The sources that matter are on lists here, and the saved items are in this library, without a one-by-one rebuild.

**Costly edges:** Re-adding every source by hand. Saved items that only exist in the current app.

**Wanted:** Import sources from that subscriptions export. Import items from the CSV and from the folder of files.
