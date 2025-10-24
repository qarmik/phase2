import os, json
from pathlib import Path
from fraud.remediation_planner import plan_remediations, write_plan

def test_plan_with_missing_items(tmp_path):
    findings = {"missing": ["fria", "mitigations", "data_categories"]}
    plan = plan_remediations(findings)
    assert isinstance(plan, list)
    # highest priority item should be 'fria'
    assert plan[0]["missing_item"] == "fria"

def test_plan_no_missing(tmp_path):
    plan = plan_remediations({"missing": []})
    assert isinstance(plan, list)
    assert plan[0]["note"] == "no_missing_evidence"

def test_write_plan_file(tmp_path):
    p = [{"missing_item":"x","action":"a","priority":2}]
    out = write_plan(p)
    assert os.path.exists(out)
    data = json.load(open(out))
    assert "plan" in data
    Path(out).unlink()
