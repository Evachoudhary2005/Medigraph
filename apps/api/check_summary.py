import json, urllib.request
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
with urllib.request.urlopen(f"http://127.0.0.1:8000/api/v1/summary/{pid}", timeout=15) as r:
    data = json.loads(r.read())
for sec in data["draft"]["sections"]:
    print(f"--- {sec['title']} ---")
    for item in sec["items"]:
        print(f"  [{item['confidence']:.2f}] {item['text']}")
