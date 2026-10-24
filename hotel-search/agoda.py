#!/usr/bin/env python3
"""Agoda 房型確認：解析各飯店各晚的房型區塊，取每晚最便宜的「可訂、非青旅／膠囊、非限女性」房型，輸出 CSV 與推薦表。"""
import csv, glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = 3000
NIGHTS = ['2026-12-31', '2027-01-01', '2027-01-02', '2027-01-03']
def nl(d): return f"{int(d[5:7])}/{int(d[8:])}"
def zh_date(d): return f"{int(d[:4])}年{int(d[5:7])}月{int(d[8:])}日"
STAYS = [('1/2-1/4（2晚）', NIGHTS[2:]), ('1/1-1/4（3晚）', NIGHTS[1:]), ('12/31-1/4（4晚）', NIGHTS)]
HOTELS = {  # key → (顯示名, 位置, Google 評論數)
    'yaja': ('Hotel Yaja Jongno', '鐘路・鐘路3街站', 140),
    'simplestay': ('SimpleStay Hotel（鐘路簡單住宿）', '鐘路・鐘路3街站 300m', 226),
    'ibis': ('宜必思大使仁寺洞', '鐘路・仁寺洞', 2900),
    'n285': ('仁寺洞 N285 酒店', '鐘路・仁寺洞', 198),
    'travelodge': ('Travelodge 東大門', '中區・乙支路4街站（鄰近鐘路）', 1700),
    'amid': ('AMID Hotel Seoul', '鐘路・仁寺洞5街', 1600),
    'ninetree': ('Nine Tree by Parnas 仁寺洞', '鐘路・仁寺洞', 1500),
}
EXCLUDE_ROOM = re.compile(r'宿舍|床位|膠囊|Dorm|Capsule|女性|Female|Women|共用|Shared', re.I)
SIZE = re.compile(r'平方公尺|最多可住')

def parse_grid(grid):
    """回傳 [{name, prices[], sold_out}]，name 為房型名稱（下一行是坪數／床型）。"""
    lines = [l.strip() for l in grid.split('\n') if l.strip()]
    rooms, cur = [], None
    for i, l in enumerate(lines):
        if i + 1 < len(lines) and SIZE.search(lines[i + 1]) and not SIZE.search(l) and not l.startswith('NT$'):
            cur = dict(name=l, info=lines[i + 1], prices=[], sold_out=False); rooms.append(cur); continue
        if cur is None: continue
        if l.startswith('已完售'): cur['sold_out'] = True
        if l == 'NT$' and i + 1 < len(lines) and re.fullmatch(r'[\d,]+', lines[i + 1]):
            cur['prices'].append(int(lines[i + 1].replace(',', '')))
    return rooms

