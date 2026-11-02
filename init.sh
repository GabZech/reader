#!/usr/bin/env bash
# Health, git, and live-state check. Run by the SessionStart hook in .claude/settings.json.
# --quick skips install/lint/test, for the SessionStart hook.
# Both modes start installing the browsers the tests need, in the background.
set -uo pipefail

INSTALL_CMD=(uv sync --locked)
LINT_CMD=(uv run ruff check)
VERIFY_CMD=(uv run pytest -q)
# --reload is unreliable on Windows in this repo (see docs/development.md);
# this is the command an agent should run when it needs the app up, not the
# one to use while actively iterating on a change.
START_CMD=(uv run uvicorn app.main:app --port 8000)

# Playwright keeps one browser build per Playwright version, and a fresh cloud
# container ships a different build from the one this repo pins, so the browser
# tests cannot launch until the right ones are installed. This installs what is
# missing (a few seconds of no-ops when all is there) and, on Linux as root,
# the system libraries an engine fails to launch without. It runs in the
# background so a session never waits on a download; the last line of the log
# says when it is done.
BROWSERS_LOG="${TMPDIR:-/tmp}/reader-browsers.log"
CAN_LAUNCH='
import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    getattr(p, sys.argv[1]).launch().close()
'
ensure_browsers() {
  (
    echo "Installing the test browsers: $(date -u +%H:%M:%S)"
    if ! uv run playwright install chromium webkit; then
      echo "Browser install FAILED"
      exit 1
    fi
    if [[ "$(uname -s)" == "Linux" && "${EUID:-1}" -eq 0 ]]; then
      for engine in chromium webkit; do
        if ! uv run python -I -c "$CAN_LAUNCH" "$engine"; then
          uv run playwright install-deps "$engine"
        fi
      done
    fi
    echo "Browsers ready"
  ) </dev/null >"$BROWSERS_LOG" 2>&1 &
}

quick=false
if [[ "${1:-}" == "--quick" ]]; then
  quick=true
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

echo "== Working directory =="
echo "$PWD"
echo

echo "== Test browsers =="
ensure_browsers
if [[ "$quick" == true ]]; then
  echo "Installing in the background if missing (log: $BROWSERS_LOG). Browser tests need its last line to read \"Browsers ready\"."
  echo
fi

if [[ "$quick" == false ]]; then
  echo "== Install, lint, test =="
  if ! "${INSTALL_CMD[@]}"; then
    echo "FAIL: ${INSTALL_CMD[*]} (say so; do not silently work around a broken lock)"
    exit 1
  fi
  # The tests launch the browsers, so wait for them.
  wait
  tail -n 1 "$BROWSERS_LOG"
  if ! grep -q "Browsers ready" "$BROWSERS_LOG"; then
    echo "FAIL: the test browsers did not install (see $BROWSERS_LOG)"
    exit 1
  fi
  if ! "${LINT_CMD[@]}"; then
    echo "FAIL: ${LINT_CMD[*]} (say it was already red; do not silently fix a baseline you did not touch)"
    exit 1
  fi
  if ! "${VERIFY_CMD[@]}"; then
    echo "FAIL: ${VERIFY_CMD[*]} (say it was already red; do not silently fix a baseline you did not touch)"
    exit 1
  fi
  echo
fi

echo "== Git state =="
branch="$(git rev-parse --abbrev-ref HEAD)"
echo "Branch: $branch"
dirty="$(git status --porcelain)"
if [[ -n "$dirty" ]]; then
  echo "Dirty files:"
  echo "$dirty"
else
  echo "Working tree clean"
fi
unpushed="$(git log '@{u}..' --oneline 2>/dev/null || true)"
if [[ -n "$unpushed" ]]; then
  echo "Unpushed commits on $branch:"
  echo "$unpushed"
fi
other_branches="$(git for-each-ref --format='%(refname:short)' refs/heads/ | grep -v -e "^main$" -e "^$branch$" || true)"
if [[ -n "$other_branches" ]]; then
  echo "Other local branches (possibly unfinished work):"
  echo "$other_branches"
fi
echo "Recent commits:"
git log --oneline -5
echo

echo "== Live vs origin/main =="
live_url="${LIVE_URL:-https://reader-skeleton.fly.dev}"
main_sha="$(git rev-parse --short origin/main 2>/dev/null || echo "unknown (no origin/main ref locally)")"
echo "origin/main: $main_sha"
health="$(curl -fsS --max-time 5 "$live_url/health" 2>/dev/null || true)"
if [[ -n "$health" ]]; then
  echo "Live $live_url/health: $health"
else
  echo "Live $live_url/health: unreachable from this session"
fi
echo

echo "== Open PRs (merge first if the next change builds on one) =="
if command -v gh >/dev/null 2>&1 && open_prs="$(gh pr list --state open 2>/dev/null)"; then
  echo "${open_prs:-None.}"
else
  echo "Unknown: gh is not installed or not logged in"
fi
echo

echo "== PROGRESS.md: In flight =="
if [[ -f PROGRESS.md ]]; then
  awk '/^## In flight/{flag=1; next} /^## /{flag=0} flag' PROGRESS.md | sed '/^$/d'
else
  echo "No PROGRESS.md"
fi
echo

echo "== Start command =="
printf '    %s\n' "${START_CMD[*]}"

if [[ "$quick" == false && "${RUN_START_COMMAND:-0}" == "1" ]]; then
  echo "==> Starting the app"
  exec "${START_CMD[@]}"
fi

if [[ "$quick" == false ]]; then
  echo "Set RUN_START_COMMAND=1 if you want init.sh to launch the app directly."
fi
