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

# 数字 -> ETF 代码映射
MAPPING = {
    "500": "510500.SS",
    "300": "510300.SS",
    "50":  "510050.SS",
    "1000": "512100.SS"
}

def get_page(gid=25427, page=1, pageSize=100):
    """
    从外部接口获取原始帖子数据
    """
    url = "https://api.redringvip.com/api/content/list/get"
    params = {
        "gid": gid,
        "plateId": 7222,
        "type": 1,
        "index": page,
        "pageSize": pageSize
    }

    resp = requests.get(url, headers=headers, params=params, timeout=5)
    resp.encoding = "utf-8"
    raw = resp.json()
    # 第二层 JSON 解码
    return json.loads(raw["data"])


def filter_trade_posts(parsed):
    """
    从原始帖子中过滤出交易类信号，返回结构:
    [
        {
            "date": "2025-01-01 09:36:00",
            "action": "B" / "S",
            "stock": "510500.SS",
            "sort": [... 或 None]
        },
        ...
    ]
    """
    result = []
    pattern = r"([^,]+),\s*(\d+)(?:,\s*强度:\s*(\[.*\]))?"

    for item in parsed.get("list", []):
        content = item.get("content", "")
        ts_f = datetime.fromtimestamp(int(item["time"])).strftime('%Y-%m-%d %H:%M:%S')

        match = re.match(pattern, content)
        if not match:
            continue

        action_text = match.group(1)   # “进场” / “离场”
        number = match.group(2)        # "500" / "300" / ...
        arr = ast.literal_eval(match.group(3)) if match.group(3) else None

        # B/S 映射
        bs = "B" if action_text == "进场" else "S"

        # 映射到具体 ETF 代码
        stock = MAPPING.get(number)
        if not stock:
            continue

        result.append({
            "date": ts_f,
            "action": bs,
            "stock": stock,
            "sort": arr,
        })

    return result


if __name__ == "__main__":
    parsed = get_page()
    trades = filter_trade_posts(parsed)
    # print("筛选到的交易类帖子（含进场/离场）:")
    for t in trades:
        print(t) 