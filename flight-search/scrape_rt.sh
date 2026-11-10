#!/bin/bash
# 來回票爬蟲已改寫為兩階段的 scrape_rt.py（先記每班去程的來回最低價，只點價格有變的前幾名）。
# usage: scrape_rt.sh ["Taipei-Seoul Taipei-Busan ..."]
exec python3 "$(dirname "$0")/scrape_rt.py" "$@"
