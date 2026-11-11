"""Password hashing and JWT issuance."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User

log = logging.getLogger("medigraph.auth")


def hash_password(plain: str) -> str:
    pwd_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def create_user(db: Session, email: str, password: str,
                full_name: str = "", role: str = "patient") -> User:
    existing = db.query(User).filter_by(email=email.lower()).first()
    if existing:
        raise ValueError("email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=email.lower(),
        full_name=full_name,
        role=role,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log.info("created user %s (%s)", user.email, user.role)
    return user


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    u = db.query(User).filter_by(email=email.lower()).first()
    if not u or not u.is_active:
        return None
    if not verify_password(password, u.password_hash):
        return None
    u.last_login_at = datetime.utcnow()
    db.commit()
    return u


def issue_token(user: User) -> dict:
    expires = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "exp": expires,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except JWTError as e:
        log.warning("jwt decode failed: %s", e)
        return None


def seed_default_admin(db: Session) -> None:
    """Create a default admin + clinician on first startup if none exist."""
    if db.query(User).count() > 0:
        return
    try:
        create_user(db, "admin@medigraph.example.com", "admin123", "Administrator", "admin")
        create_user(db, "clinician@medigraph.example.com", "clinic123", "Dr. Demo", "clinician")
        create_user(db, "patient@medigraph.example.com", "patient123", "Demo Patient", "patient")
        log.info("seeded default users (admin/clinician/patient)")
    except Exception as e:
        log.warning("failed to seed users: %s", e)