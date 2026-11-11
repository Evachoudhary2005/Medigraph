import bcrypt

def hash_password(plain: str) -> str:
    pwd_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception as e:
        print("verify error:", e)
        return False

# Test with existing hashes in DB
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    test_pw = "clinic123" if "clinician" in u.email else ("admin123" if "admin" in u.email else "patient123")
    v = verify_password(test_pw, u.password_hash)
    print(f"User {u.email}: password '{test_pw}' -> verified: {v}")

# Test hash and verify new password
new_h = hash_password("newpassword123")
print("New hash verify:", verify_password("newpassword123", new_h))
print("New hash wrong verify:", verify_password("wrong", new_h))

db.close()
