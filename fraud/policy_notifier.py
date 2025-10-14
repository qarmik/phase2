#!/usr/bin/env python3
"""
policy_notifier.py
Map scoring reasons to policy clauses and emit a tamper-evident notification bundle.

Usage (from phase2/):
  python fraud/policy_notifier.py --score-file sample_score.json --notify-to compliance@bank.local --dpia-ref ../artifacts/evidence/dpia_YYYY.json

Outputs:
  - prints notification JSON to stdout
  - writes notification bundle to phase2/artifacts/notifications/notification_<ts>.json
Notes:
  - Chains to last intervention_log signature for tamper-evidence.
  - Uses only stdlib.
"""
from __future__ import annotations
import argparse
import json
import os
import hashlib
import datetime
from typing import Dict, Any, List

ARTIFACT_ID = "fraud_v1"
MODEL_VERSION = "v0.2"
EVIDENCE_NOTIF_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/notifications")
INTERVENTION_LOG = os.path.join(os.path.dirname(__file__), "intervention_log.ndjson")
os.makedirs(EVIDENCE_NOTIF_DIR, exist_ok=True)


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def load_score(path: str) -> Dict[str, Any]:
    with open(path, "r") as fh:
        payload = json.load(fh)
    if "score" in payload and isinstance(payload["score"], dict):
        return payload["score"]
    return payload


def last_intervention_signature() -> str:
    if not os.path.exists(INTERVENTION_LOG):
        return ""
    with open(INTERVENTION_LOG, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return ""
    last = json.loads(lines[-1])
    return last.get("signature_hash", "")


# Minimal policy mapping table (extend as required)
POLICY_MAP: Dict[str, List[str]] = {
    "high_amount": [
        "RBI: Lending Prudence Clause - enhanced verification required",
        "EU AI Act: High-risk financial scoring - human oversight required"
    ],
    "country_high_risk": [
        "AML: Country risk screening required (KYC)",
        "EU AI Act: High-risk cross-border profiling"
    ],
    "age_edge": [
        "Consumer Protection: age-specific consent & product suitability checks"
    ],
    "previous_fraud_flag": [
        "Internal Fraud Policy: prior incidents require manual adjudication",
        "Insurer Guidance: evidence required for liability underwriting"
    ]
}


def map_reasons_to_policies(reasons: List[str]) -> Dict[str, List[str]]:
    mapped = {}
    for r in reasons:
        mapped[r] = POLICY_MAP.get(r, ["No specific policy mapping; consider manual review"])
    return mapped


def generate_notification(score_obj: Dict[str, Any], to_address: str, dpia_ref: str | None = None) -> Dict[str, Any]:
    now_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    input_hash = sha256_text(json.dumps(score_obj.get("raw", {}), sort_keys=True))
    output_hash = sha256_text(json.dumps({"score": score_obj.get("score"), "reasons": score_obj.get("reasons")}, sort_keys=True))
    prev_sig = last_intervention_signature()
    # Notification signature chains prev_sig + input_hash + output_hash + to_address
    signature = sha256_text(prev_sig + input_hash + output_hash + to_address)
    policies = map_reasons_to_policies(score_obj.get("reasons", []))
    bundle = {
        "artifact_id": ARTIFACT_ID,
        "model_version": MODEL_VERSION,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "to": to_address,
        "score": score_obj.get("score"),
        "reasons": score_obj.get("reasons"),
        "policies": policies,
        "dpia_ref": dpia_ref or "",
        "prev_intervention_signature": prev_sig,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "signature_hash": signature,
    }
    return bundle


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--score-file", required=True, help="Path to score JSON (or wrapper)")
    p.add_argument("--notify-to", required=True, help="Notification recipient (email or team id placeholder)")
    p.add_argument("--dpia-ref", default="", help="Relative path to DPIA/FRIA evidence")
    p.add_argument("--emit", action="store_true", help="Write notification bundle to artifacts/notifications")
    args = p.parse_args()

    score = load_score(args.score_file)
    bundle = generate_notification(score, args.notify_to, dpia_ref=args.dpia_ref or None)
    print(json.dumps(bundle, indent=2))

    if args.emit:
        fname = f"notification_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        out_path = os.path.join(EVIDENCE_NOTIF_DIR, fname)
        with open(out_path, "w") as fh:
            json.dump(bundle, fh, indent=2)
        print("\nNotification bundle written to:", out_path)
        print("bundle.signature_hash:", bundle["signature_hash"])


if __name__ == "__main__":
    main()
