# Development

## Purpose

How to run and change the walking skeleton on a local machine. Commands in this file have been run.

## Prerequisites

- [uv](https://docs.astral.sh/uv/), which manages the Python version and the virtual environment
- Docker, if you want the same image operations will deploy

## Run

From the repo root:

```text
uv sync
uv run pytest
uv run uvicorn app.main:app --reload --reload-dir app --port 8000
```

`uv sync` creates `.venv` and installs the locked dependencies; no separate activate step is needed since every command runs through `uv run`.

`--reload-dir app` watches only the app. Watching the whole repo stalls the restarter on Windows.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Home syncs a public RSS feed into SQLite when the browser is online, keeps only the latest five items from that demo feed, and those items stay available if you go offline (PWA cache after the first load).

Before trying a Python change, restart on 8000 so the running app is this revision. If 8000 is already taken, stop that process and start again. Do not switch ports.

`--reload` has proven unreliable on Windows in this repo: `WatchFiles` sometimes misses edits to `app/main.py`, `app/ingest.py`, or templates after the first reload, and a killed reloader can leave an orphaned child still bound to the port, so a later start looks successful while requests keep hitting stale code. Prefer running without `--reload` (drop that flag and `--reload-dir`) and restarting by hand after each code change; confirm the restart actually took by re-testing the specific route you changed, not just `/health`. Before restarting, always confirm nothing is still listening on 8000 (see the stop command above) rather than trusting that the previous stop succeeded.

VS Code's own embedded browser panel throttles JS timers (e.g. `setTimeout`), which can make timing-sensitive UI (an auto-dismiss toast, a poll) look broken there when it isn't. Verify timing-sensitive behaviour in a real OS browser tab, not that panel.

Windows, stop whatever is on 8000:

```text
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

macOS or Linux: `lsof -ti :8000 | xargs kill`

## Test

```text
uv run ruff check
uv run pytest
```

That is what continuous integration runs (`.github/workflows/test.yml`), lint then tests. `pytest`, `ruff`, and `playwright` are dev-only dependencies; the deployed image does not install them.

**Browser tests need Chromium.** `tests/test_highlight_browser.py` drives the reader page in a real browser, since highlighting runs in `app/static/app.js`. Install it once with `uv run playwright install chromium`; CI does the same before running the tests.

## Local config

Copy `.env.example` to `.env` if you need to override defaults. Names only, no secrets in the repo.

- `DATABASE_PATH`: SQLite file (default `data/reader.db`)
- `SKELETON_FEED_URL`: public RSS URL used by the skeleton sync (default is a public news feed)

Mailbox credentials (`MAIL_IMAP_HOST`, `MAIL_IMAP_USER`, `MAIL_IMAP_PASSWORD`) are read on `/sync` when set; without them mail sync is skipped. Local runs do not need them unless you are working on that path — see `docs/operations.md` for the live values.

## Dev container

**Purpose.** Run Claude Code (or any agent) in a container so it cannot reach the host machine. `.devcontainer/` builds Python 3.12 with the same uv version as CI and production, installs the locked dependencies and Chromium, and installs Claude Code and the GitHub CLI (`gh`).

**Open it as a volume clone.** In VS Code, run `Dev Containers: Clone Repository in Container Volume` and give it the repo URL. The checkout then lives in Docker's own storage, so the container sees no host files. Opening the Windows checkout in the container instead bind-mounts it, which gives the container write access to that folder, reports every file as executable (`ruff check` fails with `EXE002`), and shows CRLF files as modified in git.

**Inside the container.** The commands under Run and Test work unchanged. Port 8000 is forwarded to the host. Claude Code's and `gh`'s logins live in named Docker volumes, so they survive rebuilds. Log in once with `claude`, and once with `gh auth login --with-token`, pasting a fine-grained personal access token limited to this repo (Contents, Pull requests, and Actions, read and write) so an agent's reach stays limited to it.

**What it does not isolate.** VS Code forwards the host's git credentials into the container, so an agent there can push as you; with `gh` logged in it can also open PRs and start workflows within the token's permissions. `gh pr merge` and `gh workflow run` still ask first. Outbound network access is unrestricted. Do not mount the Docker socket.
