#!/usr/bin/env python3
"""
tools/faithfulness_check.py
Compute simple faithfulness metrics from logs/replay_summary.csv and logs/find_canonical_deep.txt.
Outputs: logs/faithfulness_report.json
"""
from pathlib import Path
import csv, json

CSV = Path("logs/replay_summary.csv")
OUT = Path("logs/faithfulness_report.json")
DEEP = Path("logs/find_canonical_deep.txt")

def from_csv(path):
    if not path.exists():
        return []
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def main():
    rows = from_csv(CSV)
    total = len(rows)
    if total == 0:
        print("No replay_summary.csv found or empty; nothing to compute.")
        return
    entry_hash_ok = sum(1 for r in rows if r.get("entry_hash_ok","").lower() in ("true","1","yes"))
    signature_ok = sum(1 for r in rows if r.get("signature_ok","").lower() in ("true","1","yes","ok"))
    no_pub = sum(1 for r in rows if r.get("notes","").lower().find("no_pub")!=-1)
    percent_hash_ok = round(100.0 * entry_hash_ok / total, 2)
    percent_sig_ok = round(100.0 * signature_ok / total, 2)
    report = {
        "total_entries": total,
        "entry_hash_ok": int(entry_hash_ok),
        "signature_ok": int(signature_ok),
        "no_pub_count": int(no_pub),
        "percent_entry_hash_ok": percent_hash_ok,
        "percent_signature_ok": percent_sig_ok,
        "notes": "Faithfulness check: entry_hash reproduction and signature verification summary"
    }
    # append tail of deep-find log if present (first 50 lines)
    deep_excerpt = []
    if DEEP.exists():
        deep_excerpt = DEEP.read_text(encoding='utf-8').splitlines()[-50:]
    report["find_canonical_deep_excerpt_tail"] = deep_excerpt
    OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"faithfulness report written: {OUT} total={total} hash_ok={entry_hash_ok} sig_ok={signature_ok} no_pub={no_pub}")

if __name__ == "__main__":
    main()
