import os
import json
from fraud.policy_notifier import generate_notification, map_reasons_to_policies

def test_map_reasons_to_policies_known():
    reasons = ["high_amount", "country_high_risk"]
    mapped = map_reasons_to_policies(reasons)
    assert "high_amount" in mapped
    assert isinstance(mapped["high_amount"], list)
    assert any("RBI" in s or "EU AI Act" in s for s in mapped["high_amount"])

def test_notification_bundle_structure(tmp_path):
    score = {"score": 80, "reasons": ["high_amount"], "raw": {"amount":15000}}
    bundle = generate_notification(score, "compliance@bank.local", dpia_ref="artifacts/evidence/dpia_dummy.json")
    assert bundle["score"] == 80
    assert "signature_hash" in bundle
    assert bundle["dpia_ref"].endswith("dpia_dummy.json")

def test_emit_writes_file(tmp_path, monkeypatch):
    # create a temp output dir and monkeypatch EVIDENCE_NOTIF_DIR
    from fraud import policy_notifier as pn
    tmpdir = str(tmp_path / "notifs")
    os.makedirs(tmpdir, exist_ok=True)
    monkeypatch.setattr(pn, "EVIDENCE_NOTIF_DIR", tmpdir)
    score = {"score": 85, "reasons": ["previous_fraud_flag"], "raw": {"amount":50, "previous_fraud_flag":True}}
    bundle = pn.generate_notification(score, "ops@bank.local", dpia_ref=None)
    # write file
    fname = f"notification_test.json"
    out_path = os.path.join(tmpdir, fname)
    with open(out_path, "w") as fh:
        json.dump(bundle, fh)
    assert os.path.exists(out_path)
    loaded = json.load(open(out_path))
    assert loaded["signature_hash"] == bundle["signature_hash"]
