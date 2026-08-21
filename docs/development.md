# Development

## Purpose

How to run and change the walking skeleton on a local machine. Commands in this file have been run.

## Prerequisites

- Python 3.12 or newer
- pip
- Docker, if you want the same image operations will deploy

## Run

From the repo root:

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
uvicorn app.main:app --reload --reload-dir app --port 8000
```

On macOS or Linux, activate with `source .venv/bin/activate`.

`--reload-dir app` watches only the app. Watching the whole repo stalls the restarter on Windows.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Home syncs a public RSS feed into SQLite when the browser is online, keeps only the latest five items from that demo feed, and those items stay available if you go offline (PWA cache after the first load).

Before trying a Python change, restart on 8000 so the running app is this revision. If 8000 is already taken, stop that process and start again. Do not switch ports.

`--reload` has proven unreliable on Windows in this repo: `WatchFiles` sometimes misses edits to `app/main.py`, `app/ingest.py`, or templates after the first reload, and a killed reloader can leave an orphaned child still bound to the port, so a later start looks successful while requests keep hitting stale code. Prefer running without `--reload` (drop that flag and `--reload-dir`) and restarting by hand after each code change; confirm the restart actually took by re-testing the specific route you changed, not just `/health`. Before restarting, always confirm nothing is still listening on 8000 (see the stop command above) rather than trusting that the previous stop succeeded.

Windows, stop whatever is on 8000:

```text
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

macOS or Linux: `lsof -ti :8000 | xargs kill`

## Test

```text
python -m pytest
```

That is the check continuous integration should run.

## Local config

Copy `.env.example` to `.env` if you need to override defaults. Names only, no secrets in the repo.

- `DATABASE_PATH`: SQLite file (default `data/reader.db`)
- `SKELETON_FEED_URL`: public RSS URL used by the skeleton sync (default is a public news feed)

Mailbox credentials are not used in the skeleton. They wait for Add a Source to a List.
