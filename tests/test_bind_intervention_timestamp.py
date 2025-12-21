from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(".")
LOGS = ROOT / "logs"

def test_intervention_is_timestamped(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)

    before = LOGS / "public_timestamp.ndjson"
    old_lines = before.read_text().count("\n") if before.exists() else 0

    subprocess.check_call([
        sys.executable,
        "tools/bind_intervention_timestamp.py"
    ])

    new_lines = before.read_text().count("\n")
    assert new_lines == old_lines + 1
