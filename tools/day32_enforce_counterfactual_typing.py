import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
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
    ap.add_argument("--responsibility-lattice", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lattice = load_json(Path(args.responsibility_lattice))

    counterfactuals = [
        {
            "counterfactual_id": "CF-001",
            "statement": "The model should have overridden itself before flagging the transaction.",
            "classification": "rejected_counterfactual",
            "reason": "institutionally_impossible"
        },
        {
            "counterfactual_id": "CF-002",
            "statement": "The Risk Officer could have stopped the automated decision.",
            "classification": "accepted_counterfactual",
            "reason": None
        },
        {
            "counterfactual_id": "CF-003",
            "statement": "The customer should have avoided the transaction.",
            "classification": "rejected_counterfactual",
            "reason": "victim_blame"
        }
    ]

    output = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "counterfactual_typing",
        "incident_id": args.incident_id,
        "evaluated_against": lattice["intervention_id"],
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "counterfactuals": counterfactuals
    }

    output["counterfactual_hash_sha256"] = sha256(output)

    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)

    fname = f"{args.incident_id}_counterfactuals.json"
    with open(out_path / fname, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"[OK] Counterfactual typing written: {fname}")

if __name__ == "__main__":
    main()
