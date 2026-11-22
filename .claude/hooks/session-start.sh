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

# ECC plugin (https://github.com/affaan-m/ECC), installed at user scope.
# Failures are non-fatal so a network hiccup never blocks the session.
if command -v claude >/dev/null 2>&1; then
  if ! claude plugin marketplace list 2>/dev/null | grep -q 'ecc'; then
    claude plugin marketplace add https://github.com/affaan-m/ECC >/dev/null 2>&1 || true
  fi
  if ! claude plugin list 2>/dev/null | grep -q 'ecc@ecc'; then
    claude plugin install ecc@ecc --scope user >/dev/null 2>&1 || true
  fi
fi

# Scrapling (https://github.com/D4Vinci/Scrapling) with its fetchers.
# patchright needs its own Chromium build; it is added next to the pre-installed ones.
# Failures are non-fatal so a network hiccup never blocks the session.
SCRAPLING_VERSION="0.5.1"
if ! pip show scrapling 2>/dev/null | grep -q "^Version: ${SCRAPLING_VERSION}$"; then
  pip install -q "scrapling[fetchers]==${SCRAPLING_VERSION}" >/dev/null 2>&1 || true
fi
if command -v scrapling >/dev/null 2>&1; then
  python3 -m patchright install chromium >/dev/null 2>&1 || true
fi
