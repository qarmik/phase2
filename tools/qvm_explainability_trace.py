#!/usr/bin/env python3
# tools/qvm_explainability_trace.py
# Produce a monitorability trace with a QVM stub and a simple faithfulness metric.
# Save as tools/qvm_explainability_trace.py and run from repo root.

import json, hashlib, datetime, random
from pathlib import Path

ND = Path("logs/public_timestamp.ndjson")
OUT = Path("logs/monitorability_trace.jsonld")

def load_last_entry():
    if not ND.exists():
        return None
    lines = [l for l in ND.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])

def simple_cot_stub(artifact_id):
    # deterministic pseudo-CoT for reproducibility
    seeds = {
        "fraud": [
            "Checked transaction velocity", "Matched merchant pattern", "Flagged unusual IP",
            "Applied rule: velocity>3 in 24h", "Human reviewer: reviewed receipts"
        ]
    }
    base = seeds.get("fraud", ["Model produced score","Human reviewed"])
    # select pseudo-random but stable selection using artifact_id hash
    h = int(hashlib.sha256(artifact_id.encode()).hexdigest()[:8], 16)
    random.seed(h)
    pick = random.sample(base, min(len(base), 3))
    return pick

def compute_faithfulness(decision_summary, cot):
    # naive metric: token overlap ratio
    ds_tokens = set(" ".join(decision_summary).lower().split())
    cot_tokens = set(" ".join(cot).lower().split())
    if not ds_tokens:
        return 0.0
    inter = ds_tokens.intersection(cot_tokens)
    return round(len(inter) / max(1, len(ds_tokens)), 3)

def qvm_stub_hash(payload_dict):
    # deterministic QVM stub: DER-like SHA256 of payload
    s = json.dumps(payload_dict, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "qvm_hash:" + hashlib.sha256(s).hexdigest()

def main():
    entry = load_last_entry()
    if not entry:
        print("No public_timestamp entry found. Aborting.")
        return
    artifact_id = entry.get("artifact_id","unknown")
    # build CoT stub
    cot = simple_cot_stub(artifact_id.lower())
    # decision summary guess (use fields if present)
    decision_summary = [entry.get("incident_report_id") or entry.get("bundle_path","no_bundle") , entry.get("public_hash","")]
    faith = compute_faithfulness(decision_summary, cot)
    trace = {
        "@context": "https://w3id.org/monitorability/trace/v1",
        "id": f"urn:trace:phase2:stage1:fraud:{artifact_id}:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "artifact_id": artifact_id,
        "entry_hash": entry.get("entry_hash"),
        "cot_stub": cot,
        "decision_summary": decision_summary,
        "faithfulness_score": faith,
        "qvm_version": "Rev7-stub",
        "quantum_verification_hash": qvm_stub_hash({
            "artifact_id": artifact_id,
            "entry_hash": entry.get("entry_hash"),
            "faithfulness_score": faith
        }),
        "notes": "This is a monitorability trace stub for Day-25. Use as input for auditor review."
    }
    OUT.write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"monitorability trace written: {OUT} faith={faith} qvm_hash={trace['quantum_verification_hash']}")

if __name__ == "__main__":
    main()
