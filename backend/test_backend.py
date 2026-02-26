import requests

url = "http://127.0.0.1:8000/query"

tests = [
    {"query": "объем закупок enstru 1046871"},
    {"query": "справедливая цена enstru 1046871 регион 711310000"},
    {"query": "аномалии enstru 1046871 регион 711310000"}
]

for t in tests:
    r = requests.post(url, json=t)
    print("\nQuery:", t["query"])
    print("Status:", r.status_code)
    print("Response:", r.json())