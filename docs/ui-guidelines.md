# UI Guidelines

## Purpose

The real UI follows the overall look accepted in the clickable dummy: layout, density, chrome, and quiet type. This is a copy of that look, not a design system.

## Layout, density, chrome

- **Phone column.** Content sits in a single centered column. On a phone that column is about 390px wide (`24.375rem`). On a computer the same chrome stretches to a modestly wider column; it does not become a new layout.
- **Page.** Stone page surface (`#fafaf9`) on a slightly cooler stone canvas (`#f5f5f4`). White list cards with a light border (`#e7e5e4`), 0.75rem corners, tight vertical rhythm (about 0.85rem between blocks).
- **Top.** Screen title, large and slightly tight tracking. Optional text control on the right (Edit) in the same weight as other secondary chrome. No icons.
- **Lists.** Uppercase, small, muted list name with a count. Item rows: title, then author and date, with reading length on the far right of that line (Today / Yesterday / DD/MM/YY). A small square on the left only when there is a main image; newsletters without one stay text-only.
- **Home.** Each list shows three items, then Show more / Show less in place. The list name opens the full list.
- **Bottom bar.** Fixed Home, Lists, Sources. Text only. Active tab is darker and heavier. The bar matches the column width.
- **Article.** Close, then secondary text actions (Read later, Open original). Body is readable article type, not a card grid. Highlight colour, when used later, is a pale yellow mark on the text, not a brand accent.

No icon set. No brand colour system. Controls are words.

## Type

- **Font:** `system-ui, sans-serif`
- **Body:** 1rem, line-height 1.4, near-black text (`#1c1917`)
- **Titles:** about 1.375rem, weight 650
- **Item titles:** about 1.0625rem, weight 600
- **Muted chrome:** `#57534e` / `#78716c` / `#44403c` for names, bylines, and secondary actions
- **Article body:** about 1.0625rem, line-height 1.55

Colour is stone and ink only. Do not add a product accent.

## Surfaces

- **Phone** is the primary reading surface (morning News, most of Read later).
- **Computer** uses the same chrome, wider column. Favourite channels is the computer-primary list; the dummy was phone-only, so computer width must not invent a second look.
- **Offline:** already fetched News and Read later remain readable. Favourite channels is not an offline must.

## Out of scope

Feature interactions (add to list, time window, highlighting, list edit, home edit, mark as seen, archive) wait for their SPECs. Later-scope evening video watching is out. Do not restyle to match a component library.
