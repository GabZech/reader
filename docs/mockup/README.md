# Mockup

Throwaway clickable dummy of the solution, not the product. The accepted look now lives in [UI guidelines](../ui-guidelines.md). Still the look spec for the unbuilt Highlight screens (see [journeys](../vision/journeys.md#park-highlight-and-land-in-obsidian)): highlighting and its section-title controls have not been rebuilt in the real app yet.

## How to open

From the repo root:

```text
npx --yes serve docs/mockup -p 4173
```

Open [http://localhost:4173](http://localhost:4173). The walkthrough is phone-only (about 390x844); a computer-width set was never made.

## Paths walkable

- **Add a Source to a List:** Sources; tap a source for See items of this source, Add source to list, and Delete source. Add source to list chooses a list, then a time window when the list is News (last day / last week). Favourite channels has no window.
- **Morning News Pass:** Home or News item opens the clean article (text and images, no ads). Close, Read later, Open original, Mark as seen. News list: Unseen / Seen with counts.
- **Read-Later Pass:** Library / Archive with counts. Started or Unstarted. Same clean article: Close, Open original, Archive. A started item resumes at the stop point.
- **Highlight and Land in Obsidian:** Select text to highlight; tap a highlight to add a section or subsection title, copy text and delete, or delete.
- **Evening Video Triage (in-scope part):** Favourite channels on Home; a YouTube item is treated like any other list item (Mark as seen).

Home has Edit: which lists appear, and in what order. A list view has Edit: rename the list, or delete it.

## What we learned

**Overall look.** Layout, density, chrome, and quiet type from Home are the direction the real UI copies. No icons and no brand colour system. Item rows show a small square on the left when there is a main image, and stay text-only when there is not.

**Time window.** When adding a source to News, last day / last week is on its own screen after choosing the list.

**Highlighting.** Selecting text highlights it; tapping a highlight offers section title, subsection title, copy-and-delete, or delete. The dummy does not show the note arriving in the vault, and the real app has not built this yet.

**Home and lists.** Three lists, three items then Show more / Show less, list name opens the full list. Bottom bar: Home, Lists, Sources.
