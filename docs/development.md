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
uv run pytest
```

That is the check continuous integration runs (`.github/workflows/test.yml`).

## Local config

Copy `.env.example` to `.env` if you need to override defaults. Names only, no secrets in the repo.

- `DATABASE_PATH`: SQLite file (default `data/reader.db`)
- `SKELETON_FEED_URL`: public RSS URL used by the skeleton sync (default is a public news feed)

Mailbox credentials (`MAIL_IMAP_HOST`, `MAIL_IMAP_USER`, `MAIL_IMAP_PASSWORD`) are read on `/sync` when set; without them mail sync is skipped. Local runs do not need them unless you are working on that path — see `docs/operations.md` for the live values.
