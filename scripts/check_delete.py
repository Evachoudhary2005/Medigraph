import sqlite3
c = sqlite3.connect("apps/api/medigraph.db")

print("Documents:", c.execute("SELECT COUNT(*) FROM documents").fetchone()[0])
print("Pages:", c.execute("SELECT COUNT(*) FROM document_pages").fetchone()[0])
print("Facts:", c.execute("SELECT COUNT(*) FROM clinical_facts").fetchone()[0])
print("Timeline events:", c.execute("SELECT COUNT(*) FROM timeline_events").fetchone()[0])
print()
print("Last 3 document.delete audit entries:")
for r in c.execute("SELECT details_json, created_at FROM audit_log WHERE action='document.delete' ORDER BY created_at DESC LIMIT 3"):
    print(" ", r[1])
    print("   ", r[0][:160])
