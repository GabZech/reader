# Progress

Snapshot of in-flight state, overwritten each time, not appended. Git log is
already the session log. Update this at every change-loop checkpoint commit;
clear it at Ship. A small change's Shape stays chat-only; a not-small
change's deep-plan output lives here instead, under In flight's
`### Planned` heading, since chat is not assumed to survive a lost session.

## Current verified state

- **Repository root:** `/home/user/reader`
- **Standard startup path:** `bash init.sh`
- **Standard verification path:** `uv run ruff check` then `uv run pytest`
- **Focused debug command:** `uv run pytest tests/test_app.py -k <name>`
- **Run the app:** `RUN_START_COMMAND=1 bash init.sh` (without `--quick`), or see `docs/development.md`
- **Highest-priority unfinished item:** none chosen yet. Epics in `docs/roadmap.md` do not impose an order; this names what was actually picked, not a computed priority
- **Current blocker:** none

## Live now

Run `bash init.sh` for the current live SHA against `origin/main`.

## In flight

None.

- **Change:** show a video's real length instead of the word-count read time, for YouTube items. Kinds: behaviour + external system + schema (additive). Branch: `dev/youtube-video-length`, stacked on `dev/skip-youtube-shorts` so both deploy together; Shorts PR merges first, then merge `origin/main` into this branch. Leaves alone: articles and newsletters, the look of the length label, stored `feed_url`s.
  Probe findings: watch pages are captcha-blocked from cloud IPs (429); a channel's `/videos` page loads and lists ~30 newest videos, each length in a `thumbnailBadgeViewModel` whose `animationActivationTargetId` is that video's ID (pair by that ID, not by position).
  Fallback if it goes wrong: the new column is additive; revert the change and leave it unused. Copy the library off the volume and rehearse the migration on the copy before deploy.
  ### Planned
  - [x] Slice 1: read lengths: pure function from a channel `/videos` page to `{video_id: seconds}`; tested on a real excerpt saved as a fixture plus synthetic edge cases (hours, LIVE badge, no badges).
  - [x] Slice 2: store: nullable `items.duration_seconds` (re-runnable migration, existing rows blank); each sync fetches the channel's `/videos` page once, only when some of its items lack a length; any failure leaves lengths blank and never fails the sync.
  - [x] Slice 3: show: YouTube items show the length as "N min" on the list card and the item page, nothing when unknown; other items unchanged. Live run against a real channel before sign-off.

## Stacked awaiting deploy

None.

## Blocked

None.
