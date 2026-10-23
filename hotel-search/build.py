#!/usr/bin/env python3
"""首爾各區跨年房價：解析 Google 飯店列表文字，輸出 CSV 與 HTML 摘要表。"""
import csv, glob, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
TWD_PER_USD = 32.59  # open.er-api.com 2026-10-23
AREAS = ['明洞', '弘大', '東大門', '首爾站', '鐘路', '江南', '聖水', '梨泰院', '汝矣島', '蠶室']
AREA_NOTE = {'明洞': '購物美食、機場巴士直達', '弘大': '年輕夜生活、AREX 直達', '東大門': '夜市批發、交通樞紐',
             '首爾站': 'AREX／KTX 起點，轉乘最方便', '鐘路': '景福宮、仁寺洞、古宮', '江南': '商圈、離市中心較遠',
             '聖水': '咖啡廳文青區', '梨泰院': '異國餐廳、夜店', '汝矣島': '商務區、漢江公園', '蠶室': '樂天世界、偏東南'}
RESOLVED = {}  # 區域 → Google 實際定位的地點名稱
NIGHTS = ['2026-12-31', '2027-01-01', '2027-01-02', '2027-01-03']
def night_label(d): return f"{int(d[5:7])}/{int(d[8:])}"
COMBOS = [('2026-12-31', '2027-01-02'), ('2026-12-31', '2027-01-03'), ('2026-12-31', '2027-01-04'),
          ('2027-01-01', '2027-01-02'), ('2027-01-01', '2027-01-03'), ('2027-01-01', '2027-01-04'),
          ('2027-01-02', '2027-01-03'), ('2027-01-02', '2027-01-04'), ('2027-01-03', '2027-01-04')]

PRICE = re.compile(r'^(US\$|NT\$|\$)([\d,]+)$')
SKIP = re.compile(r'^(優惠|超值優惠|比市價.*|查看價格|查看詳細資訊|環保認證|·|\(.*\)|\d\.\d)$')

def parse(path):
    raw = open(path, encoding='utf-8').read().split('\n', 1)
    dec = lambda t: json.loads(t) if t.strip().startswith('"') else t  # agent-browser eval 回傳 JSON 字串
    head = dec(raw[0])
    body = [l.strip() for l in dec(raw[1].strip()).split('\n')] if len(raw) > 1 else []
    hotels = []
    for i, l in enumerate(body):
        m = PRICE.match(l)
        if not m: continue
        j = i - 1
        while j >= 0 and (SKIP.match(body[j]) or not body[j]): j -= 1
        name = body[j] if j >= 0 else '?'
        price = int(m.group(2).replace(',', ''))
        twd = round(price * TWD_PER_USD) if m.group(1) == 'US$' else price
        stars, rating = None, None
        for k in range(i + 1, min(i + 30, len(body))):
            if PRICE.match(body[k]): break
            if rating is None and re.fullmatch(r'\d\.\d', body[k]): rating = float(body[k])
            s = re.match(r'(\d) 星級飯店', body[k])
            if s: stars = int(s.group(1)); break
        if rating is None or PRICE.match(name): continue  # 地圖標記等非列表項
        hotels.append(dict(name=name, twd=twd, stars=stars, rating=rating))
    seen, out = set(), []
    for h in hotels:
        if h['name'] in seen: continue
        seen.add(h['name']); out.append(h)
    return head, out

def stats(hs):
    p = sorted(h['twd'] for h in hs)
    if not p: return None
    p34 = sorted(h['twd'] for h in hs if h['stars'] in (3, 4))
    return dict(n=len(p), min=p[0], med=round(statistics.median(p)), med34=round(statistics.median(p34)) if p34 else None,
                cheapest=min(hs, key=lambda h: h['twd']))

