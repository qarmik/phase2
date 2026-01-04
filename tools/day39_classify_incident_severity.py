"""
Incident Severity Classifier — Protocol Qv Rev 7.1
Post-incident aggregation only. Deterministic. Explainable.
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import hashlib

SEVERITY_LEVELS = ["minor", "serious", "systemic"]

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256(obj):
    raw = json.dumps(obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def classify(inputs):
    """
    Classification rules (post-incident only):
    - systemic: repeated + correlated + persistent harm OR asymmetric impact on constrained actors
    - serious: repeated OR persistent harm with measurable outcome deltas
    - minor: isolated or low-frequency harm without persistence
    """
    observations = inputs["observations"]
    unknowns = []

    repeats = observations.get("repeated_effects")
    correlated = observations.get("correlated_across_users")
    persistent = observations.get("persistent_over_time")
    asymmetric = observations.get("asymmetric_impact")

    for k, v in observations.items():
        if v is None:
            unknowns.append(k)

    if (repeats and correlated and persistent) or asymmetric:
        level = "systemic"
        reason = "Repeated, correlated harm persisted over time or disproportionately affected constrained actors."
    elif repeats or persistent:
        level = "serious"
        reason = "Repeated or persistent harm observed beyond isolated occurrence."
    else:
        level = "minor"
        reason = "Harm observed as isolated or non-persistent effects."

    confidence = "reduced" if unknowns else "normal"

    return {
        "severity": level,
        "justification": reason,
        "confidence": confidence,
        "unknowns": unknowns
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident-id", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = load_json(Path(args.input))

    result = classify(data)

    output = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "incident_severity_classification",
        "incident_id": args.incident_id,
        "classified_at_utc": datetime.now(timezone.utc).isoformat(),
        "time_window": data["time_window"],
        "severity": result["severity"],
        "confidence": result["confidence"],
        "justification": result["justification"],
        "unknowns": result["unknowns"]
    }

    output["severity_hash_sha256"] = sha256(output)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    fname = f"{args.incident_id}_severity.json"
    with open(out_dir / fname, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"[OK] Incident severity classified: {fname}")

if __name__ == "__main__":
    main()
