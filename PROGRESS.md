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

- **Change:** keep YouTube Shorts out of channel sources: on adding a channel (latest N) and on every later sync. Kind: behaviour + external system. Branch: `dev/skip-youtube-shorts`. Small change, Shape agreed in chat.
  Shape: a channel feed is read from YouTube's hidden long-form playlist feed (`UULF` + channel ID without `UC`), falling back to the channel's own feed when that is unreachable or empty; `parse_feed` drops any `/shorts/` link either way; each sync deletes already-stored Shorts for the source; the add flow's item count comes from the same feed. Leaves alone: stored `feed_url`s, schema, UI, non-YouTube feeds.
  Built and committed; real feeds saved as fixtures in `tests/fixtures/youtube/`; ran once end to end against live Kurzgesagt (five regular videos). Not yet deployed. Next: client says deploy or keep building; then live sign-off, then Ship (roadmap line, `docs/decisions.md` entry reversing 2026-09-28's "no Shorts filtering", `docs/architecture.md` YouTube line).

## Stacked awaiting deploy

None.

## Blocked

None.
