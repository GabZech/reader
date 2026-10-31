# Reader

## Session types

After the user's first prompt, classify the session as one of the types below, tell the user which one you picked, and follow its instructions before doing anything else.

### Development

Anything that changes the live app: new features, changes to existing ones, and fixes.

- Read `docs/roadmap.md` first.
- Then load the `2-develop` skill.

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
- Suggest a PR once the user has signed off the change, and open it on a yes, following `pull-requests`. Before opening it, run the full suite locally the way CI runs it on pull requests (`uv run pytest --browsers=webkit,chromium`), and fix what fails first; if an engine cannot run in this environment, run the rest and say which part was left to CI. A Maintenance change that touches only docs and skills skips the full run: run `uv run ruff check` and `uv run pytest tests/test_harness_refs.py` instead, and say in the PR that CI runs the rest. The user merges it, or tells you to; when you merge, squash and delete the branch (`gh pr merge --squash --delete-branch`).

## Commands

- Full health check (install, lint, test): `bash init.sh`
- Run, test, lint, and local config: `docs/development.md`
- Browser: WebKit is the default for anything run in a browser (tests, screenshots, trying a page or the live app), since the app is used mostly on an iPhone. Use Chromium only where WebKit cannot do the job, or as the second engine before a pull request.

## Chat conduct

- Before a message that asks for input, add a `---` rule and a short bold label in capitals.
- Use tables, Mermaid diagrams, and headers where they make things clearer than prose.
- Give a short progress update every few steps, and end with what was done and what comes next.
- When a task is finished and merged, recommend `/clear`, or `/compact` if context has grown but continuity still matters.
- A question ("can / could you X?") is not a request: just answer it, don't act on it.
