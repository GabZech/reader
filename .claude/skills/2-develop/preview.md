# Preview

How to show the client what a change will look like before product code exists. Screenshots by default; a tappable page only when interaction is the thing being judged.

## Where the mockup lives

`preview/` at the repo root, gitignored and never committed. It is throwaway: delete its contents once the change is signed off. Do not reuse `docs/mockup/`, which is the accepted discovery dummy and stays frozen.

Never edit a Jinja template or `app/static/styles.css` to produce a preview. Those are product code, and editing them means the change was built before it was signed off.

## Making the mockup

1. Get the current page: request the route from the running app (local, or the live host when phone-only) and save the rendered HTML into `preview/`. That saved copy is the **before**.
2. Point it at the real stylesheet so the look is honest: copy `app/static/styles.css` next to it and fix the `<link>` path. Copy any page JavaScript the screen needs to render.
3. Duplicate the file and apply the change to the copy. Fill it with realistic content: real source names, real headlines, a plausible number of rows, including the long and empty cases the screen has to survive.
4. For a screen that does not exist yet, start from the closest existing page rather than a blank file, so chrome and density stay consistent.

## Capturing

Phone width, the app's current theme only. Do not produce a second capture for a theme the app does not ship.

```text
npx --yes playwright screenshot --channel=msedge --viewport-size=390,844 --full-page preview/<file>.html preview/<name>.png
```

Use `--channel=chrome` if Edge is absent. Add a desktop capture only when the change affects the wider column.

**Read the PNG before the client sees it.** Check overlap, truncated labels, missing controls, wrong viewport, and whether it still matches `docs/ui-guidelines.md`. Fix and recapture. If capture fails, say so rather than posting an unreviewed image or describing the look in words as a substitute.

## Showing it

Post the image in chat, with one ask: does this look right, or is something missing. For a change to an existing screen, post the before and after together.

Iterate on the mockup until the client signs the look off. Only then write product code.

## When a screenshot is not enough

The change is about interaction or flow rather than look (a new gesture, a multi-step path, something that depends on scroll or timing):

- At the computer: serve the folder and give the client the URL to tap through: `npx --yes serve preview -p 4173`
- Phone-only, where there is no way to hand over a page: say so, show screenshots of each step in order, and if the interaction still cannot be judged that way, skip the preview and build it on the branch. Step 5 judges it live, which is the point of trying it there.
