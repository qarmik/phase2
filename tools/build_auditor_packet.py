#!/usr/bin/env python3
# tools/build_auditor_packet.py
# Build an auditor packet (zip) ready for release attachment & external attest.
# Save as tools/build_auditor_packet.py and run from repo root.
#
# Output:
#  - dist/audit_packet_<TAG>.zip
#  - dist/audit_packet_<TAG>.zip.sha256.txt
#  - logs/audit_manifest_<TAG>.json (local summary)
#
# Behavior: non-destructive. Copies files from logs -> docs/snapshot for tracked evidence.

import json, hashlib, zipfile, shutil, os
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
DIST = ROOT / "dist"
DOCS = ROOT / "docs"
LOGS = ROOT / "logs"
KEYS = ROOT / "keys"

TAG = "EU-FRAUD-TSA-2025Q4-snapshot"  # keep consistent with your tag
TS = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
OUTNAME = f"audit_packet_{TAG}_{TS}.zip"
OUTZIP = DIST / OUTNAME
SHAOUT = DIST / (OUTNAME + ".sha256.txt")
MANIFEST = LOGS / f"audit_manifest_{TAG}_{TS}.json"

# Files we will include (only tracked or docs copies)
INCLUDE = [
    # docs & release notes
    DOCS / "release_note_DAY24_SNAPSHOT_SIGNED.md",
    DOCS / "forensic_annex_DAY24_REV7.md",
    DOCS / "42001-mapping.md",
    DOCS / "for_notified_body.md",
    DOCS / "key_reconciliation_template.md",
    # tracked key index & public key
    KEYS / "key_index.json",
    KEYS / "indusv.pub.pem",
    # traces and enhanced traces (from logs; we'll copy into docs_snapshot first)
    LOGS / "monitorability_trace.jsonld",
    LOGS / "monitorability_trace_enhanced.jsonld",
    LOGS / "public_timestamp.ndjson",
    LOGS / "public_timestamp.jsonld",
    # intervention logs + simulator outputs
    LOGS / "intervention_log.json",
    LOGS / "intervention_events.ndjson",
    LOGS / "replay_summary.csv",
    LOGS / "find_canonical_deep.txt",
    LOGS / "verification_annotations.json",
]

def ensure_dist():
    DIST.mkdir(parents=True, exist_ok=True)

def collect_files():
    # collect actual existing files only, and prepare a doc-visible snapshot folder
    snapshot = ROOT / "docs" / "snapshot_logs"
    if snapshot.exists():
        shutil.rmtree(snapshot)
    snapshot.mkdir(parents=True, exist_ok=True)
    collected = []
    for p in INCLUDE:
        if p.exists():
            # copy into snapshot for any logs (so auditors can see them in docs)
            if str(p).startswith(str(LOGS)):
                dest = snapshot / p.name
                shutil.copy2(p, dest)
                collected.append(dest)
            else:
                collected.append(p)
    return collected, snapshot

def write_manifest(collected):
    m = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tag": TAG,
        "files": [str(p.relative_to(ROOT)) for p in collected],
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=2), encoding="utf-8")
    return MANIFEST

def build_zip(collected, manifest):
    ensure_dist()
    with zipfile.ZipFile(OUTZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # include manifest at top-level
        z.write(manifest, manifest.name)
        for p in collected:
            if p.exists():
                z.write(p, p.name)
    # compute sha256
    h = hashlib.sha256(OUTZIP.read_bytes()).hexdigest()
    SHAOUT.write_text(f"{h}  {OUTZIP.name}\n", encoding="utf-8")
    return OUTZIP, SHAOUT, h

def main():
    print("Building auditor packet...")
    collected, snapshot = collect_files()
    manifest = write_manifest(collected + [snapshot])
    outzip, shaout, sha = build_zip(collected, manifest)
    print("Created", outzip)
    print("SHA-256:", sha)
    print("SHA file:", shaout)
    print("Manifest:", manifest)
    print("\nNext steps (recommended):")
    print("1) Upload", outzip.name, "to GitHub Release (attach to tag).")
    print("2) Paste SHA-256 into docs/release_note_DAY24_SNAPSHOT_SIGNED.md under SHA-256 line.")
    print("3) Share docs/for_notified_body.md with notified body (email + attach audit packet link).")
    # record a small local note
    note = {
        "packet": outzip.name,
        "sha256": sha,
        "manifest": str(manifest),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    (DIST / f"audit_record_{TAG}_{TS}.json").write_text(json.dumps(note, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
