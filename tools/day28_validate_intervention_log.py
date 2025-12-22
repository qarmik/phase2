#!/usr/bin/env python3
"""
Day 28 — Intervention Log Validator (Protocol Qv Rev 7.1)

Validates an intervention log INSTANCE against REQUIRED fields.
This is a structural gate, not a full JSON Schema validator.
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "schema_version",
    "intervention_id",
    "timestamp_utc",
    "human_accountable",
    "decision_summary",
    "eu_single_entry_point",
]

def main():
    if len(sys.argv) != 3:
        print("USAGE:")
        print("  python tools/day28_validate_intervention_log.py <log.json> <schema.json>")
        return 2

    log_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2])  # intentionally unused (structural gate only)

    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        return 2

    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}")
        return 2

    # --- LOAD LOG INSTANCE ---
    try:
        log_data = json.loads(log_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in log file: {e}")
        return 2

    # --- DEBUG LINE (THIS IS WHAT WE WERE TALKING ABOUT) ---
    print("DEBUG log_data keys:", list(log_data.keys()))

    # --- STRUCTURAL VALIDATION ---
    missing = [f for f in REQUIRED_FIELDS if f not in log_data]

    if missing:
        print("INVALID intervention log")
        print("Missing fields:", missing)
        return 1

    print("Intervention log structure: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
