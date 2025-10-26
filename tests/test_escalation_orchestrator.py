import json, os
from pathlib import Path
from fraud.escalation_orchestrator import classify_escalations, make_notification, write_notification

def create_plan(path):
    p = {"plan": [
        {"missing_item":"fria","action":"provide fria","priority":1},
        {"missing_item":"mitigations","action":"document mitigations","priority":2},
        {"note":"no_missing_evidence","action":"monitor","priority":5}
    ]}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(p, fh)
    return p

def test_classify_and_notify(tmp_path):
    plan_file = tmp_path / "plan.json"
    create_plan(str(plan_file))
    plan_obj = json.load(open(str(plan_file), "r", encoding="utf-8"))
    classified = classify_escalations(plan_obj, str(plan_file))
    # we expect at least two escalations (priority 1 and 2)
    assert classified["summary"]["escalations"] >= 2
    notif = make_notification(classified, "ops@bank.local", str(plan_file))
    out = write_notification(notif)
    assert os.path.exists(out)
    loaded = json.load(open(out, "r", encoding="utf-8"))
    assert "signature_hash" in loaded
    Path(out).unlink()
