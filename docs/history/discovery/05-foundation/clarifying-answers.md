# Foundation clarifying answers

## Landscape (2026-08-20)

**Already in play:** Paid consumer email inboxes. No self-hosted mail. No domain the product can own. GitHub: a normal account; this repo is synced there.

**Languages / stores:** Medium Python, not a must. No host or store already in play that would be expensive to leave.

**Reused from earlier phases:** Vendor reading app (~$5/month). Obsidian vault as the export target. Readwise is the current highlight hop and is not required. Cost ceiling about $5 USD/month preferred, $10 USD/month hard.

## Where it has to run (2026-08-20)

**Surfaces (reused):** Phone for morning News, usually home Wi-Fi unless away. Other reading, including Read later, mostly on the phone and sometimes on the computer. Computer primary only for Favourite channels.

**Offline:** Already ingested items in News and Read later should be readable without internet. Favourite channels was not named as an offline must.

**Sync timing:** Fetch/sync when the app is opened is enough for the morning pass, if that sync finishes in about 5–10 seconds. Offline reading is for items already fetched in that or a prior open, if the connection then drops. Overnight background fetch is not required. This amends Understand’s morning-freshness lock.

## Who operates it (2026-08-20)

**Operator:** The same person is user, maintainer, and developer. They deploy it.

**Ops work:** Updates, backups, and dealing with breakage are all acceptable; they want to learn operating a system. The service should still be stable.

**Hosting control:** No always-on machine today. Fine to run on an external host now, with a later move to their own server if they get one.

## What must stay in your hands (2026-08-20)

**Keep:** The library (sources, items, list membership, highlights) in a form that can be exported and moved to another host, including a later own machine. Obsidian vault stays theirs.

**Fine to rent:** The existing consumer mailbox for receiving newsletters. An external host for running the app until they have a server.

**Avoid renting:** A paid article-extraction service. A highlight-sync vendor. Reading quality and the vault hop must not sit on someone else’s price and uptime.

**Vault hop:** Fine to land highlights manually, or whenever the Obsidian vault is opened (automatically, a button, or running a file). Not an export ritual at the end of a reading session. Readwise is not required.

## How the outside world gets in (2026-08-20)

**First product inbound:** Newsletters into a dedicated consumer-mailbox alias (everything to that alias is for this app). That mail is forwarded to a separate mailbox used only for this app; the app’s credentials are for that isolated mailbox only, never the personal mailbox. RSS/Atom feeds polled by us from the feed URL (ordinary RSS; no third-party feed service). YouTube channels as public channel feeds for list items; in-app watching waits.

**Mail mechanism (for the later package):** Without a domain, mail cannot land on a host we control. The app reads the isolated mailbox on sync and treats everything there as newsletter input. Live mailbox credentials wait for Add a Source to a List.

**Skeleton:** Live mail is not required. A public RSS fetch is enough to prove the ingest joint.

## System package (confirmed, 2026-08-20)

Confirmed: one Python web app, SQLite, Docker, PWA cache, hosted always-on, public RSS poll as the skeleton ingest joint. Mail: isolated forwarded inbox only; no personal-mailbox credentials. Typical-morning incremental sync target under 5 seconds, 10 seconds ceiling; first sync and backlog may take longer. Live mailbox waits for Add a Source to a List. Vault hop and add-source behaviour are not in the skeleton.

## Skeleton review (2026-08-20)

**Look:** Client judged the running skeleton as looking good.

**Joints:** Add a Source to a List will be built into this same app (same screens, same library file).

**Demo feed cap:** Skeleton ingest keeps only the latest 5 items from the public RSS demo and drops the rest, including leftovers from an earlier uncapped sync. The choose-how-many step when adding a source waits for Add a Source to a List.

**Host:** Fly.io is the intended production host. A Hetzner (or similar) VPS waits until there is a domain or a machine at home.

## Accept (2026-08-20)

Foundation accepted. Remaining risk carried forward: hosted Fly deploy not smoked (Docker and Fly were not on the build machine); offline News/Read later not walked on a phone; computer width is a wider column of the same chrome. Live isolated mailbox, add-source behaviour (including RSS backfill chooser), article cleanup, and vault hop wait for later phases. Requirements for Add a Source to a List is next.

## Volunteered for Requirements (2026-08-20)

**RSS/blog backfill when adding a source:** Before ingesting, fetch and show how many items the feed currently has. Then the reader chooses: all of them, the last 5, only the latest one, or an exact count. Ingest only after that choice. Not built in the skeleton. Reuse in Add a Source to a List. This is separate from the timed-list recency window (last day / last week) already locked for what News *shows*.

## Hosted walking skeleton (2026-08-20)

The walking skeleton is on Fly.io: app `reader-skeleton`, one always-on 256 MB machine in São Paulo (`gru`), 1 GB volume `reader_data` at `/data`. Live URL: [https://reader-skeleton.fly.dev/](https://reader-skeleton.fly.dev/). The image was built on Fly's remote builder. Region is São Paulo because that is where the reader uses the app. Online smoke: Home sync kept five demo RSS items; News listed them; an item page rendered. Phone walk: an already seen item still read with airplane mode on. The demo RSS ships a teaser for some items, not the full page; pulling the linked page on open still waits. Isolated mailbox still waits for Add a Source to a List. Keep this app name and the GitHub repo name until the first product is about to go on the phone as the lasting URL; then rename the repo, create a new Fly app (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed. The skeleton favicon is a placeholder SVG, not that mark.
