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
    ap.add_argument("--unified-record", required=True)
    ap.add_argument("--unknowns", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    record = load_json(Path(args.unified_record))
    unknowns = load_json(Path(args.unknowns))

    criteria = []

    if len(unknowns.get("unknowns", [])) > 0:
        criteria.append("unresolved_unknowns_present")

    if record.get("responsibility_lattice"):
        criteria.append("human_intervention_occurred")

    if len(record.get("counterfactuals", {}).get("counterfactuals", [])) > 1:
        criteria.append("multiple_counterfactuals_assessed")

    # Deterministic mapping
    if "unresolved_unknowns_present" in criteria:
        severity = "serious"
    else:
        severity = "minor"

    severity_obj = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "incident_severity",
        "incident_id": args.incident_id,
        "classified_at_utc": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "criteria_met": criteria
    }

    severity_obj["integrity"] = {
        "severity_hash_sha256": sha256(severity_obj)
    }

    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)

    fname = f"{args.incident_id}_severity.json"
    with open(out_path / fname, "w", encoding="utf-8") as f:
        json.dump(severity_obj, f, indent=2)

    print(f"[OK] Incident severity classified: {fname}")

if __name__ == "__main__":
    main()
