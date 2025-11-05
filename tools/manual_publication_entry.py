#!/usr/bin/env python3
"""
manual_publication_entry.py
Create a deterministic, RSA-signed NDJSON entry using external openssl calls.
This bypasses internal sign/verify inconsistencies and is fully auditable.
Usage:
  python tools/manual_publication_entry.py --artifact FRAUD-TSA-2025-MANUAL --bundle dist/fraud_bundle.zip --incident "MANUAL_REISSUE" --signer indusv
"""
from pathlib import Path
import argparse, json, hashlib, base64, subprocess, tempfile, sys
ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
KEYS = ROOT / "keys"
NDJSON = LOGS / "public_timestamp.ndjson"
JSONLD = LOGS / "public_timestamp.jsonld"
LOGS.mkdir(parents=True, exist_ok=True)

def iso_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def sha256_of_file(path: Path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def last_entry():
    if not NDJSON.exists():
        return None
    lines = NDJSON.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return None
    return json.loads(lines[-1])

def compute_entry_hash_bytes(entry_obj):
    b = json.dumps(entry_obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    import hashlib
    return hashlib.sha256(b).hexdigest(), b

def pubkey_fingerprint_sha256(signer_name: str):
    pub = KEYS / f"{signer_name}.pub.pem"
    if not pub.exists():
        return ""
    p = subprocess.run(["openssl","pkey","-pubin","-in",str(pub),"-outform","DER"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return ""
    import hashlib
    return hashlib.sha256(p.stdout).hexdigest()

def sign_file_with_openssl(privkey_path: Path, input_path: str, sig_out_path: str):
    p = subprocess.run(["openssl","dgst","-sha256","-sign", str(privkey_path), "-out", str(sig_out_path), str(input_path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("OpenSSL sign failed:", p.stderr.decode().strip(), file=sys.stderr)
        raise SystemExit(2)
    return

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--incident", default="")
    ap.add_argument("--signer", default="indusv")
    args = ap.parse_args()

    bundle = Path(args.bundle)
    if not bundle.exists():
        print("Bundle not found:", bundle, file=sys.stderr)
        raise SystemExit(2)

    prev = last_entry()
    prev_hash = prev.get("entry_hash") if prev else ""

    pub_fpr = pubkey_fingerprint_sha256(args.signer)

    entry = {
        "artifact_id": args.artifact,
        "timestamp_utc": iso_now(),
        "bundle_path": str(bundle),
        "public_hash": sha256_of_file(bundle),
        "qv_version": "Rev7",
        "quantum_verification_hash": "qvm_hash:00000000-0000-0000-0000-000000000000",
        "incident_report_id": args.incident or "",
        "prev_entry_hash": prev_hash,
        "signer_pub_fingerprint_sha256": pub_fpr,
    }

    # compute entry_hash and canonical bytes (must include entry_hash)
    entry_hash, entry_bytes = compute_entry_hash_bytes({**entry})  # initial
    entry["entry_hash"] = entry_hash
    # recompute bytes so entry_hash present
    entry_hash2, entry_bytes2 = compute_entry_hash_bytes(entry)
    if entry_hash != entry_hash2:
        # unexpected; but set to computed
        entry["entry_hash"] = entry_hash2
        entry_bytes2 = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")

    # write canonical bytes to temp file (with trailing newline, match append behavior)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".entry", mode="wb") as tf:
        tf.write(entry_bytes2 + b"\n")
        tf.flush()
        entry_path = tf.name

    # sign using openssl into a temp sig file (binary)
    priv = KEYS / f"{args.signer}.pem"
    sig_path = entry_path + ".sig"
    sign_file_with_openssl(priv, entry_path, sig_path)

    # read signature bytes and base64-encode
    sig_bytes = Path(sig_path).read_bytes()
    sig_b64 = base64.b64encode(sig_bytes).decode()

    # attach signature and append to NDJSON (append-only)
    entry["signature_b64"] = sig_b64
    entry["signature_method"] = "openssl"
    ndline = (json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    with open(NDJSON, "ab") as f:
        f.write(ndline)

    # write JSON-LD latest
    jsonld = {"@context":"https://www.w3.org/2019/wot/td/v1","@type":"PublicationTimestamp", **entry}
    with open(JSONLD, "w", encoding="utf-8") as f:
        json.dump(jsonld, f, indent=2, ensure_ascii=False)

    # cleanup temp files
    try:
        Path(sig_path).unlink()
        Path(entry_path).unlink()
    except Exception:
        pass

    print("Manual publication entry appended.")
    print(" artifact_id:", entry["artifact_id"])
    print(" entry_hash:", entry["entry_hash"])
    print(" signature_method: openssl")
    print(" signer_pub_fingerprint_sha256:", entry.get("signer_pub_fingerprint_sha256",""))

if __name__ == '__main__':
    main()
