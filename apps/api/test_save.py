import json, urllib.request

pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
body = {
    "sections": [
        {
            "key": "medications_allergies",
            "title": "Medications and Allergies",
            "items": [
                {"event_id": "test-1", "text": "Metoprolol 100mg BD (edited)", "confidence": 0.95,
                 "source": "document", "needs_review": False, "verification_status": "pending", "warnings": []}
            ],
        }
    ],
    "notes": "edited during test",
    "actor": "clinician",
    "status": "draft",
}

req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/summary/{pid}/save",
    method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=15) as r:
    print("status:", r.status)
    print(json.dumps(json.loads(r.read()), indent=2))

# list
print()
print("--- drafts ---")
with urllib.request.urlopen(f"http://127.0.0.1:8000/api/v1/summary/{pid}/drafts", timeout=15) as r:
    print(json.dumps(json.loads(r.read()), indent=2))
