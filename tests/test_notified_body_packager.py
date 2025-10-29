import json, os, zipfile
from pathlib import Path
from fraud.notified_body_packager import list_matching_files, write_package, build_manifest

def create_dummy(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)

def test_list_matching_and_package(tmp_path):
    rpt = tmp_path / "reports"
    rpt.mkdir()
    # create dummy files
    f1 = rpt / "compliance_report_test.json"
    f2 = rpt / "risk_matrix_test.jsonld"
    f3 = rpt / "sla_dashboard_test.json"
    create_dummy(str(f1), '{"a":1}')
    create_dummy(str(f2), '{"b":2}')
    create_dummy(str(f3), '{"c":3}')
    files = list_matching_files(str(rpt), ["compliance_report_", "risk_matrix_", "sla_dashboard_"])
    assert len(files) == 3
    zip_path, manifest = write_package(files, str(rpt))
    assert os.path.exists(zip_path)
    # inspect zip
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "compliance_report_test.json" in names
        assert "manifest.json" in names
    # manifest sanity
    assert "package_signature" in manifest
    # cleanup
    Path(zip_path).unlink()
