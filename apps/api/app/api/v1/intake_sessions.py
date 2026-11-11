import json
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.patient import Patient
from app.models.intake import IntakeSession, IntakeAnswer
from app.schemas.intake import IntakeSessionCreate, IntakeAnswerUpsert, IntakeSessionOut, IntakeAnswerOut

router = APIRouter(tags=["intake"])

def _session_out(s: IntakeSession) -> IntakeSessionOut:
    return IntakeSessionOut(
        id=s.id, patient_id=s.patient_id, questionnaire_id=s.questionnaire_id,
        language=s.language, status=s.status, started_at=s.started_at,
        completed_at=s.completed_at,
        answers=[IntakeAnswerOut(question_id=a.question_id,
                                 value=json.loads(a.value_json),
                                 source=a.source, confidence=a.confidence,
                                 updated_at=a.updated_at) for a in s.answers],
    )

@router.post("/patients/{patient_id}/intake-sessions", response_model=IntakeSessionOut)
def create_session(patient_id: str, payload: IntakeSessionCreate, db: Session = Depends(get_db)):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")
    existing = (db.query(IntakeSession)
                  .filter_by(patient_id=patient_id, status="in_progress")
                  .order_by(IntakeSession.started_at.desc())
                  .first())
    if existing:
        return _session_out(existing)
    s = IntakeSession(
        id=str(uuid4()), patient_id=patient_id,
        questionnaire_id="gm_v1", language=payload.language,
    )
    db.add(s); db.commit(); db.refresh(s)
    return _session_out(s)

@router.get("/intake-sessions/{session_id}", response_model=IntakeSessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)):
    s = db.get(IntakeSession, session_id)
    if not s:
        raise HTTPException(404, "session not found")
    return _session_out(s)

@router.put("/intake-sessions/{session_id}/answers/{question_id}", response_model=IntakeSessionOut)
def upsert_answer(session_id: str, question_id: str, payload: IntakeAnswerUpsert,
                  db: Session = Depends(get_db)):
    s = db.get(IntakeSession, session_id)
    if not s:
        raise HTTPException(404, "session not found")
    a = (db.query(IntakeAnswer)
           .filter_by(session_id=session_id, question_id=question_id).first())
    if a is None:
        a = IntakeAnswer(
            id=str(uuid4()), session_id=session_id, question_id=question_id,
            value_json=json.dumps(payload.value),
            source=payload.source, confidence=payload.confidence,
        )
        db.add(a)
    else:
        a.value_json = json.dumps(payload.value)
        a.source = payload.source
        a.confidence = payload.confidence
    db.commit(); db.refresh(s)
    return _session_out(s)

@router.post("/intake-sessions/{session_id}/complete", response_model=IntakeSessionOut)
def complete_session(session_id: str, db: Session = Depends(get_db)):
    s = db.get(IntakeSession, session_id)
    if not s:
        raise HTTPException(404, "session not found")
    s.status = "completed"
    s.completed_at = datetime.utcnow()
    db.commit(); db.refresh(s)
    return _session_out(s)