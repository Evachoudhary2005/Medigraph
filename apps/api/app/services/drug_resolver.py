"""LLM-assisted drug brand → generic resolution.

Order: dictionary -> cache -> LLM. LLM results are cached to disk.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from app.data.drugs import lookup

log = logging.getLogger("medigraph.drug_resolver")

CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "drug_cache.json"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "medgemma:4b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False),
                          encoding="utf-8")


DRUG_RESOLVE_SYSTEM = """You are a clinical pharmacologist.

TASK: Given a list of drug brand names (possibly with OCR errors), return the generic (INN) name of each.

RULES:
1. Use medical knowledge. Examples:
   Betaloc -> Metoprolol; Oxprelol/Oxprenolol -> Oxprenolol
   Dorzolamidum -> Dorzolamide; 201calm -> Etizolam; Clonelst -> Clonazepam
   Crocin/Dolo -> Paracetamol; Glycomet -> Metformin
2. Certain match: confidence 0.8-1.0. Best guess: 0.4-0.7. No idea: null, 0.0.
3. Output ONLY JSON: {"results":[{"input":"...","generic":"...","class":"...","confidence":0.0}]}
"""


def _resolve_with_llm(unknown_brands: list[str]) -> dict[str, dict]:
    if not unknown_brands:
        return {}
    try:
        import ollama
    except ImportError:
        log.warning("ollama not installed")
        return {}

    user = "Identify the generic name of each drug brand:\n" + \
           "\n".join(f"- {b}" for b in unknown_brands)

    try:
        client = ollama.Client(host=OLLAMA_HOST, timeout=180)
        resp = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": DRUG_RESOLVE_SYSTEM},
                {"role": "user", "content": user},
            ],
            format="json",
            options={"temperature": 0},
        )
        raw = resp["message"]["content"] if isinstance(resp, dict) else resp.message.content
        raw = (raw or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw or "{}")
        out: dict[str, dict] = {}
        for r in data.get("results", []):
            key = (r.get("input") or "").strip().lower()
            if not key:
                continue
            out[key] = {
                "generic": r.get("generic"),
                "class": r.get("class"),
                "confidence": float(r.get("confidence") or 0.0),
            }
        log.info("llm resolved %d/%d brands", len(out), len(unknown_brands))
        return out
    except Exception as e:
        log.exception("llm drug resolve failed: %s", e)
        return {}


def resolve_many(brands: list[str]) -> dict[str, dict]:
    cache = _load_cache()
    results: dict[str, dict] = {}
    unknown: list[str] = []

    for b in brands:
        if not b:
            continue
        key = b.strip().lower()
        hit = lookup(b)
        if hit:
            results[key] = {"generic": hit["generic"], "class": hit.get("class"),
                            "confidence": 0.95, "source": "dictionary"}
        elif key in cache:
            c = cache[key]
            results[key] = {"generic": c.get("generic"), "class": c.get("class"),
                            "confidence": c.get("confidence", 0.5), "source": "cache"}
        else:
            unknown.append(b)

    if unknown:
        llm_results = _resolve_with_llm(unknown)
        for b in unknown:
            key = b.strip().lower()
            r = llm_results.get(key)
            if r and r.get("generic"):
                results[key] = {"generic": r["generic"], "class": r.get("class"),
                                "confidence": r.get("confidence", 0.5),
                                "source": "llm"}
                cache[key] = r
            else:
                results[key] = {"generic": b, "class": None,
                                "confidence": 0.4, "source": "unknown"}
        _save_cache(cache)

    return results