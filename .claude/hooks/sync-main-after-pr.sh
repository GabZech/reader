#!/usr/bin/env bash
# PostToolUse on Bash: once `gh pr create` has opened a PR, switch back to
# main and fast-forward it, so the next change starts from a fresh base.
#
# settings.json's `if: Bash(gh pr create*)` is not enough on its own: for a
# command Claude Code cannot parse (a loop, a $VAR, a heredoc) the hook runs
# anyway, which silently moved sessions onto main mid-change. So this script
# checks the command itself, and that it printed the new PR's URL.
input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')
out=$(printf '%s' "$input" | jq -r '.tool_response.stdout // ""')

printf '%s' "$cmd" | grep -qE '(^|[;&|[:space:]])gh[[:space:]]+pr[[:space:]]+create' || exit 0
printf '%s' "$out" | grep -qE 'github\.com/[^[:space:]]+/pull/[0-9]+' || exit 0

{ git checkout main && git fetch origin && git merge --ff-only origin/main; } >/dev/null 2>&1 || true
