"""Evaluate the entity extractor against a hand-labeled ground truth.

Usage:
    python scripts/evaluate.py

Reads:
    data/eval/ground_truth.csv     - hand-labeled expected facts
    apps/api/medigraph.db          - live extraction results

Writes:
    data/eval/report.json          - full per-entity metrics
    stdout                         - precision / recall / F1 table

Ground truth CSV format (columns required):
    document_id, kind, label, value
  One row per expected fact.
    document_id : the Document UUID from the database
    kind        : medication | demographic | date | investigation
    label       : normalized label (e.g. "Metoprolol", "age", "issue_date")
    value       : expected value string
"""
from __future__ import annotations

import csv
import json
import os
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "apps" / "api" / "medigraph.db"
GT_PATH = ROOT / "data" / "eval" / "ground_truth.csv"
OUT_PATH = ROOT / "data" / "eval" / "report.json"


def load_ground_truth() -> list[dict]:
    if not GT_PATH.exists():
        print(f"Ground truth not found at {GT_PATH}", file=sys.stderr)
        print("Create it with columns: document_id,kind,label,value", file=sys.stderr)
        print("One row per expected fact.", file=sys.stderr)
        return []
    with GT_PATH.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_extracted(document_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT kind, label, value FROM clinical_facts WHERE document_id=?",
            (document_id,),
        ).fetchall()
        return [{"kind": r[0], "label": r[1], "value": r[2]} for r in rows]
    finally:
        conn.close()


def _norm(s: str) -> str:
    import re as _re
    s = (s or "").strip().lower()
    s = _re.sub(r"(\d+)\.0+(?=\D|$)", r"\1", s)
    s = _re.sub(r"\s+", " ", s)
    return s


def match(expected: dict, actual: dict) -> bool:
    if _norm(expected["kind"]) != _norm(actual["kind"]):
        return False
    if _norm(expected["label"]) != _norm(actual["label"]):
        return False
    ev = _norm(expected["value"])
    av = _norm(actual["value"])
    # Accept either exact or substring match on value
    return ev == av or ev in av or av in ev


def prf1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 3), round(r, 3), round(f1, 3)


def evaluate() -> dict:
    gt = load_ground_truth()
    if not gt:
        return {}

    by_doc: dict[str, list[dict]] = defaultdict(list)
    for row in gt:
        by_doc[row["document_id"]].append(row)

    per_kind: dict[str, dict] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    details: list[dict] = []

    for doc_id, expected_list in by_doc.items():
        actual_list = load_extracted(doc_id)
        consumed = set()

        for exp in expected_list:
            hit = False
            for idx, act in enumerate(actual_list):
                if idx in consumed:
                    continue
                if match(exp, act):
                    per_kind[exp["kind"]]["tp"] += 1
                    consumed.add(idx)
                    hit = True
                    break
            if not hit:
                per_kind[exp["kind"]]["fn"] += 1
                details.append({"doc": doc_id, "status": "missing", "expected": exp})

        for idx, act in enumerate(actual_list):
            if idx not in consumed:
                per_kind[act["kind"]]["fp"] += 1
                details.append({"doc": doc_id, "status": "extra", "actual": act})

    # Aggregate
    rows = []
    total = {"tp": 0, "fp": 0, "fn": 0}
    for kind, c in per_kind.items():
        p, r, f1 = prf1(c["tp"], c["fp"], c["fn"])
        rows.append({
            "kind": kind,
            "tp": c["tp"], "fp": c["fp"], "fn": c["fn"],
            "precision": p, "recall": r, "f1": f1,
        })
        total["tp"] += c["tp"]
        total["fp"] += c["fp"]
        total["fn"] += c["fn"]

    tp, fp, fn = total["tp"], total["fp"], total["fn"]
    p, r, f1 = prf1(tp, fp, fn)
    rows.append({
        "kind": "ALL",
        "tp": tp, "fp": fp, "fn": fn,
        "precision": p, "recall": r, "f1": f1,
    })

    report = {
        "documents_evaluated": len(by_doc),
        "metrics": rows,
        "details": details,
    }
    return report


def print_table(report: dict) -> None:
    print()
    print(f"Evaluation on {report.get('documents_evaluated', 0)} document(s)")
    print()
    print(f"{'kind':16} {'TP':>4} {'FP':>4} {'FN':>4} {'prec':>7} {'rec':>7} {'f1':>7}")
    print("-" * 60)
    for row in report["metrics"]:
        print(f"{row['kind']:16} {row['tp']:>4} {row['fp']:>4} {row['fn']:>4} "
              f"{row['precision']:>7.3f} {row['recall']:>7.3f} {row['f1']:>7.3f}")
    print()


def main() -> int:
    report = evaluate()
    if not report:
        print("Nothing to evaluate. Add rows to data/eval/ground_truth.csv first.")
        return 1
    print_table(report)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Full report written to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())