#!/usr/bin/env python3
"""
dashboard_risk_heatmap.py
Aggregate compliance reports and produce:
 - a JSON summary (clause & category frequencies)
 - a heatmap PNG (ISO 42001 clauses vs EU AI Act categories)

Usage (from phase2/):
  python fraud/dashboard_risk_heatmap.py --reports-dir artifacts/reports --out-dir artifacts/reports --export

Notes:
- Uses matplotlib Agg backend for headless environments.
- No external deps beyond matplotlib (install if missing).
"""
from __future__ import annotations
import argparse
import json
import os
import datetime
from collections import Counter, defaultdict
from typing import Dict, Any, List

# matplotlib must use Agg for headless servers
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DEFAULT_REPORT_DIR = os.path.join(os.path.dirname(__file__), "../artifacts/reports")
os.makedirs(DEFAULT_REPORT_DIR, exist_ok=True)


def load_reports(reports_dir: str) -> List[Dict[str, Any]]:
    out = []
    for fname in sorted(os.listdir(reports_dir)):
        if not (fname.endswith(".json") or fname.endswith(".jsonld")):
            continue
        path = os.path.join(reports_dir, fname)
        try:
            with open(path, "r") as fh:
                out.append(json.load(fh))
        except Exception:
            continue
    return out


def aggregate_mappings(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    ai_cat_counter = Counter()
    iso_clause_counter = Counter()
    # also record mapping examples for audit
    examples = {"ai_act": defaultdict(list), "iso": defaultdict(list)}

    for r in reports:
        mappings = r.get("mappings", {})
        eu = mappings.get("eu_ai_act", [])
        iso = mappings.get("iso42001_hints", [])
        for e in eu:
            ai_cat_counter[e] += 1
            examples["ai_act"][e].append(r.get("input_path", "<unknown>"))
        for i in iso:
            iso_clause_counter[i] += 1
            examples["iso"][i].append(r.get("input_path", "<unknown>"))

    return {
        "ai_act_counts": dict(ai_cat_counter),
        "iso_counts": dict(iso_clause_counter),
        "examples": { "ai_act": {k: v[:3] for k, v in examples["ai_act"].items()},
                      "iso": {k: v[:3] for k, v in examples["iso"].items()} }
    }


def write_summary(summary: Dict[str, Any], out_dir: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = f"heatmap_summary_{ts}.json"
    out = os.path.join(out_dir, fname)
    with open(out, "w") as fh:
        json.dump(summary, fh, indent=2)
    return out


def generate_heatmap(summary: Dict[str, Any], out_dir: str) -> str:
    # Build ordered lists
    ai_keys = sorted(summary["ai_act_counts"].keys()) or ["none"]
    iso_keys = sorted(summary["iso_counts"].keys()) or ["none"]
    # matrix of counts with iso rows and ai columns
    matrix = []
    for iso in iso_keys:
        row = []
        for ai in ai_keys:
            row.append(summary["iso_counts"].get(iso, 0) + summary["ai_act_counts"].get(ai, 0) if False else summary["ai_act_counts"].get(ai,0))
            # primary visualization metric: frequency of AI categories (columns)
        matrix.append(row)

    # Create figure
    fig, ax = plt.subplots()
    im = ax.imshow(matrix)  # no explicit colors set (matplotlib default)
    ax.set_xticks(range(len(ai_keys)))
    ax.set_xticklabels(ai_keys, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(iso_keys)))
    ax.set_yticklabels(iso_keys, fontsize=8)
    ax.set_title("Clause Heatmap (AI Act categories vs ISO hints)")
    fig.tight_layout()

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    outpath = os.path.join(out_dir, f"risk_heatmap_{ts}.png")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reports-dir", default=DEFAULT_REPORT_DIR, help="Directory containing compliance reports")
    p.add_argument("--out-dir", default=DEFAULT_REPORT_DIR, help="Directory to write summary and heatmap")
    p.add_argument("--export", action="store_true", help="Write summary JSON and PNG heatmap")
    args = p.parse_args()

    reports = load_reports(args.reports_dir)
    summary = aggregate_mappings(reports)
    print("Aggregated AI Act counts:", summary["ai_act_counts"])
    if args.export:
        summary_path = write_summary(summary, args.out_dir)
        heatmap_path = generate_heatmap(summary, args.out_dir)
        print("Summary written to:", summary_path)
        print("Heatmap written to:", heatmap_path)


if __name__ == "__main__":
    main()
