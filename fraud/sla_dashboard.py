#!/usr/bin/env python3
"""
sla_dashboard.py
SLA Dashboard & Remediation Ownership Aggregator.

- Scans artifacts/reports for remediation_plan_*.json and ownership_remediation_plan_*.json
- Aggregates per-plan owner, priority counts, overdue status (uses file mtime as proxy)
- Writes:
  - JSON summary: artifacts/reports/sla_dashboard_<ts>.json
  - CSV summary: artifacts/reports/sla_dashboard_<ts>.csv

Usage:
  python fraud/sla_dashboard.py --reports-dir artifacts/reports --out-dir artifacts/reports --export

Design:
- Deterministic rules only.
- Uses SLA_DAYS_BY_PRIORITY from escalation_orchestrator for consistency.
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
import csv
from typing import Dict, Any, List

REPORT_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "../artifacts/reports")
OUT_DIR_DEFAULT = REPORT_DIR_DEFAULT

# Reuse the same SLA days as orchestrator (keep in sync)
SLA_DAYS_BY_PRIORITY = {1: 3, 2: 7, 3: 14, 5: 30}

def list_files(pattern_dir: str, prefix: str) -> List[str]:
    try:
        files = [f for f in os.listdir(pattern_dir) if f.startswith(prefix)]
        files = sorted(files)
        return [os.path.join(pattern_dir, f) for f in files]
    except FileNotFoundError:
        return []

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def file_age_days(path: str) -> int:
    return int((datetime.datetime.now().timestamp() - os.path.getmtime(path)) // 86400)

def aggregate(plans_dir: str) -> Dict[str, Any]:
    # find remediation plans
    rp_paths = list_files(plans_dir, "remediation_plan_")
    ownership_paths = list_files(plans_dir, "ownership_remediation_plan_")
    ownership_map = {}
    for op in ownership_paths:
        try:
            o = load_json(op)
            ownership_map[o.get("plan")] = o.get("owner")
        except Exception:
            continue

    rows = []
    totals = {"plans": 0, "overdue": 0}
    for rpath in rp_paths:
        try:
            rp = load_json(rpath)
        except Exception:
            continue
        plan = rp.get("plan", [])
        plan_age = file_age_days(rpath)
        owner = ownership_map.get(os.path.basename(rpath), None) or ownership_map.get(rpath, None) or None
        # compute counts and overdue items
        counts = {"total_items": len(plan), "overdue_items": 0}
        for it in plan:
            pr = it.get("priority", 3)
            sla = SLA_DAYS_BY_PRIORITY.get(pr, 14)
            overdue = plan_age > sla
            if overdue:
                counts["overdue_items"] += 1
        totals["plans"] += 1
        totals["overdue"] += counts["overdue_items"]
        rows.append({
            "plan_file": os.path.basename(rpath),
            "owner": owner or "",
            "plan_age_days": plan_age,
            "total_items": counts["total_items"],
            "overdue_items": counts["overdue_items"]
        })

    summary = {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "totals": totals,
               "rows": rows}
    return summary

def write_outputs(summary: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = os.path.join(out_dir, f"sla_dashboard_{ts}.json")
    csv_path = os.path.join(out_dir, f"sla_dashboard_{ts}.csv")
    with open(json_path, "w", encoding="utf-8") as jh:
        json.dump(summary, jh, indent=2)
    # write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as ch:
        writer = csv.writer(ch)
        writer.writerow(["plan_file", "owner", "plan_age_days", "total_items", "overdue_items"])
        for r in summary["rows"]:
            writer.writerow([r["plan_file"], r["owner"], r["plan_age_days"], r["total_items"], r["overdue_items"]])
    return {"json": json_path, "csv": csv_path}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reports-dir", default=REPORT_DIR_DEFAULT)
    p.add_argument("--out-dir", default=OUT_DIR_DEFAULT)
    p.add_argument("--export", action="store_true")
    args = p.parse_args()

    summary = aggregate(args.reports_dir)
    print("Plans scanned:", len(summary["rows"]), "Total overdue items:", summary["totals"]["overdue"])
    if args.export:
        out = write_outputs(summary, args.out_dir)
        print("Dashboard JSON:", out["json"])
        print("Dashboard CSV:", out["csv"])

if __name__ == "__main__":
    main()
