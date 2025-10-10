#!/usr/bin/env python3
"""
explainability.py
Tiny Explainability Lens for fraud score artifacts.

Usage (from phase2/):
  python fraud/explainability.py --score-file path/to/score.json --emit-jsonld --dpia-ref ../artifacts/evidence/dpia_YYYY.jsonld

Outputs:
  - prints a short human explanation to stdout
  - writes JSON-LD audit bundle to phase2/artifacts/evidence/explainability_<ts>.jsonld when --emit-jsonld
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
EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/evidence")
INTERVENTION_LOG = os.path.join(os.path.dirname(__file__), "intervention_log.ndjson")
os.makedirs(EVIDENCE_DIR, exist_ok=True)


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def load_score(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        data = json.load(f)
    # Accept both raw score object or wrapper used by score_engine
    if "score" in data and isinstance(data["score"], dict):
        return data["score"]
    return data


def last_intervention_signature() -> str:
    """Read last signature_hash from intervention_log.ndjson (empty -> '')."""
    if not os.path.exists(INTERVENTION_LOG):
        return ""
    with open(INTERVENTION_LOG, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return ""
    last = json.loads(lines[-1])
    return last.get("signature_hash", "")


# Small maintainable reason->explanation mapping (extend as needed)
EXPLANATION_MAP: Dict[str, str] = {
    "high_amount": "Transaction amount exceeds configured threshold; increases probability of laundering/fraud.",
    "country_high_risk": "Origin/destination country flagged as higher risk in our country-risk map.",
    "age_edge": "Account-holder age is atypical for this product segment; may indicate risk or underage activity.",
    "previous_fraud_flag": "Customer has prior confirmed suspicious behaviour on record.",
}

DEFAULT_EXPLANATION = "Standard rule-based checks applied; human review recommended for scores above threshold."


def explain_reasons(reasons: List[str]) -> List[str]:
    """Map reasons to short human-friendly bullets."""
    bullets = []
    for r in reasons:
        bullets.append(EXPLANATION_MAP.get(r, f"Trigger: {r}"))
    if not bullets:
        bullets.append(DEFAULT_EXPLANATION)
    return bullets


def generate_jsonld(score_obj: Dict[str, Any], human_expl: List[str], dpia_ref: str | None = None) -> Dict[str, Any]:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # compute input/output hashes for bundle provenance (reuse available raw and reasons)
    input_hash = sha256_text(json.dumps(score_obj.get("raw", {}), sort_keys=True))
    output_hash = sha256_text(json.dumps({"score": score_obj.get("score"), "reasons": score_obj.get("reasons")}, sort_keys=True))
    prev_sig = last_intervention_signature()
    # bundle signature: chain prev_sig + input + output + explanation
    explain_hash = sha256_text(json.dumps(human_expl, sort_keys=True))
    signature = sha256_text(prev_sig + input_hash + output_hash + explain_hash)

    bundle = {
        "@context": "https://schema.org",
        "@type": "AuditAction",
        "artifact_id": ARTIFACT_ID,
        "model_version": MODEL_VERSION,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_hash": input_hash,
        "output_hash": output_hash,
        "score": score_obj.get("score"),
        "reasons": score_obj.get("reasons"),
        "human_explanation": human_expl,
        "dpia_ref": dpia_ref or "",
        "prev_intervention_signature": prev_sig,
        "signature_hash": signature,
    }
    return bundle


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--score-file", required=True, help="Path to score JSON (or wrapper)")
    p.add_argument("--emit-jsonld", action="store_true", help="Write JSON-LD audit bundle to artifacts/evidence")
    p.add_argument("--dpia-ref", default="", help="Relative path to DPIA/FRIA file for reference")
    args = p.parse_args()

    score = load_score(args.score_file)
    reasons = score.get("reasons", [])
    bullets = explain_reasons(reasons)

    # Print concise human explanation (2-4 bullets)
    print("Human explanation (short):")
    for b in bullets:
        print(" -", b)

    if args.emit_jsonld:
        bundle = generate_jsonld(score, bullets, dpia_ref=args.dpia_ref or None)
        fname = f"explainability_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonld"
        out_path = os.path.join(EVIDENCE_DIR, fname)
        with open(out_path, "w") as fh:
            json.dump(bundle, fh, indent=2)
        print("\nJSON-LD audit bundle written to:", out_path)
        print("bundle.signature_hash:", bundle["signature_hash"])


if __name__ == "__main__":
    main()
