# tests/test_intervention_simulator.py
import json
from pathlib import Path

def test_intervention_events_exist_and_count():
    nd = Path("logs/intervention_events.ndjson")
    j = Path("logs/intervention_log.json")
    assert nd.exists(), "logs/intervention_events.ndjson missing; run tools/incident_simulator.py"
    assert j.exists(), "logs/intervention_log.json missing; run tools/incident_simulator.py"
    # count lines in ndjson
    with nd.open(encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    assert len(lines) >= 1, "No events appended to logs/intervention_events.ndjson"
    arr = json.loads(j.read_text(encoding="utf-8"))
    assert isinstance(arr, list) and len(arr) >= len(lines), "intervention_log.json does not contain expected events"
