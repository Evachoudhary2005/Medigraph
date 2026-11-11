import urllib.request
import json

req = urllib.request.Request(
    "http://localhost:3000/api/v1/auth/login",
    data=json.dumps({"email": "clinician@medigraph.example.com", "password": "clinic123"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"NEXT.JS PROXY SUCCESS: {data['user']['email']} -> {data['user']['role']}")
except Exception as e:
    print("NEXT.JS PROXY FAILED:", e)
    if hasattr(e, "read"):
        print("Body:", e.read().decode("utf-8"))
