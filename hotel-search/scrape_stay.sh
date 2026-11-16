#!/bin/bash
# Agoda 飯店頁 × 一次查整段住宿（checkIn + los 晚，1 位大人、1 間房）；房價區塊顯示「每晚（不含稅）」平均。
# usage: CHECKIN=2027-01-01 LOS=5 HOTELS="key:slug[@city] ..." bash scrape_stay.sh
export AGENT_BROWSER_EXECUTABLE_PATH=${AGENT_BROWSER_EXECUTABLE_PATH:-/opt/pw-browsers/chromium} AGENT_BROWSER_SESSION=agoda
CHECKIN=${CHECKIN:-2027-01-01}; LOS=${LOS:-5}
OUT="$(dirname "$0")/raw_stay/$CHECKIN-$LOS"; mkdir -p "$OUT"
for p in $HOTELS; do k=${p%%:*}; slug=${p#*:}; city=seoul-kr; case $slug in *@*) city=${slug#*@}; slug=${slug%@*};; esac
  f="$OUT/$k.json"; [ -s "$f" ] && continue
  agent-browser open "https://www.agoda.com/zh-tw/$slug/hotel/$city.html?checkIn=$CHECKIN&los=$LOS&rooms=1&adults=1&children=0&currency=TWD" >/dev/null 2>&1
  n=0
  for i in 1 2 3 4 5 6 7 8 9 10; do sleep 3
    agent-browser scroll down 1200 >/dev/null 2>&1
    n=$(agent-browser eval '(document.querySelector("[data-element-name=roomgrid]")?.innerText||"").length' 2>/dev/null)
    [ "${n:-0}" -gt 200 ] && break
    agent-browser eval 'document.body.innerText' 2>/dev/null | grep -q '已完售' && [ $i -ge 4 ] && break; done
  sleep 2
  agent-browser eval 'JSON.stringify({title:document.title,url:location.href,head:document.body.innerText.slice(0,3000),grid:document.querySelector("[data-element-name=roomgrid]")?.innerText||""})' > "$f" 2>/dev/null
  echo "$(date +%T) $k grid=$n"
  sleep 12
done
echo DONE
