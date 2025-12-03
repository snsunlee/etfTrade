import requests
import base64
import json

url = "https://raw.githubusercontent.com/snsunlee/etfTrade/main/signal.json"

resp = requests.get(url)
data = resp.json()
content = base64.b64decode(data["content"]).decode("utf-8")
parsed = json.loads(content)

print(parsed)
