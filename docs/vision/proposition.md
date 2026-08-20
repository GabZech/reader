# Proposition

## ⚡ Problem Statement

**A solo reader already has a working morning habit with an existing reading app.** The tool is not broken. What motivates a replacement is three gaps that sit under that habit and make the status quo costly over time:

1. **Ownership:** Content lives in a vendor silo. The reader cannot own the full corpus or reliably reuse it later: for example, querying with LLMs or building a personal knowledge base from material they already collected.
2. **Organisation:** Curated, time-bounded lists (weekly vs daily newsletters) still require hand-editing queries and copying source IDs. There is no simple "add to this list" path.
3. **Control:** Personal workflows, especially highlight export into Obsidian with rich metadata, depend on vendor behaviour and workarounds that do not always hold.

**The problem is not that reading fails today.** It is that staying means lost ownership, fiddly list management, and no room to extend the product on the reader's own terms.

## 🔭 Product Vision

**Build a self-owned personal reading hub for one person.** It should ingest newsletters, RSS, and saved web content; organise that content through intuitive curated lists; support reliable morning reading; and let the reader highlight passages and export them as markdown into an Obsidian vault, with article metadata and optional section headings.

**Usable from a computer and from daily-reading devices.** Computer means desktop or laptop; other devices include, for example, a phone in the morning.

**Day-to-day reading should feel familiar and fluid.** The differences that matter are full data ownership, lower-friction list curation, and freedom to add features over time. Operating cost should stay near what the current tool costs today (~$5 USD/month), with modest flex when ownership is worth a little more.

## ❌ Non-Goals

The following stay out of scope for this product direction until explicitly reopened:

| Non-goal | Rationale |
| --- | --- |
| **Multi-user / shared accounts** | Solo personal tool only. |
| **YouTube local save and auto-transcription** | Explicitly not needed. |
| **Parity with every feature of the current tool** | Not chasing feature-for-feature match (e.g. spaced repetition, TTS, AI summaries) unless added deliberately later. |
| **Built-in LLM / RAG querying** | Goal is to *own* content for future use; querying is a later concern, not v1. |
| **Perfect in-app reading for every site** | Browser-tab fallback is acceptable when in-app extraction is hard. |

## ⚠️ Assumptions

These beliefs shape Kickoff drafts and must be checked or proven in later phases:

- **Morning reliability:** Newsletter delivery latency and formatting quality are the highest-stakes reliability requirements.
- **Obsidian export:** Markdown export with YAML frontmatter is a first-release must-have, not a nice-to-have.
- **Cost ceiling:** Operating cost can stay near the current tool's pricing if architecture is kept lean.
- **Export examples:** The client can supply sample exports from the current workflow to inform the Obsidian format.
- **Computer access:** First-class requirement; exact form (browser vs native) belongs to Understand / Foundation.
