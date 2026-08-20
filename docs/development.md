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
uvicorn app.main:app --reload --port 8000
```

On macOS or Linux, activate with `source .venv/bin/activate`.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Home syncs a public RSS feed into SQLite when the browser is online, keeps only the latest five items from that demo feed, and those items stay available if you go offline (PWA cache after the first load).

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
