import sqlite3, json, urllib.request

c = sqlite3.connect("medigraph.db")

# Find newest document that has OCR or verified text
row = c.execute("""
    SELECT id, patient_id, filename, length(coalesce(verified_text,'')) AS vt,
           length(coalesce(ocr_text,'')) AS ot
    FROM documents
    ORDER BY uploaded_at DESC
""").fetchall()

picked = None
for r in row:
    if (r[3] or 0) > 0 or (r[4] or 0) > 0:
        picked = r
        break

if not picked:
    print("No document has any text. Upload and verify one first.")
    raise SystemExit(1)

doc_id, patient_id, fname, vt, ot = picked
print(f"Picked document: {doc_id}")
print(f"  patient:       {patient_id}")
print(f"  filename:      {fname}")
print(f"  verified_text: {vt} chars, ocr_text: {ot} chars")
print()

# Call extract
print("--- POST /facts/extract ---")
req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/facts/extract/{doc_id}",
    method="POST",
)
with urllib.request.urlopen(req, timeout=300) as r:
    body = json.loads(r.read())
print(f"  count: {body.get('count')}")
for f in body.get("facts", [])[:8]:
    print(f"  - {f['kind']:12} {f['label']:20} {f['value'][:40]:40} conf={f['confidence']:.2f}")
print()

# Call timeline build
print("--- POST /timeline/build ---")
req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/timeline/build/{patient_id}",
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    body = json.loads(r.read())
print(f"  patient: {body.get('patient_id')}")
print(f"  count:   {body.get('count')}")
for e in body.get("events", [])[:10]:
    print(f"  - {e['kind']:14} {str(e['label'])[:24]:24} "
          f"{str(e['value'])[:30]:30} src={e['source']:8} conf={e['confidence']:.2f} "
          f"review={e['needs_review']}")
