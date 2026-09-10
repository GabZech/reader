#!/usr/bin/env bash
# Health, git, and live-state check. See AGENTS.md "Start of session".
# --quick skips install/lint/test, for the SessionStart hook.
set -uo pipefail

quick=false
if [[ "${1:-}" == "--quick" ]]; then
  quick=true
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

if [[ "$quick" == false ]]; then
  echo "== Install, lint, test =="
  if ! uv sync --locked; then
    echo "FAIL: uv sync --locked (say so; do not silently work around a broken lock)"
    exit 1
  fi
  if ! uv run ruff check; then
    echo "FAIL: ruff check (say it was already red; do not silently fix a baseline you did not touch)"
    exit 1
  fi
  if ! uv run pytest -q; then
    echo "FAIL: pytest (say it was already red; do not silently fix a baseline you did not touch)"
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

echo "== PROGRESS.md: In flight =="
if [[ -f PROGRESS.md ]]; then
  awk '/^## In flight/{flag=1; next} /^## /{flag=0} flag' PROGRESS.md | sed '/^$/d'
else
  echo "No PROGRESS.md"
fi
