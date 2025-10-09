#!/usr/bin/env python3
"""
score_engine.py
Automated scoring stub + InterventionLog writer + DPIA hook (CLI).

Placement: save as phase2/fraud/score_engine.py

Usage (from repo root):
  python phase2/fraud/score_engine.py --input phase2/sample.json --append-log --fria

Notes:
- DPIA files will be written to phase2/artifacts/evidence by design.
- Uses only stdlib.
"""
import argparse
import json
import os
import hashlib
import datetime
from typing import Dict, Any

ARTIFACT_ID = "fraud_v1"
DEFAULT_MODEL_VERSION = "v0.2"

# Ensure DPIA goes to phase2/artifacts/evidence (relative to this file)
EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# Intervention log resides alongside this script
LOG_PATH = os.path.join(os.path.dirname(__file__), "intervention_log.ndjson")


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


class InterventionLog:
    """Append-only NDJSON log with chaining signature_hash for tamper evidence."""
    def __init__(self, path: str = LOG_PATH):
        self.path = path
        if not os.path.exists(self.path):
            open(self.path, "w").close()

    def _last_signature(self) -> str:
        with open(self.path, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines:
            return ""
        last = json.loads(lines[-1])
        return last.get("signature_hash", "")

    def append(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        entry = dict(entry)
        entry.setdefault("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())
        entry.setdefault("input_hash", sha256_text(json.dumps(entry.get("input", {}), sort_keys=True)))
        entry.setdefault("output_hash", sha256_text(json.dumps(entry.get("output", {}), sort_keys=True)))
        prev_sig = self._last_signature()
        entry["signature_hash"] = sha256_text(prev_sig + entry["input_hash"] + entry["output_hash"])
        required = ["timestamp", "artifact_id", "model_version", "input_hash", "decision_summary",
                    "human_id", "human_reason", "output_hash", "signature_hash"]
        for r in required:
            entry.setdefault(r, "")
        with open(self.path, "a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry


def automated_score(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic heuristic scoring (0..100) + explainable reasons list."""
    score = 0
    reasons = []
    try:
        amount = float(transaction.get("amount", 0))
    except Exception:
        amount = 0
    country = str(transaction.get("country", "unknown"))
    try:
        age = int(transaction.get("age", 30))
    except Exception:
        age = 30
    prev_flag = bool(transaction.get("previous_fraud_flag", False))

    # amount rules
    if amount <= 1000:
        score += 5
    elif amount <= 10000:
        score += 20
    else:
        score += 50
        reasons.append("high_amount")

    # synthetic high-risk country list
    high_risk_countries = {"XYZ", "ABC"}
    if country in high_risk_countries:
        score += 25
        reasons.append("country_high_risk")

    # age edge cases
    if age < 18 or age > 80:
        score += 10
        reasons.append("age_edge")

    # previous fraud flag
    if prev_flag:
        score += 40
        reasons.append("previous_fraud_flag")

    score = max(0, min(100, score))
    return {"score": int(score), "reasons": reasons, "raw": transaction}


def generate_dpia(draft: Dict[str, Any], fria: bool = False) -> Dict[str, Any]:
    """Minimal DPIA/FRIA generator hook. Writes timestamped JSON to EVIDENCE_DIR."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dpia = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "artifact_id": ARTIFACT_ID,
        "model_version": DEFAULT_MODEL_VERSION,
        "data_categories": draft.get("data_categories", ["personal_data"]),
        "processing_purpose": draft.get("processing_purpose", "risk_scoring"),
        "risk_summary": draft.get("risk_summary", "medium"),
        "mitigations": draft.get("mitigations", ["human_review", "data_minimisation"]),
        "lawful_basis": draft.get("lawful_basis", "legitimate_interest"),
        "fria_included": bool(fria)
    }
    if fria:
        dpia["fria"] = {
            "rights_potentially_affected": draft.get("rights", ["non-discrimination", "privacy"]),
            "proportionality_check": "documented",
            "less_intrusive_alternatives": draft.get("less_intrusive_alternatives", ["manual_review"])
        }
    out_path = os.path.join(EVIDENCE_DIR, f"dpia_{now}.json")
    with open(out_path, "w") as f:
        json.dump(dpia, f, indent=2)
    dpia["path"] = out_path
    return dpia


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="JSON input transaction file")
    p.add_argument("--append-log", action="store_true", help="Append intervention log")
    p.add_argument("--fria", action="store_true", help="Generate DPIA+FRIA JSON")
    p.add_argument("--human-id", default="system", help="human_id field for log")
    args = p.parse_args()

    # load input (path may be relative to repo root)
    txn_path = args.input
    if not os.path.isabs(txn_path):
        txn_path = os.path.abspath(txn_path)
    with open(txn_path, "r") as fh:
        txn = json.load(fh)

    score = automated_score(txn)
    print(json.dumps({"score": score}, indent=2))

    if args.append_log:
        logger = InterventionLog(path=os.path.join(os.path.dirname(__file__), "intervention_log.ndjson"))
        entry = {
            "artifact_id": ARTIFACT_ID,
            "model_version": DEFAULT_MODEL_VERSION,
            "input": txn,
            "output": {"score": score["score"], "reasons": score["reasons"]},
            "decision_summary": "auto_score_generated; threshold_rules",
            "human_id": args.human_id,
            "human_reason": "auto"
        }
        appended = logger.append(entry)
        print("Appended log signature:", appended["signature_hash"])

    if args.fria:
        dpia = generate_dpia({"data_categories": ["txn"], "processing_purpose": "fraud_scoring"}, fria=True)
        print("DPIA written to:", dpia["path"])


if __name__ == "__main__":
    main()
