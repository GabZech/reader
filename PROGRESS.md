# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**UI redesign** (visual, with a little behaviour), branch `dev/ui-redesign`. Signed-off look: direction C "Warm & tactile", dark first, Marigold accent `#f5a524`, Fraunces for screen titles and list names, Literata for item titles and article text, Figtree for chrome. Icons only for Settings (a cog that spins with thin arrows while updating) and the add actions. Home's Edit moves into Settings. Delete is red. Boxes only where groups of the same kind are separated. Leaves alone: routes' behaviour, swipe, highlighting, export. Mockup: the "Reader Directions" artifact (https://claude.ai/artifact/XuTGvaK2UBpRHPSyaZkN9S); the local `preview/` copy is gitignored and not on the branch.

Small deviations from the mockup, kept on purpose: a source page's heading stays the source's name (rename tests rely on it); long list names truncate in Settings' "Lists on Home" at phone width.

Feedback rounds: four mockup rounds, signed off. Live try: branch deployed 2026-10-07 (commit `f7925ee`), live host is on `dev/ui-redesign`.
Round 1 of live feedback, built and committed on the branch but not yet deployed: the app froze and then went white when tapping between pages while Home's cog was turning (cause: every page load wrote to the database and the sync held its write lock across all downloads; fixed in `app/db.py` and `app/ingest.py`, with two regression tests); source titles turning bold late (fonts now wait for the bundled file instead of swapping); source-kind headings centred; each list on the Lists page in its own card; Home's "Show more" flush right.

Round 1 was deployed 2026-10-07 (commit `49c3859`). Round 2, built and committed but not yet deployed: on the iPhone the sticky article bar left a gap above it under the status bar (cause: the viewport tag lacked `viewport-fit=cover`, so every safe-area inset in the stylesheet was 0; fixed in `base.html`, with a guard test). It cannot be checked off-device, so the client's eye on the phone is the proof; the same change moves every page's safe areas (page top, tab bar bottom, toast), so look at those too.
Round 2 was deployed 2026-10-07 (commit `7068945`), but the iPhone kept going white after tapping Lists, Sources, Home (not reproducible in Chromium: 72 loads with the service worker and a slow sync all rendered), and the top-bar gap stayed. Round 3, a diagnostic bisect not yet deployed: the full-screen grain layer and the `backdrop-filter` blur on the tab bar and article bar are removed (searches found full-viewport fixed layers and backdrop-filter blanking iOS home-screen apps), and both bars are solid. So `docs/ui-guidelines.md` must not describe grain or blurred bars. If white screens continue, next are a diagnostics log in Settings and a service-worker safety net (never return nothing; do not use navigation preload, which blanks iOS). The top-bar gap looks like the iOS 26.1+ regression (WebKit bug 301994: a strip the page cannot paint, safe-area inset 0, no developer workaround); nothing changed for it, `viewport-fit=cover` stays.
Next step: redeploy with the trial deploy, then the client tries the live app (walkthrough: Home cog spin, Settings lists/theme, list swipe and switch counts, article bars and highlight, Edit list error, source page, fonts offline in airplane mode). Fix what they report on this branch, redeploy with the `workflow_dispatch` trial deploy (see `docs/operations.md`), and once signed off live: rewrite `docs/ui-guidelines.md` for the new look, tick the "Improve UI" lines in `docs/roadmap.md`, add a `docs/decisions.md` entry (bundled fonts, one accent and two icons replace the stone-and-ink, no-icon rule), clear this entry, then suggest the PR.

### Planned

- Foundation: bundled fonts and offline cache, tokens (dark + light), base type, tab bar, states: done, awaiting live try
- Home and Settings: cog with updating spin, Lists on Home inside Settings, theme switch: done, awaiting live try
- Lists: add icon, flat single lists, segmented tabs, edit list: done, awaiting live try
- Article: action rows, reading type, highlight colour: done, awaiting live try
- Sources: add icon, source page cog, source settings, add flow: done, awaiting live try
- Docs: ui-guidelines, roadmap, decision record: not started

## Blocked

None.
