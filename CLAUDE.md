# Reader

## Session types

After the user's first prompt, classify the session as one of the types below, tell the user which one you picked, and follow its instructions before doing anything else.

### Development

Anything that changes the live app: new features, changes to existing ones, and fixes.

- Read `docs/roadmap.md` first.
- Then load the `2-develop` skill and follow its loop.

### Maintenance

Changes that don't touch the live app: docs, skills, CI, the harness, the dev container.

- Update any doc the change made wrong, on the same branch. A change to how agents work here also updates `HARNESS.md`.

### Information

Answering questions about the repo. Don't change any files unless explicitly asked to; in that case, follow the Maintenance instructions.

## Git workflow

For Development and Maintenance sessions.

- If the change builds on an open PR (session start lists them), stop before branching: say that merging it first is the best course, and continue only once the user merges it or tells you how to proceed.
- Pull `main`, then branch: `dev/<name>` for Development, `maint/<name>` for Maintenance, where `<name>` is short, lowercase and hyphenated (e.g. `dev/highlight-export`).
- Commit as you go. Load `commits` before each commit, `writing-docs` before editing `docs/`, and `write-skills` before editing a skill.
- Suggest a PR once the user has signed off the change, and open it on a yes, following `pull-requests`. The user merges it, or tells you to.

## Commands

- Full health check (install, lint, test): `bash init.sh`
- Run, test, lint, and local config: `docs/development.md`

## Chat conduct

- Before a message that asks for input, add a `---` rule and a short bold label in capitals.
- Use tables, Mermaid diagrams, and headers where they make things clearer than prose.
- Give a short progress update every few steps, and end with what was done and what comes next.
- A question is not a command: answer it, and don't act on it.
