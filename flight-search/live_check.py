"""即時查價（約 5 分鐘）：只查下方 jobs 列出的重點方案。用法：python3 live_check.py [輸出路徑]；ONLY=RT 只查來回。
Google Flights 指定去程（航空+時刻）→ 指定回程的來回總價；以及單程指定班次價格。"""
import json, re, subprocess, time, sys
ENV = {'AGENT_BROWSER_EXECUTABLE_PATH': '/opt/pw-browsers/chromium', 'AGENT_BROWSER_SESSION': 'verify'}
import os; env = dict(os.environ, **ENV)
LIST = 'Array.from(document.querySelectorAll("li div[aria-label]")).filter(e=>e.getAttribute("aria-label").includes("新台幣"))'
def ab(*a):
    return subprocess.run(['agent-browser', *a], env=env, capture_output=True, text=True).stdout.strip()
def labels():
    out = ab('eval', f"JSON.stringify(({LIST}).map(e=>e.getAttribute('aria-label')))")
    try: return json.loads(json.loads(out))
    except Exception: return []
def wait(pred, n=20):
    for _ in range(n):
        time.sleep(3); L = labels()
        if pred(L): return L
    return labels()
def price(s): return int(re.search(r'(\d+) 新台幣', s).group(1))
def find(L, airline, clock): return next((i for i, s in enumerate(L) if f'{airline}的直達' in s and clock in s), None)
def url(q): return 'https://www.google.com/travel/flights?q=' + q.replace(' ', '%20') + '&hl=zh-TW&gl=TW&curr=TWD'
def rt(o, d, d1, d2, out_air, out_clock, ret_air, ret_clock):
    ab('open', url(f'Flights from {o} to {d} on {d1} through {d2} nonstop'))
    L = wait(lambda L: len(L) > 0)
    i = find(L, out_air, out_clock)
    if i is None: return None, '去程班次不在結果中'
    ab('eval', f'({LIST})[{i}].click()')
    R = wait(lambda R: any('抵達臺' in s for s in R))
    j = find(R, ret_air, ret_clock)
    return (price(R[j]), '') if j is not None else (None, f'去程 {price(L[i])} 起，但指定回程不在結果中')
def ow(o, d, day, air, clock):
    ab('open', url(f'Flights from {o} to {d} on {day} one way'))
    L = wait(lambda L: len(L) > 0)
    i = find(L, air, clock)
    return (price(L[i]), '') if i is not None else (None, '班次不在結果中')
jobs = [
 ('RT 韓亞 12/31→1/3 08:00', rt, ('TPE','ICN','2026-12-31','2027-01-03','韓亞航空','下午5:05','韓亞航空','上午8:00')),
 ('RT 韓亞 12/31→1/2 13:50', rt, ('TPE','ICN','2026-12-31','2027-01-02','韓亞航空','下午5:05','韓亞航空','下午1:50')),
 ('RT 韓亞 1/2→1/4 08:00', rt, ('TPE','ICN','2027-01-02','2027-01-04','韓亞航空','下午5:05','韓亞航空','上午8:00')),
 ('RT 酷航 12/31→1/4 22:55', rt, ('TPE','ICN','2026-12-31','2027-01-04','酷航','下午6:10','酷航','晚上10:55')),
 ('RT 酷航 1/1→1/4 22:55', rt, ('TPE','ICN','2027-01-01','2027-01-04','酷航','下午6:10','酷航','晚上10:55')),
 ('RT 虎航 1/1→1/5 00:30', rt, ('TPE','ICN','2027-01-01','2027-01-05','台灣虎航','晚上8:00','台灣虎航','凌晨12:30')),
 ('OW 酷航 12/31 18:10 TPE→ICN', ow, ('TPE','ICN','2026-12-31','酷航','下午6:10')),
 ('OW 酷航 1/1 18:10 TPE→ICN', ow, ('TPE','ICN','2027-01-01','酷航','下午6:10')),
 ('OW 酷航 1/4 22:55 ICN→TPE', ow, ('ICN','TPE','2027-01-04','酷航','晚上10:55')),
 ('OW 虎航 1/5 00:30 ICN→TPE', ow, ('ICN','TPE','2027-01-05','台灣虎航','凌晨12:30')),
]
res = {}
for name, fn, args in [j for j in jobs if j[0].startswith(os.environ.get("ONLY", ""))]:
    p, note = fn(*args); res[name] = (p, note)
    print(time.strftime('%H:%M:%S'), name, p, note, flush=True)
    time.sleep(12)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live', time.strftime('%Y%m%d-%H%M') + '.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
print('saved', out)
