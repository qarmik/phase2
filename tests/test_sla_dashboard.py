import json, os
from pathlib import Path
from fraud.sla_dashboard import aggregate, write_outputs

def make_plan(path, priority_list):
    plan = {"plan": [{"missing_item": f"x{i}", "action":"a","priority":p} for i,p in enumerate(priority_list)]}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(plan, fh)
    return path

def make_ownership(path, plan_file, owner):
    o = {"plan": os.path.basename(plan_file), "owner": owner, "assigned_at":"20250101T000000Z"}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(o, fh)
    return path

def test_aggregate_and_write(tmp_path):
    rpt = tmp_path / "reports"
    rpt.mkdir()
    p1 = make_plan(rpt / "remediation_plan_test1.json", [1,2,5])
    p2 = make_plan(rpt / "remediation_plan_test2.json", [3])
    make_ownership(rpt / "ownership_remediation_plan_test1.json", p1, "alice")
    summary = aggregate(str(rpt))
    assert summary["totals"]["plans"] == 2
    out = write_outputs(summary, str(rpt))
    assert os.path.exists(out["json"])
    assert os.path.exists(out["csv"])
    # cleanup
    Path(out["json"]).unlink()
    Path(out["csv"]).unlink()
