#!/bin/bash
# usage: scrape_rt.sh "TPE-ICN TSA-GMP ..."
export AGENT_BROWSER_EXECUTABLE_PATH=/opt/pw-browsers/chromium
OUT="$(dirname "$0")/raw_rt"; mkdir -p $OUT
PAIRS="2026-12-31:2027-01-02 2026-12-31:2027-01-03 2026-12-31:2027-01-04 2026-12-31:2027-01-05 2027-01-01:2027-01-02 2027-01-01:2027-01-03 2027-01-01:2027-01-04 2027-01-01:2027-01-05 2027-01-02:2027-01-03 2027-01-02:2027-01-04 2027-01-02:2027-01-05 2027-01-03:2027-01-04 2027-01-03:2027-01-05"
grab(){ # $1 = substring that must appear in labels; poll up to ~30s
  for k in 1 2 3 4 5 6 7 8 9 10; do
    r=$(agent-browser eval "JSON.stringify($LIST.map(e=>e.getAttribute('aria-label')))" 2>/dev/null)
    echo "$r" | grep -q "$1" && { echo "$r"; return; }
    echo "$r" | grep -q '找不到' && break
    sleep 3
  done; echo "$r"; }
LIST='Array.from(document.querySelectorAll("li div[aria-label]")).filter(e=>e.getAttribute("aria-label").includes("新台幣"))'
for r in $1; do o=${r%-*}; a=${r#*-}
for p in $PAIRS; do d1=${p%:*}; d2=${p#*:}
  f="$OUT/$o-$a-$d1-$d2.json"; [ -s "$f" ] && continue
  url="https://www.google.com/travel/flights?q=Flights%20from%20$o%20to%20$a%20on%20$d1%20through%20$d2%20nonstop&hl=zh-TW&gl=TW&curr=TWD"
  agent-browser open "$url" >/dev/null 2>&1; sleep 4
  outs=$(grab "於.\\{2,12\\}機場出發")
  # choose indices: cheapest direct overall + cheapest direct departing <=09:30
  idx=$(echo "$outs" | python3 -c '
import sys,json,re
L=json.loads(json.loads(sys.stdin.read() or "\"[]\""))
def t(s):
  m=re.search(r"(凌晨|清晨|上午|中午|下午|晚上)(\d+):(\d+) 於",s)
  if not m: return 9999
  h=int(m.group(2))%12; h+= 12 if m.group(1) in("下午","晚上") or (m.group(1)=="中午" and h<11) else 0
  return h*60+int(m.group(3))
def pr(s): return int(re.search(r"(\d+) 新台幣",s).group(1))
c=[(pr(s),i,t(s)) for i,s in enumerate(L) if "直達" in s and "分段購票" not in s]
sel=[]
if c: sel.append(min(c)[1])
e=[x for x in c if x[2]<=570]
if e and min(e)[1] not in sel: sel.append(min(e)[1])
print(" ".join(map(str,sel)))')
  res="{\"out\":$outs,\"picks\":{"
  first=1
  for i in $idx; do
    sleep 23
    agent-browser open "$url" >/dev/null 2>&1; sleep 4; grab 新台幣 >/dev/null
    agent-browser eval "($LIST)[$i].click()" >/dev/null 2>&1; sleep 4
    rets=$(grab "抵達臺")
    [ $first = 1 ] || res="$res,"; first=0
    res="$res\"$i\":$rets"
  done
  echo "$res}}" > "$f"
  echo "$(date +%T) RT $o $a $d1 $d2 picks=[$idx]"
  sleep 23
done; done
echo RTDONE
