#!/bin/bash
# Google 飯店：首爾各區 × 各晚（單晚）列表頁文字。第 1 行：頁面標題｜日期欄位，之後為頁面文字
export AGENT_BROWSER_EXECUTABLE_PATH=${AGENT_BROWSER_EXECUTABLE_PATH:-/opt/pw-browsers/chromium} AGENT_BROWSER_SESSION=hotel
OUT="$(dirname "$0")/raw"
AREAS="明洞:Myeongdong 弘大:Hongik_University_Station 東大門:Dongdaemun_Station 首爾站:Seoul_Station 鐘路:Jongno 江南:Gangnam 聖水:Seongsu 梨泰院:Itaewon 汝矣島:Yeouido 蠶室:Jamsil"
NIGHTS="2026-12-31:2027-01-01 2027-01-01:2027-01-02 2027-01-02:2027-01-03 2027-01-03:2027-01-04"
for n in $NIGHTS; do ci=${n%:*}; co=${n#*:}
for p in $AREAS; do a=${p%%:*}; en=${p#*:}; en=${en//_/ }
  f="$OUT/$a-$ci.txt"; [ -s "$f" ] && continue
  q=$(python3 -c "
import urllib.parse,sys,datetime
ci=datetime.date.fromisoformat(sys.argv[2]); co=datetime.date.fromisoformat(sys.argv[3])
print(urllib.parse.quote(f'hotels in {sys.argv[1]} Seoul {ci:%B} {ci.day} {ci.year} to {co:%B} {co.day} {co.year} 1 adult'))" "$en" "$ci" "$co")
  agent-browser open "https://www.google.com/travel/search?q=$q&hl=zh-TW&gl=TW&curr=TWD" >/dev/null 2>&1
  for k in 1 2 3 4 5 6 7 8; do sleep 3
    t=$(agent-browser eval 'document.body.innerText' 2>/dev/null); echo "$t" | grep -q 'US\$[0-9]\|NT\$[0-9]' && break; done
  head=$(agent-browser eval 'document.title+"||"+Array.from(document.querySelectorAll("input")).map(i=>i.value).join("|")' 2>/dev/null)
  printf '%s\n%s\n' "$head" "$t" > "$f"
  echo "$(date +%T) $a $ci $(echo "$head" | head -c 90)"
  sleep 24
done; done
echo DONE
