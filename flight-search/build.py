#!/usr/bin/env python3
"""台北→首爾 跨年機票排行：解析 Google Flights 抓取結果，計算總價／停留時數，輸出 CSV 與 HTML。"""
import csv, glob, json, os, re
from datetime import datetime, timedelta, date, time

HERE = os.path.dirname(os.path.abspath(__file__))
KRW_PER_TWD = 40.66  # open.er-api.com 2026-10-23
def krw(x): return round(x / KRW_PER_TWD)

AIRPORT = {'臺灣桃園國際機場': 'TPE', '臺北松山機場': 'TSA', '仁川國際機場': 'ICN', '金浦國際機場': 'GMP',
           '清州國際機場': 'CJJ', '大邱國際機場': 'TAE', '金海國際機場': 'PUS', '釜山/金海國際機場': 'PUS'}

# 機場→首爾市區（首爾站）交通。first_out/last_out：從機場出發的首末班；first_in/last_in：從市區出發的首末班
TRANSPORT = {
    'ICN': dict(name='AREX 一般列車→首爾站', krw=4750, mins=60, immig=60, first_out='05:30', last_out='23:30', first_in='05:20', last_in='23:00'),
    'GMP': dict(name='AREX／地鐵→首爾站', krw=1650, mins=25, immig=40, first_out='05:40', last_out='23:40', first_in='05:30', last_in='23:30'),
    'CJJ': dict(name='清州機場站→五松 轉 KTX→首爾站', krw=19200, mins=100, immig=40, first_out='06:30', last_out='21:30', first_in='05:15', last_in='21:30'),
    'TAE': dict(name='公車→東大邱 轉 KTX→首爾站', krw=40700, mins=150, immig=40, first_out='06:00', last_out='21:50', first_in='05:10', last_in='21:30'),
    'PUS': dict(name='輕軌+地鐵→釜山站 轉 KTX→首爾站', krw=56000, mins=220, immig=45, first_out='05:40', last_out='21:30', first_in='05:13', last_in='21:00'),
}
for t in TRANSPORT.values(): t['twd'] = krw(t['krw'])

# 行李：每段 1 件（20kg，韓國廉航以 15kg 起跳計）。値=(台灣出發 TWD, 韓國出發 TWD, 狀態)
FULL = ('大韓航空', '韓亞航空', '長榮航空', '中華航空', '星宇航空', '國泰航空', '泰國國際航空', '新加坡航空', '日本航空', '全日空航空')
KR_LCC_EST = krw(45000)
def baggage(airline, from_tw):
    if any(a in airline for a in FULL): return 0, '含'
    if '台灣虎航' in airline: return (950, '官網') if from_tw else (krw(46000), '官網')
    if '酷航' in airline: return 940, '未確認(參考TPE-NRT價)'
    return KR_LCC_EST, '未確認(估₩45,000)'

COMBOS = [('2026-12-31', '2027-01-02'), ('2026-12-31', '2027-01-03'), ('2026-12-31', '2027-01-04'),
          ('2027-01-01', '2027-01-02'), ('2027-01-01', '2027-01-03'), ('2027-01-01', '2027-01-04'),
          ('2027-01-02', '2027-01-03'), ('2027-01-02', '2027-01-04'), ('2027-01-03', '2027-01-04')]
COMBO_COLOR = ['#fde2e4', '#fff1c1', '#e2f0cb', '#d7e3fc', '#f1d4f7', '#ffd6a5', '#caffbf', '#bde0fe', '#e9ecef']
def combo_label(c): return f"{int(c[0][5:7])}/{int(c[0][8:])}-{int(c[1][5:7])}/{int(c[1][8:])}"

MIN_STAY = 24
PAGE = 150  # 早去晚回排行每張 PNG 的列數
EARLY_OUT = time(9, 30)
LATE_RET = time(18, 0)

def hm(s): return time(*map(int, s.split(':')))

def parse_clock(word, h, m):
    h = int(h) % 12
    if word in ('下午', '晚上') or (word == '中午' and h < 11): h += 12
    return time(h, int(m))

