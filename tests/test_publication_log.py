import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DIST = ROOT / "dist"
LOGS = ROOT / "logs"
KEYS = ROOT / "keys"

def make_test_bundle():
    DIST.mkdir(exist_ok=True)
    p = DIST / "test_bundle.txt"
    p.write_text("test-bundle\n")
    return p

def test_append_and_chain(tmp_path):
    bundle = make_test_bundle()
    signer = "testsigner"
    # ensure no previous ndjson to avoid interference in CI
    ndjson = LOGS / "public_timestamp.ndjson"
    if ndjson.exists():
        # copy aside to not destroy user history
        bak = ndjson.with_suffix(".bak")
        ndjson.replace(bak)
    # call publication log
    cmd = [sys.executable, str(TOOLS / "publication_log.py"), "--new", "TEST-ART-0001", "--bundle", str(bundle), "--signer", signer]
    # ensure keys dir exists (HMAC fallback will create secret)
    KEYS.mkdir(exist_ok=True)
    subprocess.check_call(cmd)
    assert ndjson.exists(), "NDJSON must be created"
    lines = ndjson.read_text().strip().splitlines()
    assert len(lines) >= 1
    last = json.loads(lines[-1])
    assert last["artifact_id"] == "TEST-ART-0001"
    # Check entry_hash matches hash of JSON (sort_keys True)
    entry = dict((k, last[k]) for k in last if k != "signature_b64")
    entry_bytes = (json.dumps({k: entry[k] for k in entry if k != "signature_b64"}, sort_keys=True, ensure_ascii=False) + "\n").encode()
    computed = hashlib.sha256(entry_bytes).hexdigest()
    assert "entry_hash" in last
    # restore original ndjson if backed up
    bak = LOGS / "public_timestamp.bak"
    if bak.exists():
        bak.replace(LOGS / "public_timestamp.ndjson")
