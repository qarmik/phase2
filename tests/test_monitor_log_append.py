# tests/test_monitor_log_append.py
import json
from pathlib import Path

def test_monitor_log_recent_entry():
    p = Path("logs/monitor_log.json")
    assert p.exists(), "monitor_log.json missing; run tools/monitor_daemon.py"
    arr = json.loads(p.read_text(encoding="utf-8") or "[]")
    assert isinstance(arr, list) and len(arr) > 0
    last = arr[-1]
    assert "timestamp_utc" in last and "artifact_id" in last and "verify_result" in last
