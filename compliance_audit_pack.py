#!/usr/bin/env python3
"""
compliance_audit_pack.py
Lightweight Compliance Audit Pack (EU AI Act + RBI FREE-AI + ISO 42001 hints).

Placement: phase2/compliance_audit_pack.py

Purpose:
- Ingest a DPIA/FRIA JSON or an intervention log NDJSON file.
- Produce a small compliance_report_<ts>.json listing:
  - risk_level (low/medium/high)
  - present_evidence keys
  - missing_evidence hints (ISO 42001 + AI Act)
  - mapped_clauses (suggested clause references)
- CLI: --input <path> (--type dpia|log) --iso-map (append ISO hint)

Design notes:
- Deterministic heuristics only (rule-based).
- Minimal, explainable outputs for notified-body / insurer review.
- Uses only stdlib.
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
from typing import Dict, Any, List

EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "artifacts", "evidence")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "artifacts", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# Tiny clause mapping tables (starter)
EU_AI_ACT_MAP = {
    "high_risk": ["AI Act Annex II: Credit scoring & underwriting (human oversight)", "Article 14: High-risk requirements"],
    "transparency": ["Article 13: Information to users", "Article 12: Logging"],
}
ISO42001_HINTS = {
    "risk_assessment": "Clause 6: Planning - risk assessment evidence needed",
    "monitoring": "Clause 9: Performance evaluation - monitorability metrics",
    "human_oversight": "Clause 7: Support - human oversight proof",
}

# Heuristic thresholds
HIGH_RISK_SCORE = 80
MEDIUM_RISK_SCORE = 50

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)

def inspect_dpia(d: Dict[str, Any]) -> Dict[str, Any]:
    present = []
    missing = []
    # Check for core DPIA fields
    keys = d.keys()
    for k in ("data_categories", "processing_purpose", "risk_summary", "mitigations", "lawful_basis"):
        if k in keys:
            present.append(k)
        else:
            missing.append(k)
    fria = d.get("fria_included", False) or ("fria" in keys)
    if fria:
        present.append("fria")
    else:
        missing.append("fria")
    return {"present": present, "missing": missing, "raw": d}

def inspect_log_ndjson(path: str) -> Dict[str, Any]:
    present = []
    missing = []
    found_sig = False
    with open(path, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if lines:
        last = json.loads(lines[-1])
        # required insurer fields
        for r in ("timestamp", "artifact_id", "model_version", "input_hash", "output_hash", "signature_hash"):
            if r in last:
                present.append(r)
            else:
                missing.append(r)
        if last.get("signature_hash"):
            found_sig = True
    else:
        missing.append("intervention_log_empty")
    return {"present": present, "missing": missing, "last_signature_present": found_sig}

def score_risk_from_scoreobj(score_obj: Dict[str, Any]) -> str:
    try:
        sc = int(score_obj.get("score", 0))
    except Exception:
        sc = 0
    if sc >= HIGH_RISK_SCORE:
        return "high"
    if sc >= MEDIUM_RISK_SCORE:
        return "medium"
    return "low"

def generate_mappings(findings: Dict[str, Any], iso_map: bool = False) -> Dict[str, Any]:
    mapped = {"eu_ai_act": [], "iso42001_hints": []}
    # simple mapping rules
    if "fria" not in findings.get("present", []):
        mapped["eu_ai_act"].append("transparency")
    if "previous_fraud_flag" in findings.get("raw", {}).get("rights", []) or "previous_fraud_flag" in findings.get("present", []):
        mapped["eu_ai_act"].append("high_risk")
    # heuristic: if 'risk_summary' indicates high, map high_risk
    rs = findings.get("raw", {}).get("risk_summary", "")
    if rs and "high" in str(rs).lower():
        mapped["eu_ai_act"].append("high_risk")
    if iso_map:
        # add ISO hints for any missing items
        for m in findings.get("missing", []):
            hint = ISO42001_HINTS.get("risk_assessment")
            if hint:
                mapped["iso42001_hints"].append(hint)
    return mapped

def evaluate_evidence(input_path: str, input_type: str = "dpia", iso_map: bool = False) -> Dict[str, Any]:
    report: Dict[str, Any] = {"input_path": input_path, "input_type": input_type, "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if input_type == "dpia":
        d = load_json(input_path)
        findings = inspect_dpia(d)
        report["findings"] = findings
        report["risk_level"] = "high" if ("high" in str(d.get("risk_summary","")).lower()) else score_risk_from_scoreobj(d)
    else:
        info = inspect_log_ndjson(input_path)
        report["findings"] = info
        report["risk_level"] = "medium" if info.get("last_signature_present") else "high"
    # mappings
    report["mappings"] = generate_mappings(report.get("findings", {}), iso_map=iso_map)
    # missing evidence summary
    report["missing_evidence"] = report["findings"].get("missing", [])
    return report

def write_report(report: Dict[str, Any]) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"compliance_report_{ts}.json"
    out = os.path.join(REPORT_DIR, fname)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to DPIA JSON or intervention log NDJSON")
    p.add_argument("--type", choices=["dpia", "log"], default="dpia", help="Input type")
    p.add_argument("--iso-map", action="store_true", help="Append ISO42001 hints in mappings")
    args = p.parse_args()
    report = evaluate_evidence(args.input, input_type=args.type, iso_map=args.iso_map)
    path = write_report(report)
    print("Compliance report written to:", path)
    print("Risk level:", report.get("risk_level"))
    print("Missing evidence:", report.get("missing_evidence"))

if __name__ == "__main__":
    main()
