#!/usr/bin/env python3
"""
publication_log.py
Insurer-grade publication/timestamp generator (Rev7)
- Append-only NDJSON chain: logs/public_timestamp.ndjson
- Latest JSON-LD: logs/public_timestamp.jsonld
- File-based OpenSSL signing (robust on Windows/GitBash)
Usage:
 python tools/publication_log.py --new FRAUD-TSA-2025-001 --bundle dist/fraud_bundle.zip --incident EU_AI_ACT_ART73_0001 --signer indusv
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
KEYS = ROOT / "keys"
LOGS.mkdir(parents=True, exist_ok=True)
KEYS.mkdir(parents=True, exist_ok=True)

NDJSON_PATH = LOGS / "public_timestamp.ndjson"
JSONLD_PATH = LOGS / "public_timestamp.jsonld"
QVM_PLACEHOLDER = "qvm_hash:00000000-0000-0000-0000-000000000000"

def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def last_entry() -> Optional[dict]:
    if not NDJSON_PATH.exists():
        return None
    with open(NDJSON_PATH, "rb") as f:
        lines = f.read().strip().splitlines()
        if not lines:
            return None
        last = json.loads(lines[-1].decode("utf-8"))
        return last

def compute_entry_hash(entry_bytes: bytes) -> str:
    return hashlib.sha256(entry_bytes).hexdigest()

def pubkey_fingerprint_sha256(signer_name: str) -> Optional[str]:
    pub = KEYS / f"{signer_name}.pub.pem"
    if not pub.exists():
        return None
    # convert PEM to DER using openssl and hash DER bytes
    try:
        p = subprocess.run(["openssl", "pkey", "-pubin", "-in", str(pub), "-outform", "DER"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            return None
        der = p.stdout
        return hashlib.sha256(der).hexdigest()
    except Exception:
        return None

def sign_with_openssl(entry_bytes: bytes, signer_name: str) -> str:
    priv = KEYS / f"{signer_name}.pem"
    if not priv.exists():
        raise FileNotFoundError(f"Private key not found at {priv}. Generate with openssl.")
    # write entry to temp file and sign to temp sig file for robustness on Windows
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(entry_bytes)
        tf.flush()
        entry_path = tf.name
    sig_path = entry_path + ".sig"
    p = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(priv), "-out", str(sig_path), str(entry_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        try:
            os.remove(sig_path)
        except Exception:
            pass
        try:
            os.remove(entry_path)
        except Exception:
            pass
        raise RuntimeError(f"OpenSSL sign failed: {p.stderr.decode().strip()}")
    sig_bytes = Path(sig_path).read_bytes()
    # cleanup
    try:
        os.remove(sig_path)
        os.remove(entry_path)
    except Exception:
        pass
    return base64.b64encode(sig_bytes).decode()

def verify_with_openssl(entry_bytes: bytes, signature_b64: str, signer_name: str) -> bool:
    pub = KEYS / f"{signer_name}.pub.pem"
    if not pub.exists():
        raise FileNotFoundError(f"Public key not found at {pub}.")
    sig = base64.b64decode(signature_b64)
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(entry_bytes)
        tf.flush()
        entry_path = tf.name
    with tempfile.NamedTemporaryFile(delete=False) as ts:
        ts.write(sig)
        ts.flush()
        sig_path = ts.name
    try:
        p = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", str(pub), "-signature", sig_path, entry_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        ok = (p.returncode == 0)
    finally:
        try:
            os.remove(sig_path)
        except Exception:
            pass
        try:
            os.remove(entry_path)
        except Exception:
            pass
    return ok

def hmac_sign(entry_bytes: bytes, signer_name: str) -> str:
    secret_path = KEYS / f"{signer_name}.hmac.secret"
    if not secret_path.exists():
        import secrets
        secret = secrets.token_hex(32)
        secret_path.write_text(secret)
    secret = secret_path.read_text().strip().encode()
    import hmac
    sig = hmac.new(secret, entry_bytes, digestmod=hashlib.sha256).digest()
    return base64.b64encode(sig).decode()

def verify_hmac(entry_bytes: bytes, signature_b64: str, signer_name: str) -> bool:
    secret_path = KEYS / f"{signer_name}.hmac.secret"
    if not secret_path.exists():
        return False
    secret = secret_path.read_text().strip().encode()
    import hmac
    expected = hmac.new(secret, entry_bytes, digestmod=hashlib.sha256).digest()
    return base64.b64decode(signature_b64) == expected

def append_entry(entry: dict, signature_b64: str):
    entry["signature_b64"] = signature_b64
    entry_bytes = (json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    with open(NDJSON_PATH, "ab") as f:
        f.write(entry_bytes)
    jsonld = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "@type": "PublicationTimestamp",
        **entry,
    }
    with open(JSONLD_PATH, "w", encoding="utf-8") as f:
        json.dump(jsonld, f, indent=2, ensure_ascii=False)

def generate_entry(artifact_id: str, bundle_path: Path, incident_id: str, signer_name: str):
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")
    public_hash = sha256_of_file(bundle_path)
    prev = last_entry()
    prev_hash = prev.get("entry_hash") if prev else ""
    timestamp = iso_now()
    signer_fpr = pubkey_fingerprint_sha256(signer_name) or ""
    entry = {
        "artifact_id": artifact_id,
        "timestamp_utc": timestamp,
        "bundle_path": str(bundle_path),
        "public_hash": public_hash,
        "qv_version": "Rev7",
        "quantum_verification_hash": QVM_PLACEHOLDER,
        "incident_report_id": incident_id or "",
        "prev_entry_hash": prev_hash,
        "signer_pub_fingerprint_sha256": signer_fpr,
    }
    entry_bytes = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
    entry_hash = compute_entry_hash(entry_bytes)
    entry["entry_hash"] = entry_hash
    # recompute canonical bytes to include entry_hash (fix signing bug)
    entry_bytes = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
    # try openssl sign; fallback to hmac
    try:
        sig = sign_with_openssl(entry_bytes, signer_name)
        verify_ok = verify_with_openssl(entry_bytes, sig, signer_name)
        if not verify_ok:
            raise RuntimeError("OpenSSL signature verification failed after signing")
        method = "openssl"
    except Exception:
        sig = hmac_sign(entry_bytes, signer_name)
        verify_ok = verify_hmac(entry_bytes, sig, signer_name)
        method = "hmac"
    entry["signature_method"] = method
    return entry, sig

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--new", required=True, help="artifact id")
    p.add_argument("--bundle", required=True, help="path to release bundle (zip)")
    p.add_argument("--incident", default="", help="incident id (EU_AI_ACT_ART73 etc.)")
    p.add_argument("--signer", default="indusv", help="signer name (private key at keys/<signer>.pem)")
    args = p.parse_args()

    bundle = Path(args.bundle)
    entry, sig = generate_entry(args.new, bundle, args.incident, args.signer)
    append_entry(entry, sig)
    # simple ASCII-only prints for Windows friendliness
    print("Publication entry appended.")
    print(f" artifact_id: {entry['artifact_id']}")
    print(f" timestamp: {entry['timestamp_utc']}")
    print(f" entry_hash: {entry['entry_hash']}")
    print(f" public_hash(bundle): {entry['public_hash']}")
    print(f" signature_method: {entry['signature_method']}")
    print(f" signer_pub_fingerprint_sha256: {entry.get('signer_pub_fingerprint_sha256','')}")
    print(f" NDJSON path: {NDJSON_PATH}")
    print(f" JSON-LD path: {JSONLD_PATH}")

if __name__ == "__main__":
    main()
