#!/usr/bin/env python3
"""
verify_last_signature.py
Verify the last entry in logs/public_timestamp.ndjson using file-based OpenSSL.
Usage:
  python tools/verify_last_signature.py --signer indusv
Outputs diagnostic info (signature len, sha256, entry bytes sha256, pubkey fingerprint)
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NDJSON = ROOT / "logs" / "public_timestamp.ndjson"
KEYS = ROOT / "keys"
PUB_DEFAULT = "keys/indusv.pub.pem"

def load_last_entry():
    if not NDJSON.exists():
        print("ERROR: NDJSON not found:", NDJSON, file=sys.stderr)
        raise SystemExit(2)
    text = NDJSON.read_text(encoding="utf-8").strip()
    if not text:
        print("ERROR: NDJSON is empty", file=sys.stderr)
        raise SystemExit(2)
    last = json.loads(text.splitlines()[-1])
    return last

def compute_sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def compute_pub_fingerprint(pub_path: Path) -> str:
    if not pub_path.exists():
        return ""
    p = subprocess.run(["openssl","pkey","-pubin","-in", str(pub_path), "-outform", "DER"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return ""
    return hashlib.sha256(p.stdout).hexdigest()

def write_temp_file_bytes(b: bytes, suffix: str = "") -> Path:
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tf.write(b)
    tf.flush()
    tf.close()
    return Path(tf.name)

def run_openssl_verify(pub_path: Path, sig_path: Path, entry_path: Path):
    cmd = ["openssl", "dgst", "-sha256", "-verify", str(pub_path), "-signature", str(sig_path), str(entry_path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p

def canonical_entry_bytes(entry: dict) -> bytes:
    # Remove signature field if present
    e = dict(entry)
    e.pop("signature_b64", None)
    # canonical JSON with sort_keys True, ensure_ascii False, then append newline (matches append_entry)
    j = json.dumps(e, sort_keys=True, ensure_ascii=False)
    return (j + "\n").encode("utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signer", default="indusv", help="signer name (will use keys/<signer>.pub.pem)")
    args = ap.parse_args()

    last = load_last_entry()
    sig_b64 = last.get("signature_b64")
    sig_method = last.get("signature_method", "")
    signer_fpr = last.get("signer_pub_fingerprint_sha256","")
    artifact_id = last.get("artifact_id","<unknown>")

    print("Verifying last entry:", artifact_id)
    print(" signature_method:", sig_method)
    print(" signer_pub_fingerprint_sha256 (entry):", signer_fpr)

    if not sig_b64:
        print("ERROR: no signature_b64 found in last entry", file=sys.stderr)
        raise SystemExit(2)

    # build canonical bytes and write to temp file
    entry_bytes = canonical_entry_bytes(last)
    entry_sha = compute_sha256_bytes(entry_bytes)
    print(" entry canonical bytes SHA256:", entry_sha)
    entry_path = write_temp_file_bytes(entry_bytes, suffix=".entry")
    print(" entry temp file:", entry_path, "len:", entry_path.stat().st_size)

    # write stored signature bytes to temp file
    try:
        sig_bytes = base64.b64decode(sig_b64)
    except Exception as e:
        print("ERROR: stored signature base64 decode failed:", e, file=sys.stderr)
        raise SystemExit(2)
    sig_path = write_temp_file_bytes(sig_bytes, suffix=".sig")
    print(" stored signature bytes len:", len(sig_bytes))
    print(" stored signature sha256:", compute_sha256_bytes(sig_bytes))
    print(" signature temp file:", sig_path)

    # determine pubkey path
    pub_path = KEYS / f"{args.signer}.pub.pem"
    if not pub_path.exists():
        # fall back to default if exists
        dp = Path(PUB_DEFAULT)
        if dp.exists():
            pub_path = dp
    print(" using public key:", pub_path)
    pub_fpr = compute_pub_fingerprint(pub_path) if pub_path.exists() else ""
    print(" computed public key DER sha256:", pub_fpr)

    # run openssl verify
    print("\nRunning OpenSSL verification...")
    p = run_openssl_verify(pub_path, sig_path, entry_path)
    stdout = p.stdout.decode().strip()
    stderr = p.stderr.decode().strip()
    if stdout:
        print(" openssl stdout:", stdout)
    if stderr:
        print(" openssl stderr:", stderr)
    if p.returncode == 0:
        print("Signature verification: OK")
        rc = 0
    else:
        print("Signature verification: FAILED (returncode {})".format(p.returncode))
        rc = 3

    # cleanup temp files
    try:
        entry_path.unlink()
        sig_path.unlink()
    except Exception:
        pass

    raise SystemExit(rc)

if __name__ == "__main__":
    main()
