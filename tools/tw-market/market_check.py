"""台股收盤市場檢查 (post-close).

Adapted from the claude-trading-skills market-regime-daily workflow
(market-breadth-analyzer -> uptrend-analyzer -> exposure-coach), applied to TWSE listed stocks.
This is an approximation; scores are not comparable with the US skills.

Usage: python3 market_check.py [--out DIR] [--date YYYY-MM-DD]
Writes DIR/tw_market_check_<date>.md and .json. Exit code 3 = no trading data for that date.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twdata as T  # noqa: E402

INDUSTRY = {"01": "水泥", "02": "食品", "03": "塑膠", "04": "紡織", "05": "電機", "06": "電器電纜", "08": "玻璃陶瓷",
            "09": "造紙", "10": "鋼鐵", "11": "橡膠", "12": "汽車", "14": "建材營造", "15": "航運", "16": "觀光餐旅",
            "17": "金融保險", "18": "貿易百貨", "20": "其他", "21": "化學", "22": "生技醫療", "23": "油電燃氣",
            "24": "半導體", "25": "電腦週邊", "26": "光電", "27": "通信網路", "28": "電子零組件", "29": "電子通路",
            "30": "資訊服務", "31": "其他電子", "35": "綠能環保", "36": "數位雲端", "37": "運動休閒", "38": "居家生活"}
BANDS = [(80, "積極", "80–100%"), (65, "正常偏多", "60–80%"), (50, "中性", "40–60%"), (35, "防守", "25–45%"),
         (20, "保守", "10–30%"), (0, "現金優先", "0–15%")]


def pct_rank(series: pd.Series, v: float) -> float:
    return float((series.dropna() <= v).mean() * 100)


def rally_status(ix: pd.DataFrame, lookback: int = 40) -> dict:
    """O'Neil rally-attempt / Follow-Through Day tracker on TAIEX close + turnover.
    Day 1 = first up close after the lowest close of the lookback window. FTD = day 4+ (to day 10),
    gain >= 1.5% and turnover above the previous session. Undercutting the low resets the count."""
    w = ix.iloc[-lookback:].copy()
    w["pct"] = w["close"].pct_change()
    low_i = int(np.argmin(w["close"].values))
    low_date, low_close = w.index[low_i], float(w["close"].iloc[low_i])
    after = w.iloc[low_i + 1:]
    res = {"low_date": str(low_date.date()), "low_close": low_close, "day": 0, "ftd": None,
           "high_since_low": float(after["close"].max()) if len(after) else low_close}
    up = after[after["pct"] > 0]
    if up.empty:
        res["state"] = "尚未出現反彈嘗試（仍在創低或低點後未收紅）"
        return res
    d1 = w.index.get_loc(up.index[0])
    days = w.iloc[d1:]
    res["day1"] = str(up.index[0].date())
    res["day"] = len(days)
    for k, (date, r) in enumerate(days.iterrows(), start=1):
        if 4 <= k <= 10 and r["pct"] >= 0.015:
            prev = w["turnover"].iloc[w.index.get_loc(date) - 1]
            if r["turnover"] > prev:
                res["ftd"] = {"date": str(date.date()), "day": k, "pct": float(r["pct"]), "turnover": float(r["turnover"]),
                              "prev_turnover": float(prev)}
                break
    if res["ftd"]:
        res["state"] = f"已出現 Follow-Through Day（{res['ftd']['date']}，反彈第 {res['ftd']['day']} 天）"
    elif res["day"] < 4:
        res["state"] = f"反彈第 {res['day']} 天；最快第 4 天起才可能出現 FTD"
    elif res["day"] <= 10:
        res["state"] = f"反彈第 {res['day']} 天，尚未出現 FTD（需漲 ≥1.5% 且量增）"
    else:
        res["state"] = f"反彈已 {res['day']} 天仍無 FTD，反彈嘗試轉弱"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
    ap.add_argument("--date", help="trading date YYYY-MM-DD (default: today, Asia/Taipei)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(T.TPE).date()

    ix = T.twse_daily_index(months=4, today=day)
    if ix.empty or ix.index[-1].date() != day:
        print(f"{day}: 證交所無此日交易資料（休市或尚未公布）。最近交易日 {ix.index[-1].date() if len(ix) else '?'}")
        sys.exit(3)

    cos = T.twse_companies()
    ind_map = {c["公司代號"].strip(): c["產業別"].strip() for c in cos}
    closes = {}
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(T.yahoo_closes, f"{code}.TW"): code for code in ind_map}
        for f in cf.as_completed(futs):
            s = f.result()
            if s is not None and len(s) > 220:
                closes[futs[f]] = s[s.index <= pd.Timestamp(day)]
    px = pd.DataFrame(closes).sort_index().ffill(limit=5)
    fresh = int((px.iloc[-1].notna() & (px.index[-1] == pd.Timestamp(day))).sum()) if len(px) else 0
    if px.index[-1] != pd.Timestamp(day) or fresh < 0.8 * len(closes):
        print(f"Yahoo 個股資料尚未更新到 {day}（最新 {px.index[-1].date()}）")
        sys.exit(4)

    ma50, ma200 = px.rolling(50).mean(), px.rolling(200).mean()
    valid = ma200.notna()
    nvalid = valid.sum(axis=1)
    above200 = (((px > ma200) & valid).sum(axis=1) / nvalid)[nvalid > 300]
    upt_mask = (px > ma50) & (ma50 > ma200) & valid
    uptrend = (upt_mask.sum(axis=1) / nvalid)[nvalid > 300]
    b8, b200 = above200.rolling(8).mean(), above200.rolling(200).mean()
    u10 = uptrend.rolling(10).mean()

    # breadth
    comp = {}
    b8_now = float(b8.iloc[-1])
    comp["廣度水準與趨勢"] = float(np.clip(b8_now * 100 + (10 if b8_now > b8.iloc[-6] else -10), 0, 100))
    base = b200.iloc[-1] if not np.isnan(b200.iloc[-1]) else above200.mean()
    comp["8MA vs 200MA"] = float(np.clip(50 + (b8_now - base) * 250, 0, 100))
    comp["廣度歷史百分位"] = pct_rank(b8, b8_now)
    idx = ix["close"]
    idx60 = idx.iloc[-1] / idx.iloc[-61] - 1 if len(idx) > 61 else 0.0
    br60 = b8_now - b8.iloc[-61]
    comp["指數 vs 廣度背離"] = 20.0 if (idx60 > 0 and br60 < -0.05) else 75.0 if (idx60 < 0 and br60 > 0.05) else float(50 + np.sign(br60) * 15)
    breadth_score = float(np.mean(list(comp.values())))

    # uptrend + sectors
    up_now = float(uptrend.iloc[-1])
    rows = []
    for code, name in INDUSTRY.items():
        cols = [c for c in px.columns if ind_map.get(c) == code]
        if len(cols) < 5:
            continue
        v = valid[cols].iloc[-1]
        r = float(upt_mask[cols].iloc[-1][v].mean())
        r_prev = float(upt_mask[cols].iloc[-2][valid[cols].iloc[-2]].mean())
        r20 = float(upt_mask[cols].iloc[-21][valid[cols].iloc[-21]].mean())
        rows.append({"產業": name, "家數": len(cols), "上升趨勢比例": r, "前日": r_prev, "20日變化": r - r20})
    sectors = pd.DataFrame(rows).sort_values("上升趨勢比例", ascending=False)
    ucomp = {"整體上升趨勢比例": float(np.clip(up_now / 0.5 * 100, 0, 100)),
             "產業參與度": float((sectors["上升趨勢比例"] > 0.3).mean() * 100),
             "動能": float(np.clip(50 + (u10.iloc[-1] - u10.iloc[-11]) * 500, 0, 100)),
             "歷史百分位": pct_rank(uptrend, up_now)}
    uptrend_score = float(np.mean(list(ucomp.values())))

    # index trend (TAIEX from TWSE; need >=200 sessions -> use Yahoo ^TWII history for MAs)
    yidx = T.yahoo_closes("%5ETWII", "2y")
    yidx = yidx[yidx.index < pd.Timestamp(day)]
    full = pd.concat([yidx, idx[idx.index >= pd.Timestamp(day)]]).sort_index()
    full = full[~full.index.duplicated(keep="last")]
    i_close, i50, i200 = float(full.iloc[-1]), float(full.rolling(50).mean().iloc[-1]), float(full.rolling(200).mean().iloc[-1])
    ihigh = float(full.iloc[-252:].max())
    trend_score = 25 * (i_close > i50) + 25 * (i_close > i200) + 25 * (i50 > i200) + 25 * (i_close / ihigh - 1 > -0.08)

    composite = 0.4 * breadth_score + 0.4 * uptrend_score + 0.2 * trend_score
    zone, expo = next((z, e) for lo, z, e in BANDS if composite >= lo)

    rally = rally_status(ix)
    ad = T.twse_breadth_counts(day)
    inst = T.twse_institutional(day)

    # previous report for comparison
    prev = None
    prior = sorted(f for f in os.listdir(a.out) if f.startswith("tw_market_check_") and f.endswith(".json") and f < f"tw_market_check_{day}")
    if prior:
        prev = json.load(open(os.path.join(a.out, prior[-1])))
    prev_day = ix.index[-2]
    prev_above = float(above200.loc[:prev_day].iloc[-1]) if len(above200.loc[:prev_day]) else None
    prev_up = float(uptrend.loc[:prev_day].iloc[-1]) if len(uptrend.loc[:prev_day]) else None

    res = {"date": str(day), "n_stocks": int(valid.iloc[-1].sum()), "taiex": i_close, "taiex_chg": float(ix["chg"].iloc[-1]),
           "taiex_pct": float(ix["close"].iloc[-1] / ix["close"].iloc[-2] - 1), "turnover": float(ix["turnover"].iloc[-1]),
           "turnover_prev": float(ix["turnover"].iloc[-2]), "ma50": i50, "ma200": i200, "from_52w_high": i_close / ihigh - 1,
           "above200": float(above200.iloc[-1]), "above200_prev": prev_above, "uptrend": up_now, "uptrend_prev": prev_up,
           "breadth_components": comp, "breadth_score": breadth_score, "uptrend_components": ucomp, "uptrend_score": uptrend_score,
           "trend_score": trend_score, "composite": composite, "zone": zone, "exposure": expo,
           "prev_composite": prev["composite"] if prev else None, "rally": rally, "advance_decline": ad, "institutional": inst,
           "sectors": sectors.to_dict("records")}
    json.dump(res, open(os.path.join(a.out, f"tw_market_check_{day}.json"), "w"), ensure_ascii=False, indent=2, default=float)

    f = lambda x: "—" if x is None else f"{x:.1%}"  # noqa: E731
    yi = lambda x: "—" if x is None else (f"買超 {x:,.1f} 億" if x >= 0 else f"賣超 {-x:,.1f} 億")  # noqa: E731
    L = [f"# 台股收盤市場檢查 — {day}", "",
         "> 改編自 claude-trading-skills 的 market-regime-daily 流程（近似版，分數不可與美股版比較）。"
         "資料：TWSE、Yahoo Finance。非投資建議。", "",
         f"## 結論：{zone}，建議持股 {expo}（綜合 {composite:.0f}/100"
         + (f"，前次 {res['prev_composite']:.0f}" if res["prev_composite"] is not None else "") + "）", "",
         "| 指標 | 前一交易日 | 今日 |", "|---|---|---|",
         f"| 加權指數 | {ix['close'].iloc[-2]:,.2f} | **{i_close:,.2f}**（{res['taiex_chg']:+,.2f}，{res['taiex_pct']:+.2%}） |",
         f"| 成交金額 | {res['turnover_prev']/1e8:,.0f} 億 | {res['turnover']/1e8:,.0f} 億 |",
         f"| 站上 200 日線比例 | {f(prev_above)} | **{f(res['above200'])}** |",
         f"| 上升趨勢比例（收>50MA>200MA） | {f(prev_up)} | **{f(up_now)}** |",
         f"| 廣度分數 / 上升趨勢分數 / 指數趨勢 | | {breadth_score:.0f} / {uptrend_score:.0f} / {trend_score} |", "",
         "## 盤面"]
    if ad:
        L.append(f"- 上市股票：上漲 {ad.get('up', 0):,.0f}（漲停 {ad.get('limit_up') or 0:,.0f}）、下跌 {ad.get('down', 0):,.0f}"
                 f"（跌停 {ad.get('limit_down') or 0:,.0f}）、平盤 {ad.get('flat', 0):,.0f}")
    if inst:
        L.append(f"- 三大法人：合計 {yi(inst.get('合計'))}；外資 {yi(inst.get('外資'))}、投信 {yi(inst.get('投信'))}、"
                 f"自營商自行 {yi(inst.get('自營商自行'))}、自營商避險 {yi(inst.get('自營商避險'))}")
    else:
        L.append("- 三大法人：TWSE 尚未公布")
    L += ["", "## 加權指數位置",
          f"- 50 日線 {i50:,.0f}（{i_close/i50-1:+.1%}）、200 日線 {i200:,.0f}（{i_close/i200-1:+.1%}）",
          f"- 距 52 週高點 {res['from_52w_high']:+.1%}", "",
          "## 反彈嘗試 / Follow-Through Day",
          f"- 近期收盤低點：{rally['low_date']} {rally['low_close']:,.2f}", f"- 狀態：**{rally['state']}**"]
    if rally.get("ftd"):
        ftd = rally["ftd"]
        L.append(f"- FTD：{ftd['date']} 漲 {ftd['pct']:.2%}，量 {ftd['turnover']/1e8:,.0f} 億 > 前日 {ftd['prev_turnover']/1e8:,.0f} 億")
    L.append("- 若收盤跌破上述低點，反彈嘗試失效、重新計算")
    L += ["", "## 產業上升趨勢比例（前 8 / 後 5）", "| 產業 | 家數 | 今日 | 前日 | 20日變化 |", "|---|---|---|---|---|"]
    show = pd.concat([sectors.head(8), sectors.tail(5)])
    for _, r in show.iterrows():
        L.append(f"| {r['產業']} | {r['家數']} | {r['上升趨勢比例']:.0%} | {r['前日']:.0%} | {r['20日變化']:+.0%} |")
    L.append(f"\n有上升趨勢個股的產業：{int((sectors['上升趨勢比例'] > 0).sum())}/{len(sectors)}")
    md = "\n".join(L) + "\n"
    path = os.path.join(a.out, f"tw_market_check_{day}.md")
    open(path, "w").write(md)
    print(md)
    print(f"[saved] {path}")


if __name__ == "__main__":
    main()
