# Roadmap

## Where We Are

**📍 Phase:** Build for Manage sources (increment map complete; not yet asked to Deploy)

**🏁 Next Milestone:** MVP

**📄 Summary:**

- Foundation accepted: architecture, development, operations, UI guidelines, and a walking skeleton that follows the accepted look, including a live Fly URL
- Manage sources: all 8 increments signed off (feed-to-News, list creation, choose-list, existing-source screen, rename, add-to-list from a source's screen, YouTube channels onto Favourite channels, and newsletters auto-detected via the isolated mailbox). Sources can belong to several lists at once, a scope change made mid-build; see the deviation note on increment 6 in [plan.md](epics/manage-sources/plan.md)
- Newsletters are auto-detected, not manually added: mail from a never-seen sender at the isolated mailbox creates its source on its own, unlisted. Sources groups by kind (Newsletter, RSS, YouTube), newest first per group; a newly-arrived source keeps a highlight and a red dot on the Sources tab until that specific source is opened (refined mid-increment by client request; see the deviation note on increment 8 in plan.md)
- PR #14 merged `build/manage-sources` into `main` (2026-08-24), through increment 7 plus two small out-of-epic fixes (dark mode with a Settings screen; Home Edit). Mid-epic merge, not this epic's Deploy — `plan.md`/`clarifying-answers.md` stay open until Deploy
- A new **Improve UI** epic was added to the MVP catalog, last in build order: it revisits `docs/ui-guidelines.md` beyond the mockup-era look once the rest of the MVP is built
- Client subscribed to a real newsletter through the isolated mailbox (2026-08-24) and confirmed it works, clearing increment 8's carried test-approach risk (the timing target itself is still unmeasured, not yet flagged as a problem)

**⚠️ Open:**

- Next up: the ingested newsletter text's formatting is not great and needs improving — not yet planned as part of any named increment
- Not asked to Deploy the Manage sources epic yet

## 📌 Post-MVP Notes

- Keep the GitHub repo name and the Fly URL `reader-skeleton.fly.dev` through feature work. Before the MVP is put on the phone as the lasting URL, rename the repo, stand up a new Fly app name (Fly cannot rename in place), and add a home-screen logo that shows when the site is installed
- Review the deploy-per-increment cadence adopted so Build's try-and-sign-off loop could run against the live Fly URL while working phone-only. Revisit whether to keep it once local testing is viable again, possibly splitting into separate dev/prod Fly apps
- Once the MVP is up, back up the Fly volume's SQLite library regularly (roughly weekly); sources and articles live only on Fly and are never committed to the repo

## Concluded

- ✅ **Kickoff:** [proposition](vision/proposition.md), [metrics](vision/metrics.md); session log under [history/discovery/01-kickoff](history/discovery/01-kickoff/)
- ✅ **Understand:** [personas](vision/personas.md), [journeys](vision/journeys.md), [constraints](vision/constraints.md); session log under [history/discovery/02-understand](history/discovery/02-understand/)
- ✅ **Scope:** [epics](vision/epics.md); session log under [history/discovery/03-scope](history/discovery/03-scope/)
- ✅ **Mockup:** [mockup](history/discovery/04-mockup/mockup.md); session log under [history/discovery/04-mockup](history/discovery/04-mockup/)
- ✅ **Foundation:** [architecture](architecture.md), [development](development.md), [operations](operations.md), [UI guidelines](ui-guidelines.md); session log under [history/discovery/05-foundation](history/discovery/05-foundation/)
