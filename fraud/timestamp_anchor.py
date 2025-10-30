#!/usr/bin/env python3
"""
timestamp_anchor.py
Day 23 — External Timestamping & Notarisation stub (provider-agnostic).

Behavior (default — offline simulation):
- Reads a local timestamp file (timestamp_<ts>.txt) produced by release_checklist.
- Produces a provider receipt JSON under artifacts/reports/receipt_<ts>.json
- Receipt fields:
    - provider: string (default: "simulated-anchor")
    - receipt_id: provider-unique id (sha256 of timestamp_file + provider)
    - package: package basename
    - package_sha256: original package sha256
    - anchored_at: ISO timestamp (UTC)
    - raw_timestamp: contents of timestamp file
    - signature: sha256(provider + receipt_id + anchored_at)
- CLI supports:
    --timestamp-file (required)
    --provider (default: simulated-anchor)
    --emit (writes receipt to disk)
    --dry-run (prints JSON only)
- Designed so a real provider wrapper can be added (e.g., HTTP POST to timestamping service) without changing receipt schema.
"""
from __future__ import annotations
import argparse
import json
import os
import hashlib
import datetime
from typing import Dict

OUT_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/reports")

def load_timestamp(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def make_receipt(timestamp_file: str, provider: str) -> Dict:
    txt = load_timestamp(timestamp_file)
    # extract package and sha line if present
    pkg = None
    pkg_sha = None
    for line in txt.splitlines():
        if line.startswith("package:"):
            pkg = line.split("package:",1)[1].strip()
        if line.startswith("sha256:"):
            pkg_sha = line.split("sha256:",1)[1].strip()
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    base = provider + timestamp_file + txt + ts
    receipt_id = sha256_text(base)[:48]
    signature = sha256_text(provider + receipt_id + ts)
    return {
        "provider": provider,
        "receipt_id": receipt_id,
        "package": pkg,
        "package_sha256": pkg_sha,
        "anchored_at": ts,
        "raw_timestamp": txt,
        "signature": signature
    }

def write_receipt(receipt: Dict, out_dir: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"receipt_{ts}.json"
    out = os.path.join(out_dir, fname)
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--timestamp-file", required=True, help="Path to timestamp_<ts>.txt")
    p.add_argument("--provider", default="simulated-anchor", help="Provider id (simulated by default)")
    p.add_argument("--emit", action="store_true", help="Write receipt to artifacts/reports/")
    p.add_argument("--dry-run", action="store_true", help="Print receipt JSON only")
    args = p.parse_args()

    if not os.path.exists(args.timestamp_file):
        raise SystemExit(f"Timestamp file not found: {args.timestamp_file}")

    receipt = make_receipt(args.timestamp_file, args.provider)
    if args.dry_run:
        print(json.dumps(receipt, indent=2))
    if args.emit:
        path = write_receipt(receipt, OUT_DIR)
        print("Receipt written to:", path)
        print("receipt_id:", receipt["receipt_id"])

if __name__ == "__main__":
    main()
