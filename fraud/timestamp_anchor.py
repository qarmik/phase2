#!/usr/bin/env python3
"""
timestamp_anchor.py
Day 23 — External Timestamping & Notarisation stub (provider-agnostic).

Default mode (--simulated):
  • Reads a local timestamp_<ts>.txt produced by release_checklist.
  • Generates a simulated receipt JSON under artifacts/reports/.
  • Schema fields:
      provider, receipt_id, package, package_sha256,
      anchored_at, raw_timestamp, signature, raw_provider_response(optional)
CLI Options:
  --timestamp-file (required)
  --provider (default simulated-anchor)
  --provider-url (optional real endpoint)
  --api-key-env (env var name for provider API key)
  --emit (write receipt file)
  --dry-run (print JSON only)
"""
from __future__ import annotations
import argparse
import json
import os
import hashlib
from datetime import datetime, timezone
import urllib.request
import urllib.error
from typing import Dict, Optional

OUT_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/reports")

# ---------------------------------------------------------------------
# Basic utilities
# ---------------------------------------------------------------------
def load_timestamp(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ---------------------------------------------------------------------
# Simulated receipt generator (default mode)
# ---------------------------------------------------------------------
def make_simulated_receipt(timestamp_file: str, provider: str) -> Dict:
    txt = load_timestamp(timestamp_file)
    pkg, pkg_sha = None, None
    for line in txt.splitlines():
        if line.startswith("package:"):
            pkg = line.split("package:", 1)[1].strip()
        if line.startswith("sha256:"):
            pkg_sha = line.split("sha256:", 1)[1].strip()
    ts = datetime.now(timezone.utc).isoformat()
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

# backward-compatibility alias used by tests
def make_receipt(timestamp_file: str, provider: str) -> Dict:
    return make_simulated_receipt(timestamp_file, provider)

# ---------------------------------------------------------------------
# Receipt writer
# ---------------------------------------------------------------------
def write_receipt(receipt: Dict, out_dir: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"receipt_{ts}.json"
    out = os.path.join(out_dir, fname)
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
    return out

# ---------------------------------------------------------------------
# Provider HTTP adapter (for real anchor integration)
# ---------------------------------------------------------------------
def call_provider_http(timestamp_file: str, provider_url: str,
                       api_key: Optional[str] = None, timeout: int = 15) -> Dict:
    data = load_timestamp(timestamp_file)
    payload = json.dumps({"timestamp": data}).encode("utf-8")
    req = urllib.request.Request(provider_url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            j = json.loads(body)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Provider HTTP error: {e.code} {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Provider call failed: {e}")

    receipt = {
        "provider": j.get("provider") or provider_url,
        "receipt_id": j.get("receipt_id") or j.get("id") or j.get("tx"),
        "anchored_at": j.get("anchored_at") or j.get("timestamp") or j.get("time"),
        "signature": j.get("signature") or j.get("sig"),
        "raw_timestamp": data,
        "raw_provider_response": j,
    }

    if not (receipt["receipt_id"] and receipt["anchored_at"] and receipt["signature"]):
        raise RuntimeError(f"Provider response missing required fields: {j}")

    # package extraction
    receipt["package"] = j.get("package") or next(
        (l.split("package:", 1)[1].strip() for l in data.splitlines() if l.startswith("package:")),
        None,
    )
    receipt["package_sha256"] = j.get("package_sha256") or j.get("sha256") or next(
        (l.split("sha256:", 1)[1].strip() for l in data.splitlines() if l.startswith("sha256:")),
        None,
    )
    return receipt

# ---------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--timestamp-file", required=True, help="Path to timestamp_<ts>.txt")
    p.add_argument("--provider", default="simulated-anchor", help="Provider id (simulated by default)")
    p.add_argument("--provider-url", help="Optional provider URL to POST timestamp to (overrides simulated)")
    p.add_argument("--api-key-env", default="TIMESTAMP_PROVIDER_API_KEY", help="Env var name for provider API key")
    p.add_argument("--emit", action="store_true", help="Write receipt to artifacts/reports/")
    p.add_argument("--dry-run", action="store_true", help="Print receipt JSON only")
    args = p.parse_args()

    if not os.path.exists(args.timestamp_file):
        raise SystemExit(f"Timestamp file not found: {args.timestamp_file}")

    # Build simulated receipt first
    sim_receipt = make_simulated_receipt(args.timestamp_file, args.provider)

    # Dry-run prints simulated receipt
    if args.dry_run:
        print(json.dumps(sim_receipt, indent=2))
        return

    # Real provider path
    if args.provider_url:
        api_key = os.environ.get(args.api_key_env)
        try:
            prov_receipt = call_provider_http(args.timestamp_file, args.provider_url, api_key=api_key)
        except Exception as e:
            raise SystemExit(f"Provider anchoring failed: {e}")
        if args.emit:
            out = write_receipt(prov_receipt, OUT_DIR)
            print("Provider receipt written to:", out)
            print("receipt_id:", prov_receipt["receipt_id"])
        else:
            print(json.dumps(prov_receipt, indent=2))
        return

    # Simulated write
    if args.emit:
        path = write_receipt(sim_receipt, OUT_DIR)
        print("Receipt written to:", path)
        print("receipt_id:", sim_receipt["receipt_id"])
    else:
        print(json.dumps(sim_receipt, indent=2))

if __name__ == "__main__":
    main()
