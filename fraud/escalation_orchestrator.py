#!/usr/bin/env python3
"""
escalation_orchestrator.py
Simple Escalation Orchestrator + SLA Notifier stub.

Behavior:
- Read a remediation plan JSON (remediation_plan_<ts>.json).
- Classify items by priority and age (file mtime used as proxy if 'created_at' absent).
- Emit escalation notices for high-priority items or overdue actions.
- Write escalation bundle to artifacts/notifications/escalation_<ts>.json

Usage (from phase2/):
  python fraud/escalation_orchestrator.py --plan artifacts/reports/remediation_plan_<ts>.json --notify-to ops@bank.local --emit

Notes:
- Deterministic rules only.
- Uses file timestamps as simple SLA proxy (age in days).
- No external libs required.
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
import hashlib
from typing import Dict, Any, List

ARTIFACT_ID = "fraud_v1"
MODEL_VERSION = "v0.2"
NOTIF_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/notifications")
os.makedirs(NOTIF_DIR, exist_ok=True)

# SLA rules (days)
SLA_DAYS_BY_PRIORITY = {
    1: 3,   # critical -> 3 days
    2: 7,   # high -> 7 days
    3: 14,  # medium -> 14 days
    5: 30,  # monitoring -> 30 days
}

def load_plan(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def age_days(path: str) -> int:
    # use file modification time as simple age proxy
    mtime = os.path.getmtime(path)
    delta = datetime.datetime.now().timestamp() - mtime
    return int(delta // 86400)

def classify_escalations(plan_obj: Dict[str, Any], path: str) -> Dict[str, Any]:
    # plan_obj expected to contain {"plan": [...]}
    out = {"to_notify": [], "summary": {"total": 0, "escalations": 0}}
    items = plan_obj.get("plan", [])
    now = datetime.datetime.now(datetime.timezone.utc)
    file_age = age_days(path)
    out["summary"]["total"] = len(items)
    for it in items:
        pr = it.get("priority", 3)
        sla_days = SLA_DAYS_BY_PRIORITY.get(pr, 14)
        overdue = file_age > sla_days
        note = {
            "missing_item": it.get("missing_item", it.get("note", "unknown")),
            "action": it.get("action", ""),
            "priority": pr,
            "file_age_days": file_age,
            "sla_days": sla_days,
            "overdue": overdue
        }
        if pr <= 2 or overdue:
            out["to_notify"].append(note)
            out["summary"]["escalations"] += 1
    return out

def make_notification(bundle: Dict[str, Any], notify_to: str, plan_path: str) -> Dict[str, Any]:
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    body = {
        "artifact_id": ARTIFACT_ID,
        "model_version": MODEL_VERSION,
        "generated_at": ts,
        "notify_to": notify_to,
        "plan_path": plan_path,
        "escalation_summary": bundle.get("summary", {}),
        "escalations": bundle.get("to_notify", []),
    }
    # signature: chain plan_path + timestamp + json(escalations)
    sig_input = plan_path + ts + json.dumps(body.get("escalations", []), sort_keys=True)
    body["signature_hash"] = hashlib.sha256(sig_input.encode("utf-8")).hexdigest()
    return body

def write_notification(notif: Dict[str, Any]) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"escalation_{ts}.json"
    out = os.path.join(NOTIF_DIR, fname)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(notif, fh, indent=2)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, help="Path to remediation_plan JSON")
    p.add_argument("--notify-to", required=True, help="Recipient (email or team id placeholder)")
    p.add_argument("--emit", action="store_true", help="Write escalation bundle to artifacts/notifications")
    args = p.parse_args()

    plan_obj = load_plan(args.plan)
    classified = classify_escalations(plan_obj, args.plan)
    print(json.dumps(classified, indent=2))
    notif = make_notification(classified, args.notify_to, args.plan)
    if args.emit:
        out = write_notification(notif)
        print("Escalation notification written to:", out)
        print("signature_hash:", notif["signature_hash"])

if __name__ == "__main__":
    main()
