import json, urllib.request
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/fhir/export/{pid}",
    method="POST",
)
print("Running HAPI validation (30-90 s first time)...")
with urllib.request.urlopen(req, timeout=300) as r:
    data = json.loads(r.read())

print()
print("=== Structural validation ===")
print("valid:", data["validation"]["valid"])
print("entries:", data["validation"]["entries"])

print()
print("=== HAPI FHIR validation ===")
hapi = data.get("hapi_validation")
if hapi is None:
    print("NOT WIRED")
elif not hapi.get("available"):
    print("NOT AVAILABLE:", hapi.get("stderr", "")[:300])
else:
    print("valid:", hapi["valid"])
    print("errors:", hapi["error_count"])
    print("warnings:", hapi["warning_count"])
    print("info:", hapi["info_count"])
    print()
    if hapi["issues"]:
        print(f"Issues ({len(hapi['issues'])} total):")
        for i in hapi["issues"][:15]:
            print(f"  [{i['severity']}] {i['diagnostics'][:110]}")
            if i["location"]:
                print(f"      at {i['location']}")
