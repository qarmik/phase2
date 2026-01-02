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
    ap.add_argument("--severity", required=True)
    ap.add_argument("--unknowns", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    unified = load_json(Path(args.unified_record))
    severity = load_json(Path(args.severity))
    unknowns = load_json(Path(args.unknowns))

    routing = {
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
        }
    }

    included = [
        "unified_incident_record",
        "incident_severity",
        "unknowns_register"
    ]

    excluded = [
        "notification_timeline",
        "legal_assessment",
        "root_cause_analysis",
        "remediation_plan"
    ]

    pack = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "regulator_handoff_pack",
        "incident_id": args.incident_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "routing": routing,
        "included_artifacts": included,
        "excluded_artifacts": excluded,
        "references": {
            "unified_record_hash": unified.get("integrity", {}).get("record_hash_sha256"),
            "severity_hash": severity.get("integrity", {}).get("severity_hash_sha256"),
            "unknowns_hash": unknowns.get("integrity", {}).get("register_hash_sha256")
        }
    }

    pack["integrity"] = {
        "handoff_pack_hash_sha256": sha256(pack)
    }

    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)

    json_name = f"{args.incident_id}_regulator_handoff_pack.json"
    with open(out_path / json_name, "w", encoding="utf-8") as f:
        json.dump(pack, f, indent=2)

    md_lines = [
        f"# Regulator Handoff Pack — {args.incident_id}",
        "",
        f"Generated: {pack['generated_at_utc']}",
        "",
        "## Routing",
        json.dumps(routing, indent=2),
        "",
        "## Included Artifacts",
        "\n".join([f"- {i}" for i in included]),
        "",
        "## Explicitly Excluded",
        "\n".join([f"- {e}" for e in excluded]),
        "",
        "## Integrity",
        f"- Pack hash (SHA-256): `{pack['integrity']['handoff_pack_hash_sha256']}`"
    ]

    md_name = f"{args.incident_id}_regulator_handoff_pack.md"
    with open(out_path / md_name, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[OK] Regulator handoff pack written: {json_name}, {md_name}")

if __name__ == "__main__":
    main()
