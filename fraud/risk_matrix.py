#!/usr/bin/env python3
"""
risk_matrix.py
Risk Matrix + Notified-Body Export Stub (EU AI Act Annex III | ISO 42001 Mapping)

Usage:
  python fraud/risk_matrix.py --input artifacts/reports/compliance_report_*.json --export

Generates:
  - Risk classification (low / medium / high)
  - Clause mapping summary
  - JSON-LD export to artifacts/reports/risk_matrix_<ts>.jsonld
"""
from __future__ import annotations
import argparse, json, os, datetime, hashlib
from typing import Dict, Any

ARTIFACT_ID = "fraud_v1"
MODEL_VERSION = "v0.2"
REPORT_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/reports")
os.makedirs(REPORT_DIR, exist_ok=True)

EU_AI_ACT_CLASSES = {
    "high": ["Credit scoring", "Insurance underwriting", "Biometric ID", "Essential service access"],
    "medium": ["Customer support chatbots", "Document verification"],
    "low": ["Marketing analytics", "Non-critical decision support"],
}

ISO42001_CLAUSES = {
    "4": "Context of the organization",
    "6": "Planning – risk assessment and mitigation",
    "8": "Operation – control of AI lifecycle processes",
    "9": "Performance evaluation – monitorability and audit",
}

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()

def load_compliance(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)

def build_matrix(report: Dict[str, Any]) -> Dict[str, Any]:
    lvl = report.get("risk_level", "medium")
    mapped_clauses = []
    if lvl == "high":
        mapped_clauses = [ISO42001_CLAUSES["6"], ISO42001_CLAUSES["9"]]
    elif lvl == "medium":
        mapped_clauses = [ISO42001_CLAUSES["6"]]
    else:
        mapped_clauses = [ISO42001_CLAUSES["4"]]

    return {
        "artifact_id": ARTIFACT_ID,
        "model_version": MODEL_VERSION,
        "risk_level": lvl,
        "applicable_ai_act_categories": EU_AI_ACT_CLASSES.get(lvl, []),
        "iso42001_clauses": mapped_clauses,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "signature_hash": sha256_text(json.dumps(mapped_clauses) + lvl),
    }

def write_export(matrix: Dict[str, Any]) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(REPORT_DIR, f"risk_matrix_{ts}.jsonld")
    export = {
        "@context": "https://schema.org",
        "@type": "RiskAssessment",
        "artifact_id": matrix["artifact_id"],
        "model_version": matrix["model_version"],
        "risk_level": matrix["risk_level"],
        "ai_act_categories": matrix["applicable_ai_act_categories"],
        "iso42001_clauses": matrix["iso42001_clauses"],
        "generated_at": matrix["generated_at"],
        "signature_hash": matrix["signature_hash"],
    }
    with open(path, "w") as f:
        json.dump(export, f, indent=2)
    return path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to compliance_report JSON")
    p.add_argument("--export", action="store_true", help="Write JSON-LD export")
    args = p.parse_args()

    report = load_compliance(args.input)
    matrix = build_matrix(report)
    print(json.dumps(matrix, indent=2))
    if args.export:
        out = write_export(matrix)
        print("Export written to:", out)

if __name__ == "__main__":
    main()
