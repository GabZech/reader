# Mockup setup

Run **every time** Mockup starts or resumes. Assume nothing is installed. Tool choice happens first (phase skill); this file is how to connect that tool and prove it works.

Do not commit secrets (Penpot MCP keys, Figma tokens). Prefer Cursor **user-level** MCP config, not a repo file.

On resume: if `docs/vision/mockup.md` already names a tool and a file or folder, reuse it. Do not create a second dummy.

## Inferring the tool recommendation

Before the tool-choice ask, read locked constraints, mockup learning purpose, devices, and cost. Recommend:

- **HTML** when there is no paid Figma Full/Dev seat, when a paid design plan would fight a cost ceiling, when the agent must visually review many screens, or when the learning questions need real browser behaviour (scroll, type, select text).
- **Penpot** when the client needs a canvas and a shareable play link for someone who is not on this machine, and localhost HTML is a poor fit.
- **Figma** only when a Full or Dev seat on a **paid** plan already exists. Starter read/export quotas (on the order of several calls per month) cannot support agent self-review.

State that recommendation in the same message as the three options.

## Self-review (all tools)

Decide whether to capture. Do it when a change could look wrong: a first-seen screen, layout, density, chrome, new controls, or visual character. Skip when the risk of looking wrong is low: a label, a sentence, a link target, a dead-end note. Do not ask the client whether to capture.

When you capture:

1. Take a picture of the screen (HTML screenshot, Penpot `export_shape`, Figma `get_screenshot`).
2. Look at it. Check overlap, truncated labels, missing controls for the learning questions, wrong viewport, and whether overall look matches the confirmed visual approach. Do not polish scenery.
3. Fix; recapture if the issue was visual.
4. **Then** share a link or invite the client to walk it.

Do not dump a first-seen screen into chat without a capture pass. If capture is rate-limited or broken, say so and either switch tool or ask the client to look while you name what to check.

Review images may live under `docs/history/discovery/04-mockup/review/` during the phase. Do not treat them as the dummy.

---

## HTML (recommended default)

Throwaway static pages. Not the product. Not Foundation.

**Dummy location:** `docs/mockup/` (HTML + one CSS file). No framework, no `package.json` in that folder, no backend. Fake data in the pages. Put a one-line note in `docs/mockup/README.md`: throwaway clickable dummy; do not copy into production.

**Need:** Node.js 20+ (for `npx`), and Chrome or Edge.

### Check

1. `node -v` (20+). If missing, walk the client through installing the current Node LTS, then recheck.
2. Chrome or Edge present (`msedge` on Windows is enough).

### Local walkthrough URL

From the repo root, serve only the dummy folder (not the whole repo):

```text
npx --yes serve docs/mockup -p 4173
```

Client opens `http://localhost:4173`. Phone-sized review: browser device toolbar, or capture with a phone viewport.

### Capture (agent)

Prefer the browser already on the machine (no extra Chromium download):

```text
npx --yes playwright screenshot --channel=msedge --viewport-size=390,844 http://localhost:4173/home.html docs/history/discovery/04-mockup/review/home.png
```

Use `--channel=chrome` if Edge is absent. Desktop viewport when that surface is in the screen list.

The agent must **read the PNG** (not only write it). Click-through dry run is optional: open the same URL and follow the linked path once before inviting the client.

### Smoke test

1. Write a one-screen `docs/mockup/index.html` (or reuse the real home page if it already exists).
2. Serve; screenshot; read the image.
3. Fail the check if Node is missing, the server did not start, or the image is blank or unreadable.

---

## Penpot

Closest canvas equivalent that stays free for this job. Official MCP; `export_shape` is how the agent sees boards.

**Need:** free Penpot Professional account at [penpot.app](https://penpot.app) (no card). Cursor MCP pointing at Penpot’s remote server.

### Check

1. Client has a Penpot account. If not, walk them through signup.
2. In Penpot: **Your account → Integrations → MCP Server**: enable, generate key, copy the server URL (includes `userToken`). Show the key only to the client; do not write it into the repo.
3. Add that URL as a Cursor MCP server (user-level). Transport: HTTP.
4. Open the dummy file in Penpot (create one if this is the first run). **File → MCP Server → Connect**. MCP acts on the **focused page in the connected tab**; keep that tab active while the agent works.
5. Confirm Penpot tools are listed (`execute_code`, `export_shape`, `high_level_overview`, `penpot_api_info`).

Create and edit via `execute_code` (Plugin API). Self-review via `export_shape` (PNG). Prototype: On click → navigate to a board; share from View mode (**Get link**). Viewers do not need an account.

Keep the dummy in this one file. Do not rely on paid Figma-style prototype variables.

### Smoke test

1. `high_level_overview` or a tiny `execute_code` read (current page name).
2. Create a small board; `export_shape`; look at the image.
3. Fail the check if MCP is disconnected, the plugin tab is not connected, or export returns nothing usable.

If remote MCP will not stay connected, say so and recommend HTML rather than fighting it.

---

## Figma

Use only with a **paid** Full or Dev seat, or if the client insists after hearing the quota. Starter can host a clickable file in **Drafts**, but agent **reads and screenshots** share a small monthly cap (Figma docs: on the order of several to ~20 calls per month). Writes (`use_figma`, `create_new_file`, `whoami`) are exempt during Figma’s current write-to-canvas beta; that beta will later be usage-based paid.

**Need:** Figma account; official **remote** MCP (not a community server).

### Check

1. In Cursor agent chat: `/add-plugin figma` (preferred), or user MCP URL `https://mcp.figma.com/mcp`. Then **Connect** and allow access.
2. `whoami`: note plan and seat. If Starter (or View/Collab only), warn that self-review will burn the read quota immediately; recommend HTML unless they upgrade.
3. First run: `create_new_file` into **Drafts** (unlimited on Starter; do not move into the 3-file team folder). Resume: open the URL in `mockup.md`.
4. `use_figma` to add a tiny frame; `get_screenshot` of it; look at the image.

Prototype: simple On click → Navigate to via Plugin API `setReactionsAsync` if `use_figma` can set it; otherwise list the connections for the client to add in the Prototype tab, or walk screens in order. Share a view/prototype link with anyone-can-view. Do not rely on variables, conditionals, or password-protected prototype links (paid).

### Smoke test

1. `whoami` succeeds.
2. File exists in Drafts; one frame; screenshot is readable.
3. Fail if auth failed, write to Drafts failed, or a 429/quota error hits on the first screenshot. Then recommend switching to HTML.

Do not use `generate_figma_design` (code-to-canvas). Do not use Figma Make as the dummy.
