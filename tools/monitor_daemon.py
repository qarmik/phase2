#!/usr/bin/env python3
"""
tools/monitor_daemon.py
Single-run monitor: verifies last NDJSON entry signature and records a monitor log.
Depends on tools/verify_last_signature.py being present and working.
Output: logs/monitor_log.json (appends new entry)
"""
from pathlib import Path
import json, subprocess, datetime

VERIFY = Path("tools/verify_last_signature.py")
ND = Path("logs/public_timestamp.ndjson")
OUT = Path("logs/monitor_log.json")

def last_entry_id():
    if not ND.exists():
        return None
    lines = [l for l in ND.read_text(encoding='utf-8').strip().splitlines() if l.strip()]
    if not lines:
        return None
    j = json.loads(lines[-1])
    return j.get("artifact_id"), j.get("entry_hash")

def run_verify(signer="indusv"):
    if not VERIFY.exists():
        return {"ok": False, "error": "verify script missing"}
    p = subprocess.run(["python", str(VERIFY), "--signer", signer], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def append_log(entry):
    logs = []
    if OUT.exists():
        logs = json.loads(OUT.read_text(encoding='utf-8') or "[]")
    logs.append(entry)
    OUT.write_text(json.dumps(logs, indent=2), encoding='utf-8')

def main():
    art = last_entry_id()
    artifact_id = art[0] if art else None
    entry_hash = art[1] if art else None
    verify = run_verify()
    monitor = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "artifact_id": artifact_id,
        "entry_hash": entry_hash,
        "verify_result": verify
    }
    append_log(monitor)
    print(f"Monitor run recorded: artifact={artifact_id} entry_hash={entry_hash} rc={verify.get('returncode')}")

if __name__ == "__main__":
    import json
    main()
