#!/usr/bin/env python3
"""整段住宿（scrape_stay.sh 抓的 checkIn+los）→ 每間飯店最便宜的可訂私人房型，含稅每晚平均與總價。
用法：python3 agoda_stay.py [2027-01-01] [5] [區域,…]   輸出 agoda_stay_<checkin>_<los>.html / .csv"""
import csv, os, re, sys
import agoda

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKIN = sys.argv[1] if len(sys.argv) > 1 else '2027-01-01'
LOS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
AREAS = tuple((sys.argv[3] if len(sys.argv) > 3 else '鐘路,新村,弘大').split(','))
RAW = os.path.join(HERE, 'raw_stay', f'{CHECKIN}-{LOS}')
BUDGET, MIN_REVIEWS = agoda.BUDGET, agoda.MIN_REVIEWS
SIZE = agoda.SIZE

def offers(grid):
    """[{room, info, price(每晚不含稅), free(可免費取消), breakfast, sold_out}]"""
    lines = [l.strip() for l in grid.split('\n') if l.strip()]
    out, room, cur = [], None, None
    for i, l in enumerate(lines):
        if i + 1 < len(lines) and SIZE.search(lines[i + 1]) and not SIZE.search(l) and not l.startswith('NT$'):
            room = dict(name=l, info=lines[i + 1], sold_out=False); cur = None; continue
        if room is None: continue
        if l.startswith('已完售'): room['sold_out'] = True
        if re.fullmatch(r'優惠\d+', l):
            cur = dict(room=room['name'], info=room['info'], free=False, breakfast=False, price=None); out.append(cur); continue
        if cur is None: continue
        if '免費取消' in l: cur['free'] = True
        if l == '附早餐': cur['breakfast'] = True
        if l == 'NT$' and i + 1 < len(lines) and re.fullmatch(r'[\d,]+', lines[i + 1]) and cur['price'] is None:
            cur['price'] = int(lines[i + 1].replace(',', ''))
    return [o for o in out if o['price']]

def main():
    end = f"{CHECKIN[:4]}年{int(CHECKIN[5:7])}月{int(CHECKIN[8:]) + LOS}日"  # 只處理同月內
    rows, notes = [], []
    for k, (disp, area, loc) in agoda.HOTELS.items():
        if area not in AREAS: continue
        f = os.path.join(RAW, f'{k}.json')
        if not os.path.exists(f): notes.append(f'{disp} 未抓'); continue
        d = agoda.load(f)
        m = re.search(r'\n(\d\.\d)\n+[^\n]+\n+([\d,]+) 篇評鑑', d['head'])
        rating, reviews = (float(m.group(1)), int(m.group(2).replace(',', ''))) if m else (None, 0)
        if reviews and reviews < MIN_REVIEWS: notes.append(f'{disp}（評鑑 {reviews} < {MIN_REVIEWS}）'); continue
        if agoda.zh_date(CHECKIN) not in d['head']: notes.append(f'{disp} 日期未套用'); continue
        ratio = agoda.tax_ratio(k) or 1.10
        ok = [o for o in offers(d['grid']) if not agoda.EXCLUDE_ROOM.search(o['room'])]
        if not ok:
            rows.append(dict(k=k, disp=disp, area=area, loc=loc, rating=rating, reviews=reviews, ratio=ratio, best=None, free=None,
                             why='已完售' if '已完售' in d['head'] or not d['grid'] else '無私人房型'))
            continue
        best = min(ok, key=lambda o: o['price'])
        fr = [o for o in ok if o['free']]
        free = min(fr, key=lambda o: o['price']) if fr else None
        rows.append(dict(k=k, disp=disp, area=area, loc=loc, rating=rating, reviews=reviews, ratio=ratio, best=best, free=free, why=''))
    tax = lambda r, o: round(o['price'] * r['ratio']) if o else None
    rows.sort(key=lambda r: (r['best'] is None, tax(r, r['best']) or 0))
    base = os.path.join(HERE, f'agoda_stay_{CHECKIN}_{LOS}')
    with open(base + '.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['飯店', '區域', '位置', 'Agoda評分', '評鑑數', '稅率', '最低房型', '每晚含稅', f'{LOS}晚含稅', '最低可免費取消房型', '每晚含稅(可取消)', '備註'])
        for r in rows:
            b, f = r['best'], r['free']
            w.writerow([r['disp'], r['area'], r['loc'], r['rating'] or '', r['reviews'] or '', r['ratio'], b['room'] if b else '', tax(r, b) or '',
                        tax(r, b) * LOS if b else '', f['room'] if f else '', tax(r, f) or '', r['why']])
    def cell(r, o, budget=True):
        v = tax(r, o)
        if v is None: return "<td class='num na'>—</td>"
        return (f"<td class='num{' ok' if budget and v <= BUDGET else (' over' if budget else '')}'>{v:,}<br>"
                f"<span class='s'>{o['room']}{'・含早' if o['breakfast'] else ''}</span></td>")
    trs = ''.join(
        f"<tr class='{'dd' if r['area'] != '鐘路' else ''}'><td><b>{r['disp']}</b><br><span class='s'>{r['area']}・{r['loc']}・Agoda {r['rating'] or '?'}（{r['reviews']:,} 篇）・稅率 {(r['ratio'] - 1) * 100:.0f}%</span></td>"
        + (cell(r, r['best']) + f"<td class='num'>{tax(r, r['best']) * LOS:,}</td>" + cell(r, r['free'], False) if r['best'] else f"<td colspan=3 class='na'>{r['why']}</td>")
        + '</tr>' for r in rows)
    m1, d1 = int(CHECKIN[5:7]), int(CHECKIN[8:])
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:16px;background:#fff;color:#222;font-size:13px}}
h1{{font-size:20px;margin:0 0 4px}} .sub,.s{{color:#555}} .s{{font-size:11px}}
table{{border-collapse:collapse}} th,td{{border:1px solid #ccc;padding:4px 8px;vertical-align:top}} th{{background:#333;color:#fff;font-weight:normal}}
.num{{text-align:right}} .ok{{background:#c8f0c8;font-weight:bold}} .over{{background:#ffe0e0}} .na{{color:#999}} tr.dd td:first-child{{background:#eef4ff}}
.foot{{color:#555;font-size:12px;margin-top:8px;line-height:1.5;max-width:1100px}}</style></head><body>
<h1>{'・'.join(AREAS)} 飯店 Agoda 含稅房價：{m1}/{d1} 入住 {LOS} 晚（每晚預算 NT${BUDGET:,}）</h1>
<div class='sub'>Agoda 1 位大人・1 間房，一次查整段住宿（每晚平均）；已排除青旅、膠囊、宿舍、限女性與共用房，以及評鑑 &lt; {MIN_REVIEWS} 篇。含稅＝不含稅 × 該飯店結帳頁稅率。綠＝每晚 ≤ {BUDGET:,}；藍底＝新村／弘大。</div>
<table><tr><th>飯店</th><th>最低價每晚（含稅）</th><th>{LOS} 晚總價</th><th>最低「可免費取消」每晚</th></tr>{trs}</table>
<div class='foot'>Agoda Mega Sale 期間（11/16–11/30）抓取。最低價多為不可退款方案。{('；'.join(notes)) if notes else ''}</div></body></html>"""
    open(base + '.html', 'w').write(html)
    for r in rows:
        print(f"{r['disp'][:22]:22} {r['area']} {r['rating']}({r['reviews']}) {tax(r, r['best'])} free={tax(r, r['free'])} {r['why']} {(r['best'] or {}).get('room', '')[:30]}")
    print('notes', notes)

if __name__ == '__main__':
    main()
