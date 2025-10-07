# intervention_log.py
# Stage 1 – Fraud Red-Team | Insurance Alignment Clause implementation

import json, hashlib, time
from pathlib import Path

LOG_PATH = Path("logs/immutable_intervention.jsonl")
LOG_PATH.parent.mkdir(exist_ok=True)

def sha256_str(payload: str) -> str:
    """Return SHA-256 hex digest of a string."""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_intervention(artifact_id, model_version, input_payload,
                        decision_summary, human_id, human_reason, output_payload):
    """Append one immutable record to JSONL log and return the record."""
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact_id": artifact_id,
        "model_version": model_version,
        "input_hash": sha256_str(json.dumps(input_payload, sort_keys=True)),
        "decision_summary": decision_summary,
        "human_id": human_id,
        "human_reason": human_reason,
        "output_hash": sha256_str(json.dumps(output_payload, sort_keys=True))
    }
    record["signature_hash"] = sha256_str(json.dumps(record, sort_keys=True))
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record

def verify_record(record: dict) -> bool:
    """Recompute signature_hash; return True if intact, False if tampered."""
    sig = record.get("signature_hash")
    data_copy = {k:v for k,v in record.items() if k != "signature_hash"}
    expected = sha256_str(json.dumps(data_copy, sort_keys=True))
    return sig == expected

# Quick manual test when run directly
if __name__ == "__main__":
    r = append_intervention("fraud_redteam", "v0.1",
                            {"tx_id":123,"amount":1000},
                            "flagged_suspicious", "CadetQ0", "manual review",
                            {"decision":"hold"})
    print("Record written. Hash OK:", verify_record(r))
