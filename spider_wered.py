import requests
import json
import re
import ast
import os
from datetime import datetime
ACCESS_TOKEN = os.getenv("WE_RED_TOKEN")
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "access_token": ACCESS_TOKEN,
    "accesstoken": ACCESS_TOKEN,
    "apiversion": "6",
    "origin": "https://www.red-ring.cn",
    "referer": "https://www.red-ring.cn/",
    "accept": "application/json, text/plain, */*"
}
def get_page(gid=25427, page=1, pageSize=100):
    url = "https://api.redringvip.com/api/content/list/get"
    params = {
        "gid": gid,
        "plateId": 7222,
        "type": 1,
        "index": page,
        "pageSize": pageSize
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.encoding = "utf-8"
    raw = resp.json()
    # 第 2 次 JSON 解码
    return json.loads(raw["data"])
def filter_trade_posts(parsed):
    mapping = {
        "500": "510500.SS",
        "300": "510300.SS",
        "50": "510050.SS",
        "1000": "512100.SS"
    }
    result = []
    for item in parsed["list"]:
        content = item.get("content", "")
        ts_f = datetime.fromtimestamp(int(item["time"])).strftime('%Y-%m-%d %H:%M:%S')
        pattern = r"([^,]+),\s*(\d+)(?:,\s*强度:\s*(\[.*\]))?"
        match = re.match(pattern, content)
        if match:
            action = match.group(1)
            number = match.group(2)
            arr = ast.literal_eval(match.group(3)) if match.group(3) else None

            # B/S 映射
            bs = "B" if action == "进场" else "S"
            result.append({
                # "ts": item["time"],
                "date":ts_f,
                # "raw_data": content,
                "action": bs,   # 进场 or 离场
                "stock": mapping[number],        # 具体数值，如 "500"
                "sort":arr
            })
    return result


if __name__ == "__main__":
    parsed = get_page()
    trades = filter_trade_posts(parsed)
    # print("筛选到的交易类帖子（含进场/离场）:")
    for t in trades:
        print(t)