# Architecture

## Purpose

Reader is a personal reading hub for one person. A single hosted web app holds the library (sources, items, list membership, highlights later). The phone and computer open that app, sync when it is opened online, and keep already fetched News and Read later items on the device if the connection then drops.

## ❗ Tradeoffs

- **Control over convenience.** We store the library in a file we can copy, and we clean up article HTML in our own code. We do not rent a database product or a paid extractor. Some sites will still need the browser as a rare escape.
- **Host now, move later.** The app runs on a small always-on container until there is a home server. The unit of move is a Docker image plus a SQLite file, not a vendor-only data plane. We pay to keep the host awake: a sleeping free tier would blow the morning sync bound.
- **Web app, not a store app.** One codebase for phone and computer, no App Store fee. We give up a native iPhone app.
- **Hosted hub plus device cache.** Phone and computer share one library. News and Read later remain readable offline after a successful sync. This is not a phone-only local app.
- **Python and HTML over a heavier JavaScript client.** The dummy is HTML, and Python is already somewhat familiar. We give up a single-language TypeScript client framework.

## Parts

1. **Web app.** Serves Home, Lists, Sources, list views, and item reading. Copies the accepted dummy look.
2. **SQLite file.** The library on the host. Copied off for backup and for a later move to another machine.
3. **Ingest on sync.** On open (when online): poll RSS/Atom and public YouTube channel feeds; later, read new mail from the isolated newsletter mailbox. Incremental sync aims to stay under 5 seconds on a typical morning (10 second ceiling). First sync and a large backlog may take longer. Linked-article cleanup waits until an item is opened. Newsletter bodies come with the mail, once mail is wired.
4. **Device cache.** A PWA (installable site with an offline cache) keeps already fetched News and Read later pages on the phone or computer.
5. **Vault files (later).** Markdown in a folder the Obsidian vault can open. Not a highlight-sync vendor. Not in the walking skeleton.

Data moves: browser opens the app → if online, the app syncs inbound sources into SQLite → pages render from SQLite → the device caches those pages → if the connection drops, cached News and Read later remain readable.

## Stack

- Python, FastAPI, Jinja templates, a small amount of page JavaScript
- HTML and CSS copied from the accepted dummy look
- SQLite
- Docker
- GitHub for the repo and deploy
- Fly.io as the intended host, with a volume for the database. A later move to a machine you own is the same Docker image plus that file.

## Outside connections

- **RSS/Atom:** HTTP GET of the feed URL. We poll; there is no third-party feed service.
- **YouTube:** public channel feed for list items. Watching inside the app waits.
- **Newsletters:** the reader signs up from a dedicated alias, then forwards that mail to a separate mailbox used only for this app. The app holds credentials for that isolated mailbox only, never the personal mailbox. Mechanism: IMAP on sync. Live credentials wait for Add a Source to a List. Without a domain, mail cannot land on a host we control.
- **Obsidian:** markdown files, later. Manual, or when the vault is opened.

Secrets stay out of the repo.

## ⚠️ Skeleton

**Proved (this slice):** the shell (Home, Lists, Sources), SQLite, a public RSS fetch on sync that keeps only the latest five items from the demo feed, item reading, PWA cache registration, tests, local run, and the hosted path. The walking skeleton is live on Fly.io at [https://reader-skeleton.fly.dev/](https://reader-skeleton.fly.dev/): one always-on 256 MB machine in São Paulo (gru), 1 GB volume for the library file, HTTPS on the fly.dev URL. Online smoke: Home sync kept five demo items, News listed them, and an item page rendered. Phone smoke: the live URL opened, an already seen item still read with airplane mode on.

**Still to stand up in the first feature and after:** isolated-mailbox IMAP; adding a source to a list; article cleanup on open for linked pages (the demo RSS often ships a teaser, not the full page); vault markdown; list edit, home edit, highlighting, and the rest of MVP behaviour. The lasting GitHub repo name, Fly URL, and home-screen logo wait until that MVP is about to go on the phone; until then the host stays `reader-skeleton` and the install icon stays the skeleton SVG.
