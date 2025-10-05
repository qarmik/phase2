# fraud_simulator.py
# Stage 1 - Fraud Red-Team
# Generates fake transactions and uses is_suspicious(tx) from fraud_redteam.py

import random
from fraud_redteam import is_suspicious

def simulate_transactions(n=10):
    """Return a list of fake transaction dicts."""
    countries = ["IN", "US", "SG", "NG"]
    devices = ["android", "ios", "emulator"]
    txs = []
    for _ in range(n):
        tx = {
            "id": random.randint(1000, 9999),
            "amount": random.choice([500, 2000, 50000, 150000]),
            "country": random.choice(countries),
            "device": random.choice(devices)
        }
        txs.append(tx)
    return txs

if __name__ == "__main__":
    transactions = simulate_transactions(10)
    suspicious = [tx for tx in transactions if is_suspicious(tx)]
    print(f"\nGenerated {len(transactions)} transactions.")
    print(f"Flagged {len(suspicious)} as suspicious:\n")
    for tx in suspicious:
        print(tx)
