---
name: pull-requests
description: >-
  PR title and description conventions.
  Use when opening or updating a pull request.
---

# Pull requests

## Title

`type: description`, imperative mood, no scope segment.

- **type:** one word — `feat`, `fix`, `update`, `docs`, `chore`, or similar.
- **description:** concise enough to serve as a mini summary of the change on its own.
- Reference the issue or ticket when one applies: `feat: implement user profile view (closes #123)`.

This differs from the commit subject format in `commits` — PR titles carry no scope segment. This matters here because squash-merge is enforced: the PR title becomes `main`'s permanent commit message, while the branch's own commits are discarded.

## Description

1. **Summary:** one or two sentences — what changed and why.
2. **Changes:** bullet list of what was done.
3. **Testing:** how the change was verified, or scenarios considered.
4. **Out of scope:** anything deliberately left for later, if applicable.
5. **AI disclosure:** state plainly that the PR was AI-generated, e.g. `🤖 Generated with [Claude Code](https://claude.com/claude-code)`. Never omit this line.
