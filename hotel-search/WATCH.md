# 追蹤中的住宿

| 名稱 | 地點 | Agoda 網址代稱 | 加入日期 | 備註 |
|---|---|---|---|---|
| Hotel Firststay Hongdae（Google 地圖名稱：First Stay） | 首爾西大門區延世路 2 街路 12（新村） | `hotel-firststay-hongdae` | 2026-11-04 | Google 評分 4.9（576）；Priceline 9.3（356），附按摩浴缸套房約 30㎡、1 張大床 |

## 查詢紀錄
| 查詢時間 | Agoda（1 位大人，12/31–1/5 每晚） | Google 飯店 | 說明 |
|---|---|---|---|
| 2026-11-04 03:35 | 6 晚皆「已完售」；2 位大人與 1/12 也是 | 有卡片無價格（無通路販售） | 連非旺季日期也完售，較可能是 Agoda 未開放此飯店的房間，而非跨年客滿 |

## 重新查詢
```bash
cd hotel-search
HOTELS="firststay:hotel-firststay-hongdae" NIGHTS="2026-12-31 2027-01-01 2027-01-02 2027-01-03 2027-01-04 2027-01-05" ./scrape_agoda.sh
python3 agoda.py sinchon
```

## 2026-11-16 更新
Agoda 1/1 入住 5 晚（1/1–1/6）**有空房**：高級雙床房 (Superior Twin) 每晚含稅約 NT$4,214（可免費取消），Agoda 9.2 分（2,144 篇）。見 agoda_stay_2027-01-01_5.html。
