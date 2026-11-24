#!/bin/bash
# 飯店名稱 → Agoda id 與網址 slug（suggest API 找 id，GetSecondaryData 取 defaultSearchURL）
# usage: bash agoda_slug.sh "Grid Inn Hotel" "Hotel Sunbee Insadong" ...
for q in "$@"; do
  id=$(curl -s -m 20 -A "Mozilla/5.0" "https://www.agoda.com/api/cronos/search/GetUnifiedSuggestResult/3/20/1/0/zh-tw/?searchText=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$q")&origin=TW&cid=-1&pageTypeId=1&logtime=x&logTypeId=1&isHotelLandSearch=true" \
     | python3 -c "import sys,json;d=json.load(sys.stdin);v=[x for x in d.get('ViewModelList') or [] if x.get('ObjectId') and x.get('IsHotel')];print(v[0]['ObjectId'] if v else '')")
  [ -z "$id" ] && { echo "$q	-	-"; continue; }
  s=$(curl -s -m 20 -A "Mozilla/5.0" "https://www.agoda.com/api/cronos/property/BelowFoldParams/GetSecondaryData?hotel_id=$id&all=false&isHostPropertiesEnabled=false" \
     | python3 -c "import sys,json,re;d=json.load(sys.stdin);u=d['searchbox']['config']['defaultSearchURL'];m=re.match(r'/([^/]+)/hotel/([^.]+)\.html',u);print(m.group(1)+('' if m.group(2)=='seoul-kr' else '@'+m.group(2)))" 2>/dev/null)
  echo "$q	$id	$s"
done
