#!/usr/bin/env python3
"""鐘路候選飯店：解析逐間單晚查詢結果（取搜尋結果第一張卡片），輸出 CSV 與推薦表 HTML。"""
import csv, glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TWD_PER_USD = 32.59  # open.er-api.com 2026-10-23
BUDGET = 3000
NIGHTS = ['2026-12-31', '2027-01-01', '2027-01-02', '2027-01-03']
def nl(d): return f"{int(d[5:7])}/{int(d[8:])}"
# 查詢名稱 → (顯示名, 位置／最近站, 是否在鐘路區)
HOTELS = {
    'Hanok Hotel DAAM': ('韓屋飯店 DAAM', '鐘路・北村／安國站一帶韓屋', True),
    'Insadong N285 Hotel': ('仁寺洞 N285 酒店', '鐘路・仁寺洞', True),
    'takt jongno': ('takt jongno', '鐘路', True),
    'VIA Jongno': ('VIA Jongno', '鐘路', True),
    'Hotel Yaja Jongno': ('Hotel Yaja Jongno', '鐘路（汽車旅館型）', True),
    'AMID Hotel Seoul': ('AMID Hotel Seoul', '鐘路・仁寺洞5街 38', True),
    'ibis Ambassador Seoul Insadong': ('宜必思大使仁寺洞', '鐘路・仁寺洞／鐘路3街站', True),
    'Travelodge Dongdaemun Seoul': ('Travelodge 東大門', '中區・乙支路4街站（鄰近鐘路）', False),
    'SimpleStay Hotel Seoul': ('SimpleStay Hotel', '鐘路・鐘路3街站 300m', True),
    'Ikseon Atelier': ('益善 Atelier', '鐘路・益善洞（民宿型）', True),
    'Mangrove Dongdaemun': ('Mangrove 東大門', '中區・東大門歷史文化公園站（鄰近）', False),
    'Nine Tree by Parnas Seoul Insadong': ('Nine Tree by Parnas 仁寺洞', '鐘路・仁寺洞', True),
}
ALIAS = {'ibis Ambassador Seoul Insadong': '宜必思', 'Insadong N285 Hotel': 'N285', 'Nine Tree by Parnas Seoul Insadong': 'Nine Tree', 'Ikseon Atelier': 'Ikseon'}
def matches(q, name):
    if q in ALIAS: return ALIAS[q].lower() in name.lower()
    return all(w.lower() in name.lower() for w in q.split() if len(w) > 3 and w != 'Seoul')
# 性別限定房型（訂房網站房型資料，2026-10-24 查）
FEMALE_ONLY = {'takt jongno'}  # 全館女性專用膠囊旅館 → 排除
GENDER_NOTE = {
    'Hanok Hotel DAAM': '全為男女分開的共用房；Google 最低價可能是女性房，男性房價格未確認',
    'Mangrove Dongdaemun': '有女性／男性 6 人宿舍與私人房；最低價可能是宿舍床位，未確認',
}
PRICE = re.compile(r'^(US\$|NT\$|\$)([\d,]+)$')

def first_card(path):
    raw = open(path, encoding='utf-8').read().split('\n', 1)
    dec = lambda t: json.loads(t) if t.strip().startswith('"') else t
    head = dec(raw[0]); body = [l.strip() for l in dec(raw[1].strip()).split('\n')]
    try: i = next(k for k, l in enumerate(body) if '項結果' in l)
    except StopIteration: return head, None
    name = body[i + 1]; price = rating = stars = reviews = None
    for l in body[i + 2:i + 40]:
        if l in ('查看價格', '查看詳細資訊'): break
        m = PRICE.match(l)
        if m and price is None: price = round(int(m.group(2).replace(',', '')) * (TWD_PER_USD if m.group(1) == 'US$' else 1))
        if rating is None and re.fullmatch(r'\d\.\d', l): rating = float(l)
        if reviews is None and re.fullmatch(r'\([\d.,]+\)', l): reviews = l.strip('()')
        s = re.match(r'(\d) 星級飯店', l)
        if s: stars = int(s.group(1))
    return head, dict(name=name, price=price, rating=rating, stars=stars, reviews=reviews)

