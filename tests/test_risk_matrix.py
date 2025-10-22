import os, json
from fraud.risk_matrix import build_matrix, write_export

def test_build_matrix_levels():
    r = {"risk_level": "high"}
    m = build_matrix(r)
    assert "high" in m["risk_level"]
    assert "signature_hash" in m

def test_write_export_creates_file(tmp_path):
    matrix = build_matrix({"risk_level": "medium"})
    path = tmp_path / "risk_matrix.jsonld"
    os.makedirs(tmp_path, exist_ok=True)
    out = write_export(matrix)
    assert os.path.exists(out)
    data = json.load(open(out))
    assert data["@type"] == "RiskAssessment"

def test_low_risk_matrix_signature_unique():
    m1 = build_matrix({"risk_level": "low"})
    m2 = build_matrix({"risk_level": "high"})
    assert m1["signature_hash"] != m2["signature_hash"]
