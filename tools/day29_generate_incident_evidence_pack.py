#!/usr/bin/env python3
"""
Day 29 — Incident Evidence Pack Generator (Pre-Notification, Rev 7.1)

Zero-drift rules:
- Consume only existing artifacts
- No invented fields
- Surface gaps explicitly
"""

import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_canonical(obj) -> str:
    canonical = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def build_evidence_pack(intervention, monitor_snapshot):
    evidence = {
        "incident_id": f"INC-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "incident_status": "IDENTIFIED",
        "scope_note": (
            "Pre-notification evidence pack. "
            "No escalation or regulatory reporting has occurred."
        ),

        "eu_single_entry_point": {
            "route": "ENISA",
            "routing_classification": [
                "AI_ACT_73",
                "GDPR_33",
                "NIS2",
                "DORA",
                "CER"
            ],
            "harmonized_template": True
        },

        "bound_evidence": {
            "intervention_log": intervention,
            "monitorability_snapshot": monitor_snapshot
        },

        "observed_gaps": []
    }

    # Explicit gap surfacing
    if not isinstance(intervention, dict):
        evidence["observed_gaps"].append(
            "Intervention log is not a JSON object."
        )

    if not isinstance(monitor_snapshot, dict):
        evidence["observed_gaps"].append(
            "Monitorability snapshot is not a JSON object."
        )

    # No assumptions about scores or fields
    expected_monitor_fields = ["qvm_alert", "faithfulness", "monitorability"]
    for field in expected_monitor_fields:
        if field not in monitor_snapshot:
            evidence["observed_gaps"].append(
                f"Monitorability snapshot missing field: {field}"
            )

    evidence["sha256"] = sha256_canonical(evidence)
    return evidence

def write_outputs(pack, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{pack['incident_id']}.json"
    md_path = out_dir / f"{pack['incident_id']}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pack, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Incident Evidence Pack — {pack['incident_id']}\n\n")
        f.write(f"**Generated:** {pack['generated_at']}\n\n")
        f.write("## Status\n")
        f.write(f"{pack['incident_status']}\n\n")
        f.write("## Scope Note\n")
        f.write(f"{pack['scope_note']}\n\n")
        f.write("## ENISA Single Entry Point\n")
        f.write(json.dumps(pack["eu_single_entry_point"], indent=2))
        f.write("\n\n## Observed Gaps\n")
        if pack["observed_gaps"]:
            for g in pack["observed_gaps"]:
                f.write(f"- {g}\n")
        else:
            f.write("None observed at generation time.\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intervention-log", required=True)
    ap.add_argument("--monitor-snapshot", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    intervention = load_json(Path(args.intervention_log))
    monitor = load_json(Path(args.monitor_snapshot))

    pack = build_evidence_pack(intervention, monitor)
    write_outputs(pack, Path(args.out))

    print(f"[OK] Incident Evidence Pack generated: {pack['incident_id']}")

if __name__ == "__main__":
    main()