RX = re.compile(r'(\d+) 新台幣起。 搭乘(.+?)的直達航班。 星期., (\d+)月 (\d+) (凌晨|清晨|上午|中午|下午|晚上)(\d+):(\d+) 於(.+?)出發，'
                r'星期., (\d+)月 (\d+) (凌晨|清晨|上午|中午|下午|晚上)(\d+):(\d+) 抵達(.+?)。')

def dt(mo, d, clock):
    y = 2026 if int(mo) == 12 else 2027
    return datetime.combine(date(y, int(mo), int(d)), clock)

def parse(label):
    m = RX.search(label)
    if not m: return None
    g = m.groups()
    dep = dt(g[2], g[3], parse_clock(*g[4:7]))
    arr = dt(g[8], g[9], parse_clock(*g[10:13]))
    return dict(price=int(g[0]), airline=g[1], dep=dep, arr=arr,
                frm=AIRPORT.get(g[7], g[7]), to=AIRPORT.get(g[13], g[13]))

def load_oneway():
    flights, seen = [], set()
    for f in sorted(glob.glob(os.path.join(HERE, 'raw', '*.json'))):
        try: labels = json.loads(json.loads(open(f).read()))
        except Exception: continue
        for s in labels:
            x = parse(s)
            if not x: continue
            k = (x['frm'], x['to'], x['dep'], x['airline'], x['price'])
            if k in seen: continue
            seen.add(k); flights.append(x)
    return flights

def eff_return_date(dep):
    """00:00–04:59 起飛的回程算前一天晚上。"""
    return (dep - timedelta(days=1)).date() if dep.time() < time(5) else dep.date()

def city_arrival(f):
    t = TRANSPORT[f['to']]; L = f['arr']; note = ''
    exit_ = L + timedelta(minutes=t['immig'])
    if L.time() < time(5):
        note = '大眾運輸已收班'
        start = datetime.combine(L.date(), hm(t['first_out']))
    elif exit_.date() > L.date() or exit_.time() > hm(t['last_out']):
        note = '隔天早上才到'
        start = datetime.combine(L.date() + timedelta(days=1), hm(t['first_out']))
    else:
        start = exit_
    return start + timedelta(minutes=t['mins']), note

def city_departure(f):
    t = TRANSPORT[f['frm']]; note = ''
    leave = f['dep'] - timedelta(minutes=120 + t['mins'])
    lt = leave.time()
    if lt < hm(t['first_in']) and lt >= time(0) and leave.date() == f['dep'].date() and f['dep'].time() >= time(5):
        note = '需前一晚離開'
        leave = datetime.combine(leave.date() - timedelta(days=1), hm(t['last_in']))
    elif lt > hm(t['last_in']) or lt < hm(t['first_in']):
        leave = datetime.combine(leave.date() if lt > hm(t['last_in']) else leave.date() - timedelta(days=1), hm(t['last_in']))
        note = '需提早於末班車離開市區'
    return leave, note

def fmt(d): return f"{d.month}/{d.day} {d:%H:%M}"
def leg(f): return f"{fmt(f['dep'])}→{f['arr']:%H:%M} {f['frm']}-{f['to']} {f['airline']}"

def make_row(combo, ob, rb, out_price, ret_price, rt_price=None):
    bo, so = baggage(ob['airline'], True)
    br, sr = baggage(rb['airline'], False)
    tr = TRANSPORT[ob['to']]['twd'] + TRANSPORT[rb['frm']]['twd']
    arrive, n1 = city_arrival(ob)
    leave, n2 = city_departure(rb)
    stay = (leave - arrive).total_seconds() / 3600
    fare = rt_price if rt_price is not None else out_price + ret_price
    notes = [n for n in (n1 and '去程' + n1, n2 and '回程' + n2) if n]
    if rb['dep'].time() < time(5): notes.append('回程深夜班(算前一晚)')
    if ob['to'] != rb['frm']: notes.append(f"{ob['to']}進{rb['frm']}出")
    bag_note = sorted({s for s in (so, sr) if s.startswith('未確認')})
    notes += ['行李' + s for s in bag_note]
    return dict(combo=combo, total=fare + bo + br + tr, out_price=out_price, ret_price=ret_price, rt=rt_price,
                bag=bo + br, bag_unconfirmed=bool(bag_note), transport=tr, out=leg(ob), arrive=fmt(arrive),
                ret=leg(rb), leave=fmt(leave), stay=round(stay, 1),
                early_late=ob['dep'].time() <= EARLY_OUT and (rb['dep'].time() >= LATE_RET or rb['dep'].time() < time(5)),
                note='；'.join(notes), ob=ob, rb=rb)

