# test_fraud_redteam.py
from fraud_redteam import is_suspicious

def test_high_amount():
    tx = {"amount": 200000, "country": "IN", "device": "mobile"}
    assert is_suspicious(tx)

def test_foreign_country():
    tx = {"amount": 5000, "country": "NG", "device": "mobile"}
    assert is_suspicious(tx)

def test_clean_tx():
    tx = {"amount": 3000, "country": "IN", "device": "mobile"}
    assert not is_suspicious(tx)
