#!/usr/bin/env python3
"""
intervention_log.py
Rev 7-compliant intervention log writer.

Usage:
  from fraud.intervention_log import emit_intervention
  emit_intervention({
      "artifact_id":"fraud_v1",
      "model_version":"v0.2",
      "input": {"amount":15000, "country":"XYZ", "age":29},
      "output": {"score":75, "reasons":["high_amount"]},
      "human_id": None,
      "human_reason": None,
      "decision_summary": "auto_score_generated; threshold_rules",
      # optional Rev7 fields:
      # "quantum_verification_hash": None,
      # "incident_report_id": None,
      # "gpa_model_id": None,
      # "joules_per_verified_operation": None,
  })
"""
from __future__ import annotations
import json, os, hashlib, datetime, uuid
from typing import Dict, Any

LOG_PATH = os.path.join(os.path.dirname(__file__), "../fraud/intervention_log.ndjson")

def _sha256_of_obj(obj: Any) -> str:
    j = json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False)
    return hashlib.sha256(j.encode('utf-8')).hexdigest()

def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def emit_intervention(entry: Dict[str, Any], path: str = LOG_PATH) -> Dict[str, Any]:
    """
    Ensure required fields, compute hashes and append entry as NDJSON.
    Returns the full emitted entry.
    """
    # defaults
    entry = dict(entry)  # shallow copy
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry.setdefault("timestamp", now)
    entry.setdefault("artifact_id", "unknown_artifact")
    entry.setdefault("model_version", "unknown_version")
    # compute canonical input/output hashes if not provided
    if "input_hash" not in entry:
        if "input" in entry:
            entry["input_hash"] = _sha256_of_obj(entry["input"])
        else:
            entry["input_hash"] = ""
    if "output_hash" not in entry:
        if "output" in entry:
            entry["output_hash"] = _sha256_of_obj(entry["output"])
        else:
            entry["output_hash"] = ""
    # signature: deterministic SHA256 over core identifiers + human fields
    # include human fields so edits to human_id/human_reason/decision_summary are detectable
    aid = str(entry.get("artifact_id","") or "")
    mv  = str(entry.get("model_version","") or "")
    ih  = str(entry.get("input_hash","") or "")
    oh  = str(entry.get("output_hash","") or "")
    hid = str(entry.get("human_id","") or "")
    hreason = str(entry.get("human_reason","") or "")
    dsummary = str(entry.get("decision_summary","") or "")
    sig_base = "|".join([aid, mv, ih, oh, hid, hreason, dsummary])
    entry.setdefault("signature_hash", hashlib.sha256(sig_base.encode('utf-8')).hexdigest())

    # human fields
    entry.setdefault("human_id", entry.get("human_id", None))
    entry.setdefault("human_reason", entry.get("human_reason", None))
    entry.setdefault("decision_summary", entry.get("decision_summary", None))
    # Rev7 additions (nullable placeholders)
    entry.setdefault("quantum_verification_hash", entry.get("quantum_verification_hash", None))
    entry.setdefault("incident_report_id", entry.get("incident_report_id", None))
    entry.setdefault("gpa_model_id", entry.get("gpa_model_id", None))
    entry.setdefault("joules_per_verified_operation", entry.get("joules_per_verified_operation", None))
    # provenance metadata
    meta = entry.get("metadata", {})
    meta.setdefault("tool", "intervention_log.py")
    meta.setdefault("version", "rev7")
    meta.setdefault("run_id", str(uuid.uuid4()))
    entry["metadata"] = meta

    # write NDJSON
    _ensure_dir(path)
    line = json.dumps(entry, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    return entry

# CLI convenience for manual emission
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--json", help="Path to JSON file containing entry dict")
    p.add_argument("--emit", action="store_true", help="Emit sample entry")
    args = p.parse_args()
    if args.json:
        data = json.load(open(args.json,'r',encoding='utf-8'))
        e = emit_intervention(data)
        print("Emitted:", e["timestamp"], e["artifact_id"])
    elif args.emit:
        sample = {
            "artifact_id":"fraud_v1",
            "model_version":"v0.2",
            "input":{"amount":15000,"country":"XYZ","age":29,"previous_fraud_flag":False},
            "output":{"score":75,"reasons":["high_amount","country_high_risk"]},
            "decision_summary":"auto_score_generated; threshold_rules"
        }
        e = emit_intervention(sample)
        print("Emitted sample:", e["timestamp"], e["artifact_id"])
    else:
        p.print_help()
