import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient, Consent
from app.models.document import Document, DocumentPage
from app.models.fact import ClinicalFact
from app.models.timeline import TimelineEvent
from app.models.intake import IntakeSession, IntakeAnswer
from app.services import audit

router = APIRouter(prefix="/consents", tags=["consents"])


@router.post("/{consent_id}/revoke")
def revoke_consent(consent_id: str, actor: str = "patient",
                   db: Session = Depends(get_db)):
    """Revoke a consent and purge all linked clinical data (DPDP Act 2023)."""
    c = db.get(Consent, consent_id)
    if not c:
        raise HTTPException(404, "consent not found")
    if c.revoked_at:
        return {"consent_id": consent_id, "already_revoked": True,
                "revoked_at": c.revoked_at, "purged": {}}

    c.revoked_at = datetime.utcnow()
    c.granted = False
    pid = c.patient_id

    # Cascade delete (order matters due to FKs)
    facts_deleted = db.query(ClinicalFact).filter_by(patient_id=pid).delete()
    timeline_deleted = db.query(TimelineEvent).filter_by(patient_id=pid).delete()

    doc_ids = [d.id for d in db.query(Document).filter_by(patient_id=pid).all()]
    pages_deleted = 0
    if doc_ids:
        pages_deleted = db.query(DocumentPage).filter(
            DocumentPage.document_id.in_(doc_ids)
        ).delete(synchronize_session=False)
    docs_deleted = db.query(Document).filter_by(patient_id=pid).delete()

    session_ids = [s.id for s in db.query(IntakeSession).filter_by(patient_id=pid).all()]
    answers_deleted = 0
    if session_ids:
        answers_deleted = db.query(IntakeAnswer).filter(
            IntakeAnswer.session_id.in_(session_ids)
        ).delete(synchronize_session=False)
    sessions_deleted = db.query(IntakeSession).filter_by(patient_id=pid).delete()

    db.commit()

    purged = {
        "clinical_facts": facts_deleted,
        "timeline_events": timeline_deleted,
        "documents": docs_deleted,
        "document_pages": pages_deleted,
        "intake_sessions": sessions_deleted,
        "intake_answers": answers_deleted,
    }

    audit.record(
        db, action="consent.revoke", actor=actor, patient_id=pid,
        resource_type="Consent", resource_id=consent_id,
        details={"purged": purged},
    )

    return {
        "consent_id": consent_id,
        "revoked_at": c.revoked_at,
        "purged": purged,
    }


@router.get("/patient/{patient_id}")
def list_consents(patient_id: str, db: Session = Depends(get_db)):
    rows = db.query(Consent).filter_by(patient_id=patient_id).all()
    return [
        {"id": r.id, "purpose": r.purpose, "granted": r.granted,
         "granted_at": r.granted_at, "revoked_at": r.revoked_at}
        for r in rows
    ]


@router.get("/audit")
def list_audit(patient_id: str | None = None, limit: int = 100,
               db: Session = Depends(get_db)):
    from app.models.audit import AuditLog
    q = db.query(AuditLog)
    if patient_id:
        q = q.filter_by(patient_id=patient_id)
    rows = q.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {"id": r.id, "actor": r.actor, "action": r.action,
         "patient_id": r.patient_id, "resource_type": r.resource_type,
         "resource_id": r.resource_id,
         "details": json.loads(r.details_json or "{}"),
         "created_at": r.created_at}
        for r in rows
    ]

@router.get("/audit/page")
def audit_page(patient_id: str | None = None,
               action: str | None = None,
               page: int = 1,
               page_size: int = 20,
               db: Session = Depends(get_db)):
    """Paginated audit log with optional filters."""
    from app.models.audit import AuditLog
    from sqlalchemy import func as _func

    page = max(1, page)
    page_size = max(1, min(100, page_size))

    q = db.query(AuditLog)
    if patient_id:
        q = q.filter(AuditLog.patient_id == patient_id)
    if action:
        q = q.filter(AuditLog.action.like(action + "%"))

    total = q.count()
    rows = (
        q.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = (total + page_size - 1) // page_size if total else 1

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "entries": [
            {
                "id": r.id,
                "actor": r.actor,
                "action": r.action,
                "patient_id": r.patient_id,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "details": json.loads(r.details_json or "{}"),
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }
