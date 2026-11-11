import sqlite3
import urllib.request
import json
from app.db.session import SessionLocal
from app.services.auth_service import authenticate, verify_password
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
print("Total users in DB:", len(users))
for u in users:
    print(f"User: {u.email}, active: {u.is_active}, role: {u.role}")

print("\nTesting authenticate():")
print("admin:", authenticate(db, "admin@medigraph.example.com", "admin123"))
print("clinician:", authenticate(db, "clinician@medigraph.example.com", "clinic123"))
print("patient:", authenticate(db, "patient@medigraph.example.com", "patient123"))
db.close()

print("\nTesting HTTP POST to http://127.0.0.1:8000/api/v1/auth/login:")
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/auth/login",
    data=json.dumps({"email": "clinician@medigraph.example.com", "password": "clinic123"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req) as resp:
        print("HTTP Status:", resp.status)
        print("Response:", resp.read().decode("utf-8")[:200])
except Exception as e:
    print("HTTP Error:", e)
    if hasattr(e, "read"):
        print("Error body:", e.read().decode("utf-8"))
