# Evaluator rubric

A scorecard for a completed session's own work, run after Ship on a not-small change, not on every typo fix. It grades what a session did, not whether the change can merge: the client's live sign-off is the only merge gate (`AGENTS.md` Definition of Done), and this rubric never substitutes for it. Optional, like the rest of `docs/decisions.md` 2026-09-10's position on review passes.

| Category | Question | Score (0-2) | Notes |
| --- | --- | --- | --- |
| Correctness | Does the implemented behaviour match what Shape said it would be? |  |  |
| Verification | Did the required checks for each kind the change carried actually run, per the change-kinds table in `.claude/skills/2-develop/SKILL.md`? |  |  |
| Scope discipline | Did the session stay inside what Shape said it would leave alone? |  |  |
| Reliability | Does the result survive `bash init.sh` from a clean checkout, without repair? |  |  |
| Maintainability | Is the code and documentation clear enough for the next session? |  |  |
| Handoff readiness | Can a fresh session continue from `PROGRESS.md` and the committed code alone? |  |  |

## Verdict

- Accept
- Revise
- Block

## Required follow-up

- Missing evidence:
- Required fixes:
- Next review trigger:

## Tuning

Out of the box, agents are poor self-judges: they identify issues then talk themselves into approving. Plan for three to five rounds of scoring a completed change, comparing the score against the client's own judgement, and tightening whichever row diverged. Record each tightening here so the alignment work is visible, rather than re-litigating it from scratch each time.
