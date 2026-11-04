#!/bin/bash
export AGENT_BROWSER_EXECUTABLE_PATH=/opt/pw-browsers/chromium
export NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt
OUT="$(dirname "$0")/raw"
# 以城市查詢：Taipei 涵蓋 TPE+TSA，Seoul 涵蓋 ICN+GMP（一頁同時列出兩個機場）
CITIES=${CITIES:-"Seoul"}  # 只看台北⇄首爾（仁川）；要放寬可設 CITIES="Seoul Busan Daegu Cheongju"
jobs=()
for d in 2026-12-31 2027-01-01 2027-01-02 2027-01-03; do for a in $CITIES; do jobs+=("Taipei $a $d"); done; done
# 回程查到 1/7（1/7 凌晨 00:00–04:59 起飛的深夜班算 1/6 晚上）
for d in 2027-01-02 2027-01-03 2027-01-04 2027-01-05 2027-01-06 2027-01-07; do for a in $CITIES; do jobs+=("$a Taipei $d"); done; done
JS='JSON.stringify(Array.from(document.querySelectorAll("li div[aria-label]")).map(e=>e.getAttribute("aria-label")).filter(s=>s.includes("新台幣")))'
for j in "${jobs[@]}"; do
  set -- $j; f="$OUT/$1-$2-$3.json"
  [ -s "$f" ] && continue
  url="https://www.google.com/travel/flights?q=Flights%20from%20$1%20to%20$2%20on%20$3%20one%20way&hl=zh-TW&gl=TW&curr=TWD"
  agent-browser open "$url" >/dev/null 2>&1
  loaded=
  for k in $(seq 1 20); do sleep 3  # 等結果載入（有票價，或頁面已顯示找不到航班）
    r=$(agent-browser eval "$JS" 2>/dev/null)
    echo "$r" | grep -q '新台幣' && break
    # 頁面已載入完成（顯示「找到 N 項結果」或「找不到」）但沒有票價 → 再等一輪就放棄，不必等滿上限
    if agent-browser eval 'document.body.innerText' 2>/dev/null | grep -qE '找到 [0-9]+ 項結果|找不到'; then
      [ -n "$loaded" ] && break; loaded=1; fi
  done
  echo "$r" > "$f"
  echo "$(date +%T) $j $(echo "$r" | head -c 80)"
  sleep 12  # 每頁間隔（含載入）約 15 秒
done
echo DONE
