# fraud_logger.py
# PURPOSE: Run the simulator, log each transaction as JSONL and append a human summary.
# OUTPUTS:
#  - logs/fraud_report.log         (human readable append)
#  - logs/fraud_report.jsonl       (one JSON object per tx)
#  - logs/fraud_run_summary.json   (run-level metadata)
#  - logs/immutable_intervention.jsonl (append-only tamper-evident log)

import json                 # JSON encode/decode
import time                 # for timestamp
from pathlib import Path    # portable path handling
from fraud_simulator import simulate_transactions
from fraud_redteam import is_suspicious
from intervention_log import append_intervention   # <-- NEW import for Insurance Alignment

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # ensure folder exists

def now_iso():
    """Return current time in ISO format (string)."""
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")

def run_and_log(n=10):
    """
    Simulate n transactions, evaluate with is_suspicious,
    write per-transaction JSONL and append a short human summary.
    Also trigger immutable intervention logs for flagged cases.
    """
    txs = simulate_transactions(n)
    flagged = []

    # file paths
    human_path = LOG_DIR / "fraud_report.log"
    jsonl_path = LOG_DIR / "fraud_report.jsonl"
    summary_path = LOG_DIR / f"fraud_run_summary_{int(time.time())}.json"

    # open jsonl for append (text mode)
    with jsonl_path.open("a", encoding="utf-8") as jf, human_path.open("a", encoding="utf-8") as hf:
        run_ts = now_iso()
        hf.write(f"\n=== Run at {run_ts} ===\n")
        for tx in txs:
            tx_result = {
                "id": tx["id"],
                "amount": tx["amount"],
                "country": tx["country"],
                "device": tx["device"]
            }
            tx_result["suspicious"] = bool(is_suspicious(tx))

            # JSONL: one JSON object per line
            jf.write(json.dumps(tx_result, ensure_ascii=False) + "\n")
            # Human log: short line
            hf.write(
                f"TX {tx_result['id']}: amount={tx_result['amount']} "
                f"country={tx_result['country']} device={tx_result['device']} "
                f"suspicious={tx_result['suspicious']}\n"
            )

            # --- Insurance Alignment Clause (NEW) ---
            if tx_result["suspicious"]:
                flagged.append(tx_result)
                # Append immutable intervention record
                append_intervention(
                    artifact_id="fraud_redteam",
                    model_version="v0.1",
                    input_payload=tx,
                    decision_summary="flagged_suspicious",
                    human_id="CadetQ0",
                    human_reason="manual review triggered",
                    output_payload=tx_result
                )
            # --- End Clause ---

        # after loop, write summary file
        summary = {
            "run_timestamp": run_ts,
            "total": len(txs),
            "flagged_count": len(flagged),
            "flagged_ids": [f["id"] for f in flagged]
        }
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        hf.write(
            f"Summary: total={summary['total']} flagged={summary['flagged_count']} "
            f"flagged_ids={summary['flagged_ids']}\n"
        )

    # return summary for immediate CLI feedback
    return summary

if __name__ == "__main__":
    s = run_and_log(10)
    print(f"Run complete. Total={s['total']} Flagged={s['flagged_count']}")
