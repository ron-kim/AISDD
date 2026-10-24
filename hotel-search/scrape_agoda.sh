#!/bin/bash
# Agoda 飯店頁 × 各晚（1 位大人、1 間房）。存：標題、頁首文字（日期／地址）、房型區塊文字
export AGENT_BROWSER_EXECUTABLE_PATH=${AGENT_BROWSER_EXECUTABLE_PATH:-/opt/pw-browsers/chromium} AGENT_BROWSER_SESSION=agoda
OUT="$(dirname "$0")/raw_agoda"
HOTELS=${HOTELS:-"yaja:hotel-yaja-jongno simplestay:h47228412 ibis:ibis-ambassador-seoul-insadong-hotel n285:n285hotel travelodge:travelodge-dongdaemun-seoul amid:center-mark-hotel ninetree:nine-tree-premier-hotel-insadong"}
for d in 2026-12-31 2027-01-01 2027-01-02 2027-01-03; do
for p in $HOTELS; do k=${p%%:*}; slug=${p#*:}
  f="$OUT/$k-$d.json"; [ -s "$f" ] && continue
  agent-browser open "https://www.agoda.com/zh-tw/$slug/hotel/seoul-kr.html?checkIn=$d&los=1&rooms=1&adults=1&children=0&currency=TWD" >/dev/null 2>&1
  for i in 1 2 3 4 5 6 7 8 9 10; do sleep 3
    agent-browser scroll down 1200 >/dev/null 2>&1
    n=$(agent-browser eval '(document.querySelector("[data-element-name=roomgrid]")?.innerText||"").length' 2>/dev/null)
    [ "${n:-0}" -gt 200 ] && break; done
  sleep 2
  agent-browser eval 'JSON.stringify({title:document.title,url:location.href,head:document.body.innerText.slice(0,3000),grid:document.querySelector("[data-element-name=roomgrid]")?.innerText||""})' > "$f" 2>/dev/null
  echo "$(date +%T) $k $d grid=$n"
  sleep 15
done; done
echo DONE
