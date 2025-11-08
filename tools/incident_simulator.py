#!/usr/bin/env python3
# tools/incident_simulator.py
# Standalone incident simulator for Day-25: generate synthetic intervention events and refresh traces.
# Save as tools/incident_simulator.py and run from repo root:
#   python tools/incident_simulator.py

import json, hashlib, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ND = Path("logs/public_timestamp.ndjson")
EVENTS_ND = Path("logs/intervention_events.ndjson")
EVENTS_JSON = Path("logs/intervention_log.json")
QVM_TRACE_TOOL = Path("tools/qvm_explainability_trace.py")
QVM_SCORE_TOOL = Path("tools/qvm_scoring_upgrade.py")

def read_ndjson(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

def deterministic_choice(seed_hex, options, idx=0):
    i = int(seed_hex[:8], 16)
    return options[(i >> (idx*3)) % len(options)]

def synth_cot(artifact_id):
    base = [
        "Checked transaction velocity",
        "Matched merchant pattern",
        "Flagged unusual IP",
        "Applied rule: velocity>3 in 24h",
        "Human reviewer: reviewed receipts",
        "Checked account age",
        "Checked chargeback history",
        "Validated 2FA logs",
        "Cross-checked billing address",
    ]
    h = hashlib.sha256((artifact_id or "none").encode("utf-8")).hexdigest()
    # pick 3 deterministic items
    return [deterministic_choice(h, base, i) for i in range(3)]

def synth_model_score(seed_hex):
    # deterministically derive a score 0.0-1.0
    v = int(seed_hex[-8:], 16) % 101
    return round(v / 100.0, 3)

def synth_human_verdict(score):
    # simple rule: score>0.7 -> REJECT (suspicious), else ACCEPT
    return "REJECT" if score >= 0.7 else "ACCEPT"

def make_event(entry):
    seed = (entry.get("entry_hash") or entry.get("public_hash") or entry.get("artifact_id") or "seed")
    seed_hex = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    artifact_id = entry.get("artifact_id") or "unknown"
    cot = synth_cot(artifact_id.lower())
    score = synth_model_score(seed_hex)
    human = synth_human_verdict(score)
    ts = datetime.now(timezone.utc).isoformat()
    event = {
        "generated_at": ts,
        "artifact_id": artifact_id,
        "entry_hash": entry.get("entry_hash"),
        "bundle_path": entry.get("bundle_path"),
        "public_hash": entry.get("public_hash"),
        "cot": cot,
        "model_score": score,
        "human_verdict": human,
        "simulator_tag": "Day25-incident-sim",
    }
    return event

def append_ndjson(path, events):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

def write_json(path, events):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")

def run_tool(script_path):
    if not script_path.exists():
        return False, f"{script_path} missing"
    # run with the same Python interpreter
    p = subprocess.run([sys.executable, str(script_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out = p.stdout.strip()
    err = p.stderr.strip()
    return p.returncode == 0, out if out else err

def main(n=5):
    entries = read_ndjson(ND)
    if not entries:
        # synth a safe placeholder entry so simulator still produces events
        entries = [{
            "artifact_id": "SYNTH-PLACEHOLDER",
            "entry_hash": hashlib.sha256(b"placeholder").hexdigest(),
            "bundle_path": "dist/placeholder.zip",
            "public_hash": hashlib.sha256(b"bundle").hexdigest()
        }]
    # choose last n entries
    last = entries[-n:] if len(entries) >= n else entries
    events = [make_event(e) for e in last]
    # append to ndjson and write full json array
    append_ndjson(EVENTS_ND, events)
    # merge existing JSON array if present
    existing = []
    if EVENTS_JSON.exists():
        try:
            existing = json.loads(EVENTS_JSON.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    combined = existing + events
    write_json(EVENTS_JSON, combined)
    # refresh traces by invoking QVM tools
    ok1, out1 = run_tool(QVM_TRACE_TOOL)
    ok2, out2 = run_tool(QVM_SCORE_TOOL)
    summary = {
        "simulated_events": len(events),
        "events_ndjson": str(EVENTS_ND),
        "events_json": str(EVENTS_JSON),
        "qvm_trace_run": ok1,
        "qvm_trace_output": out1,
        "qvm_score_run": ok2,
        "qvm_score_output": out2
    }
    print(f"Simulated {summary['simulated_events']} events; qvm_trace_run={ok1} qvm_score_run={ok2}")
    # also print last flag if enhanced trace exists
    enhanced = Path("logs/monitorability_trace_enhanced.jsonld")
    if enhanced.exists():
        try:
            j = json.loads(enhanced.read_text(encoding="utf-8"))
            print(f"enhanced_flag={j.get('faithfulness_flag')} weighted_faith={j.get('weighted_faithfulness')}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
