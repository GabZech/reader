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

- **Client to do manually:** force-push `news-highlights` to a clean slate (their own call, once this shipped) — not yet done as of this note.

- **Change:** Fix capture body extraction dropping images. Kind: bug. Branch: `dev/fix-capture-image-extraction`.
  - Found while investigating a client report that captured articles were missing images. A broad probe across 20 real capture URLs (fetched live, extracted, compared) confirmed two real bugs and ruled out several false leads (apparent encoding corruption turned out to be a display artifact of the diagnostic tooling, not a real bug; switching trafilatura's extraction mode away from `favor_recall` was investigated and rejected — trafilatura's own docs recommend recall mode for archiving use cases like this one, and the tradeoffs cut both ways per-site).
  - Client confirmed proceeding with both slices below, including the lxml dependency for slice 2.

### Planned

- [x] Slice 1: pass `include_images=True` to the `trafilatura.extract()` call in `capture_article` (`app/ingest.py`). Fixes every captured article silently dropping inline body images (missing site-wide, not just on tables). Test: capture an article with a plain non-table inline image, assert it survives into `body_html`. Done, committed 5b46750.
- [ ] Slice 2: declare `lxml` as a direct dependency (already installed transitively via `trafilatura`). Add a helper that, before extraction, finds any `<table>` containing an `<img>` and replaces it with an equivalent `<div>`/`<p>` structure (one paragraph per cell, images and captions kept together, row order preserved) — works around a confirmed trafilatura defect where a table mixing an image-only row with a text-only row gets emptied entirely. Tables without images are left untouched. Falls back to the original HTML unchanged if parsing fails. Test: reproduce the exact image-row/text-row shape from the real article that surfaced this bug, assert both images and captions survive into `body_html`.

## Stacked awaiting deploy

None.

## Blocked

None.
