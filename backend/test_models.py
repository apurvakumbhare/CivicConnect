import requests

response = requests.get("https://openrouter.ai/api/v1/models")
data = response.json()

for m in data.get("data", []):
    id = m.get("id", "")
    if "free" in id:
        print(id)
