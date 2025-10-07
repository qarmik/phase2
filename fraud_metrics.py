# fraud_metrics.py
# Stage 1 – Fraud Red-Team: automated run loop + basic metrics stub

import statistics
from fraud_logger import run_and_log

def automated_runs(runs=5, n_per_run=10):
    """
    Execute multiple fraud simulations, collect flagged counts,
    compute mean flag rate, and print basic metrics stub.
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
    return {"flagged_counts": flagged_counts, "avg_rate": avg_rate, "stub": metrics_stub}


if __name__ == "__main__":
    automated_runs()
