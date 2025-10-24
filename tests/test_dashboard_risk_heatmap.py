import os
import json
from pathlib import Path
from fraud import dashboard_risk_heatmap as drh

def create_dummy_report(path, ai_list=None, iso_list=None):
    r = {"mappings": {"eu_ai_act": ai_list or [], "iso42001_hints": iso_list or []}, "input_path": str(path)}
    with open(path, "w") as fh:
        json.dump(r, fh)

def test_aggregate_and_summary(tmp_path):
    rpt_dir = tmp_path / "reports"
    rpt_dir.mkdir()
    # create two dummy reports
    create_dummy_report(rpt_dir / "r1.json", ai_list=["high_risk"], iso_list=["ClauseX"])
    create_dummy_report(rpt_dir / "r2.json", ai_list=["high_risk","transparency"], iso_list=[])
    reports = drh.load_reports(str(rpt_dir))
    summary = drh.aggregate_mappings(reports)
    assert summary["ai_act_counts"].get("high_risk", 0) == 2
    out = drh.write_summary(summary, str(rpt_dir))
    assert os.path.exists(out)

def test_generate_heatmap_creates_png(tmp_path):
    rpt_dir = tmp_path / "reports"
    rpt_dir.mkdir()
    create_dummy_report(rpt_dir / "r1.json", ai_list=["high_risk"], iso_list=["ClauseX"])
    reports = drh.load_reports(str(rpt_dir))
    summary = drh.aggregate_mappings(reports)
    png = drh.generate_heatmap(summary, str(rpt_dir))
    assert os.path.exists(png)
    # cleanup
    Path(png).unlink()
