#!/usr/bin/env python3
"""
owner_assignment.py
Automates assignment of owners to remediation plans.

Behavior:
- Scans a reports directory for remediation_plan_*.json
- Uses an optional org-map JSON (plan_pattern -> owner) to assign owners
- Writes ownership_remediation_plan_<plan_ts>.json to artifacts/reports/
- Supports --dry-run to preview assignments without writing files

CLI:
  python fraud/owner_assignment.py --reports-dir artifacts/reports --org-map org_map.json --dry-run
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
from typing import Dict, Any, List

REPORT_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "../artifacts/reports")

def list_remediation_plans(reports_dir: str) -> List[str]:
    try:
        files = sorted([f for f in os.listdir(reports_dir) if f.startswith("remediation_plan_") and f.endswith(".json")])
        return [os.path.join(reports_dir, f) for f in files]
    except FileNotFoundError:
        return []

def load_org_map(path: str | None) -> Dict[str, str]:
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}

def assign_owner_for_plan(plan_path: str, org_map: Dict[str, str]) -> str:
    # pattern-based assignment: if basename contains a key in org_map, use it
    b = os.path.basename(plan_path)
    for pattern, owner in org_map.items():
        if pattern in b:
            return owner
    # fallback default owner
    return "compliance_lead"

def write_ownership(plan_path: str, owner: str, out_dir: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"ownership_{os.path.basename(plan_path).replace('.json','')}_{ts}.json"
    out_path = os.path.join(out_dir, fname)
    entry = {"plan": os.path.basename(plan_path), "owner": owner, "assigned_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(entry, fh, indent=2)
    return out_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reports-dir", default=REPORT_DIR_DEFAULT)
    p.add_argument("--org-map", help="Optional JSON file with pattern->owner mapping")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    org_map = load_org_map(args.org_map)
    plans = list_remediation_plans(args.reports_dir)
    results = []
    for plan in plans:
        owner = assign_owner_for_plan(plan, org_map)
        results.append({"plan": os.path.basename(plan), "owner": owner})
        if not args.dry_run:
            write_ownership(plan, owner, args.reports_dir)
    print(json.dumps({"assigned": results}, indent=2))

if __name__ == "__main__":
    main()
