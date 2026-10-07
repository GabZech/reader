# UI Guidelines

## Purpose

The durable look the real UI follows: warm and tactile, dark first, one accent. It replaced the stone-and-ink look of the clickable dummy after four mockup rounds and a live trial on a phone. This is a copy of that look, not a design system.

## Layout, density, chrome

- **Phone column.** Content sits in a single centred column, about 390px wide (`24.375rem`), with 10px of padding on each side (`--gutter`); full-width rows and the article's top bar cancel it to reach the screen edges. On a computer the same chrome stretches to a modestly wider column; it does not become a new layout.
- **Screen shell.** The page itself never scrolls. One full-screen container (`.scroller`) scrolls, and the bottom bar sits outside it. On an iPhone a scrolling page drags fixed elements with it, which lifted the bar off the bottom edge. Safe areas are respected at the top of the page and under the bar.
- **Solid bars, no effects.** The bottom bar and the article's top bar are opaque. No blur behind them and no full-screen overlay or blend layer anywhere: both can blank an installed iPhone app. In the installed app a 12px solid bar on the top edge colours the status strip instead of letting scrolled text show through it.
- **Cards.** A group of the same kind sits in one rounded card (1.375rem corners, soft shadow) on the page colour: each list on Home, each kind of source on Sources (its name centred, in italic). Lists is the exception that proves it: each list is its own card, with no hairlines between them. Rows inside a card are separated by hairlines. A single list on its own page is flat rows on the page, not a card.
- **Top.** Screen title, large. Icons appear in only two places: a cog for Settings (it turns inside two thin arrows while Home updates) and a plus for every add action. Everything else is words. Edit lives in Settings, not on Home.
- **Lists.** Item rows: title, then author and date, with reading or video length on the far right of that line. A small square on the left only when there is a main image. A row swiped right to left shows a panel naming what it will do (Mark as read, Mark as unread, Archive, Move to Library) and acts on release; swiped left to right it shows a red Delete panel, then a small centred popup (title, Cancel / Delete) before anything is deleted. A list page switches between its states (Unread / Read, Library / Archive) with a segmented control showing counts.
- **Home.** Only lists with something unread appear. Each shows three items, then Show more / Show less in place, flush right. The list name opens the full list. When every list is empty, one muted, centred line says "You're all caught up."
- **Bottom bar.** Fixed Home, Lists, Sources, text only. The active tab is accent-coloured on a soft accent pill. The space under the buttons is small, and the outer corners of the first and last buttons are round so they follow the curve of the phone's screen.
- **Article.** A sticky top bar with Close on the left and Read later and Open original on the right, then the title, then the body in reading type. Delete is red. A highlight is a mark in a warm amber (pale in light, deep in dark); an image a highlight covers gets a 4px outline in the same colour. A highlight carrying a section or subsection title gets a small bold `§` just before it, in the accent colour.

## Type and colour

- **Fonts.** Three, bundled with the app and cached for offline: **Fraunces** for screen titles, list names and article headings; **Literata** for item titles and article text; **Figtree** for chrome. Text waits for the font file rather than showing in a stand-in first, so weights never change after load.
- **Sizes.** Screen title about 2rem, weight 600. Item titles about 1.03rem, weight 600 until read, then regular and a shade lighter. Article body in reading type with generous line height.
- **Colour.** One accent, Marigold: `#f5a524` on dark, `#a86200` on light, used for the active tab, counts, links in articles and the `§`. Red is only for Delete and its panel. Everything else is warm paper and warm ink: page `#17120e` and cards `#221b15` on dark, `#f5eee3` and `#fffaf2` on light, with text, muted and hairline shades from the same family. Do not add a second accent.

## Dark theme

Dark is the default: a reader who has never touched the theme switch in Settings gets dark. The switch lets a reader choose light on purpose, which sticks from then on. The PWA install splash (`manifest.webmanifest`) is static and can't follow that choice, so it always matches the dark default.

## Surfaces

- **Phone** is the primary reading surface (morning News, most of Read later).
- **Computer** uses the same chrome, wider column. Favourite channels is the computer-primary list; computer width must not invent a second look.
- **Offline:** already fetched News and Read later remain readable, and so do the fonts. A page that cannot load and was never cached shows a short "Couldn't load this page" screen with a Try again button, never a blank one. Favourite channels is not an offline must.

## Out of scope

Do not restyle to match a component library. A home-screen and tab logo for Add to Home Screen waits until the MVP ships; it does not add icons inside the app.
