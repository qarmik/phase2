#!/usr/bin/env python3
"""
notified_body_packager.py
Automated Notified-Body Packaging stub.

Behavior:
- Collects selected evidence files (compliance_report_*.json, risk_matrix_*.jsonld, sla_dashboard_*.json)
- Builds a timestamped zip bundle: notified_body_package_<ts>.zip
- Includes a manifest.json inside the zip with:
  - list of included files (basename, sha256, size)
  - generated_at timestamp
  - package_signature (sha256 of concatenated file hashes + ts)
- CLI: --reports-dir, --out-dir, --include (comma-separated patterns), --emit

Design constraints:
- Deterministic, uses stdlib only.
- Produces a zip safe for upload to notified-body or regulator portal.
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
import hashlib
import zipfile
from typing import List, Dict, Any

REPORTS_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "../artifacts/reports")
OUT_DIR_DEFAULT = REPORTS_DIR_DEFAULT
DEFAULT_PATTERNS = ["compliance_report_", "risk_matrix_", "sla_dashboard_"]

def list_matching_files(reports_dir: str, patterns: List[str]) -> List[str]:
    out = []
    try:
        for f in sorted(os.listdir(reports_dir)):
            for p in patterns:
                if f.startswith(p):
                    out.append(os.path.join(reports_dir, f))
                    break
    except FileNotFoundError:
        pass
    return out

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def build_manifest(file_paths: List[str]) -> Dict[str, Any]:
    entries = []
    concat_hashes = ""
    for p in file_paths:
        b = os.path.basename(p)
        s = os.path.getsize(p)
        h = file_sha256(p)
        entries.append({"file": b, "size": s, "sha256": h})
        concat_hashes += h
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    package_sig = hashlib.sha256((concat_hashes + ts).encode("utf-8")).hexdigest()
    manifest = {"generated_at": ts, "entries": entries, "package_signature": package_sig}
    return manifest

def write_package(file_paths: List[str], out_dir: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    zip_name = os.path.join(out_dir, f"notified_body_package_{ts}.zip")
    manifest = build_manifest(file_paths)
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        # add files
        for p in file_paths:
            zf.write(p, arcname=os.path.basename(p))
        # add manifest
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
    return zip_name, manifest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reports-dir", default=REPORTS_DIR_DEFAULT, help="Directory with reports")
    p.add_argument("--out-dir", default=OUT_DIR_DEFAULT, help="Where to write package")
    p.add_argument("--include", help="Comma-separated filename prefixes to include (overrides defaults)")
    p.add_argument("--emit", action="store_true", help="Write package to disk")
    args = p.parse_args()

    patterns = DEFAULT_PATTERNS
    if args.include:
        patterns = [x.strip() for x in args.include.split(",") if x.strip()]
    files = list_matching_files(args.reports_dir, patterns)
    print("Files matched:", [os.path.basename(x) for x in files])
    if not files:
        print("No matching files found. Exiting.")
        return

    zip_path, manifest = write_package(files, args.out_dir)
    print("Package written to:", zip_path)
    print("Package signature:", manifest["package_signature"])

if __name__ == "__main__":
    main()
