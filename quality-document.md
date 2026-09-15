# Quality document

A snapshot of the codebase's health by product domain and architectural layer, distinct from `evaluator-rubric.md`: that grades a single session's output, this grades the codebase over time. `docs/roadmap.md` is the source of truth for which domains exist and what is built; this file only grades them.

**Update cadence:** after each significant session, or before a milestone comparison.

**Grading scale:**

- **A:** verification passing, clean boundaries, agent-legible, stable tests
- **B:** verification passing, mostly clean, minor gaps in legibility or coverage
- **C:** partially working, known gaps, some areas hard for an agent to understand
- **D:** not working, or not yet started

---

## Product domains

| Domain | Grade | Verification | Agent legibility | Test stability | Key gaps | Last updated |
| --- | --- | --- | --- | --- | --- | --- |
| Manage Lists | A | `uv run pytest` green | Clear, small handlers in `main.py` | ~158 list-related assertions in `test_app.py` | None open | 2026-09-15 |
| Manage Sources | A | `uv run pytest` green | Clear, one route family per action | ~141 source-related assertions | None open | 2026-09-15 |
| Read Later | B | `uv run pytest` green | Clear | 19 dedicated test functions (later/resume/archive) | Started/unstarted label not yet its own signal (roadmap: seen tracking exists but isn't surfaced as a label) | 2026-09-15 |
| Reading Progress | A | `uv run pytest` green | Clear, shared logic in `db.py` | 15 unread/seen assertions | None open | 2026-09-15 |
| Bring the Library Over | D | Not started | N/A | No OPML, CSV, or folder-import code or tests exist yet | Whole domain unbuilt | 2026-09-15 |
| Highlight and Land in Obsidian | D | Not started | N/A | 1 stray keyword hit, no real coverage | Whole domain unbuilt | 2026-09-15 |
| Improve UI | D | Not started | N/A | N/A | Deliberately gated on a full built app per roadmap | 2026-09-15 |

## Architectural layers

| Layer | Files | Grade | Boundary enforcement | Agent legibility | Key gaps | Last updated |
| --- | --- | --- | --- | --- | --- | --- |
| Data access | `app/db.py` (714 lines) | A | All SQL confined here (58 statements); zero SQL literals found in `main.py` | Function names describe intent (`mark_item_seen`, `add_item_to_list`) | None open | 2026-09-15 |
| Config | `app/config.py` (43 lines) | A | All environment reads confined here | Small, single-purpose functions | None open | 2026-09-15 |
| Mail | `app/mail.py` (140 lines) | A | Zero direct SQL; delegates to `db.py` functions (e.g. `find_source_by_mail_address`) | Clear separation of IMAP mechanics from persistence | None open | 2026-09-15 |
| Routes and request handling | `app/main.py` (1343 lines) | B | Zero SQL literals leak in, but ~15+ handlers each hand-roll `connect()`/`commit()`/`close()` instead of using the `db.session()` context manager `db.py` already provides | Route-per-action structure is easy to follow; the connection-lifecycle duplication is not | Replace the repeated open/commit/close blocks with `db.session()` | 2026-09-15 |
| Templates and static | `app/templates/` (22 files), `app/static/` | B | Presentation only in a spot check (conditionals per template stay under 7); not read in full | Consistent macro use (`macros.html`) | Full read not done this pass; grade is a proxy from conditional density, not a line-by-line review | 2026-09-15 |
| Ingest | `app/ingest.py` (602 lines) | B | Two raw SQL statements (a source-title `SELECT`/`UPDATE`) bypass `db.py` | Otherwise clear: feed parsing, capture, and discovery are separable functions | Move the two source-title statements into a `db.py` helper | 2026-09-15 |

## Change history

### 2026-09-15

- Changes: file created; first grading pass, done by reading the actual modules (SQL grep, function inventory, test keyword counts) rather than guessed from file size alone.
- Domains promoted: none (baseline)
- Domains demoted: none (baseline)
- New gaps identified: `main.py`'s repeated connection-lifecycle boilerplate; `ingest.py`'s two raw SQL statements; templates not read in full
- Gaps closed: none (baseline)

## Harness-simplification loop

Every harness component encodes an assumption about what the model cannot do; as models improve, that assumption can go stale. To check whether a component still earns its place:

1. Take a snapshot of this file.
2. Remove one harness component.
3. Re-run `uv run pytest` and `uv run ruff check`.
4. Take another snapshot.
5. If grades did not drop, the component was overhead; restore it if they did.

This is the same reasoning `docs/decisions.md` 2026-09-10 used to delete roughly 900 lines of dormant discovery-phase skills; this loop is that reasoning written down as a repeatable method instead of a one-off judgement call.
