#!/usr/bin/env python3
# tools/day25_reconciliation.py
# Standalone reconciliation script for Day-25: create verification annotations,
# record missing legacy key in key_index, update forensic annex, and commit changes.
# Save as tools/day25_reconciliation.py and run from repo root.

import json, csv, sys
from pathlib import Path
import subprocess
from datetime import datetime

ROOT = Path(".")
LOG_REPLAY = ROOT / "logs" / "replay_summary.csv"
ND = ROOT / "logs" / "public_timestamp.ndjson"
ANNOT = ROOT / "logs" / "verification_annotations.json"
KEY_INDEX = ROOT / "keys" / "key_index.json"
FORENSIC = ROOT / "docs" / "forensic_annex_DAY24_REV7.md"

def load_replay(path):
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def build_annotations(rows):
    ann = {}
    for r in rows:
        notes = (r.get("notes") or "").lower()
        sig_ok = (r.get("signature_ok") or "").lower()
        if "no_pub" in notes or sig_ok not in ("true","ok","1","yes"):
            key = r.get("entry_hash") or r.get("artifact_id")
            ann[key] = {
                "artifact_id": r.get("artifact_id"),
                "entry_hash": r.get("entry_hash"),
                "issue": "legacy_pub_missing_or_signature_mismatch",
                "notes": r.get("notes"),
                "recorded_at": datetime.utcnow().isoformat() + "Z"
            }
    return ann

def fallback_last_entry():
    if not ND.exists():
        return {}
    try:
        lines = [l for l in ND.read_text(encoding="utf-8").splitlines() if l.strip()]
        last = json.loads(lines[-1])
        return { last.get("entry_hash") or last.get("artifact_id"): {
            "artifact_id": last.get("artifact_id"),
            "entry_hash": last.get("entry_hash"),
            "issue": "verification_not_attempted_or_failed",
            "notes": "Fallback annotation created",
            "recorded_at": datetime.utcnow().isoformat() + "Z"
        } }
    except Exception:
        return {}

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print(f"Wrote {path}")

def ensure_key_index_note(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    j = {"keys": []}
    if path.exists():
        try:
            j = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            print("Warning: could not parse existing key_index.json; overwriting append-only structure.")
            j = {"keys": j.get("keys", [])}
    # check if note already present
    exists = False
    for k in j.get("keys", []):
        if k.get("key_id") == "indusv_v1_legacy_or_missing":
            exists = True
            break
    if not exists:
        note = {
            "key_id":"indusv_v1_legacy_or_missing",
            "role":"signing_legacy",
            "status":"missing",
            "pub_path":"keys/indusv_v1.pub.pem (missing)",
            "fingerprint_der_sha256":"UNKNOWN",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "notes":"Legacy key expected for historical verification; missing locally as of script run."
        }
        j.setdefault("keys", []).append(note)
        write_json(path, j)
        return True
    print("Key-index note already present; no change.")
    return False

def append_forensic_note(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    marker = "NOTE (Day25-Reconciliation): legacy public key indusv_v1 not present locally"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in content:
        print("Forensic annex already contains reconciliation note.")
        return False
    note = f"\n- {marker}; see logs/verification_annotations.json for details. Recorded: {datetime.utcnow().isoformat()}Z\n"
    path.write_text(content + note, encoding="utf-8")
    print(f"Appended forensic note to {path}")
    return True

def git_commit_and_push(files, message):
    try:
        subprocess.run(["git", "add"] + [str(f) for f in files], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "stage1/fraud"], check=True)
        print("Committed & pushed changes.")
        return True
    except subprocess.CalledProcessError as e:
        print("Git operation failed:", e)
        return False

def main():
    rows = load_replay(LOG_REPLAY)
    annotations = build_annotations(rows)
    if not annotations:
        annotations = fallback_last_entry()
    # merge with existing annotations if present
    if ANNOT.exists():
        try:
            existing = json.loads(ANNOT.read_text(encoding="utf-8"))
            existing.update(annotations)
            annotations = existing
        except Exception:
            pass
    write_json(ANNOT, annotations)
    changed1 = ensure_key_index_note(KEY_INDEX)
    changed2 = append_forensic_note(FORENSIC)
    # commit files if changed
    to_commit = [ANNOT]
    if changed1:
        to_commit.append(KEY_INDEX)
    if changed2:
        to_commit.append(FORENSIC)
    if to_commit:
        ok = git_commit_and_push(to_commit, "docs(audit): add Day25 verification annotations and record missing legacy key")
        if not ok:
            print("Git commit/push failed. Files written locally; commit manually if needed.")
    else:
        print("No files required committing.")
    print("Done.")

if __name__ == "__main__":
    main()
