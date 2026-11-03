#!/bin/bash
export AGENT_BROWSER_EXECUTABLE_PATH=/opt/pw-browsers/chromium
export NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt
OUT="$(dirname "$0")/raw"
# 以城市查詢：Taipei 涵蓋 TPE+TSA，Seoul 涵蓋 ICN+GMP（一頁同時列出兩個機場）
CITIES="Seoul Busan Daegu Cheongju"
jobs=()
for d in 2026-12-31 2027-01-01 2027-01-02 2027-01-03; do for a in $CITIES; do jobs+=("Taipei $a $d"); done; done
for d in 2027-01-02 2027-01-03 2027-01-04 2027-01-05; do for a in $CITIES; do jobs+=("$a Taipei $d"); done; done
JS='JSON.stringify(Array.from(document.querySelectorAll("li div[aria-label]")).map(e=>e.getAttribute("aria-label")).filter(s=>s.includes("新台幣")))'
for j in "${jobs[@]}"; do
  set -- $j; f="$OUT/$1-$2-$3.json"
  [ -s "$f" ] && continue
  url="https://www.google.com/travel/flights?q=Flights%20from%20$1%20to%20$2%20on%20$3%20one%20way&hl=zh-TW&gl=TW&curr=TWD"
  agent-browser open "$url" >/dev/null 2>&1
  for k in $(seq 1 20); do sleep 3  # 等結果載入（有票價，或頁面已顯示找不到航班）
    r=$(agent-browser eval "$JS" 2>/dev/null)
    echo "$r" | grep -q '新台幣' && break
    agent-browser eval 'document.body.innerText' 2>/dev/null | grep -q '找不到\|沒有符合' && break
  done
  echo "$r" > "$f"
  echo "$(date +%T) $j $(echo "$r" | head -c 80)"
  sleep 24
done
echo DONE
