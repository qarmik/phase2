import json, os
from fraud.owner_assignment import assign_owner_for_plan, write_ownership, list_remediation_plans, load_org_map

def test_assign_with_org_map(tmp_path):
    # create fake plan file
    rpt = tmp_path / "reports"
    rpt.mkdir()
    p = rpt / "remediation_plan_specialcase.json"
    p.write_text(json.dumps({"plan":[]}))
    org = tmp_path / "org.json"
    org.write_text(json.dumps({"specialcase":"alice"}))
    m = load_org_map(str(org))
    owner = assign_owner_for_plan(str(p), m)
    assert owner == "alice"

def test_write_ownership(tmp_path):
    rpt = tmp_path / "reports"
    rpt.mkdir()
    p = rpt / "remediation_plan_x.json"
    p.write_text(json.dumps({"plan":[{"missing_item":"a"}]}))
    out = write_ownership(str(p), "bob", str(rpt))
    assert os.path.exists(out)
    data = json.load(open(out))
    assert data["owner"] == "bob"
    os.remove(out)
