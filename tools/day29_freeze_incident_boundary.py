#!/usr/bin/env python3
"""
Day 29 — Incident Boundary Freezing Artifact (Rev 7.1)

Purpose:
Freeze the evidentiary boundary of an incident using existing artifacts only.
"""

import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def sha256_canonical(obj) -> str:
    canonical = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident-id", required=True)
    ap.add_argument("--intervention-log", required=True)
    ap.add_argument("--monitor-snapshot", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    intervention_path = Path(args.intervention_log)
    monitor_path = Path(args.monitor_snapshot)

    boundary = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "incident_boundary_freeze",
        "incident_id": args.incident_id,
        "freeze_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "in_scope_evidence": [
            {
                "type": "intervention_log",
                "path": str(intervention_path),
                "hash_sha256": sha256_file(intervention_path)
            },
            {
                "type": "monitorability_snapshot",
                "path": str(monitor_path),
                "hash_sha256": sha256_file(monitor_path)
            }
        ],
        "out_of_scope_note": (
            "Any evidence generated after freeze_timestamp_utc "
            "is explicitly excluded from this incident boundary."
        )
    }

    boundary["freeze_hash_sha256"] = sha256_canonical(boundary)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.incident_id}_boundary_freeze.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(boundary, f, indent=2)

    print(f"[OK] Incident boundary frozen: {out_path.name}")

if __name__ == "__main__":
    main()
