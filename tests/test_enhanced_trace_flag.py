# tests/test_enhanced_trace_flag.py
import json
from pathlib import Path

def test_enhanced_trace_flag_and_range():
    p = Path("logs/monitorability_trace_enhanced.jsonld")
    assert p.exists(), "Enhanced trace missing; run tools/qvm_scoring_upgrade.py (or incident_simulator)"
    j = json.loads(p.read_text(encoding="utf-8"))
    assert "faithfulness_flag" in j, "faithfulness_flag missing"
    assert j["faithfulness_flag"] in ("OK", "REVIEW", "ALERT"), "faithfulness_flag not one of OK/REVIEW/ALERT"
    assert "weighted_faithfulness" in j
    wf = float(j["weighted_faithfulness"])
    assert 0.0 <= wf <= 1.0, f"weighted_faithfulness out of range: {wf}"
