import sqlite3
c = sqlite3.connect("apps/api/medigraph.db")
doc = "4a4b636f-4ab6-41a4-88cc-8150e0218975"
rows = c.execute(
    "SELECT kind, label, value FROM clinical_facts WHERE document_id=?", (doc,)
).fetchall()
print(f"facts for {doc}: {len(rows)}")
for r in rows:
    print(f"  kind={r[0]!r:15} label={r[1]!r:20} value={r[2]!r}")
