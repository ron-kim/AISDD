#!/bin/bash
# HTML → PNG（需 agent-browser 與 Chromium）
cd "$(dirname "$0")"
export AGENT_BROWSER_EXECUTABLE_PATH=${AGENT_BROWSER_EXECUTABLE_PATH:-/opt/pw-browsers/chromium} AGENT_BROWSER_SESSION=render
agent-browser set viewport 1800 900 >/dev/null
rm -f rank_*.png
for h in rank_all.html rank_early_late_p*.html; do
  agent-browser open "file://$PWD/$h" >/dev/null && sleep 1
  agent-browser screenshot --full "$PWD/${h%.html}.png" >/dev/null && echo "${h%.html}.png"
done
agent-browser close >/dev/null
