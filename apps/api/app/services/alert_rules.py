"""Deterministic red-flag alert rules.

Rules are literal (kind,label,value) patterns over timeline events.
No ML. No ambiguity. Auditable.

Each rule:
  id: string
  name: short human label
  severity: "urgent" | "caution" | "info"
  description: what the flag means
  match_any: list of match conditions (event label contains X and value contains Y)
  min_matches: how many distinct conditions must be present
  source_hint: brief clinician-facing explanation
"""
from __future__ import annotations

RULES: list[dict] = [
    {
        "id": "cardiac_chest_pain",
        "name": "Possible acute coronary event",
        "severity": "urgent",
        "description": "Chest pain with sweating or breathlessness - rule out ACS.",
        "match_any": [
            {"label_contains": "chest", "value_contains": "pain"},
            {"label_contains": "chest", "value_contains": "pressure"},
            {"label_contains": "sweating"},
            {"label_contains": "breathless"},
            {"label_contains": "dyspnea"},
            {"label_contains": "shortness of breath"},
        ],
        "min_matches": 2,
        "source_hint": "Combination suggests a cardiac red flag.",
    },
    {
        "id": "stroke_like",
        "name": "Possible stroke / TIA",
        "severity": "urgent",
        "description": "Sudden weakness, slurred speech, or facial droop.",
        "match_any": [
            {"label_contains": "weakness"},
            {"label_contains": "slurred"},
            {"label_contains": "facial droop"},
            {"label_contains": "vision loss"},
            {"label_contains": "numbness"},
            {"label_contains": "paralysis"},
        ],
        "min_matches": 2,
        "source_hint": "Neurological red flags.",
    },
    {
        "id": "sepsis_like",
        "name": "Possible sepsis / serious infection",
        "severity": "urgent",
        "description": "High fever with confusion, hypotension, or rapid breathing.",
        "match_any": [
            {"label_contains": "fever", "value_contains": "high"},
            {"label_contains": "fever", "value_contains": "> 39"},
            {"label_contains": "confusion"},
            {"label_contains": "rigors"},
            {"label_contains": "hypotension"},
            {"label_contains": "tachycardia"},
        ],
        "min_matches": 2,
        "source_hint": "Systemic infection red flags.",
    },
    {
        "id": "gi_bleed",
        "name": "Possible gastrointestinal bleed",
        "severity": "urgent",
        "description": "Vomiting blood, black stools, or severe abdominal pain.",
        "match_any": [
            {"label_contains": "vomiting", "value_contains": "blood"},
            {"label_contains": "hematemesis"},
            {"label_contains": "melena"},
            {"label_contains": "black stools"},
            {"label_contains": "abdominal pain", "value_contains": "severe"},
        ],
        "min_matches": 1,
        "source_hint": "GI bleeding red flags.",
    },
    {
        "id": "respiratory_distress",
        "name": "Respiratory distress",
        "severity": "caution",
        "description": "Breathlessness with cough or low oxygen.",
        "match_any": [
            {"label_contains": "breathless"},
            {"label_contains": "dyspnea"},
            {"label_contains": "cough"},
            {"label_contains": "wheeze"},
            {"label_contains": "spo2", "value_contains": "<"},
        ],
        "min_matches": 2,
        "source_hint": "Respiratory caution.",
    },
    {
        "id": "suicidal_ideation",
        "name": "Suicidal ideation",
        "severity": "urgent",
        "description": "Any mention of self-harm or suicidal thoughts.",
        "match_any": [
            {"label_contains": "suicid"},
            {"value_contains": "suicid"},
            {"value_contains": "self harm"},
            {"value_contains": "end my life"},
        ],
        "min_matches": 1,
        "source_hint": "Immediate mental-health referral required.",
    },
    {
        "id": "pregnancy_alert",
        "name": "Pregnancy with red flags",
        "severity": "caution",
        "description": "Pregnancy status with bleeding or severe pain.",
        "match_any": [
            {"label_contains": "pregnan", "value_contains": "yes"},
            {"label_contains": "pregnan", "value_contains": "positive"},
            {"label_contains": "vaginal bleeding"},
            {"label_contains": "severe abdominal pain"},
        ],
        "min_matches": 2,
        "source_hint": "Obstetric caution.",
    },
]


def _event_matches(event: dict, cond: dict) -> bool:
    """Match against the whole event text (label + value + excerpt).

    `label_contains` and `value_contains` both search the combined haystack,
    because a clinician reading the timeline sees them as one statement.
    """
    label = (event.get("label") or "").lower()
    value = str(event.get("value") or "").lower()
    excerpt = (event.get("source_excerpt") or "").lower()
    haystack = label + " " + value + " " + excerpt

    if "label_contains" in cond:
        if cond["label_contains"].lower() not in haystack:
            return False
    if "value_contains" in cond:
        if cond["value_contains"].lower() not in haystack:
            return False
    if "any_text_contains" in cond:
        if cond["any_text_contains"].lower() not in haystack:
            return False
    return True


def evaluate(events: list[dict]) -> list[dict]:
    """Return a list of triggered alerts, each with the evidence events."""
    fired: list[dict] = []
    for rule in RULES:
        matched: list[dict] = []
        for cond in rule["match_any"]:
            for e in events:
                if _event_matches(e, cond) and e not in matched:
                    matched.append(e)
                    break
        if len(matched) >= rule.get("min_matches", 1):
            fired.append({
                "rule_id": rule["id"],
                "name": rule["name"],
                "severity": rule["severity"],
                "description": rule["description"],
                "source_hint": rule["source_hint"],
                "evidence": [
                    {
                        "event_id": e.get("id"),
                        "label": e.get("label"),
                        "value": e.get("value"),
                        "source": e.get("source"),
                        "confidence": e.get("confidence"),
                    }
                    for e in matched
                ],
            })
    # Urgent first
    fired.sort(key=lambda a: {"urgent": 0, "caution": 1, "info": 2}.get(a["severity"], 3))
    return fired