# test_intervention_log.py
# Unit tests for intervention_log.py

from intervention_log import append_intervention, verify_record

def test_append_and_verify():
    rec = append_intervention("fraud_redteam","v0.1",
                              {"tx_id":1,"amount":500},
                              "flagged","CadetQ0","test run",
                              {"decision":"review"})
    assert verify_record(rec)

def test_tamper_detection():
    rec = append_intervention("fraud_redteam","v0.1",
                              {"tx_id":2,"amount":600},
                              "flagged","CadetQ0","tamper test",
                              {"decision":"review"})
    rec["human_reason"] = "malicious edit"
    assert not verify_record(rec)
