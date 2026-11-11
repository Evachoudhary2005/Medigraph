"""Build a provenance-linked timeline from facts + intake answers.

Rules:
- Every event keeps its source (intake / voice / document) and confidence.
- Conflicting entries (same kind+label, different values, from different sources)
  are kept side by side and share a conflict_group id. Nothing is silently merged.
- Undated events are still stored; they sort to the end.
"""
from __future__ import annotations

import json
import logging
import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.fact import ClinicalFact
from app.models.intake import IntakeSession
from app.models.timeline import TimelineEvent

log = logging.getLogger("medigraph.timeline")


def _fact_to_event(f: ClinicalFact, doc_dates: dict) -> dict:
    # Inherit the document's date if this fact has none
    event_date = f.fact_date
    if event_date is None and f.document_id:
        event_date = doc_dates.get(f.document_id)
    return {
        "kind": f.kind,
        "label": f.label,
        "value": f.value or "",
        "normalized": json.loads(f.normalized_json or "{}"),
        "source": "document",
        "source_ref": f.document_id or "",
        "source_excerpt": f.source_text or "",
        "confidence": float(f.confidence or 0.0),
        "needs_review": bool(f.needs_review),
        "event_date": event_date,
    }


def _answer_to_event(session: IntakeSession, answer) -> dict:
    try:
        val = json.loads(answer.value_json)
    except Exception:
        val = answer.value_json
    if isinstance(val, (list, dict)):
        val_str = json.dumps(val, ensure_ascii=False)
    else:
        val_str = str(val) if val is not None else ""
    return {
        "kind": "intake_answer",
        "label": answer.question_id,
        "value": val_str,
        "normalized": {},
        "source": "voice" if (answer.source or "").lower() == "voice" else "intake",
        "source_ref": session.id,
        "source_excerpt": "",
        "confidence": float(answer.confidence) if answer.confidence is not None else 0.9,
        "needs_review": False,
        "event_date": session.started_at,
    }


def build_timeline(patient_id: str, db: Session) -> list[TimelineEvent]:
    # Clear prior events for this patient (idempotent rebuild)
    db.query(TimelineEvent).filter_by(patient_id=patient_id).delete()

    raw_events: list[dict] = []

    # First pass: collect the earliest date per document
    facts = db.query(ClinicalFact).filter_by(patient_id=patient_id).all()
    doc_dates = {}
    for f in facts:
        if f.document_id and f.fact_date:
            cur = doc_dates.get(f.document_id)
            if cur is None or f.fact_date < cur:
                doc_dates[f.document_id] = f.fact_date

    for f in facts:
        raw_events.append(_fact_to_event(f, doc_dates))

    for s in db.query(IntakeSession).filter_by(patient_id=patient_id).all():
        for a in s.answers:
            raw_events.append(_answer_to_event(s, a))

    # Detect conflicts: same (kind,label), different values, different sources
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for e in raw_events:
        groups[(e["kind"], e["label"])].append(e)

    conflict_map: dict[int, str] = {}
    for _, group in groups.items():
        if len(group) < 2:
            continue
        values = {str(e["value"]) for e in group if e["value"]}
        sources = {e["source"] for e in group}
        if len(values) > 1 and len(sources) > 1:
            cg = str(uuid.uuid4())
            for e in group:
                conflict_map[id(e)] = cg

    created: list[TimelineEvent] = []
    for e in raw_events:
        cg = conflict_map.get(id(e))
        ev = TimelineEvent(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            event_date=e["event_date"],
            kind=e["kind"],
            label=e["label"],
            value=e["value"],
            normalized_json=json.dumps(e["normalized"], ensure_ascii=False),
            source=e["source"],
            source_ref=e["source_ref"] or "",
            source_excerpt=e["source_excerpt"] or "",
            confidence=e["confidence"],
            needs_review=bool(e["needs_review"]) or cg is not None,
            verification_status="conflicting" if cg else "pending",
            conflict_group=cg,
        )
        db.add(ev)
        created.append(ev)

    db.commit()
    for ev in created:
        db.refresh(ev)
    log.info("timeline built for %s: %d events, %d conflict groups",
             patient_id, len(created), len(set(conflict_map.values())))
    return created