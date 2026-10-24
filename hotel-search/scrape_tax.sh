#!/bin/bash
# 每間飯店進一次 Agoda 結帳頁（1/2 入住 1 晚），記錄房型區塊第一個價格（不含稅）與結帳頁含稅總價，用來換算稅率
export AGENT_BROWSER_EXECUTABLE_PATH=${AGENT_BROWSER_EXECUTABLE_PATH:-/opt/pw-browsers/chromium} AGENT_BROWSER_SESSION=agoda
OUT="$(dirname "$0")/raw_agoda"; D=${D:-2027-01-02}
for p in $HOTELS; do k=${p%%:*}; slug=${p#*:}
  f="$OUT/tax-$k.json"; [ -s "$f" ] && continue
  agent-browser open "https://www.agoda.com/zh-tw/$slug/hotel/seoul-kr.html?checkIn=$D&los=1&rooms=1&adults=1&children=0&currency=TWD" >/dev/null 2>&1
  for i in 1 2 3 4 5 6 7 8 9 10; do sleep 3; agent-browser scroll down 1200 >/dev/null 2>&1
    n=$(agent-browser eval '(document.querySelector("[data-element-name=roomgrid]")?.innerText||"").length' 2>/dev/null); [ "${n:-0}" -gt 200 ] && break; done
  first=$(agent-browser eval '(()=>{const t=document.querySelector("[data-element-name=roomgrid]").innerText;const m=t.match(/NT\$\s*\n?([\d,]+)\s*\n?每晚/);const b=Array.from(document.querySelectorAll("[data-element-name=roomgrid] button, [data-element-name=roomgrid] a")).find(x=>/^預訂$|立即預訂/.test(x.innerText.trim()));if(b)b.click();return m?m[1]:""})()' 2>/dev/null | tr -d '"')
  sleep 12
  agent-browser eval "JSON.stringify({first:\"$first\",url:location.href.slice(0,200),body:document.body.innerText.slice(0,4000)})" > "$f" 2>/dev/null
  echo "$(date +%T) tax $k first=$first"
  sleep 10
done
echo TAXDONE
