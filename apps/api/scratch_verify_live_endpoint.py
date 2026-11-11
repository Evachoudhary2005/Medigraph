import urllib.request
import json

test_accounts = [
    ("clinician@medigraph.example.com", "clinic123"),
    ("admin@medigraph.example.com", "admin123"),
    ("patient@medigraph.example.com", "patient123"),
]

for email, password in test_accounts:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/auth/login",
        data=json.dumps({"email": email, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"SUCCESS: {email} -> logged in! Token: {data['access_token'][:20]}... Role: {data['user']['role']}")
    except Exception as e:
        print(f"FAILED: {email} -> {e}")
        if hasattr(e, "read"):
            print("  Body:", e.read().decode("utf-8"))
