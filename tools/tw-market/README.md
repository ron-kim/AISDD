# tw-market — 台股每日檢查腳本

依 [claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) 的 market-regime-daily
流程（市場廣度 → 上升趨勢 → 持股建議）改編到台股（上市），另加開盤前預估。近似版，非投資建議。

需求：Python 3.11+、`requests`、`pandas`、`numpy`、`lxml`（TAIFEX 表格解析）。

| 腳本 | 何時跑 | 內容 |
|---|---|---|
| `market_check.py` | 台股收盤後（建議 15:40 之後，三大法人才公布） | 站上200MA比例、上升趨勢比例（收>50MA>200MA）、產業參與、加權趨勢、綜合分數與持股建議、漲跌家數、三大法人、反彈天數與 Follow-Through Day |
| `preopen.py` | 美股收盤與台指期夜盤結束後（約 07:00） | 夜盤 + 期現貨基差推估加權開盤、美股/費半/輝達/TSM ADR、ADR 溢價變化 |

```bash
python3 market_check.py --out output            # 今天（Asia/Taipei）
python3 market_check.py --date 2026-11-24
python3 preopen.py --out output                 # 預估今天開盤
```

結束碼：`3` = 該日無交易資料／無夜盤（休市、週末）；`4` = Yahoo 個股資料尚未更新。

資料來源：TWSE（FMTQIK、MI_INDEX、BFI82U、OpenAPI t187ap03_L）、TAIFEX 期貨每日交易行情、Yahoo Finance chart API。
