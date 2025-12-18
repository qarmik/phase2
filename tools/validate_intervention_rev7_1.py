#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path("schemas/intervention_log_rev7_1.json")

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_intervention_rev7_1.py <file.json>")
        return 2

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    instance = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(instance))

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print("-", "/".join(map(str, e.path)), ":", e.message)
        return 1

    print("Validation OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
