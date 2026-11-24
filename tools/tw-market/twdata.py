"""Shared data helpers for the Taiwan market scripts (TWSE / TAIFEX / Yahoo Finance)."""
from __future__ import annotations

import datetime as dt
import re
import time
from io import StringIO

import pandas as pd
import requests

UA = {"User-Agent": "Mozilla/5.0"}
TPE = dt.timezone(dt.timedelta(hours=8))


def get(url: str, *, method: str = "GET", data: dict | None = None, tries: int = 4, timeout: int = 30):
    last = None
    for i in range(tries):
        try:
            r = requests.request(method, url, headers=UA, data=data, timeout=timeout)
            if r.status_code == 200 and r.content:
                return r
            last = f"HTTP {r.status_code}"
        except Exception as e:  # network hiccup
            last = repr(e)
        time.sleep(2 + 3 * i)
    raise RuntimeError(f"fetch failed: {url} ({last})")


def get_json(url: str, **kw):
    for i in range(4):
        try:
            return get(url, **kw).json()
        except ValueError:  # TWSE sometimes returns an HTML throttle page
            time.sleep(3 + 3 * i)
    raise RuntimeError(f"non-JSON response: {url}")


def num(s) -> float | None:
    """Parse '1,234.5', '▲3170', '▼-1881', '-' -> float/None."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    m = re.search(r"-?\d[\d,]*\.?\d*", str(s))
    return float(m.group(0).replace(",", "")) if m else None


# ---------------- Yahoo ----------------
def yahoo_closes(symbol: str, rng: str = "2y") -> pd.Series | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={rng}&interval=1d"
    for i in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=20)
            if r.status_code == 200:
                res = r.json()["chart"]["result"][0]
                q = res["indicators"]["quote"][0]
                tz = dt.timezone(dt.timedelta(seconds=res["meta"].get("gmtoffset", 0)))
                idx = pd.to_datetime([dt.datetime.fromtimestamp(t, tz).date() for t in res["timestamp"]])
                s = pd.Series(q["close"], index=idx, dtype="float64")
                return s[~s.index.duplicated(keep="last")].dropna()
            if r.status_code == 429:
                time.sleep(2 + 3 * i)
        except Exception:
            time.sleep(1)
    return None


# ---------------- TWSE ----------------
def twse_companies() -> list[dict]:
    cos = get_json("https://openapi.twse.com.tw/v1/opendata/t187ap03_L")
    return [c for c in cos if c["公司代號"].strip().isdigit() and len(c["公司代號"].strip()) == 4]


def twse_daily_index(months: int = 4, today: dt.date | None = None) -> pd.DataFrame:
    """TAIEX close + total turnover (成交金額) per trading day, from FMTQIK (monthly)."""
    today = today or dt.datetime.now(TPE).date()
    rows = []
    y, m = today.year, today.month
    for _ in range(months):
        d = get_json(f"https://www.twse.com.tw/exchangeReport/FMTQIK?response=json&date={y}{m:02d}01")
        for r in d.get("data", []) or []:
            ry, rm, rd = (int(x) for x in r[0].split("/"))
            rows.append({"date": pd.Timestamp(ry + 1911, rm, rd), "turnover": num(r[2]), "close": num(r[4]), "chg": num(r[5])})
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        time.sleep(0.5)
    df = pd.DataFrame(rows).drop_duplicates("date").set_index("date").sort_index()
    return df[df.index <= pd.Timestamp(today)]


def twse_breadth_counts(date: dt.date) -> dict | None:
    d = get_json(f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date:%Y%m%d}&type=MS")
    if d.get("stat") != "OK":
        return None
    for t in d.get("tables", []):
        if "漲跌證券數" in (t.get("title") or ""):
            out = {}
            for r in t["data"]:
                key, stocks = r[0], r[2]  # column 2 = 股票 only
                m = re.match(r"([\d,]+)(?:\(([\d,]+)\))?", stocks)
                a, b = (num(m.group(1)), num(m.group(2)) if m.group(2) else None) if m else (None, None)
                if key.startswith("上漲"):
                    out["up"], out["limit_up"] = a, b
                elif key.startswith("下跌"):
                    out["down"], out["limit_down"] = a, b
                elif key.startswith("持平"):
                    out["flat"] = a
            return out
    return None


def twse_institutional(date: dt.date) -> dict | None:
    d = get_json(f"https://www.twse.com.tw/fund/BFI82U?response=json&dayDate={date:%Y%m%d}&type=day")
    if d.get("stat") != "OK" or not d.get("data"):
        return None
    out = {}
    for r in d["data"]:
        net = num(r[3]) / 1e8  # 億元
        name = r[0]
        if name.startswith("外資及陸資"):
            out["外資"] = net
        elif name == "投信":
            out["投信"] = net
        elif "自行買賣" in name:
            out["自營商自行"] = net
        elif "避險" in name:
            out["自營商避險"] = net
        elif name == "合計":
            out["合計"] = net
    return out


# ---------------- TAIFEX ----------------
def taifex_tx(query_date: dt.date, night: bool) -> pd.DataFrame | None:
    """TX futures daily report. night=True -> after-hours session belonging to trading day `query_date`
    (it ran from the previous trading day 15:00 to 05:00)."""
    mc = "1" if night else "0"
    r = get("https://www.taifex.com.tw/cht/3/futDailyMarketReport", method="POST",
            data={"queryType": "2", "marketCode": mc, "commodity_id": "TX", "queryDate": f"{query_date:%Y/%m/%d}",
                  "MarketCode": mc, "commodity_idt": "TX"})
    try:
        tables = pd.read_html(StringIO(r.content.decode("utf-8", "replace")))
    except ValueError:
        return None
    for t in tables:
        cols = [re.sub(r"\s+", "", str(c)) for c in t.columns]
        if t.shape[1] > 8 and any("契約" in c for c in cols):
            t.columns = cols
            t = t[t[cols[0]].astype(str).str.strip() == "TX"].copy()
            if t.empty:
                return None

            def col(key):
                return next(c for c in cols if key in c)

            out = pd.DataFrame({
                "month": t[col("到期")].astype(str),
                "open": t[col("開盤")].map(num), "high": t[col("最高")].map(num), "low": t[col("最低")].map(num),
                "last": t[col("最後成交")].map(num), "chg": t[col("漲跌價")].map(num),
                "volume": t[[c for c in cols if "成交量" in c][-1]].map(num),
                "settle": t[col("結算")].map(num),
            })
            return out.reset_index(drop=True)
    return None
