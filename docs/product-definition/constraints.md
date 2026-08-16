# Constraints

Cross-cutting **limits** confirmed in Understand. They steer Scope. They are not epic cuts, not stack choices, and not a list of product wishes. What should change on a path sits as **Wanted** on that [journey](journeys.md).

Hard limits are fixed for this product direction until explicitly reopened. Soft limits are real preferences that can yield if they collide with cost or complexity.

## ❗ Hard

- **Solo.** One person’s tool. Not shared, not multi-user.
- **Ownership.** Ingested content and highlights live in client-controlled, exportable formats.
- **Vault format.** Obsidian export matches the settled sample: YAML frontmatter (`author`, `published_date`, `source`, `last_highlighted_date`), title, summary, highlights, and `###` section headings. See [export-example-obsidian.md](../history/discovery/02-understand/export-example-obsidian.md).
- **Morning freshness.** Once the source has sent, those newsletters must already be in the News list by the morning phone pass.
- **Devices.** Phone for the morning News pass, usually on home Wi-Fi unless the reader is not at home. Computer for evening read-later and video.
- **Cost.** About $5 USD/month preferred. $10 USD/month is the hard ceiling. That total includes hosting, ingestion, storage, and any store or developer fees.
- **List membership.** Manual author-name or feed-ID query editing is not an acceptable standing workflow. A list groups sources for a moment; it is not a single media type. The current named set is enough to cut from; more lists will appear later, including mixed YouTube plus newsletter/RSS lists. The replacement path is **Wanted** on [Add a Source to a List](journeys.md#add-a-source-to-a-list).
- **Extraction quality.** In-app extraction of newsletters, RSS, and other source content the reader actually uses must be consistently readable, including layout and images. Opening in the browser should be rare, not a standing workaround. This tightens Kickoff’s “perfect for every site is out”: browser fallback remains for exceptional cases, not as an excuse for sloppy in-app reading of this corpus.
- **Must not.** Local YouTube save or auto-transcription. Built-in LLM / RAG querying in the first release. Unauthorised paywall circumvention (no going through a publisher wall without their access). Feature-for-feature parity with the current reading app.

## ⚠️ Soft

- **Avoid a paid Apple Developer / App Store path** if that fee would blow the monthly cost ceiling.
- **Readwise as the sync hop** is how highlights reach the vault today. It is not required in the new product, as long as the vault still gets the same format.
