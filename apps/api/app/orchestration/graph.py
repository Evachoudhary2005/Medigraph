"""LangGraph state machine for the MediGraph clinical pipeline.

Nodes:
    extract  -> run OCR + AI verification on a document (or skip if none)
    validate -> decide whether to accept or route to human review
    timeline -> build the provenance-linked timeline
    summarize-> build the evidence-linked draft
    alerts   -> run the deterministic rule engine
    fhir     -> produce the FHIR R4 bundle
    review   -> pause point for low-confidence data
    finalize -> exit

Conditional edges:
    after `validate`: if confidence >= 0.8 and no low-conf meds -> timeline
                      else -> review (human-in-the-loop)
    after `review`:   -> timeline (approver clicked proceed) or -> finalize
"""
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from app.orchestration.state import PipelineState
from app.services.alert_rules import evaluate as evaluate_alerts
from app.services.entity_extractor import extract_all
from app.services.summary_builder import build_draft
from app.services.document_ai import classify, run_ocr
from app.services.ocr_verifier import verify_ocr

log = logging.getLogger("medigraph.graph")

CONFIDENCE_THRESHOLD = 0.8


# ---------- node implementations ----------

def node_extract(state: PipelineState) -> dict:
    """Run OCR + AI verification if a document is present, else skip."""
    log.info("graph: extract")
    update: dict = {"stage": "extract", "log": ["started extract"]}

    doc_id = state.get("document_id")
    if not doc_id:
        update["verified"] = None
        update["ocr_text"] = ""
        update["confidence"] = 1.0
        update["needs_review"] = False
        return update

    from app.db.session import SessionLocal
    from app.models.document import Document
    from app.models.fact import ClinicalFact
    import uuid as _uuid
    import json as _j

    db = SessionLocal()
    try:
        d = db.get(Document, doc_id)
        if not d:
            update["errors"] = [f"document {doc_id} not found"]
            return update

        text = d.verified_text or d.ocr_text or ""
        if not text:
            # run OCR now
            regions = run_ocr(d.stored_path, lang=d.language or "en")
            text = " ".join(r["text"] for r in regions).strip()
            update["ocr_regions"] = regions

        update["ocr_text"] = text
        update["document_type"] = d.document_type or classify(text)

        # AI verification (cached if it was already run via /verify endpoint)
        if d.verified_json and d.verified_json != "{}":
            verified = _j.loads(d.verified_json)
        else:
            verified = verify_ocr(
                [{"text": text, "confidence": 0.9}],
                document_type=update["document_type"],
                language=d.language or "en",
            ) or {}
            if verified:
                d.verified_text = verified.get("verified_text", text)
                d.verified_json = _j.dumps(verified, ensure_ascii=False)
                d.verified_confidence = verified.get("overall_confidence")
                d.needs_review = bool(verified.get("needs_human_review", False))
                db.commit()

        update["verified"] = verified
        update["confidence"] = float(verified.get("overall_confidence") or 0.9)
        update["needs_review"] = bool(verified.get("needs_human_review", False))

        # Extract entities and save to ClinicalFact
        db.query(ClinicalFact).filter_by(document_id=doc_id).delete()
        extracted = extract_all(text)
        for f in extracted:
            fact = ClinicalFact(
                id=str(_uuid.uuid4()),
                patient_id=d.patient_id,
                document_id=doc_id,
                kind=f["kind"],
                label=f["label"],
                value=f["value"],
                unit=f.get("unit"),
                normalized_json=_j.dumps(f.get("normalized", {}), ensure_ascii=False),
                source_text=f.get("source_text", ""),
                confidence=f.get("confidence", 0.0),
                needs_review=f.get("needs_review", False),
                fact_date=f.get("fact_date"),
            )
            db.add(fact)
        db.commit()
        update["facts"] = extracted
        update["log"] = ["started extract", f"extracted {len(extracted)} clinical entities from {d.filename}"]
    finally:
        db.close()
    return update


