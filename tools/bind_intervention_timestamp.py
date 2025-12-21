#!/usr/bin/env python3
"""
Bind an intervention event to the public timestamp log (Rev 7.1).
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(".")
LOGS = ROOT / "logs"

INTERVENTION_FILE = LOGS / "intervention_event_rev7_1.json"
TIMESTAMP_LOG = LOGS / "public_timestamp.ndjson"

def canonical_bytes(obj: dict) -> bytes:
    return (
        json.dumps(obj, sort_keys=True, separators=(",", ":"))
        .encode("utf-8") + b"\n"
    )

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main():
    if not INTERVENTION_FILE.exists():
        print("Missing intervention file:", INTERVENTION_FILE)
        return 1

    intervention = json.loads(
        INTERVENTION_FILE.read_text(encoding="utf-8")
    )

    canon = canonical_bytes(intervention)
    h = sha256_hex(canon)

    entry = {
        "artifact_type": "intervention_event",
        "artifact_id": intervention["intervention_id"],
        "hash_sha256": h,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_version": "Qv-7.1",
        "eu_single_entry_point": intervention["eu_single_entry_point"]
    }

    TIMESTAMP_LOG.parent.mkdir(exist_ok=True)
    with TIMESTAMP_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")

    print("Intervention bound to public timestamp log.")
    print("Hash:", h)
    return 0

if __name__ == "__main__":
    sys.exit(main())
