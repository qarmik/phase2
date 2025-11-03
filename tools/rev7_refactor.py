#!/usr/bin/env python3
"""
rev7_refactor.py — simple checker / fixer for Protocol Qv Rev 7 (Draft 0.1)

Checks:
 - README.md contains Protocol-Version and classification
 - schemas/intervention_log.json exists
 - schemas/evidence_package.json exists
 - COMPLIANCE_MAPPING.md exists

Optional auto-fix: --fix will prepend header to README.md if missing.

Usage:
  python tools/rev7_refactor.py           # run checks
  python tools/rev7_refactor.py --fix     # apply simple fixes
"""
from __future__ import annotations
import argparse, sys, os, json

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
README = os.path.join(REPO_ROOT, "README.md")
SCHEMA1 = os.path.join(REPO_ROOT, "schemas", "intervention_log.json")
SCHEMA2 = os.path.join(REPO_ROOT, "schemas", "evidence_package.json")
MAPPING = os.path.join(REPO_ROOT, "COMPLIANCE_MAPPING.md")

HEADER_LINES = [
    "Protocol-Version: Qv Rev 7 (Draft 0.1)",
    "classification: EXTERNAL-INDUSTRY",
    ""
]

def file_has_header(path: str) -> bool:
    if not os.path.exists(path): return False
    with open(path, "r", encoding="utf-8") as fh:
        head = [next(fh).rstrip("\n") for _ in range(3)]
    return HEADER_LINES[0] in head[0] or HEADER_LINES[0] in "".join(head)

def prepend_header(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        body = fh.read()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(HEADER_LINES) + body)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fix", action="store_true")
    args = p.parse_args()

    errs = []
    # README header
    if not file_has_header(README):
        errs.append("README.md missing Protocol-Version header.")
        if args.fix:
            if os.path.exists(README):
                prepend_header(README)
                print("Prepended header to README.md")
            else:
                with open(README, "w", encoding="utf-8") as fh:
                    fh.write("\n".join(HEADER_LINES) + "# Project\n")
                print("Created README.md with header")

    # schemas
    for f in (SCHEMA1, SCHEMA2):
        if not os.path.exists(f):
            errs.append(f"Missing schema: {os.path.relpath(f,REPO_ROOT)}")

    # compliance mapping
    if not os.path.exists(MAPPING):
        errs.append("Missing COMPLIANCE_MAPPING.md")

    if errs:
        print("REV7 CHECK: issues found:")
        for e in errs:
            print(" -", e)
        sys.exit(2)
    print("REV7 CHECK: all required files present.")
    return 0

if __name__ == "__main__":
    main()
