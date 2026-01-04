import json
import hashlib
import argparse
import sys
import platform
from datetime import datetime, timezone
from pathlib import Path

REFUSAL_CODES = {
    "REFUSAL_TAMPER_DETECTED",
    "REFUSAL_EVIDENCE_WITHHELD",
    "REFUSAL_SOVEREIGN_BLOCK",
    "REFUSAL_VENDOR_NONCOOP",
    "REFUSAL_OUT_OF_SCOPE",
}

def load_bytes(p: Path) -> bytes:
    with open(p, "rb") as f:
        return f.read()

def load_json(p: Path):
    return json.loads(load_bytes(p))

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def emit(report: dict, exit_code: int = 0):
    report["emitted_at_utc"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(report, indent=2, sort_keys=True))
    sys.exit(exit_code)

def refuse(incident_id: str, code: str, detail: str):
    if code not in REFUSAL_CODES:
        code = "REFUSAL_EVIDENCE_WITHHELD"
    emit({
        "schema_version": "qv_rev7_1",
        "artifact_type": "public_replay_report",
        "incident_id": incident_id,
        "replay_status": "REFUSED",
        "reason": code,
        "detail": detail,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform()
        }
    }, exit_code=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident-record", required=True)
    ap.add_argument("--bundle-hash", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    incident_path = Path(args.incident_record)
    hash_path = Path(args.bundle_hash)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    incident = load_json(incident_path)
    expected_hash = load_bytes(hash_path).decode().strip()

    incident_id = incident.get("incident_id")
    if not incident_id:
        refuse("UNKNOWN", "REFUSAL_EVIDENCE_WITHHELD", "incident_id missing")

    canonical = json.dumps(incident, sort_keys=True, separators=(",", ":")).encode()
    actual_hash = sha256_bytes(canonical)
    if actual_hash != expected_hash:
        refuse(incident_id, "REFUSAL_TAMPER_DETECTED", "incident hash mismatch")

    if incident.get("scope_frozen") is not True:
        refuse(incident_id, "REFUSAL_OUT_OF_SCOPE", "incident boundary not frozen")

    steps = incident.get("decision_steps")
    if not isinstance(steps, list):
        refuse(incident_id, "REFUSAL_EVIDENCE_WITHHELD", "decision_steps missing")

    replayed = {}
    try:
        ordered = sorted(steps, key=lambda s: s["order"])
    except Exception:
        refuse(incident_id, "REFUSAL_EVIDENCE_WITHHELD", "invalid step ordering")

    for step in ordered:
        if "id" not in step or "recorded_outcome" not in step:
            refuse(incident_id, "REFUSAL_EVIDENCE_WITHHELD", "step fields missing")
        replayed[step["id"]] = step["recorded_outcome"]

    report = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "public_replay_report",
        "incident_id": incident_id,
        "replay_status": "VERIFIED",
        "bundle_hash_sha256": expected_hash,
        "replayed_outputs": replayed,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform()
        }
    }

    out_file = out_dir / f"{incident_id}_public_replay_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    print(f"[OK] Public replay report written: {out_file}")

if __name__ == "__main__":
    main()
