# tests/test_verify_monitorability_tfidf.py
import json
from pathlib import Path
from tools.verify_monitorability import verify_monitorability


def test_tfidf_faithfulness(tmp_path):
    trace = {
        "artifact_id": "CI-FAITH-TFIDF",
        "model_output_text": "The transaction was flagged for review due to high risk.",
        "explanation_text": "High risk transaction flagged for manual review.",
    }
    monitor = []

    trace_path = tmp_path / "trace.jsonld"
    monitor_path = tmp_path / "monitor.json"
    out_path = tmp_path / "out.jsonld"
    trace_path.write_text(json.dumps(trace))
    monitor_path.write_text(json.dumps(monitor))

    code = verify_monitorability(trace_path, monitor_path, out_path)
    result = json.loads(out_path.read_text())

    assert code == 0
    assert 0.4 < result["faithfulness_score_tfidf"] <= 1.0
    assert not result["qvm_alert"]
