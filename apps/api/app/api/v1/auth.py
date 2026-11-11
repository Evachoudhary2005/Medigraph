import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import authenticate, create_user, issue_token
from app.services import audit

log = logging.getLogger("medigraph.auth.api")
router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = ""
    role: str = "patient"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if payload.role not in ("patient", "clinician", "admin"):
        raise HTTPException(400, "invalid role")
    try:
        user = create_user(db, payload.email, payload.password,
                           payload.full_name, payload.role)
    except ValueError as e:
        raise HTTPException(400, str(e))
    audit.record(db, action="auth.register", actor=user.email,
                 resource_type="User", resource_id=user.id,
                 details={"role": user.role})
    return user


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(401, "invalid credentials")
    out = issue_token(user)
    audit.record(db, action="auth.login", actor=user.email,
                 resource_type="User", resource_id=user.id,
                 details={"role": user.role})
    return out


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/protected-demo")
def protected_demo(user: User = Depends(get_current_user)):
    return {
        "message": "You are authenticated.",
        "email": user.email,
        "role": user.role,
    }

class ToggleActiveRequest(BaseModel):
    is_active: bool


@router.post("/users/{user_id}/toggle-active", response_model=UserOut)
def toggle_active(user_id: str, payload: ToggleActiveRequest,
                  admin: User = Depends(require_admin),
                  db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "user not found")
    if target.id == admin.id:
        raise HTTPException(400, "cannot deactivate yourself")
    target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    audit.record(db, action="auth.toggle_active", actor=admin.email,
                 resource_type="User", resource_id=target.id,
                 details={"is_active": target.is_active})
    return target


@router.delete("/users/{user_id}")
def delete_user(user_id: str,
                admin: User = Depends(require_admin),
                db: Session = Depends(get_db)):
    """Permanently delete a user. Guards:
       - cannot delete yourself
       - cannot delete the last remaining admin
    """
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "user not found")
    if target.id == admin.id:
        raise HTTPException(400, "cannot delete yourself")

    if target.role == "admin":
        remaining = db.query(User).filter(
            User.role == "admin", User.id != user_id
        ).count()
        if remaining == 0:
            raise HTTPException(400, "cannot delete the last remaining admin")

    email = target.email
    role = target.role
    db.delete(target)
    db.commit()

    audit.record(db, action="auth.delete_user", actor=admin.email,
                 resource_type="User", resource_id=user_id,
                 details={"email": email, "role": role})
    return {"deleted": True, "email": email, "role": role}
