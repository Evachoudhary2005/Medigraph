import sqlite3
c = sqlite3.connect("medigraph.db")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print(f"Total tables: {len(tables)}")
for t in tables:
    n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:25} {n:>6} rows")
