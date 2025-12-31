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
    ap.add_argument("--evidence-classification", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    evidence = load_json(Path(args.evidence_classification))

    unknowns = []
    now = datetime.now(timezone.utc).isoformat()

    for item in evidence.get("evidence_items", []):
        if item.get("evidence_type") == "unknown":
            unknowns.append({
                "unknown_id": f"UNK-{item['evidence_id'][:12]}",
                "evidence_id": item["evidence_id"],
                "description": "Evidence present but not yet asserted as observed fact or inferred relation.",
                "why_unknown": item.get("confidence_note", "Unspecified uncertainty."),
                "knowable_in_principle": True,
                "declared_at_utc": now
            })

    register = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "unknowns_register",
        "incident_id": args.incident_id,
        "generated_at_utc": now,
        "unknowns": unknowns
    }

    register["integrity"] = {
        "register_hash_sha256": sha256(register)
    }

    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)

    fname = f"{args.incident_id}_unknowns_register.json"
    with open(out_path / fname, "w", encoding="utf-8") as f:
        json.dump(register, f, indent=2)

    print(f"[OK] Unknowns register written: {fname}")

if __name__ == "__main__":
    main()
