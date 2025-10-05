# fraud_redteam.py
# PURPOSE: simple fraud detector for simulated transactions

def is_suspicious(tx):
    """
    tx: dict with keys {"amount", "country", "device"}
    returns True if suspicious else False
    """
    if tx["amount"] > 100000:  # unusually high
        return True
    if tx["country"] not in ("IN", "US"):  # cross-border anomaly
        return True
    if tx["device"] in ("unknown", "emulator"):  # fake device
        return True
    return False
