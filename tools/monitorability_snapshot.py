#!/usr/bin/env python3
"""
tools/monitorability_snapshot.py
Produce a monitorability JSON-LD snapshot from logs/public_timestamp.ndjson.
Outputs: logs/monitorability_snapshot.jsonld and prints a one-line summary.
"""
from pathlib import Path
import json, datetime, hashlib

ND = Path("logs/public_timestamp.ndjson")
OUT = Path("logs/monitorability_snapshot.jsonld")
PUB = Path("keys/indusv.pub.pem")

def load_ndjson(path):
    if not path.exists():
        return []
    lines = [l for l in path.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
    return [json.loads(l) for l in lines]

def safe_iso(ts):
    return ts if ts else None

def compute_bundle_digest(bundle_path):
    p = Path(bundle_path)
    if not p.exists():
        return None
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    entries = load_ndjson(ND)
    total = len(entries)
    qv_count = sum(1 for e in entries if e.get("qv_version"))
    sig_present = all(bool(e.get("signature_b64")) for e in entries) if entries else False
    last_ts = None
    if entries:
        last_ts = entries[-1].get("timestamp_utc") or entries[-1].get("timestamp")
    # sample public key fingerprint (DER-SHA256)
    pub_fpr = None
    if PUB.exists():
        import subprocess,hashlib,tempfile
        p = subprocess.run(["openssl","pkey","-pubin","-in",str(PUB),"-outform","DER"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode == 0:
            pub_fpr = hashlib.sha256(p.stdout).hexdigest()
    snapshot = {
        "@context": "https://w3id.org/monitorability/context/v1",
        "id": f"urn:monitorability:phase2:stage1:fraud:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "repo": "qarmik/phase2",
        "branch": "stage1/fraud",
        "total_public_timestamp_entries": total,
        "entries_with_qv_version": qv_count,
        "all_entries_have_signature": sig_present,
        "last_entry_timestamp_utc": safe_iso(last_ts),
        "signer_public_key_fingerprint_der_sha256": pub_fpr,
        "sample_bundle_public_hash": compute_bundle_digest("dist/fraud_bundle.zip") or "",
        "notes": "Snapshot produced by tools/monitorability_snapshot.py under Protocol Qv Rev 7"
    }
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"monitorability snapshot written: {OUT}  entries={total} qv={qv_count} sigs_all={sig_present} last_ts={safe_iso(last_ts)}")

if __name__ == "__main__":
    main()
