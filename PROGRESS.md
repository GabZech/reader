# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Password protection** (`dev/password-protection`). Kinds: behaviour, data/schema, visual, external system (sending mail). Not small. Planning confirmed and mockups signed off in chat. All four slices built; the branch (050383f, with the security review fixes) is live on the Fly app for the client to try. Awaiting sign-off.

### Agreed

- One password, set and changed only as a Fly secret (never typed in chat, no change form in the app). Only a hash is compared; no password set means the app refuses everyone.
- Password only: no passkeys (revisit after the planned URL rename).
- A correct password gives that browser a long-lived cookie; the server keeps only a hash of each device's token, in a new table.
- A browser sign-in ends after 30 days unused (each use resets the clock) or when revoked. Changing the password on Fly signs out every browser, not the save keys.
- Save keys (bookmarklet, iOS Shortcut): one per tool, can only save to Read later (`/capture`), never expire, revoked by hand. Shown once at creation; stored hashed.
- Always open: `/health`, the login page, its styles and fonts. Everything else needs a sign-in.
- 5 wrong passwords from one network locks that network for 15 minutes.
- Email alert (from the app's newsletter mailbox) on a new sign-in or a lockout, to an address set on Fly. A failed send never blocks sign-in; it shows on Diagnostics.
- Left alone: the library schema (one new table only), the Obsidian export, ingest, sync.

### Offline work meets auth (found on re-reading main, merged after the plan was first sketched)

- The service worker syncs and prefetches in the background on every open. A signed-out or revoked device must get a plain 401 from fetches, never a redirect to the login page, so the worker can never store the login page as a saved copy of an article.
- On a 401 the worker stops its background work and clears its stored pages; the phone shows the login page instead.
- Highlights and moves waiting in the phone's queue are kept through a sign-out or revoke and sent after the next sign-in, so nothing written offline is lost.
- The login page is added to the worker's offline answers so an installed app signed out offline still shows something sensible.

### Planned

1. Password gate (login page, cookie, lockout, service worker 401 handling, sign-out in Settings): built, tests green, on the branch; live for trying
2. Devices page (list, rename, revoke, sign out everything else): built, tests green, looked at on the real local app; live for trying
3. Save keys (create, revoke, bookmarklet and Shortcut steps, `docs/operations.md`): built, tests green (including the bookmarklet run from another site in a real browser), looked at on the real local app; live for trying
4. Email alerts: built and tested against a fake mail server; not yet proved against Gmail from Fly (the first real alert after deploy is the probe); live for trying

Mockups signed off in chat: login page (sentence about 30 days removed), Devices page, Settings with the Security section, the one-time save key screen.

Slices 1 to 3 ship together, since slice 1 alone would leave `/capture` closed to the bookmarklet and Shortcut. Library copied off the volume before the first deploy of the new table.

### Client to do

1. Set the password as the LOGIN_PASSWORD Fly secret before slice 1 goes live.
2. Redo the Shortcut and bookmarklet (slice 3).
3. Set the alert address as a Fly secret (slice 4).

## Blocked

None.
