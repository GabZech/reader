#!/usr/bin/env bash
# PreToolUse on Bash: refuse a `git push` that targets main, explicitly or
# implicitly while checked out on main; let a push to any other branch
# through without a prompt.
#
# settings.json's `if: Bash(git push *)` is not enough on its own: for a
# command Claude Code cannot parse (a loop, a $VAR, a heredoc) the hook runs
# anyway. So this script checks the command itself and stays silent for
# anything that is not a push.
cmd=$(jq -r '.tool_input.command // ""')
push=$(printf '%s' "$cmd" | grep -oE 'git[[:space:]]+push[^;&|]*' | head -n 1)
[ -n "$push" ] || exit 0

decide() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"%s","permissionDecisionReason":"%s"}}\n' "$1" "$2"
}

if printf '%s' "$push" | grep -qE '(^|[[:space:]:+])main([[:space:]]|$)' \
  || [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "main" ]; then
  decide deny "git push targets main directly; merge via a PR instead (gh pr merge)"
else
  decide allow "git push to a non-main branch"
fi
