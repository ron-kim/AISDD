#!/usr/bin/env python3
"""Agoda 房型確認（鐘路＋東大門）：每晚取最便宜的「可訂、非青旅／膠囊／宿舍、非限女性」房型，
依各飯店結帳頁實際稅率換算含稅價，輸出 CSV 與推薦表。"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = 3000  # 含稅每晚平均
MIN_REVIEWS = 100  # Agoda 評鑑數
NIGHTS = ['2026-12-31', '2027-01-01', '2027-01-02', '2027-01-03']
def nl(d): return f"{int(d[5:7])}/{int(d[8:])}"
def zh_date(d): return f"{int(d[:4])}年{int(d[5:7])}月{int(d[8:])}日"
STAYS = [('1/2-1/4（2晚）', NIGHTS[2:]), ('1/1-1/4（3晚）', NIGHTS[1:]), ('12/31-1/4（4晚）', NIGHTS)]
HOTELS = {  # key → (顯示名, 區域, 位置)
    'yaja': ('Hotel Yaja Jongno', '鐘路', '鐘路3街站'),
    'simplestay': ('SimpleStay Hotel（鐘路簡單住宿）', '鐘路', '鐘路3街站 300m'),
    'ibis': ('宜必思大使仁寺洞', '鐘路', '仁寺洞'),
    'n285': ('仁寺洞 N285 酒店', '鐘路', '仁寺洞'),
    'amid': ('AMID Hotel Seoul', '鐘路', '仁寺洞5街'),
    'ninetree': ('Nine Tree by Parnas 仁寺洞', '鐘路', '仁寺洞'),
    'travelodge': ('Travelodge 東大門', '東大門', '乙支路4街站'),
    'toyoko1': ('東橫INN 首爾東大門1號店', '東大門', '東大門歷史文化公園站'),
    'toyoko2': ('東橫INN 首爾東大門2號店', '東大門', '東大門歷史文化公園站'),
    'ibisbudget': ('宜必思快捷大使東大門', '東大門', '東大門歷史文化公園站 160m'),
    'skypark1': ('Skypark 東大門1', '東大門', '東大門'),
    'kingstown': ('Skypark Kingstown 東大門', '東大門', '東大門歷史文化公園站'),
    'westerncoop': ('西方 Co-op 東大門飯店公寓', '東大門', '東大門'),
    'ramada': ('華美達首爾東大門', '東大門', '東大門'),
    'glue': ('glue hotel', '東大門', '東大門'),
    'migliore': ('Hotel Migliore 首爾', '東大門', '東大門'),
    'aboutstay': ('ABOUTSTAY 東大門', '東大門', '東大門'),
    'thezip': ('THEZIP 首爾', '新村', '新村／弘大'),
    'urban': ('新村 Urban Hotel & Play', '新村', '新村站'),
    'havenue': ('H Avenue 梨大新村', '新村', '梨大站'),
    'brownsuites': ('Brown Suites 新村中央', '新村', '新村站'),
    'srcompact': ('SR Compact 新村', '新村', '新村'),
    'hotels': ('Hotel S 新村', '新村', '新村'),
    'nesto': ('Nesto 弘大', '弘大', '弘大'),
    'gaeul': ('Hotel Gaeul 新村', '新村', '新村'),
    'ever8': ('新村 Ever8 服務式公寓', '新村', '新村站'),
    'browndot': ('Brown Dot 新村店', '新村', '新村'),
    'petercat': ('彼得貓酒店 新村弘大', '新村', '新村／弘大'),
    'ninebrick': ('Nine Brick Hotel', '弘大', '弘大入口站'),
    'designershd': ('弘大設計師飯店', '弘大', '弘大'),
    'theore': ('The-Ore 飯店', '弘大', '弘大'),
    'amanti': ('Amanti Hotel 首爾', '弘大', '合井站'),
    'lazycube': ('Lazy Cube 懶方飯店', '弘大', '弘大'),
}
GROUPS = {  # 輸出組：(標題, 區域, 檔名前綴, 已排除說明)
    'jongno': ('鐘路＋東大門', ('鐘路', '東大門'), 'agoda',
               '韓屋飯店 DAAM（共用房）、Mangrove 東大門（青旅宿舍）、takt jongno（女性專用膠囊旅館）、VIA Jongno（評論數過少）'),
    'sinchon': ('新村＋弘大', ('新村', '弘大'), 'agoda_sinchon',
                'Agoda 新村／弘大清單中的青旅、民宿、膠囊、女性限定與短租公寓；梨大首爾大旅館（4 晚皆已完售）'),
}
EXCLUDE_ROOM = re.compile(r'宿舍|床位|膠囊|Dorm|Capsule|女性|Female|Women|共用|Shared', re.I)
SIZE = re.compile(r'平方公尺|最多可住')

def load(path):
    v = json.loads(open(path).read())
    return json.loads(v) if isinstance(v, str) else v  # agent-browser eval 回傳 JSON 字串

def parse_grid(grid):
    """回傳 [{name, info, prices[], sold_out}]；房型名稱的下一行是坪數／入住人數。"""
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

def tax_ratio(k):
    """結帳頁「含稅總價」÷ 房型區塊第一個（不含稅）價格。"""
    f = os.path.join(HERE, 'raw_agoda', f'tax-{k}.json')
    if not os.path.exists(f): return None
    d = load(f)
    m = re.search(r'含稅總價\s*\n?\s*NT\$\s*([\d,.]+)', d.get('body', ''))
    first = float(str(d.get('first', '')).replace(',', '') or 0)
    return round(float(m.group(1).replace(',', '')) / first, 4) if m and first else None

def main(group='jongno'):
    gtitle, gareas, prefix, gexcl = GROUPS[group]
    hotels = {k: v for k, v in HOTELS.items() if v[1] in gareas}
    data, problems, raw_rows, meta = {}, [], [], {}
    for k, (disp, area, loc) in hotels.items():
        ratio = tax_ratio(k)
        sold_out_all = all('已完售' in load(p)['head'] and not load(p)['grid']
                           for p in [os.path.join(HERE, 'raw_agoda', f'{k}-{n}.json') for n in NIGHTS] if os.path.exists(p))
        if ratio is None and not sold_out_all: problems.append(f'{disp} 稅率未取得（以 1.10 估）')
        meta[k] = dict(ratio=ratio or 1.10, ratio_ok=ratio is not None)
        for n in NIGHTS:
            f = os.path.join(HERE, 'raw_agoda', f'{k}-{n}.json')
            if not os.path.exists(f): problems.append(f'{disp} {nl(n)} 未抓'); continue
            d = load(f)
            if zh_date(n) not in d['head']: problems.append(f'{disp} {nl(n)} 日期未套用'); continue
            m = re.search(r'\n(\d\.\d)\n+[^\n]+\n+([\d,]+) 篇評鑑', d['head'])
            if m and 'rating' not in meta[k]:
                meta[k].update(rating=float(m.group(1)), reviews=int(m.group(2).replace(',', '')))
            rooms = parse_grid(d['grid'])
            if not rooms and '已完售' in d['head']: data[(k, n)] = None; continue  # Agoda 整間已完售
            if not rooms: problems.append(f'{disp} {nl(n)} 無房型資料'); continue
            meta[k]['had_rooms'] = True
            if any(not EXCLUDE_ROOM.search(r['name']) for r in rooms): meta[k]['has_private'] = True
            ok = [r for r in rooms if r['prices'] and not r['sold_out'] and not EXCLUDE_ROOM.search(r['name'])]
            best = min(ok, key=lambda r: min(r['prices'])) if ok else None
            data[(k, n)] = best
            for r in rooms:
                p = None if r['sold_out'] or not r['prices'] else min(r['prices'])
                raw_rows.append([disp, area, nl(n), r['name'], r['info'], p or '已完售',
                                 round(p * meta[k]['ratio']) if p else '', '排除' if EXCLUDE_ROOM.search(r['name']) else ''])
    with open(os.path.join(HERE, f'{prefix}_rooms.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['飯店', '區域', '入住晚', '房型', '坪數／人數', '最低價 NT$（不含稅）', '含稅 NT$', '備註']); w.writerows(raw_rows)

    rows, low_rev, dorm_only = [], [], []
    for k, (disp, area, loc) in hotels.items():
        mt = meta[k]
        if mt.get('reviews', 0) < MIN_REVIEWS: low_rev.append(disp); continue
        if mt.get('had_rooms') and not mt.get('has_private'): dorm_only.append(disp); continue  # 只有膠囊／宿舍／限女性房型
        best = {n: data.get((k, n)) for n in NIGHTS}
        price = {n: round(min(b['prices']) * mt['ratio']) if b else None for n, b in best.items()}
        avgs = [round(sum(price[n] for n in ns) / len(ns)) if all(price[n] for n in ns) else None for _, ns in STAYS]
        rows.append((k, disp, area, loc, mt, best, price, avgs))
    rows.sort(key=lambda r: (r[7][0] is None, r[7][0] or 0))

    with open(os.path.join(HERE, f'{prefix}_summary.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['飯店', '區域', '位置', 'Agoda評分', '評鑑數', '稅率'] + [f'{nl(n)} 含稅' for n in NIGHTS] + [f'平均 {s}' for s, _ in STAYS])
        for k, disp, area, loc, mt, best, price, avgs in rows:
            w.writerow([disp, area, loc, mt.get('rating', ''), mt.get('reviews', ''), mt['ratio']] + [price[n] or '無空房' for n in NIGHTS] + [a or '' for a in avgs])

    def td(v, budget=False):
        if v is None: return "<td class='num na'>無空房</td>"
        return f"<td class='num{' ok' if budget and v <= BUDGET else (' over' if budget else '')}'>{v:,}</td>"
    def room_cell(b): return f"<span class='s'>{b['name']}</span>" if b else ''
    trs = ''.join(
        f"<tr class='{'dd' if area in ('東大門', '弘大') else ''}'><td><b>{disp}</b><br><span class='s'>{area}・{loc}・Agoda {mt.get('rating', '?')}（{mt.get('reviews', 0):,} 篇）"
        f"・稅率 {'%.0f' % ((mt['ratio'] - 1) * 100)}%{'' if mt['ratio_ok'] else '(估)'}</span></td>"
        + ''.join(f"<td class='num'>{'—' if price[n] is None else f'{price[n]:,}'}<br>{room_cell(best[n])}</td>" for n in NIGHTS)
        + ''.join(td(a, True) for a in avgs) + '</tr>'
        for k, disp, area, loc, mt, best, price, avgs in rows)
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:16px;background:#fff;color:#222;font-size:13px}}
h1{{font-size:20px;margin:0 0 4px}} .sub,.s{{color:#555}} .s{{font-size:11px}}
table{{border-collapse:collapse}} th,td{{border:1px solid #ccc;padding:4px 8px;vertical-align:top}} th{{background:#333;color:#fff;font-weight:normal}}
.num{{text-align:right}} .ok{{background:#c8f0c8;font-weight:bold}} .over{{background:#ffe0e0}} .na{{color:#999}} tr.dd td:first-child{{background:#eef4ff}}
.foot{{color:#555;font-size:12px;margin-top:8px;line-height:1.5;max-width:1250px}}</style></head><body>
<h1>{gtitle}飯店 Agoda 含稅房價（每晚預算 NT${BUDGET:,}）</h1>
<div class='sub'>Agoda 1 位大人・1 間房，每晚最便宜的可訂房型（已排除青旅、膠囊、宿舍、限女性與共用房）；<b>含稅價</b>＝不含稅價 × 該飯店結帳頁實際稅率。綠＝平均 ≤ {BUDGET:,}；藍底＝{'東大門' if group == 'jongno' else '弘大'}。依 2 晚平均排序。</div>
<table><tr><th>飯店</th>{''.join(f'<th>{nl(n)}</th>' for n in NIGHTS)}{''.join(f'<th>平均 {s}</th>' for s, _ in STAYS)}</tr>{trs}</table>
<div class='foot'>已排除：{gexcl}{('、' + '、'.join(dorm_only) + '（只有膠囊／宿舍／女性房）') if dorm_only else ''}{('、' + '、'.join(low_rev) + f'（Agoda 評鑑 < {MIN_REVIEWS}）') if low_rev else ''}。
2026-10-24 Agoda 抓取；最低價多為不可退款方案，可免費取消方案另加價。{('未完成：' + '、'.join(problems)) if problems else ''}</div></body></html>"""
    open(os.path.join(HERE, 'agoda_jongno.html' if group == 'jongno' else f'{prefix}.html'), 'w').write(html)
    for k, disp, area, loc, mt, best, price, avgs in rows:
        print(f"{disp:24} {area} ★{mt.get('rating')}({mt.get('reviews')}) tax={mt['ratio']} {[price[n] for n in NIGHTS]} avg={avgs}")
    print('low reviews', low_rev); print('problems', problems)

if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else 'jongno')
