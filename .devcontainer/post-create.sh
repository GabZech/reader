#!/usr/bin/env bash
set -euo pipefail

# Windows checkouts have CRLF files; match the host's autocrlf so git does not
# report every file as modified. Global to the container, not the repo's config.
git config --global core.autocrlf true

# A bind-mounted checkout is owned by another user, which git refuses by default.
git config --global --add safe.directory "$PWD"

# A fresh named volume is root-owned; Claude Code needs to write to it.
sudo chown -R "$(id -u):$(id -g)" "$HOME/.claude"

uv sync --locked

# Browser tests need Chromium plus its system libraries (apt, so root).
uv run playwright install chromium
sudo -E env "PATH=$PATH" uv run playwright install-deps chromium
