# Roadmap

Feature development is currently underway.

## Where we are

### 🔭 Discovery

Before any code was written, a discovery phase mapped out who this app is for and what it needs to do, producing:

- [proposition](vision/proposition.md) and [metrics](vision/metrics.md): the problem this solves and how success is measured
- [personas](vision/personas.md), [journeys](vision/journeys.md), and [constraints](vision/constraints.md): who uses it, how, and the limits to design within
- [epics](vision/epics.md): the capabilities scoped in for the MVP
- [mockup](mockup/README.md): a clickable mockup of the app, built before the real thing
- [architecture](architecture.md), [development](development.md), [operations](operations.md), and [UI guidelines](ui-guidelines.md): the technical foundation the app is built on

Session logs from this phase, and the working files from an earlier per-epic way of running feature work (since replaced by the change loop; see [decisions](decisions.md) 2026-08-28), are frozen at git tag `archive/history-2026-09` (was `docs/history/`; collapsed per [decisions](decisions.md) 2026-09-10).

### ✅ Live features

- **Lists and sources:** lists can be created, renamed, and deleted beyond the three that ship by default. A source (RSS or blog feed, YouTube channel, or newsletter) can be added to any list from its own screen, added to further lists, renamed, and deleted; adding a URL that's already a source shows a notice instead of duplicating it.
- **Bringing content in:** RSS and blog feeds pull in automatically within a recency window when added by URL, and the count chosen when adding is only how many items to start with: later syncs add every newer item and never remove an older one; YouTube channels are added the same way and land in the Favourite channels list; only a channel's regular videos come in, never its Shorts, including for channels added earlier. A blog whose feed sends only a title and link, with no text, has each post's page fetched and cleaned during sync so it opens with its full text (from the feed's own host when the post's link points at one that cannot be reached); a post with any text in its feed, however short, is left as it is. Newsletters arrive through a private mailbox and sit unlisted with a red-dot notice until sorted onto a list.
- **Read later:** a link can be sent to Read Later while browsing, and the saved article keeps its links and its bold and italic text (only web links, relative links and email links stay clickable). Saved articles sit in a library, move to an archive once finished (and back again if that was a mistake), resume from wherever reading was left off, and can be removed outright.
- **Reading progress:** every list except Read Later (which has its own Library/Archive and Started/Unstarted state) splits items into Unread and Read, with a "Mark as read" action on the article and automatic tracking as items are opened, so the Home screen shows only what's unread. An article reopens at its saved spot as soon as the text is ready, without waiting on images, and closing a highlight (or saving its title) returns to that highlight. Swiping a row right to left moves it straight to the other tab (read or unread, archive or library, on Home too), and swiping left to right deletes it after a confirmation.
- **Highlighting and Obsidian export:** passages can be highlighted on first opening an article, including any image the selection covers; a standalone image can also be highlighted on its own with a double-click or double-tap, no surrounding text needed. Either way the image gets an outline in the highlight colour and travels into the export, with section titles that stick to the highlights below them and can be deleted along with them; a highlight carrying a title shows a small `§` before it in the article. A highlight can also be marked as a key passage from its own page: it shows a small `★` before it in the article and lands in the note as a yellow mark followed by the tag `#key`, so searching that tag in Obsidian finds every key passage across all notes. Highlights land as a note in a private Obsidian vault, in the agreed format, kept to roughly one commit per article via an archive/mark-as-read trigger with a daily 5am (Brasilia time) fallback. A link inside a highlighted passage stays a link in the note, and only the selected words are linked; notes exported before this was added were sent again once. A paragraph a source wraps across several lines stays one bullet instead of splitting at each wrap, and past notes split that way were sent again once. A highlight inside a single list item is a plain bullet instead of hanging under an empty one, and past notes written that way were sent again once. Deleting an item, or a source with its items, removes everything the app holds about it, read marks, list entries and highlights included, after one last export of any highlights not yet sent; notes already in the vault are never removed.
- **Working offline:** pages and articles open from the copy kept on the phone, online too, so tapping around is as quick as offline. Each time the app is opened (unless it was opened within the last minute), and while Home's cog turns, it syncs the sources, fetches every kept page again and downloads ahead, with images, the unread articles of every list and source whose "Available offline" switch is on (on each list's editor and each source's page: off by default, Read later on). A downloaded article leaves the phone once it is read, archived or gone from its list, unless something for it still waits to sync. A change made on the phone shows at once on the pages it touches; one made on another device shows from the next open. Offline, those articles, Home, Lists, every list with both its tabs, Settings, Sources and each source's pages open, and an article opens from wherever it was reached. Highlighting works offline too: a highlight is drawn at once with a dashed underline, can be joined with others, given a section or subsection title, marked as a key passage or deleted, and all of it is sent in order when the connection returns, without duplicating anything. The article bar says "Offline", and "Offline · N to sync" while saves wait. The reading spot is kept offline as well. Archiving, moving back to Library, marking read or unread, swiping and saving to Read later work offline too: the row moves at once, counts follow, a message says "will sync", and it is sent in order with the highlights when the connection returns. An article opened offline is dimmed and told to the server later. What needs the server (delete, adding, renaming, Home order) says "This needs a connection", and an article that was never saved says so.
- **Watching videos:** a YouTube item plays inside its own page, below the top bar and above the row of buttons at the bottom, using YouTube's embedded player. A video shows its own length (for example "14 min") on its card and page instead of a reading time, for a channel's 30 newest videos; an older video, a live stream, or one YouTube's page did not give a length for shows none. Other items are unchanged.
- **Sign-in:** the app asks for a password before showing anything, and a device that gives it stays signed in until it goes 30 days unused, is revoked, or the password is changed. Settings, Devices lists every signed-in browser with when it was last used, and renames it, revokes it, or signs out all the others. The iPhone Shortcut and the bookmarklet each use their own key that can only save to Read later, and a separate access key lets development tooling use the live app except the device and key pages. Five wrong passwords lock a network out for 15 minutes, a new sign-in or a lockout sends an email, and a phone that is signed out clears the library it kept while holding on to anything it had not yet sent.
- **Look and feel:** every screen shares one warm look, dark by default with a light option, set in three bundled fonts that also work offline with one amber accent. Each list on Lists and each kind of source on Sources sits in its own card, Settings holds the list editor and the theme switch, and the bottom bar and the article's top bar stay put on an iPhone. In the installed app, a page that cannot load shows a short retry screen instead of a blank one, and a Diagnostics page under Settings shows what the phone and server did, for tracking down faults.

