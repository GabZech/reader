# Conventions

Repo writing and building conventions that are not product behaviour.

## Markdown Titles

Headings use Title Case.

## How We Build

Standing preferences about how changes are made, gathered as they come up rather than decided upfront. A change that establishes one of these adds it here in the loop's Ship step; anything stated once and never repeated does not belong here.

- **Test the behaviour, not the look.** Logic, routes, data, and state get automated tests. Pure visual and copy changes do not: the signed-off mockup and the live app are their check.
- **Screens follow `ui-guidelines.md`.** New screens copy the existing chrome and density rather than inventing a variant. Restyling is its own epic.