def main():
    rows, problems = [], []
    for q, (disp, loc, in_jongno) in HOTELS.items():
        prices, card0 = {}, None
        for n in NIGHTS:
            f = os.path.join(HERE, 'raw_jongno', f"{q.replace(' ', '_')}-{n}.txt")
            if not os.path.exists(f): problems.append(f'{disp} {nl(n)} 未抓'); continue
            head, c = first_card(f)
            if f'{int(n[5:7])}月{int(n[8:])}日' not in head: problems.append(f'{disp} {nl(n)} 日期未套用'); continue
            if not c: problems.append(f'{disp} {nl(n)} 無結果'); continue
            if not matches(q, c['name']): problems.append(f"{disp} {nl(n)} 搜尋結果是別間（{c['name']}）"); continue
            card0 = card0 or c
            prices[n] = c['price']
        avail = [p for p in prices.values() if p]
        rows.append(dict(q=q, disp=disp, loc=loc, in_jongno=in_jongno, card=card0, prices=prices,
                         avg=round(sum(avail) / len(avail)) if avail else None, nights_ok=len(avail)))
    # 驗證第一張卡片就是該飯店（名稱有共同字詞）
    for r in rows:
        c = r['card']
        r['match'] = bool(c)
    rows.sort(key=lambda r: (not r['in_jongno'], r['avg'] is None, r['avg'] or 0))
    with open(os.path.join(HERE, 'jongno_hotels.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['飯店', 'Google名稱', '位置', '在鐘路區', '星級', '評分', '評論數'] + [f'{nl(n)} NT$' for n in NIGHTS] + ['4晚平均', '≤3000'])
        for r in rows:
            c = r['card'] or {}
            w.writerow([r['disp'], c.get('name', ''), r['loc'], 'Y' if r['in_jongno'] else '', c.get('stars') or '', c.get('rating') or '', c.get('reviews') or '']
                       + [r['prices'].get(n) or '滿房/無價' for n in NIGHTS] + [r['avg'] or '', 'Y' if r['avg'] and r['avg'] <= BUDGET else ''])
    for r in rows:
        c = r['card'] or {}
        print(f"{r['disp']:28} match={r['match']} {c.get('name','')[:30]:30} ★{c.get('stars')} {c.get('rating')}({c.get('reviews')}) "
              + ' '.join(f"{nl(n)}:{r['prices'].get(n)}" for n in NIGHTS) + f" avg={r['avg']}")
    print('problems', problems)

if __name__ == '__main__':
    main()

# 推薦表：各機票日期組的每晚平均（只算有價格的晚數齊全時）
STAYS = [('1/2-1/4（2晚）', NIGHTS[2:]), ('1/1-1/4（3晚）', NIGHTS[1:]), ('12/31-1/4（4晚）', NIGHTS)]
def render():
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): pass
    rows = []
    for q, (disp, loc, inj) in HOTELS.items():
        if q in FEMALE_ONLY: continue
        prices, card = {}, None
        for n in NIGHTS:
            f = os.path.join(HERE, 'raw_jongno', f"{q.replace(' ', '_')}-{n}.txt")
            if not os.path.exists(f): continue
            head, c = first_card(f)
            if c and matches(q, c['name']) and f'{int(n[5:7])}月{int(n[8:])}日' in head:
                prices[n] = c['price']; card = card or c
        if not card: continue
        avgs = [round(sum(prices[n] for n in ns) / len(ns)) if all(prices.get(n) for n in ns) else None for _, ns in STAYS]
        rows.append((disp, loc + ('' if q not in GENDER_NOTE else f"<br><span class='warn'>⚠ {GENDER_NOTE[q]}</span>"), inj, card, prices, avgs))
    rows.sort(key=lambda r: (not r[2], r[5][0] or 99999))
    def td(v, budget=False):
        if v is None: return "<td class='num na'>滿房/無價</td>"
        return f"<td class='num{' ok' if budget and v <= BUDGET else (' over' if budget else '')}'>{v:,}</td>"
    trs = ''.join(
        f"<tr class='{'' if inj else 'near'}'><td><b>{d}</b><br><span class='s'>{l}</span></td><td>{c.get('stars') or '—'}</td><td>{c.get('rating')}（{c.get('reviews')}）</td>"
        + ''.join(td(p.get(n)) for n in NIGHTS) + ''.join(td(a, True) for a in av) + '</tr>'
        for d, l, inj, c, p, av in rows)
    html = f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:16px;background:#fff;color:#222;font-size:13px}}
h1{{font-size:20px;margin:0 0 4px}} .sub,.s{{color:#555}} .s{{font-size:11px}}
table{{border-collapse:collapse}} th,td{{border:1px solid #ccc;padding:4px 8px}} th{{background:#333;color:#fff;font-weight:normal}}
.num{{text-align:right}} .ok{{background:#c8f0c8;font-weight:bold}} .over{{background:#ffe0e0}} .na{{color:#999}} tr.near td:first-child{{background:#f2f2f2}}
.warn{{color:#b45309}} .foot{{color:#555;font-size:12px;margin-top:8px;line-height:1.5;max-width:1100px}}</style></head><body>
<h1>鐘路推薦飯店（每晚預算 NT${BUDGET:,}）</h1><div class='sub'>Google 飯店單晚查詢，每晚最低價；綠＝平均 ≤ {BUDGET:,}，紅＝超出。灰底＝在中區、鄰近鐘路。已排除限女性住宿（takt jongno 為女性專用膠囊旅館）；⚠＝有性別限定房型，最低價可能是女性房。</div>
<table><tr><th>飯店</th><th>星級</th><th>評分（評論數）</th>{''.join(f'<th>{nl(n)}</th>' for n in NIGHTS)}{''.join(f'<th>平均 {s}</th>' for s, _ in STAYS)}</tr>{trs}</table>
<div class='foot'>匯率 1 USD = {TWD_PER_USD} TWD。2026-10-24 抓取；房價為 Google 顯示的最低價，含稅與否依通路而定，以訂房頁為準。益善 Atelier 搜不到正確結果，已排除。</div></body></html>"""
    open(os.path.join(HERE, 'jongno_hotels.html'), 'w').write(html)
    for d, l, inj, c, p, av in rows: print(d, inj, av)

if __name__ == '__main__':
    render()
