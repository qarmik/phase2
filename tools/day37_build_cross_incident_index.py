import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incidents", required=True, help="docs/incidents directory")
    ap.add_argument("--out", required=True, help="output directory")
    args = ap.parse_args()

    incidents_dir = Path(args.incidents)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    index = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "cross_incident_index",
        "index_generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "incidents": []
    }

    for boundary_file in sorted(incidents_dir.glob("*_boundary_freeze.json")):
        boundary = load_json(boundary_file)
        incident_id = boundary["incident_id"]

        evidence_file = incidents_dir / f"{incident_id}_evidence_classification.json"
        severity_file = incidents_dir / f"{incident_id}_severity.json"

        responsibility_files = list(
            incidents_dir.glob(f"*{incident_id}*_responsibility_lattice.json")
        )

        evidence = load_json(evidence_file) if evidence_file.exists() else None
        severity = load_json(severity_file) if severity_file.exists() else None
        responsibility = (
            load_json(responsibility_files[0])
            if responsibility_files
            else None
        )

        evidence_profile = {
            "observed_fact": 0,
            "inferred_relation": 0,
            "unknown": 0
        }

        if evidence:
            for item in evidence.get("evidence_items", []):
                et = item.get("evidence_type", "unknown")
                if et in evidence_profile:
                    evidence_profile[et] += 1
                else:
                    evidence_profile["unknown"] += 1

        incident_entry = {
            "incident_id": incident_id,
            "boundary_hash_sha256": boundary["freeze_hash_sha256"],
            "incident_severity": severity["severity"] if severity else "unknown",
            "intervention_types": [
                e.get("type", "unknown")
                for e in boundary.get("in_scope_evidence", [])
            ],
            "responsible_roles": (
                [a.get("role") for a in responsibility.get("actors", [])]
                if responsibility
                else []
            ),
            "evidence_profile": evidence_profile,
            "unknowns_count": evidence_profile["unknown"],
            "incident_timestamp_utc": boundary["freeze_timestamp_utc"]
        }

        index["incidents"].append(incident_entry)

    out_file = out_dir / "cross_incident_index.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"[OK] Cross-incident index written: {out_file}")

if __name__ == "__main__":
    main()
