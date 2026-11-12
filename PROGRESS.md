# Progress

Snapshot of in-flight state, overwritten rather than appended. When to update it is in the `2-develop` skill.

## In flight

**Security fixes** from the security review (Behaviour, Bug, Chore). Branch `dev/security-fixes`. Agreed: the six slices below; bookmarklet becomes a hand-off to a Reader tab that keeps the rendered HTML and needs no key. Leaves alone: the iPhone Shortcut's save key, the schema. Feedback rounds: 0. Next: build slice 1.

### Planned

1. Dependency upgrades (FastAPI/Starlette, python-multipart, urllib3, certifi): not started
2. Link schemes: only http(s) item and image URLs stored and rendered: not started
3. Server fetch guard: refuse private and internal addresses, every redirect hop: not started
4. Cross-site POST Origin check and script policy (inline scripts moved out): not started
5. Bookmarklet hand-off, no key: not started
6. Lockout email cap, one an hour: not started

## Blocked

None.
