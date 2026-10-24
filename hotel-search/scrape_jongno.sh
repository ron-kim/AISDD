#!/bin/bash
# 鐘路候選飯店 × 各晚（單晚）。第 1 行：頁面標題｜日期欄位，之後為頁面文字
export AGENT_BROWSER_EXECUTABLE_PATH=${AGENT_BROWSER_EXECUTABLE_PATH:-/opt/pw-browsers/chromium} AGENT_BROWSER_SESSION=hotel
OUT="$(dirname "$0")/raw_jongno"
HOTELS=("Hanok Hotel DAAM" "Insadong N285 Hotel" "takt jongno" "VIA Jongno" "Hotel Yaja Jongno" "AMID Hotel Seoul" "ibis Ambassador Seoul Insadong" "Travelodge Dongdaemun Seoul" "SimpleStay Hotel Seoul" "Ikseon Atelier" "Mangrove Dongdaemun" "Nine Tree by Parnas Seoul Insadong")
NIGHTS="2026-12-31:2027-01-01 2027-01-01:2027-01-02 2027-01-02:2027-01-03 2027-01-03:2027-01-04"
for n in $NIGHTS; do ci=${n%:*}; co=${n#*:}
for h in "${HOTELS[@]}"; do
  f="$OUT/${h// /_}-$ci.txt"; [ -s "$f" ] && continue
  q=$(python3 -c "
import urllib.parse,sys,datetime
ci=datetime.date.fromisoformat(sys.argv[2]); co=datetime.date.fromisoformat(sys.argv[3])
print(urllib.parse.quote(f'hotels near {sys.argv[1]} Seoul {ci:%B} {ci.day} {ci.year} to {co:%B} {co.day} {co.year} 1 adult'))" "$h" "$ci" "$co")
  agent-browser open "https://www.google.com/travel/search?q=$q&hl=zh-TW&gl=TW" >/dev/null 2>&1
  for k in 1 2 3 4 5 6 7 8; do sleep 3
    t=$(agent-browser eval 'document.body.innerText' 2>/dev/null); echo "$t" | grep -q '項結果' && break; done
  head=$(agent-browser eval 'document.title+"||"+Array.from(document.querySelectorAll("input")).map(i=>i.value).join("|")' 2>/dev/null)
  printf '%s\n%s\n' "$head" "$t" > "$f"
  echo "$(date +%T) $h $ci"
  sleep 24
done; done
echo DONE
