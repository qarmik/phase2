import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import hashlib

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256(obj):
    raw = json.dumps(obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident-id", required=True)
    ap.add_argument("--boundary", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--responsibility", required=True)
    ap.add_argument("--counterfactuals", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    boundary = load_json(Path(args.boundary))
    evidence = load_json(Path(args.evidence))
    responsibility = load_json(Path(args.responsibility))
    counterfactuals = load_json(Path(args.counterfactuals))

    unknowns = []
    for item in evidence.get("evidence_items", []):
        if item.get("evidence_type") == "unknown":
            unknowns.append({
                "evidence_id": item["evidence_id"],
                "reason": item.get("confidence_note", "Unspecified")
            })

    record = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "unified_incident_record",
        "incident_id": args.incident_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "incident_boundary": boundary,
        "evidence_classification": evidence,
        "responsibility_lattice": responsibility,
        "counterfactuals": counterfactuals,
        "declared_unknowns": unknowns
    }

    record["integrity"] = {
        "record_hash_sha256": sha256(record)
    }

    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)

    fname = f"{args.incident_id}_unified_incident_record.json"
    with open(out_path / fname, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"[OK] Unified incident record written: {fname}")

if __name__ == "__main__":
    main()
