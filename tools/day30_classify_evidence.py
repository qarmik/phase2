#!/usr/bin/env python3
"""
Day 30 — Evidence Classification Schema (GAP 2)
Protocol Qv Rev 7.1
"""

import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def sha256_canonical(obj) -> str:
    data = json.dumps(obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident-id", required=True)
    ap.add_argument("--boundary-freeze", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    boundary_path = Path(args.boundary_freeze)
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))

    evidence_items = []
    for entry in boundary.get("in_scope_evidence", []):
        evidence_items.append({
            "evidence_id": entry["hash_sha256"],
            "source_path": entry["path"],
            "evidence_type": "unknown",
            "confidence_note": "Initial classification defaults to unknown.",
            "classification_rationale": (
                "Evidence has not yet been analyzed sufficiently "
                "to be asserted as observed fact or inferred relation."
            ),
            "tamper_risk": "low"
        })

    classification = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "evidence_classification",
        "incident_id": args.incident_id,
        "classified_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_items": evidence_items
    }

    classification["classification_hash_sha256"] = sha256_canonical(classification)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.incident_id}_evidence_classification.json"
    out_path.write_text(json.dumps(classification, indent=2), encoding="utf-8")

    print(f"[OK] Evidence classification written: {out_path.name}")

if __name__ == "__main__":
    main()
