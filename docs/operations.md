# Operations

## Purpose

How this one-person system is hosted, deployed, and kept on, within the $10 USD/month ceiling.

## Where it runs

A small always-on Fly.io machine in São Paulo (`gru`) serving the web app. The SQLite file lives on a 1 GB volume attached to that machine. The phone and computer reach it over HTTPS at [https://reader-skeleton.fly.dev/](https://reader-skeleton.fly.dev/). There is no custom domain. A later move to a machine you own is the same Docker image plus that file.

Local run is for development. The intended production path is this hosted app. Machine auto-stop is off; one machine stays running.

## Deploy

A push to `main` deploys automatically: a GitHub Actions job (`.github/workflows/test.yml`, `deploy`) runs after tests pass and pushes that commit live with `flyctl deploy --remote-only --ha=false`, using a `FLY_API_TOKEN` repository secret. This is what Ship's merge-and-redeploy relies on. It requires that secret to be set once in the repo's GitHub settings (Settings → Secrets and variables → Actions); without it the deploy job fails cleanly and the live app simply stays on its last successful deploy.

Trying a branch on the live host before it is merged uses the same job on demand, without deploying every push. Locally, with `gh` installed and authenticated: `gh workflow run test.yml --ref <branch>`. In a cloud session `gh` is not installed; dispatch the same `workflow_dispatch` event on `test.yml` for that branch through the GitHub MCP server's workflow-trigger tool instead (verified 2026-09-10: `gh` is absent, the MCP tool is present and reaches this repo). This is what Try's "once told to deploy" step relies on for a change built in a cloud session, which cannot reach Fly's remote builder directly (see below).

Deploying by hand (a machine that can reach Fly's remote builder directly) still works the same way: the image is built from the `Dockerfile` at the repo root, using Fly's remote builder; Docker Desktop is not required on the operator machine. The volume must stay attached so the library survives a new version. Deploy one machine only (`--ha=false`) so a spare copy is not created. A cloud agent session's own network cannot reach Fly's remote builder (its gRPC handshake fails through the sandbox's egress proxy), which is why the GitHub Actions job above exists.

First standup (already done for `reader-skeleton`):

1. `flyctl apps create reader-skeleton --org personal`
2. `flyctl volumes create reader_data --region gru --size 1 --yes -a reader-skeleton`
3. From the repo root: `flyctl deploy --remote-only --ha=false -a reader-skeleton`

A later version of the same app, from the repo root:

```text
flyctl deploy --remote-only --ha=false --build-arg GIT_SHA=$(git rev-parse --short HEAD)
```

`GIT_SHA` lands in the running container and comes back from `/health`, so a deploy from any path (hand or CI) can be confirmed against `git rev-parse --short HEAD` afterward.

Do not allocate a dedicated IPv4. Shared IPv4 on fly.dev is enough.

**Public name and home-screen mark when the MVP ships.** Keep `reader-skeleton` and the current GitHub repo name through feature work. Fly cannot rename an app in place; the fly.dev URL is the app name. The skeleton install icon is a plain SVG rectangle, which many phones will not show as a proper home-screen logo. When Add a Source to a List, Bring the Library Over, Read Later, and Highlight and Land in Obsidian are done, and you are about to put the lasting URL on the phone, do this before that deploy's smoke:

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
- `MAIL_IMAP_HOST`, `MAIL_IMAP_USER`, `MAIL_IMAP_PASSWORD`: isolated newsletter mailbox (dedicated Gmail account, app password, IMAP enabled), set as Fly secrets 2026-08-24. Never personal-mailbox credentials.

## Capturing a page to Read later

Sending a link to Read later from outside the app (any site, not just a subscribed source) uses the same `/capture` endpoint from two one-time setups, since Reader is a web app rather than a native app with its own Share Sheet extension:

- **Desktop:** a bookmarklet, listed in Settings. Drag it to the bookmarks bar once; clicking it on any page sends that page.
- **iPhone:** a Shortcut, set up once in the Shortcuts app so it then appears in the Share Sheet:
  1. Create a new shortcut. Set "Accepts" (under the shortcut's Share Sheet settings) to Safari web pages.
  2. Add **Run JavaScript on Webpage**, with the script `completion(document.documentElement.outerHTML);`.
  3. Add **Get Contents of URL**: URL `https://reader-skeleton.fly.dev/capture`, Method POST, Request Body Form, with fields `url` (Shortcut Input) and `html` (the previous action's result). No headers needed; `/capture` returns JSON by default and only serves the confirmation page when called with `?format=html` (what the bookmarklet uses).
  4. Parse the response as a dictionary and read its `title` and `item_url` fields.
  5. Show an alert with the title and two options, Done and Read now; Read now opens `https://reader-skeleton.fly.dev` + the returned `item_url`.
  6. Name it (e.g. "Save to Reader"), turn on "Show in Share Sheet", and restrict its share types to Safari web pages.

Once set up, sharing any page from Safari offers this shortcut, saving it to Read later with a confirmation and a way to jump straight in.

## Backup and data control

The library is the SQLite file. Copy it off the volume (or off `data/reader.db` locally) to back up. That file is what you move to another host. Highlights will later be markdown you already keep in the vault.

## Cost

One always-on shared-cpu 256 MB machine in São Paulo plus a 1 GB volume is about $3.29 USD per month, plus outbound traffic at $0.04 per GB. That sits under the $5 preference and the $10 ceiling. Fly does not offer a dashboard spend cap or billing alerts. Stay off sleeping free tiers: wake time would eat the morning sync bound. Do not add a dedicated IPv4, a second machine, or extra RAM unless the $10 ceiling is reopened.

## Smoke test

After deploy: open [https://reader-skeleton.fly.dev/](https://reader-skeleton.fly.dev/), wait for Home to finish sync, confirm News shows feed items, then turn on airplane mode and open an item already seen. It should still read.

Online part ran 2026-08-20 on the live URL: health returned ok, Home sync kept five demo RSS items (feed had 107), News listed those five, and an item page rendered. Phone walk the same day: an already seen item still read with airplane mode on.

`/health` also reports the deployed commit (`{"ok": true, "sha": "<short sha>"}`, `"dev"` outside a built image), so "live is back on main" is a comparison, not an assumption: `init.sh` does that comparison automatically.
