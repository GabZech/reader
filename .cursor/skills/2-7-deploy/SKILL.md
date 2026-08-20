---
name: 2-7-deploy
description: >-
  Runs Feature Development step 2.7 Deploy: ship the finished slice per
  docs/operations.md; append notes under docs/specs/<feature-slug>/deploy/.
  Use when deploying a feature, or after Documentation is accepted.
---

# Deploy

Ship the finished slice to its live environment.

## Entry

- Documentation is accepted
- Follow `docs/operations.md`; do not invent a parallel deploy story

## Artifact

- `docs/specs/<feature-slug>/deploy/`: append-only deploy notes

## Do

**Agent does:**
- Prepare the deploy checklist from `docs/operations.md`
- Remind required env/secrets and host prerequisites
- Run or draft the exact commands that apply
- Write a dated note under `deploy/` (what shipped, where, result)

**Human role:** Confirm production steps (host access, secrets, this revision). Treat Deploy as a real gate: merge/tag as ops describe, bring the live environment to the new revision, smoke whatever health or smoke checks ops define. First-time host standup (account, Docker, first live URL) is Foundation, not this step. If this is the first-product ship (Add a Source to a List, Morning News Pass, Read-Later Pass, and Highlight and Land in Obsidian all done) and the lasting public URL is about to go on the phone, run the repo-and-Fly rename and the home-screen logo in `docs/operations.md` before smoke; do not leave `reader-skeleton` as that URL, and do not ship with only the skeleton SVG favicon.

## Gate

Ask for explicit accept. On accept: update `docs/roadmap.md` “Where we are” to Monitor. Do not advance without confirmation.