def build_oneway_rows(flights):
    rows = []
    out = [f for f in flights if f['frm'] in ('TPE', 'TSA') and f['to'] in TRANSPORT]
    ret = [f for f in flights if f['frm'] in TRANSPORT and f['to'] in ('TPE', 'TSA')]
    for c in COMBOS:
        d_out, d_ret = date.fromisoformat(c[0]), date.fromisoformat(c[1])
        obs = [f for f in out if f['dep'].date() == d_out]
        rbs = [f for f in ret if eff_return_date(f['dep']) == d_ret]
        for ob in obs:
            for rb in rbs:
                rows.append(make_row(c, ob, rb, ob['price'], rb['price']))
    return rows

def build_rt_rows():
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(HERE, 'raw_rt', '*.json'))):
        try: data = json.load(open(f))
        except Exception: continue
        outs = data.get('out') or []
        for idx, rets in (data.get('picks') or {}).items():
            ob = parse(outs[int(idx)].replace('來回總價 ', ''))
            if not ob: continue
            for s in rets:
                if '分段購票' in s: continue
                rb = parse(s.replace('來回總價 ', ''))
                if not rb: continue
                rd = eff_return_date(rb['dep'])
                c = (ob['dep'].date().isoformat(), rd.isoformat())
                if c not in COMBOS: continue
                k = (c, ob['dep'], ob['airline'], rb['dep'], rb['airline'])
                if k in seen: continue
                seen.add(k)
                rows.append(make_row(c, ob, rb, None, None, rt_price=rb['price']))
    return rows

def price_cell(r, key):
    if r['rt'] is not None: return f"來回 {r['rt']:,}" if key == 'out_price' else '—'
    return f"{r[key]:,}"

COLS = ['名次', '日期組', '總價', '去程票價', '回程票價', '行李', '交通', '去程', '到達市區', '回程', '離開市區', '停留時數', '備註']