def node_validate(state: PipelineState) -> dict:
    """Decide whether confidence is high enough to proceed without human review."""
    log.info("graph: validate")
    conf = state.get("confidence", 1.0)
    needs = state.get("needs_review", False)
    errors = state.get("errors", [])
    low_ok = conf >= CONFIDENCE_THRESHOLD and not needs and not errors
    return {
        "stage": "validate",
        "log": state.get("log", []) + [f"validate: conf={conf:.2f} needs_review={needs} ok={low_ok}"],
    }


def node_review(state: PipelineState) -> dict:
    """Human-in-the-loop pause point. In the API we just mark it."""
    log.info("graph: review (pause)")
    return {
        "stage": "review",
        "human_approved": False,
        "log": state.get("log", []) + ["routed to human review - awaiting clinician"],
    }


def node_timeline(state: PipelineState) -> dict:
    log.info("graph: timeline")
    from app.db.session import SessionLocal
    from app.services.timeline_builder import build_timeline

    pid = state["patient_id"]
    db = SessionLocal()
    try:
        events = build_timeline(pid, db)
        count = len(events)
    finally:
        db.close()
    return {
        "stage": "timeline",
        "timeline_count": count,
        "log": state.get("log", []) + [f"timeline built: {count} events synchronized"],
    }


def node_summarize(state: PipelineState) -> dict:
    log.info("graph: summarize")
    from app.db.session import SessionLocal
    from app.models.timeline import TimelineEvent
    from app.services.clinical_summary_generator import generate_narrative
    from app.models.summary_draft import SummaryDraft
    import uuid as _uuid
    import json as _j

    pid = state["patient_id"]
    db = SessionLocal()
    narrative_text = ""
    draft_id = None
    draft_ver = None
    try:
        rows = db.query(TimelineEvent).filter_by(patient_id=pid).all()
        dicts = [{
            "id": e.id, "event_date": e.event_date.isoformat() if e.event_date else None,
            "kind": e.kind, "label": e.label, "value": e.value,
            "normalized": _j.loads(e.normalized_json or "{}"),
            "source": e.source, "source_ref": e.source_ref,
            "source_excerpt": e.source_excerpt,
            "confidence": e.confidence, "needs_review": e.needs_review,
            "verification_status": e.verification_status,
            "conflict_group": e.conflict_group,
        } for e in rows]
        draft = build_draft(pid, dicts)

        # Synthesize AI clinical narrative note
        try:
            gen_res = generate_narrative(pid, db)
            narrative_text = gen_res.get("narrative", "")
            prev = (
                db.query(SummaryDraft)
                .filter_by(patient_id=pid)
                .order_by(SummaryDraft.version.desc())
                .first()
            )
            draft_ver = (prev.version + 1) if prev else 1
            draft_id = str(_uuid.uuid4())

            section = [{
                "key": "narrative",
                "title": "Clinical Note (AI-generated)",
                "items": [{
                    "event_id": "narrative",
                    "text": narrative_text,
                    "confidence": 1.0,
                    "source": "ai",
                    "needs_review": False,
                    "verification_status": "pending",
                    "warnings": [],
                }],
            }]

            draft_row = SummaryDraft(
                id=draft_id,
                patient_id=pid,
                version=draft_ver,
                sections_json=_j.dumps(section, ensure_ascii=False),
                notes=f"AI-generated narrative via {gen_res.get('model','?')} (orchestrated)",
                actor=state.get("actor", "clinician"),
                status="ai_generated",
            )
            db.add(draft_row)
            db.commit()
        except Exception as ge:
            log.warning("narrative gen error: %s", ge)
    finally:
        db.close()

    new_logs = state.get("log", []) + [f"summary built: {len(draft['sections'])} sections"]
    if draft_ver:
        new_logs.append(f"AI clinical narrative synthesized (v{draft_ver})")

    return {
        "stage": "summarize",
        "summary": draft,
        "narrative": narrative_text,
        "draft_id": draft_id,
        "draft_version": draft_ver,
        "log": new_logs,
    }


