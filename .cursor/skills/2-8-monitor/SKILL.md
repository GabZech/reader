---
name: 2-8-monitor
description: >-
  Runs Feature Development step 2.8 Monitor: short post-deploy evidence under
  docs/specs/<feature-slug>/monitor/. Use when monitoring a deployed feature,
  or after Deploy is accepted.
---

# Monitor

Look at the feature running in the real environment and gather short evidence that it behaves as intended. The SPEC cycle is complete only after this succeeds.

## Entry

- Deploy is accepted
- Use checks and procedures from `docs/operations.md` when present

## Artifact

- `docs/specs/<feature-slug>/monitor/`: append-only evidence notes

## Do

**Minimum bar:**
- Health or smoke check defined in ops docs (or equivalent)
- Service status / recent logs for the services this feature touched
- Confirm the feature’s acceptance criteria in the live environment when practical
- Note backup/restore items only when the change touched backup or data layout
- Write a dated evidence note under `monitor/`

If Monitor fails, return to Build (fix) or Deploy (rollback/redeploy). Do not silently mark the SPEC complete.

**Human role:** Confirm the evidence is enough to close the cycle.

## Gate

Ask for explicit accept. On accept:
- Update `docs/roadmap.md` “Where we are” (feature complete; propose next MVP epic or mark **Milestone: MVP** if the MVP cut is done)
- Do not mark the SPEC complete without that confirmation
