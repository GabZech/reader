# Mockup

Throwaway clickable dummy of the solution, not the product. Foundation will build the real shell from what this file records. After Foundation is accepted, this file moves to Mockup history.

## 🎯 Purpose

Find out whether choosing a time window when adding a source to a timed list is obvious, and whether highlighting is obvious (select text to highlight; tap a highlight to add a section title or delete it). Settle whether the overall look of those journeys is compatible with how the app should feel.

The dummy also walks Home and the basic workings of the app: the lists in the picture (News, Read later, Favourite channels), a list of all sources, moving between those parts, and removing any item from the list it is on. A YouTube item is not treated as a special case.

## Tool

HTML pages under `docs/mockup/`. Throwaway; do not copy into production.

## How to open

From the repo root:

```text
npx --yes serve docs/mockup -p 4173
```

Open [http://localhost:4173](http://localhost:4173). The walkthrough is phone-only (about 390×844). A computer-width set waits.

## Paths walkable

- **Add a Source to a List:** Sources; tap a source for See items of this source, Add source to list, and Delete source (what those do in the product can wait). Add source to list still chooses a list, then a time window when the list is News (last day / last week). Favourite channels has no window. After those options, the top-left control is Back.
- **Morning News Pass:** Home or News item opens the clean article (text and images; no ads). Close, Read later, Open original, Mark as seen. News list: Unseen / Seen with counts.
- **Read-Later Pass:** Library / Archive with counts. Started or Unstarted. Same clean article: Close, Open original, Archive. A started item resumes at the stop point; earlier text stays.
- **Highlight and Land in Obsidian:** Select text to highlight; tap a highlight to add a section or subsection title, copy text and delete, or delete. Title screens: highlight quote, empty field, Done.
- **Evening Video Triage (in-scope part):** Favourite channels on Home; a YouTube item is treated like any other list item (Mark as seen). Watching inside the app, the evening session, and filtering Shorts are not in this dummy.

Home has Edit: which lists appear, and in what order. A list view has Edit: rename the list, or delete it.

## What we learned

**Overall look.** Layout, density, chrome, and quiet type from Home are the direction to copy. No icons and no brand colour system. Item rows show a small square on the left when there is a main image (article opening image or video thumbnail), and stay text-only when there is not (newsletters often).

**Time window.** When adding a source to News, last day / last week is on its own screen after choosing the list. Sources already on News show the window (for example News (<24h) or News (<7days)).

**Highlighting.** Selecting text highlights it. Tapping a highlight offers section title, subsection title, copy-and-delete, or delete. That is enough to judge the control. The dummy does not show the note arriving in the vault.

**Home and lists.** Three lists, three items then Show more / Show less, list name opens the full list. Bottom bar: Home, Lists, Sources. Home Edit chooses visibility and order. List Edit changes the name or deletes the list.

## ⚠️ Still open

- **Vault landing.** Scope asked whether highlighting is obvious including the note arriving in the vault. This dummy does not show that step.
- **Computer width.** Favourite channels is primarily a computer session; this walkthrough is phone-only.
- **Later video work.** Watching inside the app, the evening session, and filtering Shorts wait; they were never in this dummy.
- **Not for a dummy to prove.** Morning newsletters already in News once the source has sent; in-app reading staying readable for the sources actually used; operating cost at or under $10 USD/month; adding a newsletter finishing before the first email arrives.
- **Dummy limits.** Home does not live-update after Mark as seen or Archive (the real app will take those items off Home). Open original states that it would use the default browser; it does not leave the dummy.
- **Inbound email.** How mail is received is a Foundation system choice. Standing up the live inbox belongs with building Add a Source to a List.
