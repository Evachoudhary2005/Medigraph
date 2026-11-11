from app.db.session import SessionLocal
from app.services.auth_service import _pwd
from app.models.user import User
import bcrypt

print("bcrypt version:", getattr(bcrypt, "__version__", None))

db = SessionLocal()
u = db.query(User).filter_by(email="clinician@medigraph.example.com").first()
print("Stored hash:", u.password_hash)

try:
    res = _pwd.verify("clinic123", u.password_hash)
    print("passlib verify result:", res)
except Exception as e:
    import traceback
    print("passlib verify exception:")
    traceback.print_exc()

# Also test bcrypt directly
try:
    direct = bcrypt.checkpw("clinic123".encode("utf-8"), u.password_hash.encode("utf-8"))
    print("direct bcrypt.checkpw result:", direct)
except Exception as e:
    import traceback
    print("direct bcrypt exception:")
    traceback.print_exc()

db.close()
