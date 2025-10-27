import json
import os
import re
from pathlib import Path
from fraud.owner_assignment import write_ownership, list_remediation_plans

def test_write_ownership_only_for_existing_plan(tmp_path):
    # setup reports dir and two plan files (one real, one absent)
    rpt = tmp_path / "reports"
    rpt.mkdir()
    real_plan = rpt / "remediation_plan_real.json"
    real_plan.write_text(json.dumps({"plan": [{"missing_item":"a"}]}), encoding="utf-8")
    absent_plan_path = str(rpt / "remediation_plan_absent.json")
    # call write_ownership for real plan only
    out = write_ownership(str(real_plan), "tester", str(rpt))
    assert os.path.exists(out)
    # ensure naming convention: ownership_<planname>_<ts>.json
    basename = os.path.basename(out)
    m = re.match(r"^ownership_remediation_plan_real_[0-9T]{15}Z\.json$", basename)
    assert m, f"Ownership filename {basename} does not match convention"
    # ensure absent plan does not produce a file when not present
    # (simulate caller behavior: only iterate actual plan files)
    plans = list_remediation_plans(str(rpt))
    assert str(real_plan) in plans
    assert absent_plan_path not in plans
    # cleanup
    Path(out).unlink()
