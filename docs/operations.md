# Operations

## Purpose

How this one-person system is hosted, deployed, and kept on, within the $10 USD/month ceiling.

## Where it runs

A small always-on Fly.io machine in São Paulo (`gru`) serving the web app. The SQLite file lives on a 1 GB volume attached to that machine. The phone and computer reach it over HTTPS at [https://reader-skeleton.fly.dev/](https://reader-skeleton.fly.dev/). There is no custom domain. A later move to a machine you own is the same Docker image plus that file.

Local run is for development. The intended production path is this hosted app. Machine auto-stop is off; one machine stays running.

## Deploy

The image is built from the `Dockerfile` at the repo root. Fly's remote builder is enough; Docker Desktop is not required on the operator machine. The volume must stay attached so the library survives a new version. Deploy one machine only (`--ha=false`) so a spare copy is not created.

First standup (already done for `reader-skeleton`):

1. `flyctl apps create reader-skeleton --org personal`
2. `flyctl volumes create reader_data --region gru --size 1 --yes -a reader-skeleton`
3. From the repo root: `flyctl deploy --remote-only --ha=false -a reader-skeleton`

A later version of the same app, from the repo root:

```text
flyctl deploy --remote-only --ha=false
```

Do not allocate a dedicated IPv4. Shared IPv4 on fly.dev is enough.

**Public name and home-screen mark when the MVP ships.** Keep `reader-skeleton` and the current GitHub repo name through feature work. Fly cannot rename an app in place; the fly.dev URL is the app name. The skeleton install icon is a plain SVG rectangle, which many phones will not show as a proper home-screen logo. When Add a Source to a List, Bring the Library Over, Morning News Pass, Read-Later Pass, and Highlight and Land in Obsidian are done, and you are about to put the lasting URL on the phone, do this before that deploy's smoke:

1. Choose the short Fly app name (it becomes `https://<name>.fly.dev/`) and the matching GitHub repo name. Do not keep `reader-skeleton` as the public URL.
2. Create a logo (the home-screen and browser-tab mark only). Wire it so Add to Home Screen, the app switcher, and the tab icon show that mark: PNG icons the phone actually uses (including an Apple touch icon), listed in the web app manifest, not only an SVG favicon. This is not an in-app icon set; screens stay word chrome.
3. Create a new Fly app and a 1 GB volume in `gru`. Copy the SQLite library onto that volume (volume snapshot restore, or copy the file), so the real library is not left on the old app.
4. Point `fly.toml` at the new app name, deploy one always-on machine (`--remote-only --ha=false`), and smoke the new URL, including installing on the phone and checking the home-screen icon.
5. Rename the GitHub repo. Update the live URL in this file and in `docs/architecture.md`.
6. Destroy `reader-skeleton` so two machines are not billed.

The name on the phone (Add to Home Screen) can stay Reader unless that is changed on purpose with the logo.

## Config and secrets

Injected as environment variables on the host. Secrets stay out of Git.

- `DATABASE_PATH`: path to the SQLite file on the volume (`/data/reader.db` on Fly)
- `SKELETON_FEED_URL`: public RSS URL for the skeleton sync
- Later: isolated-mailbox IMAP host, user, and app password. Never personal-mailbox credentials.

## Backup and data control

The library is the SQLite file. Copy it off the volume (or off `data/reader.db` locally) to back up. That file is what you move to another host. Highlights will later be markdown you already keep in the vault.

## Cost

One always-on shared-cpu 256 MB machine in São Paulo plus a 1 GB volume is about $3.29 USD per month, plus outbound traffic at $0.04 per GB. That sits under the $5 preference and the $10 ceiling. Fly does not offer a dashboard spend cap or billing alerts. Stay off sleeping free tiers: wake time would eat the morning sync bound. Do not add a dedicated IPv4, a second machine, or extra RAM unless the $10 ceiling is reopened.

## Smoke test

After deploy: open [https://reader-skeleton.fly.dev/](https://reader-skeleton.fly.dev/), wait for Home to finish sync, confirm News shows feed items, then turn on airplane mode and open an item already seen. It should still read.

Online part ran 2026-08-20 on the live URL: health returned ok, Home sync kept five demo RSS items (feed had 107), News listed those five, and an item page rendered. Phone walk the same day: an already seen item still read with airplane mode on.
