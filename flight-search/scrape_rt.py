#!/usr/bin/env python3
"""來回票爬蟲（兩階段，省查詢量）。用法：python3 scrape_rt.py ["Taipei-Seoul ..."]

第一階段：每組日期只開 1 頁，記下每班去程的「來回總價 X 起」，不點選。
第二階段：只點「價格和前版不同（或前版沒有）」而且排在最便宜前 MAX_CLICKS 名的去程，確認回程班次與票價。
其餘去程沿用前版的回程清單：最低價沒變 → 原價沿用；有變 → 依最低價的差額推估（est）。

環境變數：GAP 每次查詢間隔秒數（預設 24）；MAX_CLICKS 第二階段最多點幾班（預設 15）；
PAIRS 指定日期組 "2026-12-31:2027-01-05 ..."；FORCE_CLICK=1 不管前版，候選全部重點。
被 Google 限流或要求驗證時立即停止（exit 2）；已抓到的會保留，重跑會接續。
"""
import json, os, re, subprocess, sys, time
import build

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'raw_rt'); os.makedirs(OUT, exist_ok=True)
GAP = int(os.environ.get('GAP', 24))
MAX_CLICKS = int(os.environ.get('MAX_CLICKS', 15))
MAX_AIRLINES = int(os.environ.get('MAX_AIRLINES', 6))
OUT_DATES = ['2026-12-31', '2027-01-01', '2027-01-02', '2027-01-03']
RET_DATES = ['2027-01-02', '2027-01-03', '2027-01-04', '2027-01-05', '2027-01-06', '2027-01-07']
LAST_RET = RET_DATES[-1]            # 這天只用來抓前一晚的深夜班
NIGHT_AIRLINES = os.environ.get('NIGHT_AIRLINES', '台灣虎航').split(',')
ENV = dict(os.environ, AGENT_BROWSER_EXECUTABLE_PATH=os.environ.get('AGENT_BROWSER_EXECUTABLE_PATH', '/opt/pw-browsers/chromium'))
LIST = 'Array.from(document.querySelectorAll("li div[aria-label]")).filter(e=>e.getAttribute("aria-label").includes("新台幣"))'

def ab(*a): return subprocess.run(['agent-browser', *a], env=ENV, capture_output=True, text=True).stdout.strip()
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def labels():
    try: return json.loads(json.loads(ab('eval', f"JSON.stringify(({LIST}).map(e=>e.getAttribute('aria-label')))")))
    except Exception: return []
def page_text(): return ab('eval', 'location.href+document.body.innerText')
def throttled(t=None): return bool(re.search(r'系統發生錯誤|/sorry/|異常流量', t if t is not None else page_text()))
def grab(pred, n=20):
    """等到列表符合 pred；頁面已載入完成但沒有符合的項目時，多等一輪就放棄。"""
    loaded = False
    for _ in range(n):
        L = labels()
        if pred(L): return L
        if re.search(r'找到 \d+ 項結果|找不到', page_text()):
            if loaded: break
            loaded = True
        time.sleep(3)
    return L
is_out = lambda L: any(re.search(r'於.{2,12}機場出發', s) for s in L)
is_ret = lambda L: any('抵達臺' in s for s in L)

def price(s): return int(re.search(r'(\d+) 新台幣', s).group(1))
def airline(s):
    m = re.search(r'搭乘(.+?)的直達航班', s); return m.group(1) if m else '?'
def clock(s):
    m = re.search(r'(凌晨|清晨|上午|中午|下午|晚上)(\d+):(\d+) 於', s)
    if not m: return None
    h = int(m.group(2)) % 12
    if m.group(1) in ('下午', '晚上') or (m.group(1) == '中午' and h < 11): h += 12
    return h * 60 + int(m.group(3))
def key(s): return (airline(s), clock(s))
def direct(s): return '直達' in s and '分段購票' not in s and '新台幣' in s

def candidates(outs, d2):
    """每家航空最便宜的一班去程（最多 MAX_AIRLINES 家）＋最便宜的早班（09:30 前）。回傳索引。"""
    c = sorted((price(s), i) for i, s in enumerate(outs) if direct(s))
    best = {}
    for p, i in c: best.setdefault(airline(outs[i]), (p, i))
    if d2 == LAST_RET: return [i for a, (p, i) in best.items() if a in NIGHT_AIRLINES]
    sel = [i for p, i in sorted(best.values())][:MAX_AIRLINES]
    early = [(p, i) for p, i in c if (clock(outs[i]) or 9999) <= 570]
    if early and early[0][1] not in sel: sel.append(early[0][1])
    return sel

def dec(v): return json.loads(v) if isinstance(v, str) else (v or [])
def prev_returns(name):
    """前版同一組日期：{(航空, 去程時刻): (來回最低價, 回程清單, 是否推估)}"""
    res = {}
    for f in (os.path.join(build.PREV, 'raw_rt', name + '.prev'), os.path.join(build.PREV, 'raw_rt', name)):
        try: d = json.load(open(f))
        except Exception: continue
        outs = dec(d.get('out'))
        for i, v in (d.get('carried') or {}).items():
            if v.get('rets'): res[key(outs[int(i)])] = (price(outs[int(i)]), v['rets'], bool(v.get('est')))
        for i, v in (d.get('picks') or {}).items():
            if dec(v): res[key(outs[int(i)])] = (price(outs[int(i)]), dec(v), False)
    return res

