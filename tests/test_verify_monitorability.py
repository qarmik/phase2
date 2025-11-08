import json, pathlib, tempfile
from pathlib import Path
from tools import verify_monitorability as vm

def make_trace(tmpdir, faith_scores=None, flag=None):
    data = {
        "artifact_id": "TEST-TRACE-1",
        "generated_at": "2025-11-08T00:00:00Z",
    }
    if faith_scores is not None:
        data["faith_scores"] = faith_scores
    if flag is not None:
        data["enhanced_flag"] = flag
    p = Path(tmpdir) / "monitorability_trace.jsonld"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p

def make_monitor_log(tmpdir, n=3):
    p = Path(tmpdir) / "monitor_log.json"
    arr = [{"ts": i} for i in range(n)]
    p.write_text(json.dumps(arr), encoding="utf-8")
    return p

def test_snapshot_ok(tmp_path, monkeypatch):
    trace = make_trace(tmp_path, faith_scores=[0.5,0.6], flag=None)
    mlog = make_monitor_log(tmp_path, 2)
    out = Path(tmp_path) / "snapshot.jsonld"
    rc = vm.main(["--trace", str(trace), "--monitor", str(mlog), "--out", str(out), "--threshold", "0.25"])
    assert rc == 0
    j = json.loads(out.read_text(encoding="utf-8"))
    assert j["faithfulness_score"] >= 0.5
    assert j["qvm_alert"] is False

def test_snapshot_alert_flag(tmp_path):
    trace = make_trace(tmp_path, faith_scores=[0.9], flag="ALERT")
    mlog = make_monitor_log(tmp_path, 1)
    out = Path(tmp_path) / "snapshot2.jsonld"
    rc = vm.main(["--trace", str(trace), "--monitor", str(mlog), "--out", str(out), "--threshold", "0.25"])
    assert rc == 2
    j = json.loads(out.read_text(encoding="utf-8"))
    assert j["qvm_alert"] is True
