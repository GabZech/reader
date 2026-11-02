# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Bottom bar left raised after closing Original** (Bug, behaviour only). Branch `dev/bottom-bar-after-original`. Cause, from the phone's own Diagnostics: after the in-app browser that Original opens is closed, the installed app's window can stay about 136px short (innerHeight 626 against 762) until the app is reopened, so the bar rides above the bottom edge; once in 2 of 3 returns traced it fixed itself within half a second. Shape agreed: when the app returns to the front (or a page loads) with the window much shorter than the tallest height seen this launch, not typing and only in the installed app, it tries up to three nudges to make iOS measure again, logging each try and the heights to Diagnostics (`viewport` entries). Built and committed with tests; not yet deployed or tried on the phone. Leaves alone: the bar's styling, the Original link, list rows. If the page cannot resize the window at all, two failed trial rounds mean switching Original to open in Safari itself. Feedback rounds so far: 0. Live: `main`.

Next step: trial deploy on the client's go, then they open Original, close it, and the Diagnostics `viewport` entries show whether it recovered.

## Blocked

None.