def path(name): return os.path.join(OUT, name)
def load(name):
    try: return json.load(open(path(name)))
    except Exception: return None
def save(name, d): json.dump(d, open(path(name), 'w'), ensure_ascii=False)

def finalize(names):
    """沒點選的去程沿用前版回程清單（最低價有變就依差額推估），讓每個檔案自成一份完整資料。"""
    for name in names:
        d = load(name)
        if not d: continue
        outs, prev, carried = d['out'], prev_returns(name), {}
        for i, s in enumerate(outs):
            if str(i) in d['picks'] or not direct(s) or key(s) not in prev: continue
            pmin, rets, est = prev[key(s)]
            delta = price(s) - pmin
            if delta: rets = [re.sub(r'(\d+) 新台幣', lambda m: f"{int(m.group(1)) + delta} 新台幣", r, count=1) for r in rets]
            carried[str(i)] = {'rets': rets, 'est': bool(est or delta)}
        d['carried'] = carried; save(name, d)

def stop(names):
    finalize(names)
    log('THROTTLED：Google 限流，停止（已抓到的保留，稍後重跑會接續）'); sys.exit(2)

def main():
    routes = (sys.argv[1] if len(sys.argv) > 1 else 'Taipei-Seoul').split()
    pairs = os.environ.get('PAIRS', '').split() or [f'{o}:{r}' for o in OUT_DATES for r in RET_DATES if r > o]
    jobs = [(f'{rt}-{p.replace(":", "-")}.json', rt, *p.split(':')) for rt in routes for p in pairs]
    names = [j[0] for j in jobs]
    url = lambda rt, d1, d2: ('https://www.google.com/travel/flights?q=Flights%20from%20' + rt.split('-')[0] + '%20to%20' + rt.split('-')[1]
                              + f'%20on%20{d1}%20through%20{d2}%20nonstop&hl=zh-TW&gl=TW&curr=TWD')
    # 第一階段：去程列表
    for name, rt, d1, d2 in jobs:
        if load(name): continue
        ab('open', url(rt, d1, d2)); time.sleep(4)
        outs = grab(is_out)
        if not any('新台幣' in s for s in outs):
            if throttled(): stop(names)
            log('RT', rt, d1, d2, '無結果，略過'); time.sleep(GAP); continue
        save(name, {'out': outs, 'picks': {}, 'carried': {}})
        log('RT', rt, d1, d2, f'去程 {len(set(outs))} 班，最低 {min(price(s) for s in outs if direct(s))}')
        time.sleep(GAP)
    # 第二階段：挑要點選的去程（價格變了或前版沒有），全部日期一起依價格排序取前 MAX_CLICKS 名
    need, done = [], 0
    for name, rt, d1, d2 in jobs:
        d = load(name)
        if not d: continue
        prev = {} if os.environ.get('FORCE_CLICK') else prev_returns(name)
        done += len(d['picks'])
        for i in candidates(d['out'], d2):
            s = d['out'][i]
            if str(i) in d['picks']: continue
            if key(s) in prev and prev[key(s)][0] == price(s) and not prev[key(s)][2]: continue  # 最低價沒變，沿用
            need.append((price(s), name, rt, d1, d2, i))
    need = sorted(need)[:max(0, MAX_CLICKS - done)]
    log(f'第二階段：點選 {len(need)} 班去程確認回程')
    cur = None  # 目前瀏覽器停在哪一組的去程列表
    for p, name, rt, d1, d2, i in sorted(need, key=lambda x: (x[1], x[0])):
        d = load(name); s = d['out'][i]
        if cur == name:
            ab('back'); time.sleep(3)
        if cur != name or labels() != d['out']:
            ab('open', 'about:blank'); ab('open', url(rt, d1, d2)); time.sleep(4); L = grab(is_out)
            if not any('新台幣' in x for x in L) and throttled(): stop(names)
        else: L = d['out']
        j = next((k for k, x in enumerate(L) if key(x) == key(s) and direct(x)), None)
        if j is None: log('RT', d1, d2, airline(s), '去程班次已不在列表，略過'); cur = None; time.sleep(GAP); continue
        ab('eval', f'({LIST})[{j}].click()'); time.sleep(4)
        rets = grab(is_ret)
        if not is_ret(rets):
            if throttled(): stop(names)
            log('RT', d1, d2, airline(s), '回程列表沒出現，略過'); cur = None; time.sleep(GAP); continue
        d['picks'][str(i)] = rets; save(name, d); cur = name
        log('RT', d1, d2, airline(s), f'{p} 起 → 回程 {len(set(rets))} 班')
        time.sleep(GAP)
    finalize(names)
    log('RTDONE')

if __name__ == '__main__':
    main()