def html_table(title, subtitle, rows, extra_title=None, extra_rows=None, start=1):
    def trs(rs, ranked=True, start=1):
        out = []
        for i, r in enumerate(rs, start):
            cls = 'top' if ranked and i <= 3 else ('rt' if r['rt'] is not None else '')
            ci = COMBOS.index(r['combo'])
            bag = f"{r['bag']:,}" + ('*' if r['bag_unconfirmed'] else '')
            out.append(f"<tr class='{cls}'><td>{i}</td><td><span class='chip' style='background:{COMBO_COLOR[ci]}'>{combo_label(r['combo'])}</span></td>"
                       f"<td class='num b'>{r['total']:,}</td><td class='num'>{price_cell(r, 'out_price')}</td><td class='num'>{price_cell(r, 'ret_price')}</td>"
                       f"<td class='num'>{bag}</td><td class='num'>{r['transport']:,}</td><td>{r['out']}</td><td>{r['arrive']}</td>"
                       f"<td>{r['ret']}</td><td>{r['leave']}</td><td class='num'>{r['stay']}</td><td class='note'>{r['note']}</td></tr>")
        return '\n'.join(out)
    head = ''.join(f'<th>{c}</th>' for c in COLS)
    extra = ''
    if extra_rows is not None:
        extra = f"<h2>{extra_title}</h2><table><tr>{head}</tr>{trs(extra_rows, ranked=False) or '<tr><td colspan=13>無</td></tr>'}</table>"
    legend = ''.join(f"<span class='chip' style='background:{c}'>{combo_label(k)}</span>" for k, c in zip(COMBOS, COMBO_COLOR))
    tr_note = '；'.join(f"{a} {t['name']} ₩{t['krw']:,}≈NT${t['twd']:,}/{t['mins']}分(入境{t['immig']}分)" for a, t in TRANSPORT.items())
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:16px;background:#fff;color:#222;font-size:13px}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:18px 0 6px}} .sub{{color:#555;margin-bottom:8px}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #ccc;padding:3px 5px;white-space:nowrap}}
th{{background:#333;color:#fff}} .num{{text-align:right}} .b{{font-weight:bold}} td.note{{white-space:normal;min-width:180px;font-size:12px}}
tr.top td{{background:#c8f0c8}} tr.rt td{{background:#cfe3ff}} .chip{{padding:1px 6px;border-radius:8px;border:1px solid #999;margin-right:3px}}
.foot{{color:#555;font-size:12px;margin-top:8px;line-height:1.5}}</style></head><body>
<h1>{title}</h1><div class='sub'>{subtitle}</div><div class='sub'>日期組：{legend}　<span class='chip' style='background:#c8f0c8'>前3名</span><span class='chip' style='background:#cfe3ff'>來回票</span></div>
<table><tr>{head}</tr>{trs(rows, start=start)}</table>{extra}
<div class='foot'>總價＝去程＋回程＋行李(每段1件)＋機場⇄首爾站來回交通，單位 NT$，匯率 1 TWD = {KRW_PER_TWD} KRW。行李後加 * 表示含未確認／估算值。<br>交通：{tr_note}<br>
到達市區＝落地＋入境＋交通；離開市區＝起飛－120分－交通；停留時數＝離開市區－到達市區（已排除未滿 {MIN_STAY} 小時）。資料來源：Google Flights（2026-10-23 抓取，單程與來回）。</div>
</body></html>"""

def main():
    flights = load_oneway()
    rows = [r for r in build_oneway_rows(flights) + build_rt_rows() if r['stay'] >= MIN_STAY]
    rows.sort(key=lambda r: (r['total'], r['stay'] * -1))
    early = [r for r in rows if r['early_late']]
    top60 = rows[:60]
    rts = [r for r in rows if r['rt'] is not None]
    with open(os.path.join(HERE, 'flights_ranking.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['名次', '日期組', '總價', '去程票價', '回程票價', '行李', '行李未確認', '交通', '去程', '到達市區', '回程', '離開市區', '停留時數', '早去晚回', '來回票', '備註'])
        for i, r in enumerate(rows, 1):
            w.writerow([i, combo_label(r['combo']), r['total'], price_cell(r, 'out_price'), price_cell(r, 'ret_price'), r['bag'],
                        'Y' if r['bag_unconfirmed'] else '', r['transport'], r['out'], r['arrive'], r['ret'], r['leave'], r['stay'],
                        'Y' if r['early_late'] else '', 'Y' if r['rt'] is not None else '', r['note']])
    sub = '1 成人經濟艙・只看直飛・TPE/TSA ⇄ ICN/GMP/CJJ/TAE/PUS・12/31–1/4 涵蓋 1/2 或 1/3・停留 ≥ 24 小時'
    title = f'早去晚回排行（去程 ≤09:30、回程 ≥18:00，共 {len(early)} 案）'
    open(os.path.join(HERE, 'rank_early_late.html'), 'w').write(html_table(title, sub, early))
    for old in glob.glob(os.path.join(HERE, 'rank_early_late_p*.html')): os.remove(old)
    for p in range(0, max(len(early), 1), PAGE):
        n = p // PAGE + 1
        open(os.path.join(HERE, f'rank_early_late_p{n}.html'), 'w').write(
            html_table(f'{title}　第 {n} 頁（第 {p + 1}–{min(p + PAGE, len(early))} 名）', sub, early[p:p + PAGE], start=p + 1))
    open(os.path.join(HERE, 'rank_all.html'), 'w').write(
        html_table(f'不限時間排行（總價前 60 名／共 {len(rows)} 案）', sub, top60, f'所有來回票方案（{len(rts)} 案）', rts))
    print(f'flights={len(flights)} rows={len(rows)} early={len(early)} rt={len(rts)}')
    for i, r in enumerate(rows[:6], 1):
        print(i, combo_label(r['combo']), r['total'], r['out'], '|', r['ret'], r['stay'], r['note'])
    return rows, early

if __name__ == '__main__':
    main()
