import sqlite3

c = sqlite3.connect("medigraph.db")
print("Tables in medigraph.db:")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(tables)

if "users" in tables:
    users = c.execute("SELECT id, email, full_name, role, is_active, password_hash FROM users").fetchall()
    print(f"\nTotal users: {len(users)}")
    for u in users:
        print(f"ID: {u[0]} | Email: {u[1]} | Name: {u[2]} | Role: {u[3]} | Active: {u[4]} | HashPrefix: {u[5][:15] if u[5] else 'None'}")
else:
    print("No users table found!")

c.close()
