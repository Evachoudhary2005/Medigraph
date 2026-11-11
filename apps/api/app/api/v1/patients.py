from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.patient import Patient, Consent
from app.models.intake import IntakeSession, IntakeAnswer
from app.models.document import Document
from app.models.fact import ClinicalFact
from app.models.timeline import TimelineEvent
from app.schemas.patient import PatientCreate, PatientOut, ConsentCreate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientOut)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    existing = db.query(Patient).filter_by(synthetic_id=payload.synthetic_id).first()
    if existing:
        raise HTTPException(400, "synthetic_id already exists")
    p = Patient(
        id=str(uuid4()),
        synthetic_id=payload.synthetic_id,
        preferred_language=payload.preferred_language,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("")
def list_patients(db: Session = Depends(get_db)):
    rows = db.query(Patient).order_by(Patient.created_at.desc()).limit(50).all()
    return [
        {
            "id": p.id,
            "synthetic_id": p.synthetic_id,
            "preferred_language": p.preferred_language,
            "created_at": p.created_at,
        }
        for p in rows
    ]


@router.get("/stats")
def list_patients_with_stats(db: Session = Depends(get_db)):
    """Return each patient with a counts summary for the dashboard."""
    rows = db.query(Patient).order_by(Patient.created_at.desc()).limit(50).all()
    out = []
    for p in rows:
        sessions = db.query(func.count(IntakeSession.id)).filter_by(patient_id=p.id).scalar() or 0
        answers = (
            db.query(func.count(IntakeAnswer.id))
            .join(IntakeSession, IntakeAnswer.session_id == IntakeSession.id)
            .filter(IntakeSession.patient_id == p.id)
            .scalar() or 0
        )
        documents = db.query(func.count(Document.id)).filter_by(patient_id=p.id).scalar() or 0
        facts = db.query(func.count(ClinicalFact.id)).filter_by(patient_id=p.id).scalar() or 0
        timeline_events = db.query(func.count(TimelineEvent.id)).filter_by(patient_id=p.id).scalar() or 0
        needs_review = (
            db.query(func.count(TimelineEvent.id))
            .filter(TimelineEvent.patient_id == p.id,
                    TimelineEvent.needs_review == True)  # noqa: E712
            .scalar() or 0
        )
        verified = (
            db.query(func.count(TimelineEvent.id))
            .filter(TimelineEvent.patient_id == p.id,
                    TimelineEvent.verification_status == "verified")
            .scalar() or 0
        )
        out.append({
            "id": p.id,
            "synthetic_id": p.synthetic_id,
            "preferred_language": p.preferred_language,
            "created_at": p.created_at,
            "stats": {
                "sessions": sessions,
                "answers": answers,
                "documents": documents,
                "facts": facts,
                "timeline_events": timeline_events,
                "needs_review": needs_review,
                "verified": verified,
            },
        })
    return out


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "not found")
    return p


@router.post("/{patient_id}/consents")
def add_consent(patient_id: str, payload: ConsentCreate, db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")
    c = Consent(
        id=str(uuid4()),
        patient_id=patient_id,
        purpose=payload.purpose,
        granted=payload.granted,
        notes=payload.notes,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "purpose": c.purpose, "granted": c.granted}