#!/usr/bin/env python3
"""
remediation_planner.py
Clause Remediation Planner (deterministic). 

- Ingests a compliance report (output of compliance_audit_pack.py).
- Produces a remediation plan mapping missing evidence to actionable steps.
- Writes remediation_plan_<ts>.json to artifacts/reports/.
- Uses only stdlib and small deterministic rules.

Usage:
  python fraud/remediation_planner.py --input artifacts/reports/compliance_report_*.json --emit
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
from typing import Dict, Any, List

REPORT_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# Minimal remediation rulebook
REMEDIATION_RULES = {
    "data_categories": "Provide explicit data category list and schema; include examples and minimisation rationale.",
    "processing_purpose": "Document precise processing purpose and legal basis; link to consent or legitimate interest assessment.",
    "risk_summary": "Provide risk assessment supporting evidence and scoring methodology; attach example scenarios.",
    "mitigations": "Document mitigation controls (human review SOPs, rate-limits, fallback flows).",
    "lawful_basis": "Attach legal advice memo and data protection impact assessment references.",
    "fria": "Provide FRIA documentation with proportionality and less-intrusive alternative analysis.",
    "intervention_log_empty": "Populate intervention_log.ndjson with initial system runs and appendable human reviews.",
}

# map missing -> priority : higher priority (1) means act first
PRIORITY = {
    "fria": 1,
    "lawful_basis": 1,
    "risk_summary": 1,
    "intervention_log_empty": 1,
    "mitigations": 2,
    "data_categories": 2,
    "processing_purpose": 2,
}

def load_report(path: str) -> Dict[str, Any]:
    # open with explicit UTF-8 encoding to avoid Windows cp1252 decode errors
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def plan_remediations(findings: Dict[str, Any]) -> List[Dict[str, Any]]:
    missing = findings.get("missing", []) if isinstance(findings, dict) else []
    plan = []
    for m in missing:
        step = {
            "missing_item": m,
            "action": REMEDIATION_RULES.get(m, "Manual review required; document missing evidence."),
            "priority": PRIORITY.get(m, 3)
        }
        plan.append(step)
    # sort by priority ascending (1 highest)
    plan = sorted(plan, key=lambda x: x["priority"])
    # if nothing missing, recommend monitoring
    if not plan:
        plan.append({"note":"no_missing_evidence","action":"Continue monitoring; maintain periodic reviews", "priority": 5})
    return plan

def write_plan(plan: List[Dict[str, Any]]) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"remediation_plan_{ts}.json"
    out = os.path.join(REPORT_DIR, fname)
    with open(out, "w") as fh:
        json.dump({"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "plan": plan}, fh, indent=2)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to compliance report JSON")
    p.add_argument("--emit", action="store_true", help="Write remediation plan to artifacts/reports")
    args = p.parse_args()

    report = load_report(args.input)
    findings = report.get("findings", {})
    plan = plan_remediations(findings)
    print(json.dumps({"plan": plan}, indent=2))
    if args.emit:
        path = write_plan(plan)
        print("Remediation plan written to:", path)

if __name__ == "__main__":
    main()
