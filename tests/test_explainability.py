import os
import json
from fraud.explainability import explain_reasons, generate_jsonld, sha256_text

def test_explain_reasons_mapping():
    reasons = ["high_amount", "country_high_risk"]
    bullets = explain_reasons(reasons)
    assert any("amount" in b.lower() for b in bullets)
    assert any("country" in b.lower() for b in bullets)

def test_generate_jsonld_structure(tmp_path, monkeypatch):
    # create a simple score object
    score = {"score": 75, "reasons": ["high_amount"], "raw": {"amount":15000}}
    # ensure intervention log absent or empty for deterministic test
    # monkeypatch last_intervention_signature by setting env: create empty log file
    logp = os.path.join(os.getcwd(), "fraud", "intervention_log.ndjson")
    if os.path.exists(logp):
        os.remove(logp)
    bundle = generate_jsonld(score, ["explain"], dpia_ref="artifacts/evidence/dpia_dummy.json")
    assert "signature_hash" in bundle
    assert bundle["dpia_ref"].endswith("dpia_dummy.json")

def test_json_hash_changes_with_explanation():
    score = {"score": 75, "reasons": ["high_amount"], "raw": {"amount":15000}}
    b1 = generate_jsonld(score, ["explain A"], dpia_ref=None)["signature_hash"]
    b2 = generate_jsonld(score, ["explain B"], dpia_ref=None)["signature_hash"]
    assert b1 != b2
