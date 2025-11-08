# tests/test_monitorability_snapshot.py
import json
from pathlib import Path

def test_monitorability_snapshot_exists():
    p = Path("logs/monitorability_snapshot.jsonld")
    assert p.exists(), "monitorability_snapshot.jsonld missing; run tools/monitorability_snapshot.py"
    j = json.loads(p.read_text(encoding="utf-8"))
    assert "total_public_timestamp_entries" in j
    assert "generated_at" in j