def main():
    data, problems, raw_rows = {}, [], []
    for k in HOTELS:
        for n in NIGHTS:
            f = os.path.join(HERE, 'raw_agoda', f'{k}-{n}.json')
            if not os.path.exists(f): problems.append(f'{HOTELS[k][0]} {nl(n)} 未抓'); continue
            try: d = json.loads(json.loads(open(f).read()))
            except Exception: problems.append(f'{HOTELS[k][0]} {nl(n)} 讀取失敗'); continue
            if zh_date(n) not in d['head']: problems.append(f'{HOTELS[k][0]} {nl(n)} 日期未套用'); continue
            rooms = parse_grid(d['grid'])
            if not rooms: problems.append(f'{HOTELS[k][0]} {nl(n)} 無房型資料'); continue
            ok = [r for r in rooms if r['prices'] and not r['sold_out'] and not EXCLUDE_ROOM.search(r['name'])]
            best = min(ok, key=lambda r: min(r['prices'])) if ok else None
            data[(k, n)] = dict(best=best, n_rooms=len(rooms), n_avail=len([r for r in rooms if r['prices'] and not r['sold_out']]),
                                excluded=[r['name'] for r in rooms if EXCLUDE_ROOM.search(r['name'])])
            for r in rooms:
                raw_rows.append([HOTELS[k][0], nl(n), r['name'], r['info'], '已完售' if r['sold_out'] or not r['prices'] else min(r['prices']),
                                 '排除' if EXCLUDE_ROOM.search(r['name']) else ''])
    with open(os.path.join(HERE, 'agoda_rooms.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['飯店', '入住晚', '房型', '坪數／床型', '最低價 NT$（不含稅）', '備註']); w.writerows(raw_rows)

    rows = []
    for k, (disp, loc, rev) in HOTELS.items():
        p = {n: (data.get((k, n)) or {}).get('best') for n in NIGHTS}
        price = {n: min(b['prices']) if b else None for n, b in p.items()}
        avgs = [round(sum(price[n] for n in ns) / len(ns)) if all(price[n] for n in ns) else None for _, ns in STAYS]
        rows.append((k, disp, loc, rev, p, price, avgs))
    rows.sort(key=lambda r: (r[6][0] is None, r[6][0] or 0))

    def td(v, budget=False):
        if v is None: return "<td class='num na'>無空房</td>"
        return f"<td class='num{' ok' if budget and v <= BUDGET else (' over' if budget else '')}'>{v:,}</td>"
    def room_cell(b): return f"<span class='s'>{b['name']}</span>" if b else ''
    trs = ''.join(
        f"<tr><td><b>{disp}</b><br><span class='s'>{loc}・Google 評論 {rev:,}</span></td>"
        + ''.join(f"<td class='num'>{'—' if price[n] is None else f'{price[n]:,}'}<br>{room_cell(p[n])}</td>" for n in NIGHTS)
        + ''.join(td(a, True) for a in avgs) + '</tr>'
        for k, disp, loc, rev, p, price, avgs in rows)
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:16px;background:#fff;color:#222;font-size:13px}}
h1{{font-size:20px;margin:0 0 4px}} .sub,.s{{color:#555}} .s{{font-size:11px}}
table{{border-collapse:collapse}} th,td{{border:1px solid #ccc;padding:4px 8px;vertical-align:top}} th{{background:#333;color:#fff;font-weight:normal}}
.num{{text-align:right}} .ok{{background:#c8f0c8;font-weight:bold}} .over{{background:#ffe0e0}} .na{{color:#999}}
.foot{{color:#555;font-size:12px;margin-top:8px;line-height:1.5;max-width:1200px}}</style></head><body>
<h1>鐘路飯店 Agoda 房型確認（每晚預算 NT${BUDGET:,}）</h1>
<div class='sub'>Agoda 1 位大人・1 間房，每晚最便宜的可訂房型（已排除青旅、膠囊、宿舍床位、限女性與共用房）；價格為 Agoda 顯示的每晚房價，不含稅。綠＝平均 ≤ {BUDGET:,}。</div>
<table><tr><th>飯店</th>{''.join(f'<th>{nl(n)}</th>' for n in NIGHTS)}{''.join(f'<th>平均 {s}</th>' for s, _ in STAYS)}</tr>{trs}</table>
<div class='foot'>已排除：韓屋飯店 DAAM（男女分開的共用房）、Mangrove 東大門（青旅宿舍）、takt jongno（女性專用膠囊旅館）、VIA Jongno（評論數過少）。
2026-10-24 Agoda 抓取；不含稅價，實際結帳另加稅金與服務費，以 Agoda 訂房頁為準。{('未完成：' + '、'.join(problems)) if problems else ''}</div></body></html>"""
    open(os.path.join(HERE, 'agoda_jongno.html'), 'w').write(html)
    for k, disp, loc, rev, p, price, avgs in rows:
        print(disp, {nl(n): (price[n], p[n]['name'] if p[n] else None) for n in NIGHTS}, avgs)
    print('problems', problems)

if __name__ == '__main__':
    main()
