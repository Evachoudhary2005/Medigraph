import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fact import ClinicalFact
from app.models.document import Document
from app.services.entity_extractor import extract_all

router = APIRouter(prefix="/facts", tags=["facts"])


def _out(f: ClinicalFact) -> dict:
    return {
        "id": f.id, "kind": f.kind, "label": f.label, "value": f.value,
        "unit": f.unit,
        "normalized": json.loads(f.normalized_json or "{}"),
        "source_text": f.source_text, "confidence": f.confidence,
        "needs_review": f.needs_review,
        "verification_status": f.verification_status,
        "document_id": f.document_id,
        "fact_date": f.fact_date, "created_at": f.created_at,
    }


@router.post("/extract/{document_id}")
def extract_from_document(document_id: str, db: Session = Depends(get_db)):
    d = db.get(Document, document_id)
    if not d:
        raise HTTPException(404, "document not found")
    text = d.verified_text or d.ocr_text
    if not text:
        raise HTTPException(400, "document has no text")

    db.query(ClinicalFact).filter_by(document_id=document_id).delete()

    extracted = extract_all(text)

    # Propagate the document's date to every fact from this document,
    # so the timeline groups them together chronologically.
    doc_date = None
    for f in extracted:
        if f.get("kind") == "date" and f.get("fact_date"):
            doc_date = f["fact_date"]
            break

    created = []
    for f in extracted:
        fact = ClinicalFact(
            id=str(uuid.uuid4()), patient_id=d.patient_id,
            document_id=document_id, kind=f["kind"], label=f["label"],
            value=f["value"], unit=f.get("unit"),
            normalized_json=json.dumps(f.get("normalized", {}), ensure_ascii=False),
            source_text=f.get("source_text", ""),
            confidence=f.get("confidence", 0.0),
            needs_review=f.get("needs_review", False),
            fact_date=f.get("fact_date") or doc_date,
        )
        db.add(fact)
        created.append(fact)
    db.commit()
    return {"document_id": document_id, "count": len(created),
            "facts": [_out(f) for f in created]}


@router.get("")
def list_facts(patient_id: str, kind: str | None = None,
               db: Session = Depends(get_db)):
    q = db.query(ClinicalFact).filter_by(patient_id=patient_id)
    if kind:
        q = q.filter_by(kind=kind)
    return [_out(f) for f in q.order_by(ClinicalFact.created_at.desc()).all()]


@router.post("/{fact_id}/verify")
def verify_fact(fact_id: str, action: str = "approve",
                db: Session = Depends(get_db)):
    f = db.get(ClinicalFact, fact_id)
    if not f:
        raise HTTPException(404, "fact not found")
    f.verification_status = "verified" if action == "approve" else "rejected"
    db.commit()
    return _out(f)