def node_alerts(state: PipelineState) -> dict:
    log.info("graph: alerts")
    from app.db.session import SessionLocal
    from app.models.timeline import TimelineEvent
    import json as _j

    pid = state["patient_id"]
    db = SessionLocal()
    try:
        rows = db.query(TimelineEvent).filter_by(patient_id=pid).all()
        dicts = [{
            "id": e.id, "kind": e.kind, "label": e.label, "value": e.value,
            "source": e.source, "source_excerpt": e.source_excerpt,
            "confidence": e.confidence,
        } for e in rows]
        fired = evaluate_alerts(dicts)
    finally:
        db.close()
    return {
        "stage": "alerts",
        "alerts": fired,
        "log": state.get("log", []) + [f"alerts fired: {len(fired)}"],
    }


def node_fhir(state: PipelineState) -> dict:
    log.info("graph: fhir")
    from app.db.session import SessionLocal
    from app.models.patient import Patient
    from app.models.timeline import TimelineEvent
    from app.services.fhir_mapper import build_bundle

    pid = state["patient_id"]
    db = SessionLocal()
    try:
        p = db.get(Patient, pid)
        rows = db.query(TimelineEvent).filter_by(patient_id=pid).all()
        bundle = build_bundle(p, rows) if p else None
    finally:
        db.close()

    issues: list[str] = []
    if bundle:
        if bundle.get("resourceType") != "Bundle":
            issues.append("not a Bundle")
        if not any(e["resource"]["resourceType"] == "Patient"
                   for e in bundle.get("entry", [])):
            issues.append("no Patient resource")
    validation = {"valid": len(issues) == 0, "issues": issues,
                  "entries": len(bundle.get("entry", [])) if bundle else 0}
    return {
        "stage": "fhir",
        "bundle": bundle,
        "validation": validation,
        "log": state.get("log", []) + [f"FHIR bundle: {validation['entries']} entries, valid={validation['valid']}"],
    }


def node_finalize(state: PipelineState) -> dict:
    log.info("graph: finalize")
    from app.services import audit
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        audit.record(
            db, action="pipeline.orchestrate", actor=state.get("actor", "clinician"),
            patient_id=state.get("patient_id"), resource_type="Pipeline",
            details={
                "timeline_count": state.get("timeline_count"),
                "draft_version": state.get("draft_version"),
                "alerts_count": len(state.get("alerts", [])),
            },
        )
    except Exception as e:
        log.warning("audit in finalize failed: %s", e)
    finally:
        db.close()
    return {"stage": "finalize", "log": state.get("log", []) + ["pipeline finalized successfully"]}


# ---------- conditional edges ----------

def route_after_validate(state: PipelineState) -> str:
    conf = state.get("confidence", 1.0)
    needs = state.get("needs_review", False)
    if conf >= CONFIDENCE_THRESHOLD and not needs:
        return "timeline"
    return "review"


def route_after_review(state: PipelineState) -> str:
    """After human review, always continue to timeline (approver clicked)."""
    return "timeline"


# ---------- build the graph ----------

def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("extract", node_extract)
    g.add_node("validate", node_validate)
    g.add_node("review", node_review)
    g.add_node("timeline", node_timeline)
    g.add_node("summarize", node_summarize)
    g.add_node("alerts", node_alerts)
    g.add_node("fhir", node_fhir)
    g.add_node("finalize", node_finalize)

    g.set_entry_point("extract")
    g.add_edge("extract", "validate")
    g.add_conditional_edges("validate", route_after_validate,
                            {"timeline": "timeline", "review": "review"})
    g.add_conditional_edges("review", route_after_review,
                            {"timeline": "timeline"})
    g.add_edge("timeline", "summarize")
    g.add_edge("summarize", "alerts")
    g.add_edge("alerts", "fhir")
    g.add_edge("fhir", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


GRAPH = build_graph()