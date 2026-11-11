"""Deterministic clinical summary builder.

Consumes ONLY normalized timeline events. No LLM. No diagnoses. No advice.
Produces a fixed-schema draft where every statement links to its source event.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


SECTION_ORDER = [
    ("chief_complaint",     "Chief Complaint"),
    ("hpi",                 "History of Present Illness"),
    ("past_history",        "Past Medical and Surgical History"),
    ("medications_allergies","Medications and Allergies"),
    ("family_personal",     "Family and Personal History"),
    ("ros",                 "Review of Systems"),
    ("investigations",      "Investigations"),
    ("demographics",        "Demographics"),
    ("other",               "Other"),
]


# Maps an intake_answers question_id prefix -> section key
QUESTION_PREFIX_TO_SECTION = {
    "q_cc_":   "chief_complaint",
    "q_hpi_":  "hpi",
    "q_pmh_":  "past_history",
    "q_med_":  "medications_allergies",
    "q_fam_":  "family_personal",
    "q_pers_": "family_personal",
    "q_ros_":  "ros",
}


def _section_for(event: dict) -> str:
    kind = (event.get("kind") or "").lower()
    label = (event.get("label") or "").lower()
    if kind == "medication":
        return "medications_allergies"
    if kind == "demographic":
        return "demographics"
    if kind == "date":
        return "other"
    if kind == "investigation":
        return "investigations"
    if kind == "intake_answer":
        for prefix, sec in QUESTION_PREFIX_TO_SECTION.items():
            if label.startswith(prefix):
                return sec
        return "other"
    return "other"


def _statement(event: dict) -> dict:
    """A single line in the summary, with full evidence linkage."""
    label = event.get("label") or ""
    value = event.get("value") or ""
    norm = event.get("normalized") or {}

    # Human-readable text per kind
    if event.get("kind") == "medication":
        parts = [label]
        if norm.get("dose_value") and norm.get("dose_unit"):
            parts.append(f"{norm['dose_value']}{norm['dose_unit']}")
        if norm.get("frequency"):
            parts.append(norm["frequency"])
        if norm.get("duration"):
            parts.append("x " + norm["duration"])
        if norm.get("brand") and norm["brand"].lower() != (label or "").lower():
            parts.append("(brand: " + norm["brand"] + ")")
        text = " ".join(parts)
    elif event.get("kind") == "demographic":
        text = f"{label}: {value}"
    elif event.get("kind") == "date":
        text = f"{label.replace('_', ' ')}: {value}"
    else:
        # intake answer: value may be JSON-encoded
        v = value
        if isinstance(v, str) and v.startswith("["):
            try:
                import json as _j
                v = _j.loads(v)
                v = ", ".join(map(str, v))
            except Exception:
                pass
        # Standard question ids (q_*) show just the value.
        # Custom labels show "label: value" so the reader knows what the value means.
        if label and not label.startswith("q_") and v:
            text = f"{label}: {v}"
        else:
            text = str(v) if v else label
    return {
        "event_id": event.get("id"),
        "text": text,
        "confidence": event.get("confidence", 0.0),
        "source": event.get("source"),
        "needs_review": event.get("needs_review", False),
        "verification_status": event.get("verification_status", "pending"),
        "warnings": [
            norm.get("suspicious_reason")
        ] if norm.get("suspicious_reason") else [],
    }


def build_draft(patient_id: str, events: list[dict]) -> dict:
    """Return a fixed-schema summary with per-line evidence links."""
    sections: dict[str, list[dict]] = {k: [] for k, _ in SECTION_ORDER}

    for e in events:
        sec = _section_for(e)
        sections[sec].append(_statement(e))

    # Sort medications alphabetically; keep others as-is
    sections["medications_allergies"].sort(key=lambda s: (s["text"] or "").lower())
    sections["demographics"].sort(key=lambda s: (s["text"] or "").lower())

    blocks = []
    for key, title in SECTION_ORDER:
        items = sections.get(key, [])
        if not items:
            continue
        blocks.append({
            "key": key,
            "title": title,
            "items": items,
        })

    total_facts = sum(len(b["items"]) for b in blocks)
    low_conf = sum(1 for b in blocks for it in b["items"] if it["confidence"] < 0.7)
    pending_verification = sum(
        1 for b in blocks for it in b["items"]
        if it["verification_status"] not in ("verified", "rejected")
    )

    return {
        "patient_id": patient_id,
        "generated_at": datetime.utcnow().isoformat(),
        "sections": blocks,
        "stats": {
            "total_facts": total_facts,
            "low_confidence": low_conf,
            "pending_verification": pending_verification,
        },
    }