## What's next

### 🎯 Upcoming features


None scoped yet.

### 📌 Deferred to later

Choices explicitly put off for later, each with a real trigger to revisit. Removed once acted on.

#### Looks

- Add a home-screen logo that shows when the site is installed

#### Security

- Take the Fly app name, and so the app URL, out of the public repo. It sits in `fly.toml`, the deploy workflow, `init.sh`, and several docs, and in git history. Do it with the rename under Switching over: keep the new name out of the files (the deploy workflow reads it from a GitHub Actions variable, `init.sh` from `LIVE_URL`, docs use a placeholder) and destroy the old app so the exposed URL goes dead. Editing files alone is not enough, because history keeps the old name. Revisit with the rename, before the lasting URL goes on the phone

#### Hosting and data

- One Fly app serves both trying and living. During a change, the live app briefly runs an unmerged branch against the real library. Splitting into separate dev and prod Fly apps is the real fix; revisit once local testing is viable again
- Once the MVP is up, back up the Fly volume's SQLite library regularly (roughly weekly); sources and articles live only on Fly and are never committed to the repo

#### Offline and reliability

- Offline gaps left after the whole-app stage: an item marked unread offline comes back to Home only once online (Home shows only what was stored); delete, adding and renaming lists or sources, and Home order stay online-only. Revisit if one gets in the way offline
- Stored article copies are not refreshed when the app updates: a downloaded article is fetched again only when its highlights or reading spot change, and one opened by hand is refreshed in the background each time it is opened, for the time after. So an article can show an older version's markup until then. Revisit if that bites in daily use
- The "Offline" label only appears on article pages. Home and the lists show nothing about connectivity beyond the cog turning while a download runs

#### Speed

- Home shows its kept copy at once on opening, but what the sources brought in arrives about 5 seconds later, once the sync is done: the server checks each feed one after another, then the newsletter mailbox. Two ways to shorten it: check several sources at once, or have the server sync on its own schedule so opening the app never waits. Revisit if the wait for new items gets in the way

#### Testing

- The browser tests are the slow part of the suite (about 100 of 450 tests, most of a 3 to 4 minute run), and CI is where the whole suite runs, so a failing push costs a few minutes. Tiers exist (`-m "not browser"` runs the rest in under 20 seconds). Still to do: run the browser tests in parallel (`pytest-xdist`, measured first so it does not make them flaky), replace their fixed waits with waits for the event, and let the swipe tests use a real server so they can run on WebKit like the others. Revisit when waiting on CI starts to slow changes down
