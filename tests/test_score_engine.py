import os
import json
import tempfile
from fraud.score_engine import automated_score, InterventionLog, generate_dpia


def test_automated_score_low():
    txn = {"amount": 50, "country": "IND", "age": 35, "previous_fraud_flag": False}
    r = automated_score(txn)
    assert isinstance(r["score"], int)
    assert 0 <= r["score"] <= 100
    assert "raw" in r

def test_automated_score_high_previous():
    txn = {"amount": 200000, "country": "XYZ", "age": 45, "previous_fraud_flag": True}
    r = automated_score(txn)
    assert r["score"] >= 80
    assert "previous_fraud_flag" in r["reasons"]

def test_intervention_log_chaining(tmp_path):
    p = tmp_path / "intervention_log.ndjson"
    log = InterventionLog(path=str(p))
    e1 = {"artifact_id": "fraud_v1", "model_version": "v0.1", "input": {"a":1}, "output": {"decision":"review"}, "decision_summary":"initial","human_id":"u1","human_reason":"ok"}
    r1 = log.append(e1)
    e2 = {"artifact_id": "fraud_v1", "model_version": "v0.1", "input": {"b":2}, "output": {"decision":"reject"}, "decision_summary":"override","human_id":"u2","human_reason":"override"}
    r2 = log.append(e2)
    assert r1["signature_hash"] != r2["signature_hash"]
    lines = [l for l in open(str(p)).read().splitlines() if l.strip()]
    assert len(lines) == 2

def test_dpia_generation_fria(tmp_path):
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    dpia = generate_dpia({"data_categories":["id","txn"], "processing_purpose":"credit_risk", "risk_summary":"high"}, fria=True)
    assert dpia["fria_included"]
    assert "fria" in dpia
    assert os.path.exists(dpia["path"])
