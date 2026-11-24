"""台股開盤前預估 (pre-open outlook) — run after the US close and the TAIFEX night session (~07:00 Asia/Taipei).

Inputs: US indices / TSM ADR / EWT / USDTWD (Yahoo), TX night session (TAIFEX), last TAIEX close (TWSE).
Implied TAIEX open = TX night last + (TAIEX close - TX day-session settle) basis.

Usage: python3 preopen.py [--out DIR] [--date YYYY-MM-DD]   (date = the Taiwan trading day to forecast)
Exit 3 = no night session found for that date (holiday / weekend).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twdata as T  # noqa: E402

US = [("%5EGSPC", "S&P 500"), ("%5EIXIC", "那斯達克"), ("%5EDJI", "道瓊"), ("%5ESOX", "費城半導體"),
      ("NVDA", "輝達"), ("TSM", "台積電 ADR"), ("EWT", "台股 ETF EWT"), ("%5EVIX", "VIX")]


def last_two(s: pd.Series, before: pd.Timestamp):
    s = s[s.index < before].dropna()
    return (s.index[-1], float(s.iloc[-1]), float(s.iloc[-2])) if len(s) >= 2 else (None, None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
    ap.add_argument("--date")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(T.TPE).date()
    ts_day = pd.Timestamp(day)

    night = T.taifex_tx(day, night=True)
    if night is None or night.empty or night["last"].isna().all():
        print(f"{day}: 找不到屬於此交易日的台指期夜盤（休市、週末或尚未公布）")
        sys.exit(3)

    ix = T.twse_daily_index(months=2, today=day - dt.timedelta(days=1))
    prev_day = ix.index[-1].date()
    taiex_prev = float(ix["close"].iloc[-1])
    dayses = T.taifex_tx(prev_day, night=False)

    # near-month = most-traded contract of the night session
    nrow = night.sort_values("volume", ascending=False).iloc[0]
    month = nrow["month"]
    month_label = month.split(".")[0]
    drow = dayses[dayses["month"] == month].iloc[0] if dayses is not None and (dayses["month"] == month).any() else None
    settle = float(drow["settle"]) if drow is not None and drow["settle"] else float(nrow["last"] - nrow["chg"])
    basis = taiex_prev - settle
    implied = float(nrow["last"]) + basis
    implied_pct = implied / taiex_prev - 1

    us = []
    for sym, name in US:
        s = T.yahoo_closes(sym, "1mo")
        if s is None:
            continue
        d, c, p = last_two(s, ts_day)
        if d is not None:
            us.append({"symbol": sym.replace("%5E", "^"), "name": name, "date": str(d.date()), "close": c, "pct": c / p - 1})

    # TSM ADR implied price for 2330 (1 ADR = 5 shares)
    fx = T.yahoo_closes("TWD%3DX", "1mo")
    tw2330 = T.yahoo_closes("2330.TW", "1mo")
    tsm = next((u for u in us if u["symbol"] == "TSM"), None)
    adr = None
    if fx is not None and tw2330 is not None and tsm:
        _, fx_now, _ = last_two(fx, ts_day + pd.Timedelta(days=1))
        _, c2330, c2330_prev = last_two(tw2330, ts_day)
        implied_2330 = tsm["close"] * fx_now / 5
        tsm_prev = tsm["close"] / (1 + tsm["pct"])
        prem_prev = (tsm_prev * fx_now / 5) / c2330_prev - 1
        adr = {"usdtwd": fx_now, "tsm_close": tsm["close"], "implied_2330": implied_2330, "tw_close": c2330,
               "premium": implied_2330 / c2330 - 1, "premium_prev": prem_prev}

    if implied_pct > 0.005:
        view = "開高" if implied_pct < 0.02 else "大幅開高"
    elif implied_pct < -0.005:
        view = "開低" if implied_pct > -0.02 else "大幅開低"
    else:
        view = "平盤附近"
    sox = next((u["pct"] for u in us if u["symbol"] == "^SOX"), None)
    agree = None
    if sox is not None:
        agree = (sox > 0) == (implied_pct > 0) or abs(implied_pct) < 0.005

    res = {"date": str(day), "prev_trading_day": str(prev_day), "taiex_prev": taiex_prev, "view": view,
           "implied_open": implied, "implied_pct": implied_pct, "basis": basis,
           "night": {k: (float(v) if isinstance(v, (int, float)) and pd.notna(v) else str(v)) for k, v in nrow.items()},
           "day_settle": settle, "us": us, "adr": adr, "sox_agrees": agree}
    json.dump(res, open(os.path.join(a.out, f"tw_preopen_{day}.json"), "w"), ensure_ascii=False, indent=2)

    L = [f"# 台股開盤前預估 — {day}", "",
         "> 依台指期夜盤 + 美股收盤推估，僅供參考，實際開盤受早盤消息與委託影響。非投資建議。", "",
         f"## 預估：**{view}**，加權約 {implied:,.0f} 點（{implied_pct:+.2%}，{implied - taiex_prev:+,.0f} 點）", "",
         f"- 前一交易日（{prev_day}）加權收盤 {taiex_prev:,.2f}",
         f"- 推估方式：夜盤最後價 {nrow['last']:,.0f} + 期現貨基差 {basis:+,.0f}（加權收盤 − 日盤結算 {settle:,.0f}）", "",
         f"## 台指期夜盤（TX {month_label}）", "| 開 | 高 | 低 | 最後 | 漲跌 | 成交量 |", "|---|---|---|---|---|---|",
         f"| {nrow['open']:,.0f} | {nrow['high']:,.0f} | {nrow['low']:,.0f} | **{nrow['last']:,.0f}** | "
         f"{nrow['chg']:+,.0f}（{nrow['chg'] / settle:+.2%}） | {nrow['volume']:,.0f} |", "",
         "## 美股收盤", "| 標的 | 日期 | 收盤 | 漲跌 |", "|---|---|---|---|"]
    for u in us:
        L.append(f"| {u['name']} | {u['date']} | {u['close']:,.2f} | {u['pct']:+.2%} |")
    if adr:
        L += ["", "## 台積電 ADR 換算",
              f"- TSM {adr['tsm_close']:.2f} × 匯率 {adr['usdtwd']:.3f} ÷ 5 = **{adr['implied_2330']:,.0f} 元**，"
              f"台股收盤 {adr['tw_close']:,.0f} 元 → ADR 溢價 {adr['premium']:+.1%}（前一日約 {adr['premium_prev']:+.1%}）",
              "- ADR 長期多有溢價，看「溢價變化」比看絕對值有意義"]
    L += ["", "## 判讀"]
    if agree is False:
        L.append("- ⚠️ 夜盤方向與費城半導體相反，開盤方向不確定性較高")
    L.append(f"- 夜盤區間 {nrow['low']:,.0f}–{nrow['high']:,.0f}，最後價位於區間 "
             f"{(nrow['last'] - nrow['low']) / max(nrow['high'] - nrow['low'], 1):.0%} 處"
             "（越接近 100% 代表收在夜盤高點）")
    md = "\n".join(L) + "\n"
    path = os.path.join(a.out, f"tw_preopen_{day}.md")
    open(path, "w").write(md)
    print(md)
    print(f"[saved] {path}")


if __name__ == "__main__":
    main()
