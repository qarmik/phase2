#!/usr/bin/env python3
"""
tools/log_replay.py
Validate append-only public_timestamp.ndjson chain.
Outputs a summary CSV to stdout.

Usage:
  python tools/log_replay.py
"""
from pathlib import Path
import json, base64, hashlib, subprocess, tempfile, sys

ROOT = Path(__file__).resolve().parents[1]
ND = ROOT / "logs" / "public_timestamp.ndjson"
KEYS = ROOT / "keys"

def canonical_bytes(entry):
    e = dict(entry)
    e.pop("signature_b64", None)
    return (json.dumps(e, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")

def sha256(b): return hashlib.sha256(b).hexdigest()

def verify_openssl(entry_bytes, signature_b64, signer):
    pub = KEYS / f"{signer}.pub.pem"
    if not pub.exists(): return False, "no_pub"
    sig = base64.b64decode(signature_b64)
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(entry_bytes); tf.flush(); entry_path = tf.name
    with tempfile.NamedTemporaryFile(delete=False) as ts:
        ts.write(sig); ts.flush(); sig_path = ts.name
    try:
        p = subprocess.run(["openssl","dgst","-sha256","-verify", str(pub), "-signature", sig_path, entry_path],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ok = (p.returncode == 0)
        out = p.stdout.decode().strip() + (";"+p.stderr.decode().strip() if p.stderr else "")
    finally:
        try: Path(sig_path).unlink(); Path(entry_path).unlink()
        except: pass
    return ok, out

def verify_hmac(entry_bytes, signature_b64, signer):
    secret_path = KEYS / f"{signer}.hmac.secret"
    if not secret_path.exists():
        return False, "no_hmac_secret"
    import hmac
    secret = secret_path.read_text().strip().encode()
    expected = hmac.new(secret, entry_bytes, digestmod=hashlib.sha256).digest()
    try:
        ok = base64.b64decode(signature_b64) == expected
    except Exception as e:
        return False, "hmac_decode_err"
    return ok, "hmac_ok" if ok else "hmac_mismatch"

def main():
    if not ND.exists():
        print("No NDJSON found:", ND, file=sys.stderr); sys.exit(2)
    lines = ND.read_text(encoding="utf-8").strip().splitlines()
    prev_hash = ""
    print("idx,artifact_id,entry_hash_ok,computed_entry_hash,entry_hash,prev_ok,prev_entry_hash,signature_method,signature_ok,signer,signer_pub_fpr,notes")
    for i, line in enumerate(lines):
        try:
            e = json.loads(line)
        except Exception as ex:
            print(f"{i},,,bad_json,,,,,,,{ex}")
            continue
        artifact = e.get("artifact_id","")
        entry_hash = e.get("entry_hash","")
        computed_hash = sha256(canonical_bytes(e))
        entry_hash_ok = (computed_hash == entry_hash)
        prev_ok = (e.get("prev_entry_hash","") == prev_hash) if i>0 else (e.get("prev_entry_hash","") == "" or e.get("prev_entry_hash") is None)
        sig_method = e.get("signature_method","")
        signer_fpr = e.get("signer_pub_fingerprint_sha256","")
        signer = None
        # Guess signer name from fingerprint by matching keys/*pub.pem
        for p in (KEYS.glob("*.pub.pem")):
            try:
                der = subprocess.run(["openssl","pkey","-pubin","-in",str(p),"-outform","DER"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                fp = hashlib.sha256(der.stdout).hexdigest()
                if fp == signer_fpr:
                    signer = p.stem  # filename without ext
                    break
            except:
                continue
        sig_ok = ""
        notes = ""
        if sig_method == "openssl":
            if signer is None:
                sig_ok = "no_matching_pub"
            else:
                ok, out = verify_openssl(canonical_bytes(e), e.get("signature_b64",""), signer)
                sig_ok = "ok" if ok else "fail"
                notes = out.replace(",", ";")
        elif sig_method == "hmac":
            signer = signer or e.get("signer") or "unknown"
            ok, out = verify_hmac(canonical_bytes(e), e.get("signature_b64",""), signer)
            sig_ok = "ok" if ok else "fail"
            notes = out
        else:
            sig_ok = "unknown_method"
        print(f"{i},{artifact},{entry_hash_ok},{computed_hash},{entry_hash},{prev_ok},{e.get('prev_entry_hash','')},{sig_method},{sig_ok},{signer or ''},{signer_fpr},{notes}")
        prev_hash = entry_hash
    return

if __name__ == '__main__':
    main()
