---
name: write-skills
description: >-
  Author or edit project Agent Skills under .cursor/skills/ with succinct,
  non-redundant copy. Use when creating, updating, or refactoring SKILL.md
  files or skill reference docs in this repo.
---

# Write skills

Conventions for skills in `.cursor/skills/`. Follow these when adding or changing a skill.

For **project-agnostic phase skills and question banks**, follow the engagement sequence in the **create-phase-skill** skill (`.cursor/skills/create-phase-skill/SKILL.md`) before applying the craft rules below.

## Hard rules

1. **Succinct.** Assume the agent is competent. Instructions only — no tutorials, pep talk, or restating the obvious.
2. **Say it once.** One rule → one place. Do not repeat the same point across principles, anti-patterns, and flow. Prefer the positive instruction; drop the echo.
3. **Direction, not examples.** State the constraint or desired behaviour directly. Do not teach via bad/good samples, sample dialogues, or illustrative quotes.
4. **Split style from content.** Reusable conversation or delivery norms → a cross-cutting skill (e.g. `questioning`). Phase-specific menus, exit criteria, and artifacts → the phase skill (and optional linked bank).
5. **Progressive disclosure.** Keep `SKILL.md` short. Put long menus or banks in a sibling file linked one level deep.
6. **Match the house style.** Phase skills stay terse: Entry, Artifacts, Do, Gate. Don’t inflate them toward essays.

## SKILL.md shape

```markdown
---
name: lowercase-hyphen-name
description: >-
  What it does. Use when [trigger terms].
---

# Title

One-line purpose.

## …only sections the agent needs…
```

- **description:** third person; WHAT + WHEN; include trigger terms; max 1024 chars.
- **Body:** under ~80 lines when practical; never pad to look complete.

## Edit checklist

- [ ] Can any paragraph be deleted without changing behaviour? Delete it.
- [ ] Is the same constraint stated twice? Keep the stronger wording once.
- [ ] Does this belong in another skill (style vs phase content)? Move it.
- [ ] Are long lists in `SKILL.md`? Move to a linked reference file.
- [ ] Any examples or bad/good tables? Replace with a direct rule.
