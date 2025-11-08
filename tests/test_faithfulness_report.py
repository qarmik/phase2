# tests/test_faithfulness_report.py
import json
from pathlib import Path

def test_faithfulness_report_exists_and_has_fields():
    p = Path("logs/faithfulness_report.json")
    assert p.exists(), "faithfulness_report.json missing; run tools/faithfulness_check.py"
    j = json.loads(p.read_text(encoding="utf-8"))
    for k in ("total_entries","entry_hash_ok","signature_ok"):
        assert k in j, f"{k} missing in faithfulness report"
    assert isinstance(j["total_entries"], int)
