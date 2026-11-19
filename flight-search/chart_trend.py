#!/usr/bin/env python3
"""1/1–1/6、1/2–1/6 最低總價走勢圖＋各自前 8 名 → chart_0101_0106.html（再用 agent-browser 截 PNG）。
VERS 依序列出各版資料夾與標籤；'.' 是目前 raw 的這一版。"""
import csv, html, os
HERE = os.path.dirname(os.path.abspath(__file__))
VERS = [('v10','11/6'),('v11','11/7'),('v12','11/9上'),('v13','11/9下'),('v15','11/11'),('v16','11/13'),('v17','11/14'),('v18','11/15'),('v19','11/16'),('v20','11/17'),('.','11/19')]
PAIRS = [('1/1-1/6','#2a78d6','1/1–1/6'),('1/2-1/6','#eb6834','1/2–1/6')]
def best(v, pair):
    r = list(csv.DictReader(open(os.path.join(HERE, v, 'flights_ranking.csv'), encoding='utf-8-sig')))
    xs = [x for x in r if x['日期組'] == pair and 'TPE-ICN' in x['去程'] and 'ICN-TPE' in x['回程']]
    if not xs: return None
    b = min(xs, key=lambda x: int(x['總價']))
    return int(b['總價']), b['去程'].split()[-1], ('沿用' in b['備註'] or '推估' in b['備註'])
T = [dict(d=d, **{p: best(v, p) for p, _, _ in PAIRS}) for v, d in VERS]
W, H, L, R, TP, B = 960, 380, 64, 150, 30, 56
vals = [t[p][0] for t in T for p, _, _ in PAIRS if t[p]]
ymin, ymax = (min(vals) // 500) * 500, (max(vals) // 500 + 1) * 500
X = lambda i: L + i * (W - L - R) / (len(T) - 1)
Y = lambda v: TP + (ymax - v) * (H - TP - B) / (ymax - ymin)
g = []
for v in range(ymin, ymax + 1, 500):
    g.append(f"<line x1='{L}' x2='{W-R}' y1='{Y(v):.1f}' y2='{Y(v):.1f}' stroke='#e4e3df'/><text x='{L-8}' y='{Y(v)+4:.1f}' text-anchor='end' font-size='12' fill='#52514e'>{v:,}</text>")
for i, t in enumerate(T):
    g.append(f"<text x='{X(i):.1f}' y='{H-B+20}' text-anchor='middle' font-size='12' fill='#52514e'>{t['d']}</text>")
for p, c, lab in PAIRS:
    pts = [(X(i), Y(t[p][0]), t[p]) for i, t in enumerate(T) if t[p]]
    g.append("<polyline fill='none' stroke='%s' stroke-width='2' points='%s'/>" % (c, ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in pts)))
    for x, y, v in pts:
        g.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5' fill='{'#fcfcfb' if v[2] else c}' stroke='{c}' stroke-width='2'/>")
    x, y, v = pts[-1]
    g.append(f"<text x='{x+10:.1f}' y='{y-2:.1f}' font-size='13' font-weight='700' fill='#0b0b0b'>{lab}</text><text x='{x+10:.1f}' y='{y+14:.1f}' font-size='12' fill='#52514e'>{v[0]:,}（{v[1]}）</text>")
svg = f"<svg viewBox='0 0 {W} {H}' width='{W}' height='{H}' font-family='WenQuanYi Zen Hei,sans-serif'>{''.join(g)}</svg>"
r = list(csv.DictReader(open(os.path.join(HERE, 'flights_ranking.csv'), encoding='utf-8-sig')))
def tab(pair, n=8):
    rows = [x for x in r if x['日期組'] == pair][:n]
    clean = lambda s: s.replace('行李未確認(Trip.com 2026/4 TPE-ICN 參考價)；', '').replace('行李未確認(韓國出發估同台灣價)；', '行李估價；')
    tr = ''.join(f"<tr><td class='n'>{i+1}</td><td class='n'><b>{int(x['總價']):,}</b></td><td class='n'>{html.escape(x['去程票價'])}</td><td class='n'>{html.escape(x['回程票價'] or '—')}</td><td>{html.escape(x['去程'])}</td><td>{html.escape(x['回程'])}</td><td class='s'>{html.escape(clean(x['備註']))}</td></tr>" for i, x in enumerate(rows))
    return f"<h2>{pair.replace('-','–')} 前 {n} 名（總價含行李與機場交通，NT$）</h2><table><tr><th>#</th><th>總價</th><th>去程票價</th><th>回程票價</th><th>去程</th><th>回程</th><th>備註</th></tr>{tr}</table>"
NOTE = open(os.path.join(HERE, 'chart_note.txt')).read().strip() if os.path.exists(os.path.join(HERE, 'chart_note.txt')) else ''
page = f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:'WenQuanYi Zen Hei',sans-serif;margin:24px;background:#fcfcfb;color:#0b0b0b;font-size:14px;width:1160px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:17px;margin:22px 0 8px}} .sub{{color:#52514e;font-size:13px}}
.legend{{display:flex;gap:18px;font-size:13px;color:#52514e;margin:10px 0 4px}} .legend i{{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:6px}}
.legend .o{{width:10px;height:10px;border-radius:50%;border:2px solid #52514e}} .legend .f{{width:10px;height:10px;border-radius:50%;background:#52514e}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #e4e3df;padding:6px 8px;text-align:left;vertical-align:top}} th{{font-size:12px;color:#52514e;font-weight:normal}}
td.n{{text-align:right;white-space:nowrap}} td.s{{color:#52514e;font-size:12px}}
</style></head><body>
<h1>台北⇄仁川 1/1–1/6、1/2–1/6 票價</h1>
<div class='sub'>Google Flights 直飛最低總價（含托運行李估價與 AREX 機場⇄首爾站交通）。{T[0]['d']}–{T[-1]['d']} 共 {len(T)} 次更新。</div>
<div class='legend'><span><i style='background:#2a78d6'></i>1/1–1/6</span><span><i style='background:#eb6834'></i>1/2–1/6</span><span><i class='f'></i>當次重新抓到</span><span><i class='o'></i>沿用前版或推估</span></div>
{svg}<div class='sub'>{html.escape(NOTE)}</div>
{tab('1/1-1/6')}{tab('1/2-1/6')}
</body></html>"""
open(os.path.join(HERE, 'chart_0101_0106.html'), 'w').write(page)
