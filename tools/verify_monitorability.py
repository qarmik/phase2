#!/usr/bin/env python3
"""
tools/verify_monitorability.py
Day-25 kata: verify monitorability traces, compute faithfulness + QVM flag,
emit monitorability_snapshot.jsonld and return exit code.

Usage:
  python tools/verify_monitorability.py --trace logs/monitorability_trace.jsonld --monitor logs/monitor_log.json --out logs/monitorability_snapshot.jsonld

Exit codes:
  0 = OK (no ALERT flag, faith >= threshold)
  2 = ALERT / degraded (flag ALERT or faith < threshold)
"""
from __future__ import annotations
import json, argparse, sys, datetime, hashlib
from pathlib import Path

FAITH_THRESHOLD = 0.25  # arbitrary baseline for this kata

def load_json(path: Path):
    txt = path.read_text(encoding="utf-8")
    return json.loads(txt)

def compute_faithfulness_score(trace: dict) -> float:
    """
    Lightweight proxy faithfulness:
    - If trace has 'explanations' and 'faith_scores' average them.
    - Otherwise fall back to 0.0
    """
    fs = trace.get("faith_scores") or []
    if isinstance(fs, list) and fs:
        vals = [float(v) for v in fs if isinstance(v, (int, float, str))]
        try:
            vals = [float(v) for v in vals]
        except Exception:
            return 0.0
        return sum(vals) / len(vals) if vals else 0.0
    # try heuristics: presence of 'explanation' keys
    if trace.get("explanations") and isinstance(trace["explanations"], list):
        return 0.5  # heuristic mid-score if explanations present
    return 0.0

def detect_qvm_alert(trace: dict) -> bool:
    # QVM field expected: "qvm_score" or "qvm_flag" or "qvm_hash"
    qvm_flag = trace.get("qvm_flag") or trace.get("flag") or trace.get("enhanced_flag")
    if isinstance(qvm_flag, str) and qvm_flag.upper() == "ALERT":
        return True
    # numeric low score
    qvm_score = trace.get("qvm_score")
    if qvm_score is not None:
        try:
            return float(qvm_score) < FAITH_THRESHOLD
        except Exception:
            return False
    return False

def build_snapshot(trace: dict, monitor_log: list, faith: float, qvm_alert: bool):
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    snapshot = {
        "@context": ["https://www.w3.org/ns/activitystreams", {"qv": "urn:qvm"}],
        "id": f"urn:monitorability:phase2:stage1:fraud:{hashlib.sha256(ts.encode()).hexdigest()[:12]}",
        "type": "MonitorabilitySnapshot",
        "generated_at": ts,
        "faithfulness_score": round(float(faith), 6),
        "qvm_alert": bool(qvm_alert),
        "trace_summary": {
            "artifact_id": trace.get("artifact_id"),
            "timestamp": trace.get("generated_at") or trace.get("timestamp") or trace.get("created_at")
        },
        "monitor_log_events": len(monitor_log),
    }
    return snapshot

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--trace", default="logs/monitorability_trace.jsonld")
    p.add_argument("--monitor", default="logs/monitor_log.json")
    p.add_argument("--out", default="logs/monitorability_snapshot.jsonld")
    p.add_argument("--threshold", type=float, default=FAITH_THRESHOLD)
    args = p.parse_args(argv)

    TRACE = Path(args.trace)
    MON = Path(args.monitor)
    OUT = Path(args.out)

    if not TRACE.exists():
        print("ERROR: trace not found:", TRACE, file=sys.stderr)
        return 2
    if not MON.exists():
        print("ERROR: monitor log not found:", MON, file=sys.stderr)
        return 2

    trace = load_json(TRACE)
    # allow NDJSON array or single object
    if isinstance(trace, list):
        # pick latest
        trace = trace[-1]

    monitor_log = load_json(MON)
    if isinstance(monitor_log, dict):
        # maybe wrapped; extract list under key
        monitor_log = monitor_log.get("events") or monitor_log.get("records") or [monitor_log]

    faith = compute_faithfulness_score(trace)
    qvm_alert = detect_qvm_alert(trace)

    snapshot = build_snapshot(trace, monitor_log, faith, qvm_alert)
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Wrote snapshot ->", OUT)
    print("faithfulness_score=", snapshot["faithfulness_score"], "qvm_alert=", snapshot["qvm_alert"])

    # CI-friendly exit
    if qvm_alert or (faith < args.threshold):
        return 2
    return 0

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
