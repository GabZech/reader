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
- [x] Slice 2 (revised mid-build, twice): declared `lxml` as a direct dependency. Added `_hoist_table_images` (best-effort rewrite of an image-bearing `<table>` into `<div>`/`<p>`, works around a confirmed trafilatura table defect) plus a post-extraction safety net that checks every content image in the article's own region (`_image_candidates`, not just table images — an earlier version only checked tables and silently lost 22 of 28 real images on the article that surfaced this) against what actually survived, and recovers any that didn't by embedding it directly via its own resolved URL (`_recover_missing_images`) — not a link-out notice, an earlier version of this, since the URL is already known and there's no reason not to just show the image. A dashed border marks a recovered image apart from one trafilatura extracted normally. Researched whether swapping the extraction engine (Mozilla Readability) would avoid this class of bug: ran it directly against the same 20 real URLs, found no clear winner (better on Vitalik's page, worse on two WordPress sites, fails outright on JS/paywalled pages trafilatura degrades gracefully on) — logged as a decision not to redo the pipeline. Visual: mockup screenshot signed off before the CSS/template-facing code was written, both for the original notice design and again for this embedded-image revision. Done, committed 66e14f8, 4147a8c, 24bd8b7, 21f4f8b.

## Stacked awaiting deploy

None.

## Blocked

None.