def main():
    data, problems = {}, []
    rows = []
    for a in AREAS:
        for n in NIGHTS:
            f = os.path.join(HERE, 'raw', f'{a}-{n}.txt')
            if not os.path.exists(f): problems.append(f'{a} {night_label(n)} 未抓'); continue
            head, hs = parse(f)
            if f'{int(n[5:7])}月{int(n[8:])}日' not in head: problems.append(f'{a} {night_label(n)} 日期未套用'); continue
            loc = re.search(r'搜尋(.+?)的住宿資訊', head)
            if not loc or loc.group(1) == '首爾': problems.append(f'{a} {night_label(n)} 地點未定位'); continue
            RESOLVED[a] = loc.group(1)
            st = stats(hs)
            if not st: problems.append(f'{a} {night_label(n)} 無房價'); continue
            data[(a, n)] = st
            for h in hs: rows.append([a, night_label(n), h['name'], h['stars'] or '', h['rating'] or '', h['twd']])
    with open(os.path.join(HERE, 'hotels_raw.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['區域', '入住晚', '飯店', '星級', '評分', '每晚 NT$']); w.writerows(rows)

    def cell(st, key):
        return '—' if not st or st.get(key) is None else f"{st[key]:,}"
    with open(os.path.join(HERE, 'hotels_by_area.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['區域'] + [f'{night_label(n)} {k}' for n in NIGHTS for k in ('最低', '中位數', '3–4星中位數')] + ['最低價飯店(各晚)'])
        for a in AREAS:
            w.writerow([a] + [cell(data.get((a, n)), k) for n in NIGHTS for k in ('min', 'med', 'med34')] +
                       [' / '.join(f"{night_label(n)}:{data[(a, n)]['cheapest']['name']}" for n in NIGHTS if (a, n) in data)])

    # 各日期組（入住晚數 = 回程日 − 去程日）總住宿費：以 3–4 星中位數加總
    def combo_total(a, c, key):
        ns = [n for n in NIGHTS if c[0] <= n < c[1]]
        vals = [data.get((a, n), {}).get(key) for n in ns]
        return None if any(v is None for v in vals) else sum(vals)

    th = ''.join(f'<th>{night_label(n)}<br>最低／中位／3–4★</th>' for n in NIGHTS)
    trs = []
    for a in AREAS:
        tds = ''.join(f"<td class='num'>{cell(data.get((a, n)), 'min')}<br><b>{cell(data.get((a, n)), 'med')}</b><br>{cell(data.get((a, n)), 'med34')}</td>" for n in NIGHTS)
        trs.append(f"<tr><td><b>{a}</b> <span class='s'>({RESOLVED.get(a, '?')})</span><br><span class='s'>{AREA_NOTE[a]}</span></td>{tds}</tr>")
    cth = ''.join(f"<th>{night_label(c[0])}-{night_label(c[1])}<br>{len([n for n in NIGHTS if c[0] <= n < c[1]])}晚</th>" for c in COMBOS)
    ctr = []
    for a in AREAS:
        vals = [combo_total(a, c, 'med34') for c in COMBOS]
        ctr.append(f"<tr><td><b>{a}</b></td>" + ''.join(f"<td class='num'>{'—' if v is None else f'{v:,}'}</td>" for v in vals) + '</tr>')
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:16px;background:#fff;color:#222;font-size:13px}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:18px 0 6px}} .sub,.s{{color:#555}} .s{{font-size:11px}}
table{{border-collapse:collapse}} th,td{{border:1px solid #ccc;padding:4px 8px}} th{{background:#333;color:#fff;font-weight:normal}}
.num{{text-align:right}} .foot{{color:#555;font-size:12px;margin-top:8px;line-height:1.5;max-width:1100px}}</style></head><body>
<h1>首爾各區跨年房價（每晚，NT$）</h1><div class='sub'>Google 飯店搜尋第一頁（約 20 間／區），單晚查詢；每格：最低／<b>中位數</b>／3–4 星中位數</div>
<table><tr><th>區域</th>{th}</tr>{''.join(trs)}</table>
<h2>各日期組住宿總價（3–4 星中位數加總）</h2><table><tr><th>區域</th>{cth}</tr>{''.join(ctr)}</table>
<div class='foot'>匯率 1 USD = {TWD_PER_USD} TWD（Google 以 USD 顯示後換算）；房價為 Google 顯示的每晚最低價，含稅與否依各通路而定。查詢時預設 2 位房客的一般客房（單人入住房價通常相同）。
2026-10-23 抓取。{('未完成：' + '、'.join(problems)) if problems else ''}</div></body></html>"""
    open(os.path.join(HERE, 'hotels.html'), 'w').write(html)
    print('cells', len(data), 'problems', problems)
    for a in AREAS:
        print(a, [(night_label(n), data[(a, n)]['min'], data[(a, n)]['med'], data[(a, n)]['med34']) for n in NIGHTS if (a, n) in data])

if __name__ == '__main__':
    main()
