# Metrics

**Success is measured by changed behaviour and reliability**, not by features shipped.

## 🎯 Primary Outcomes

| Metric | Target | Notes |
| --- | --- | --- |
| **Morning-ready inbox** | Daily newsletters (1–2) are present and readable **before** the morning reading session, every day | Highest-stakes freshness requirement; failure here = abandon |
| **Cross-device access** | Core reading and list workflows work from **computer** and from devices used for morning reading | Computer use is explicit; phone implied from morning routine |
| **Daily reading on own stack** | Replaces the current reading app for the morning newsletter routine within [TBD weeks of accept] | Baseline today: 100% on the current tool |
| **List curation effort** | Adding a new source to a curated list takes **seconds via UI**, not manual ID + query editing | Establish baseline from one real "add source" task in the current tool |
| **Owned corpus** | 100% of ingested article content and highlights stored in formats the client controls and can export | Enables future LLM / knowledge-base work |
| **Obsidian export fidelity** | Highlights land in the vault as markdown with YAML frontmatter and optional section headings, without unreliable workarounds | Client to supply sample exports from the current workflow as reference |
| **Reading quality** | Article body is consistently readable; broken layout or garbled extraction is rare enough not to block daily use | "Bad formatting" = product failure |
| **Monthly operating cost** | ≤ **$5 USD/month** preferred; **≤ $10 USD/month** hard ceiling | Includes hosting, storage, ingestion, domain, APIs |

## ⚠️ Guardrails

If any of these persist, the product has missed the problem:

- Ingestion failures block reading for sources the client relies on.
- Frequent downtime or slow/unpredictable newsletter arrival (especially morning emails).
- Operating cost above $10/month.
- Export to Obsidian is unreliable or loses metadata the client depends on.

## 📄 Baselines to Establish

| Signal | How to baseline |
| --- | --- |
| Time to add a source to a weekly/daily list in the current tool | One timed walkthrough with a recent newsletter source |
| Morning delivery window | Record when overnight newsletters appear in the current tool vs when client reads |
| Highlight → Obsidian workflow | Document current export path and pain points (incl. heading-via-comment hack) |

## ❌ Not Success

Avoid vanity metrics:

- Number of features built
- Number of feeds subscribed
- Lines of code or screens shipped
