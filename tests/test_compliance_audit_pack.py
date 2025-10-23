import json
import os
from pathlib import Path
from compliance_audit_pack import evaluate_evidence, write_report

def test_evaluate_dpia_tmp(tmp_path):
    dpia = {
        "data_categories": ["txn"],
        "processing_purpose": "fraud_scoring",
        "risk_summary": "high",
        "mitigations": ["human_review"],
        "lawful_basis": "legitimate_interest",
        "fria_included": True
    }
    f = tmp_path / "dpia.json"
    f.write_text(json.dumps(dpia))
    report = evaluate_evidence(str(f), input_type="dpia", iso_map=True)
    assert report["risk_level"] == "high"
    assert "fria" in report["findings"]["present"]

def test_evaluate_log_tmp(tmp_path):
    # create a minimal intervention log ndjson
    logp = tmp_path / "intervention_log.ndjson"
    entry = {"timestamp":"ts","artifact_id":"fraud_v1","model_version":"v0.2","input_hash":"ih","output_hash":"oh","signature_hash":"sig"}
    logp.write_text(json.dumps(entry)+"\n")
    report = evaluate_evidence(str(logp), input_type="log")
    assert report["risk_level"] in ("medium","high")
    assert report["findings"]["last_signature_present"] is True

def test_write_report(tmp_path):
    rpt = {"a":1}
    out = write_report(rpt)
    assert os.path.exists(out)
    # cleanup created file
    Path(out).unlink()
