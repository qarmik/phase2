import json, os, zipfile
from pathlib import Path
from fraud.notified_body_packager import write_package
from fraud.release_checklist import sanity_checks, write_timestamp_and_bundle, file_sha256

def create_dummy_reports(tmp_path):
    rpt = tmp_path / "reports"
    rpt.mkdir()
    p1 = rpt / "compliance_report_test.json"
    p2 = rpt / "risk_matrix_test.jsonld"
    p3 = rpt / "sla_dashboard_test.json"
    p1.write_text('{"a":1}', encoding="utf-8")
    p2.write_text('{"b":2}', encoding="utf-8")
    p3.write_text('{"c":3}', encoding="utf-8")
    files = [str(p1), str(p2), str(p3)]
    zip_path, manifest = write_package(files, str(rpt))
    return str(rpt), zip_path, manifest

def test_release_bundle(tmp_path):
    repdir, zippath, manifest = create_dummy_reports(tmp_path)
    checks = sanity_checks(zippath, os.path.join(repdir,"manifest.json"), ["compliance_report_","risk_matrix_","sla_dashboard_"])
    assert checks["package_exists"]
    result = write_timestamp_and_bundle(zippath, os.path.join(repdir,"manifest.json"), repdir)
    assert os.path.exists(result["timestamp_file"])
    assert os.path.exists(result["bundle"])
    # inspect zip
    with zipfile.ZipFile(result["bundle"], "r") as zf:
        assert os.path.basename(zippath) in zf.namelist()
        assert "manifest.json" in zf.namelist()
    # cleanup
    Path(result["timestamp_file"]).unlink()
    Path(result["bundle"]).unlink()
