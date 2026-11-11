import json, urllib.request
url = "http://127.0.0.1:8000/api/v1/consents/audit/page?page=1&page_size=5"
with urllib.request.urlopen(url, timeout=15) as r:
    data = json.loads(r.read())
print("total:", data["total"])
print("page:", data["page"], "of", data["total_pages"])
print("has_next:", data["has_next"], "has_prev:", data["has_prev"])
print()
for e in data["entries"]:
    print(f"  {e['action']:30} by {e['actor']:35} {e['created_at'][:19]}")
