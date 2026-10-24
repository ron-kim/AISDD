#!/bin/bash
set -euo pipefail

# Only run in Claude Code cloud sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Project dependencies
npm install --no-audit --no-fund

# agent-browser CLI (uses the pre-installed Chromium instead of downloading one)
AGENT_BROWSER_VERSION="0.39.2"
if ! agent-browser --version 2>/dev/null | grep -q "$AGENT_BROWSER_VERSION"; then
  npm install -g "agent-browser@${AGENT_BROWSER_VERSION}" --no-audit --no-fund
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export AGENT_BROWSER_EXECUTABLE_PATH=/opt/pw-browsers/chromium' >> "$CLAUDE_ENV_FILE"
fi
