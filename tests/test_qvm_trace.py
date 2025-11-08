# tests/test_qvm_trace.py
import json, hashlib
from pathlib import Path

def load_json(p):
    assert p.exists(), f"{p} missing; run tools/qvm_explainability_trace.py"
    return json.loads(p.read_text(encoding="utf-8"))

def compute_qvm_hash(payload: dict) -> str:
    # same deterministic serialization used in tools/qvm_explainability_trace.py
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "qvm_hash:" + hashlib.sha256(s).hexdigest()

def test_qvm_trace_presence_and_fields():
    p = Path("logs/monitorability_trace.jsonld")
    trace = load_json(p)
    # essential fields
    for k in ("artifact_id","entry_hash","faithfulness_score","quantum_verification_hash","cot_stub"):
        assert k in trace, f"{k} missing in trace"
    # faithfulness numeric and in [0,1]
    f = trace["faithfulness_score"]
    assert isinstance(f, (int,float)), "faithfulness_score not numeric"
    assert 0.0 <= float(f) <= 1.0, f"faithfulness_score out of range: {f}"

def test_qvm_hash_recomputes():
    p = Path("logs/monitorability_trace.jsonld")
    trace = load_json(p)
    # recompute using the same sub-payload used by the tool:
    payload = {
        "artifact_id": trace.get("artifact_id"),
        "entry_hash": trace.get("entry_hash"),
        "faithfulness_score": trace.get("faithfulness_score")
    }
    expected = compute_qvm_hash(payload)
    assert trace["quantum_verification_hash"] == expected, "quantum_verification_hash mismatch; trace may be tampered"
