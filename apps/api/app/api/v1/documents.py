import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document, DocumentPage
from app.models.patient import Patient
from app.services.document_ai import classify, run_ocr
from app.services.ocr_verifier import verify_ocr

log = logging.getLogger("medigraph.document")
router = APIRouter(prefix="/documents", tags=["documents"])

STORAGE_ROOT = Path("data/samples")
ALLOWED = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}


@router.post("/upload")
async def upload_document(
    patient_id: str = Form(...),
    language: str = Form("en"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Fast upload: OCR only. Use /documents/{id}/verify for the AI layer."""
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(404, "patient not found")
    if file.content_type not in ALLOWED:
        raise HTTPException(415, "unsupported content-type: " + str(file.content_type))

    doc_id = str(uuid.uuid4())
    suffix = Path(file.filename or "document").suffix or ".bin"
    patient_dir = STORAGE_ROOT / patient_id
    patient_dir.mkdir(parents=True, exist_ok=True)
    stored_path = patient_dir / (doc_id + suffix)

    raw = await file.read()
    stored_path.write_bytes(raw)
    log.info("stored %s (%d bytes)", stored_path, len(raw))

    regions = []
    text = ""
    mean_conf = None

    try:
        if file.content_type.startswith("image/"):
            regions = run_ocr(str(stored_path), lang=language)
            text = " ".join(r["text"] for r in regions).strip()
            if regions:
                mean_conf = sum(r["confidence"] for r in regions) / len(regions)
            log.info("ocr: %d regions, %d chars", len(regions), len(text))
        else:
            log.info("pdf upload: OCR deferred")
    except Exception as e:
        log.exception("ocr failed: %s", e)

    doc_type = classify(text)
    log.info("classified as: %s", doc_type)

    doc = Document(
        id=doc_id,
        patient_id=patient_id,
        filename=file.filename or "document",
        stored_path=str(stored_path),
        content_type=file.content_type,
        size_bytes=len(raw),
        document_type=doc_type,
        language=language,
        ocr_text=text,
        page_count=1,
        verified_text="",
        verified_json="{}",
        verified_confidence=None,
        needs_review=False,
    )
    db.add(doc)
    db.add(DocumentPage(
        id=str(uuid.uuid4()),
        document_id=doc_id,
        page_number=1,
        text=text,
        regions_json=json.dumps(regions, ensure_ascii=False),
        mean_confidence=mean_conf,
    ))
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "language": doc.language,
        "size_bytes": doc.size_bytes,
        "mean_confidence": mean_conf,
        "text": text,
        "regions": regions,
        "verified_text": "",
        "verified": None,
        "verified_confidence": None,
        "needs_review": False,
    }


@router.post("/{document_id}/verify")
def verify_document(document_id: str, db: Session = Depends(get_db)):
    """Run the local LLM verifier on an existing document."""
    d = db.get(Document, document_id)
    if not d:
        raise HTTPException(404, "document not found")
    if not d.pages:
        raise HTTPException(400, "document has no pages to verify")

    regions = json.loads(d.pages[0].regions_json or "[]")
    if not regions:
        raise HTTPException(400, "no OCR regions to verify")

    log.info("manual verify requested for %s (%d regions)", document_id, len(regions))
    verified = verify_ocr(regions, document_type=d.document_type, language=d.language)
    if not verified:
        raise HTTPException(500, "verifier failed or is not available")

    d.verified_text = verified.get("verified_text", "")
    d.verified_json = json.dumps(verified, ensure_ascii=False)
    d.verified_confidence = verified.get("overall_confidence")
    d.needs_review = bool(verified.get("needs_human_review", False))
    db.commit()
    db.refresh(d)

    return {
        "document_id": d.id,
        "verified_text": d.verified_text,
        "verified_confidence": d.verified_confidence,
        "needs_review": d.needs_review,
        "verified": verified,
    }


@router.get("")
def list_documents(patient_id: str, db: Session = Depends(get_db)):
    docs = (
        db.query(Document)
        .filter_by(patient_id=patient_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "language": d.language,
            "size_bytes": d.size_bytes,
            "uploaded_at": d.uploaded_at,
            "page_count": d.page_count,
            "needs_review": d.needs_review,
            "verified_confidence": d.verified_confidence,
        }
        for d in docs
    ]


@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    d = db.get(Document, document_id)
    if not d:
        raise HTTPException(404, "document not found")
    pages = [
        {
            "page": pg.page_number,
            "text": pg.text,
            "mean_confidence": pg.mean_confidence,
            "regions": json.loads(pg.regions_json or "[]"),
        }
        for pg in d.pages
    ]
    verified = None
    if d.verified_json and d.verified_json != "{}":
        try:
            verified = json.loads(d.verified_json)
        except Exception:
            verified = None
    file_url = None
    if d.stored_path:
        import os as _os
        rel = _os.path.basename(d.stored_path)
        file_url = f"/samples/{d.patient_id}/{rel}"

    return {
        "id": d.id,
        "patient_id": d.patient_id,
        "filename": d.filename,
        "document_type": d.document_type,
        "language": d.language,
        "size_bytes": d.size_bytes,
        "uploaded_at": d.uploaded_at,
        "verified_text": d.verified_text,
        "verified_confidence": d.verified_confidence,
        "needs_review": d.needs_review,
        "verified": verified,
        "file_url": file_url,
        "pages": pages,
    }

@router.delete("/{document_id}")
def delete_document(document_id: str, actor: str = "clinician",
                    db: Session = Depends(get_db)):
    """Delete a document and cascade: pages, facts, timeline rebuild, file on disk."""
    from app.models.fact import ClinicalFact
    from app.models.timeline import TimelineEvent
    from app.services.timeline_builder import build_timeline
    from app.services import audit
    import os as _os

    d = db.get(Document, document_id)
    if not d:
        raise HTTPException(404, "document not found")

    patient_id = d.patient_id
    stored_path = d.stored_path
    filename = d.filename

    # 1. Delete pages
    pages_deleted = db.query(DocumentPage).filter_by(document_id=document_id).delete()

    # 2. Delete extracted facts
    facts_deleted = db.query(ClinicalFact).filter_by(document_id=document_id).delete()

    # 3. Delete the document row itself
    db.delete(d)
    db.commit()

    # 4. Delete the physical file (best effort)
    file_deleted = False
    if stored_path:
        try:
            if _os.path.exists(stored_path):
                _os.unlink(stored_path)
                file_deleted = True
        except OSError as e:
            log.warning("could not delete file %s: %s", stored_path, e)

    # 5. Rebuild timeline so this document's events are gone
    timeline_count = 0
    try:
        events = build_timeline(patient_id, db)
        timeline_count = len(events)
    except Exception as e:
        log.warning("timeline rebuild failed after delete: %s", e)

    audit.record(
        db, action="document.delete", actor=actor, patient_id=patient_id,
        resource_type="Document", resource_id=document_id,
        details={
            "filename": filename,
            "pages_deleted": pages_deleted,
            "facts_deleted": facts_deleted,
            "file_deleted": file_deleted,
            "timeline_events_remaining": timeline_count,
        },
    )

    return {
        "deleted": True,
        "document_id": document_id,
        "filename": filename,
        "pages_deleted": pages_deleted,
        "facts_deleted": facts_deleted,
        "file_deleted": file_deleted,
        "timeline_events_remaining": timeline_count,
    }


@router.post("/{document_id}/process")
def process_document(document_id: str, actor: str = "system",
                     db: Session = Depends(get_db)):
    """Full pipeline for one document:
       verify (AI) -> extract facts -> rebuild timeline -> generate AI clinical summary.
    Idempotent: safe to call again.
    """
    import json as _json
    from app.models.fact import ClinicalFact
    from app.models.timeline import TimelineEvent
    from app.services.entity_extractor import extract_all
    from app.services.timeline_builder import build_timeline
    from app.services.ocr_verifier import verify_ocr
    from app.services.clinical_summary_generator import generate_narrative
    from app.models.summary_draft import SummaryDraft
    from app.services import audit
    import uuid as _uuid

    d = db.get(Document, document_id)
    if not d:
        raise HTTPException(404, "document not found")

    steps = {}

    # 1. AI verification (skip if already done)
    if not d.verified_text or d.verified_json == "{}":
        try:
            regions = []
            if d.pages:
                regions = _json.loads(d.pages[0].regions_json or "[]")
            if regions:
                v = verify_ocr(regions, document_type=d.document_type,
                               language=d.language or "en")
                if v:
                    d.verified_text = v.get("verified_text", "")
                    d.verified_json = _json.dumps(v, ensure_ascii=False)
                    d.verified_confidence = v.get("overall_confidence")
                    d.needs_review = bool(v.get("needs_human_review", False))
                    db.commit()
                    steps["verify"] = "done"
                else:
                    steps["verify"] = "skipped_no_result"
            else:
                steps["verify"] = "skipped_no_regions"
        except Exception as e:
            log.exception("auto-verify failed")
            steps["verify"] = f"error: {e}"
    else:
        steps["verify"] = "already_done"

    # 2. Extract facts (delete old ones for this doc)
    try:
        db.query(ClinicalFact).filter_by(document_id=document_id).delete()
        text = d.verified_text or d.ocr_text or ""
        extracted = extract_all(text)
        for f in extracted:
            fact = ClinicalFact(
                id=str(_uuid.uuid4()),
                patient_id=d.patient_id,
                document_id=document_id,
                kind=f["kind"],
                label=f["label"],
                value=f["value"],
                unit=f.get("unit"),
                normalized_json=_json.dumps(f.get("normalized", {}), ensure_ascii=False),
                source_text=f.get("source_text", ""),
                confidence=f.get("confidence", 0.0),
                needs_review=f.get("needs_review", False),
                fact_date=f.get("fact_date"),
            )
            db.add(fact)
        db.commit()
        steps["extract"] = f"{len(extracted)} facts"
    except Exception as e:
        log.exception("auto-extract failed")
        steps["extract"] = f"error: {e}"

    # 3. Rebuild timeline
    try:
        events = build_timeline(d.patient_id, db)
        steps["timeline"] = f"{len(events)} events"
    except Exception as e:
        log.exception("timeline rebuild failed")
        steps["timeline"] = f"error: {e}"

    # 4. Generate AI clinical summary
    try:
        result = generate_narrative(d.patient_id, db)
        # Save as a summary draft
        prev = (
            db.query(SummaryDraft)
            .filter_by(patient_id=d.patient_id)
            .order_by(SummaryDraft.version.desc())
            .first()
        )
        next_ver = (prev.version + 1) if prev else 1

        section = [{
            "key": "narrative",
            "title": "Clinical Note (AI-generated)",
            "items": [{
                "event_id": "narrative",
                "text": result["narrative"],
                "confidence": 1.0,
                "source": "ai",
                "needs_review": False,
                "verification_status": "pending",
                "warnings": [],
            }],
        }]

        draft = SummaryDraft(
            id=str(_uuid.uuid4()),
            patient_id=d.patient_id,
            version=next_ver,
            sections_json=_json.dumps(section, ensure_ascii=False),
            notes=f"AI-generated narrative via {result.get('model','?')} (auto)",
            actor=actor,
            status="ai_generated",
        )
        db.add(draft)
        db.commit()
        steps["summary"] = f"draft v{next_ver} via {result.get('model')}"
    except Exception as e:
        log.exception("auto-summary failed")
        steps["summary"] = f"error: {e}"

    audit.record(
        db, action="document.process", actor=actor, patient_id=d.patient_id,
        resource_type="Document", resource_id=document_id,
        details=steps,
    )

    return {
        "document_id": document_id,
        "patient_id": d.patient_id,
        "steps": steps,
    }
