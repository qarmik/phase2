# intervention_summary.py
# PURPOSE: Read immutable_intervention.jsonl and produce a summary table for audits.
# OUTPUT: prints run counts, unique human reviewers, and first/last timestamps.

import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("logs/immutable_intervention.jsonl")

def read_logs(path=LOG_FILE):
    """Read all intervention log entries as JSON objects."""
    entries = []
    if not path.exists():
        print("No intervention log found.")
        return entries

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                print("⚠️  Skipped corrupted log line.")
    return entries

def summarize(entries):
    """Compute simple stats from intervention log entries."""
    if not entries:
        print("No entries to summarize.")
        return

    humans = set()
    timestamps = []
    for e in entries:
        humans.add(e.get("human_id", "unknown"))
        timestamps.append(e.get("timestamp", ""))

    timestamps = [t for t in timestamps if t]
    first = min(timestamps) if timestamps else "-"
    last = max(timestamps) if timestamps else "-"
    print("\n=== Intervention Log Summary ===")
    print(f"Total entries     : {len(entries)}")
    print(f"Unique reviewers  : {len(humans)} ({', '.join(humans)})")
    print(f"First intervention: {first}")
    print(f"Last intervention : {last}")

if __name__ == "__main__":
    data = read_logs()
    summarize(data)
