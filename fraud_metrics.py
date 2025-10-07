# fraud_metrics.py
# Stage 1 – Fraud Red-Team: automated run loop + basic metrics stub
# Updated: Insurance Alignment Clause integration
# Adds post-run count of immutable intervention records (tamper-evident logs)

import statistics
from pathlib import Path
from fraud_logger import run_and_log

def automated_runs(runs=5, n_per_run=10):
    """
    Execute multiple fraud simulations, collect flagged counts,
    compute mean flag rate, and print basic metrics stub.
    Also prints total immutable intervention log entries recorded.
    """
    flagged_counts = []
    totals = []

    for i in range(runs):
        summary = run_and_log(n_per_run)
        flagged_counts.append(summary["flagged_count"])
        totals.append(summary["total"])
        print(f"Run {i+1}: {summary['flagged_count']} flagged out of {summary['total']}")

    mean_flagged = statistics.mean(flagged_counts)
    mean_total = statistics.mean(totals)
    avg_rate = (mean_flagged / mean_total) * 100

    print("\n=== Aggregate Metrics ===")
    print(f"Avg flagged per run: {mean_flagged:.1f} / {mean_total:.0f} ({avg_rate:.1f}%)")

    # TP/FP stub – placeholders for future supervised labels
    metrics_stub = {
        "true_positives": None,
        "false_positives": None,
        "false_negatives": None,
        "notes": "Populate once ground truth available (Stage 1→Stage 2 transition)."
    }
    print("\nMetrics stub:", metrics_stub)

    # === Insurance Alignment Clause Extension ===
    # Count immutable intervention records written so far
    log_file = Path("logs/immutable_intervention.jsonl")
    if log_file.exists():
        try:
            count = sum(1 for _ in log_file.open("r", encoding="utf-8"))
            print(f"\nIntervention log entries recorded so far: {count}")
        except Exception as e:
            print(f"\n[Warning] Could not read intervention log: {e}")
    else:
        print("\n[Info] No immutable intervention logs found yet.")
    # === End Extension ===

    return {"flagged_counts": flagged_counts, "avg_rate": avg_rate, "stub": metrics_stub}


if __name__ == "__main__":
    automated_runs()
