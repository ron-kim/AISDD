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
            card0 = card0 or c
            prices[n] = c['price']
        avail = [p for p in prices.values() if p]
        rows.append(dict(q=q, disp=disp, loc=loc, in_jongno=in_jongno, card=card0, prices=prices,
                         avg=round(sum(avail) / len(avail)) if avail else None, nights_ok=len(avail)))
    # 驗證第一張卡片就是該飯店（名稱有共同字詞）
    for r in rows:
        c = r['card']
        r['match'] = bool(c) and any(w.lower() in c['name'].lower() for w in r['q'].split() if len(w) > 3)
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
