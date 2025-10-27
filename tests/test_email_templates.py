from fraud.email_templates import escalation_email, owner_reminder_email, signoff_ack_email

def test_escalation_email_empty():
    notif = {"artifact_id":"fraud_v1","escalation_summary":{"total":1,"escalations":0},"escalations":[],"notify_to":"ops@x"}
    subj, body = escalation_email(notif)
    assert "No active escalations" in body

def test_owner_reminder():
    subj, body = owner_reminder_email("remediation_plan_test.json","alice",3)
    assert "remediation_plan_test.json" in body
    assert "Due in: 3 days" in body

def test_signoff_ack():
    subj, body = signoff_ack_email("rp.json","bob","deadbeef")
    assert "deadbeef" in body
