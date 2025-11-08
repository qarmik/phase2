#!/usr/bin/env python3
# tools/generate_external_anchor.py
"""
Create an external anchor receipt for an asset (ZIP) and sign it with the current key.
Usage (example):
  python tools/generate_external_anchor.py --asset dist/audit_packet_EU-FRAUD-TSA-2025Q4-snapshot_20251108T183603Z.zip --signer indusv

Outputs:
 - dist/<asset>.sha256.txt          (sha file)
 - dist/<asset>.anchor_receipt.json (canonical receipt)
 - dist/<asset>.anchor_receipt.json.sig (detached RSA signature, OpenSSL)
 - logs/anchor_log.ndjson appended entry (audit trail)
"""

import argparse, hashlib, json, subprocess, base64, datetime
from pathlib import Path

def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def canonical_bytes(obj: dict):
    # canonical JSON: sorted keys, ensure_ascii=False, newline-terminated UTF-8
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return (s + "\n").encode("utf-8")

def run_openssl_sign(priv_key: Path, in_path: Path, out_sig: Path):
    # uses file-based signing (compatible with Windows+GitBash)
    p = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(priv_key), "-out", str(out_sig), str(in_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if p.returncode != 0:
        raise RuntimeError(f"OpenSSL sign failed: {p.stderr.decode().strip()}")
    return out_sig

def compute_pub_der_fingerprint(pub_pem: Path):
    p = subprocess.run(["openssl", "pkey", "-pubin", "-in", str(pub_pem), "-outform", "DER"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("OpenSSL pub->DER failed: " + p.stderr.decode().strip())
    return hashlib.sha256(p.stdout).hexdigest()

def append_anchor_log(log_path: Path, entry: dict):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", required=True, help="Path to asset to anchor (zip)")
    ap.add_argument("--signer", required=True, help="Signer id (private key = keys/<signer>.pem)")
    ap.add_argument("--outdir", default="dist", help="Output directory (default: dist)")
    args = ap.parse_args()

    asset = Path(args.asset)
    if not asset.exists():
        raise SystemExit(f"Asset missing: {asset}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    signer = args.signer
    priv = Path("keys") / f"{signer}.pem"
    pub = Path("keys") / f"{signer}.pub.pem"
    if not priv.exists() or not pub.exists():
        raise SystemExit("Signer keys not found in keys/: " + str(priv))

    # compute asset sha256
    asset_sha = sha256_file(asset)
    sha_path = outdir / (asset.name + ".sha256.txt")
    sha_path.write_text(asset_sha + "\n", encoding="utf-8")

    # compose receipt
    receipt = {
        "asset_name": asset.name,
        "asset_path": str(asset),
        "asset_sha256": asset_sha,
        "anchor_source": "self-published",         # update if uploaded to external service
        "timestamp_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "signer": signer,
        "qvm_hash": "qvm_hash:00000000-0000-0000-0000-000000000000",
    }

    # compute pub fingerprint
    receipt["signer_pub_fingerprint_sha256"] = compute_pub_der_fingerprint(pub)

    # write canonical receipt to tmp file and sign it
    receipt_path = outdir / (asset.name + ".anchor_receipt.json")
    receipt_path.write_bytes(canonical_bytes(receipt))

    sig_path = receipt_path.with_suffix(receipt_path.suffix + ".sig")
    run_openssl_sign(priv, receipt_path, sig_path)

    # also produce base64 signature (human-readable) for easier embedding if needed
    sig_b = sig_path.read_bytes()
    (receipt_path.with_suffix(".anchor_receipt.json.b64sig")).write_text(base64.b64encode(sig_b).decode("ascii") + "\n", encoding="utf-8")

    # append to logs/anchor_log.ndjson
    entry = {
        "asset": asset.name,
        "asset_sha256": asset_sha,
        "receipt": str(receipt_path),
        "signature_file": str(sig_path),
        "signer": signer,
        "signer_pub_fpr": receipt["signer_pub_fingerprint_sha256"],
        "timestamp_utc": receipt["timestamp_utc"]
    }
    append_anchor_log(Path("logs/anchor_log.ndjson"), entry)

    # Print verification guidance
    print("WROTE SHA:", sha_path)
    print("WROTE RECEIPT:", receipt_path)
    print("WROTE SIG:", sig_path)
    print("WROTE B64SIG:", receipt_path.with_suffix(".anchor_receipt.json.b64sig"))
    print("APPENDED LOG:", "logs/anchor_log.ndjson")
    print()
    print("Verify signature locally with:")
    print(f"  openssl dgst -sha256 -verify {pub} -signature {sig_path} {receipt_path}")
    print("If verification returns 'Verified OK' the anchor receipt is signed by the current key.")
    print()
    print("Next recommended steps:")
    print(" - Upload asset ZIP to your public release (if not already).")
    print(" - Attach receipt + signature to the release OR to notified-body channel.")
    print(" - Keep private key offline after signing (keys/archive/...)")

if __name__ == "__main__":
    main()
