# tests/test_qvm_scoring_upgrade.py
import json
from pathlib import Path

def test_enhanced_trace_fields():
    p = Path("logs/monitorability_trace_enhanced.jsonld")
    assert p.exists(), "Enhanced trace missing; run tools/qvm_scoring_upgrade.py first."
    j = json.loads(p.read_text(encoding="utf-8"))
    for key in ("weighted_faithfulness", "faithfulness_flag", "feature_details"):
        assert key in j, f"{key} missing from enhanced trace."
    assert isinstance(j["weighted_faithfulness"], (int,float))
    assert j["faithfulness_flag"] in ("OK", "REVIEW", "ALERT"), "Invalid faithfulness_flag value."
    # numeric range guard
    wf = float(j["weighted_faithfulness"])
    assert 0.0 <= wf <= 1.0, f"weighted_faithfulness out of range: {wf}"
    print(f"faithfulness_flag={j['faithfulness_flag']} weighted_faith={wf}")
