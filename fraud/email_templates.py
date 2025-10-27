#!/usr/bin/env python3
"""
email_templates.py
Parameterized email templates for compliance escalations and owner reminders.

Functions:
- escalation_email(notif_bundle) -> (subject, body)
- owner_reminder_email(plan_file, owner, due_days) -> (subject, body)
- signoff_ack_email(plan_file, owner, signature_hash) -> (subject, body)

Return values are (subject:str, body:str). Bodies are plain-text, regulator-friendly.
"""
from __future__ import annotations
import datetime
from typing import Dict, Any, Tuple

def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def escalation_email(notif: Dict[str, Any]) -> Tuple[str, str]:
    """
    Build escalation subject + body from an escalation notification bundle.
    """
    subject = f"[Escalation] {notif.get('artifact_id','artifact')} — {notif.get('escalation_summary',{}).get('escalations',0)} items"
    lines = [
        f"Generated: {_now_iso()}",
        f"To: {notif.get('notify_to')}",
        "",
        f"Escalation summary: {notif.get('escalation_summary')}",
        "",
        "Escalations (if any):"
    ]
    esc = notif.get("escalations", [])
    if not esc:
        lines.append("  - No active escalations at this time.")
    else:
        for e in esc:
            lines.append(f"  - {e.get('missing_item')} | priority={e.get('priority')} | overdue={e.get('overdue')}")
    lines.append("")
    lines.append(f"Notification signature: {notif.get('signature_hash','')}")
    lines.append("")
    lines.append("Action: Review the remediation plan and respond with sign-off or corrective action.")
    return subject, "\n".join(lines)

def owner_reminder_email(plan_file: str, owner: str, due_days: int) -> Tuple[str, str]:
    subject = f"[Reminder] Action required: remediation plan {plan_file}"
    body = (
        f"Owner: {owner}\n"
        f"Plan: {plan_file}\n"
        f"Due in: {due_days} days\n\n"
        "Please review the remediation tasks and update the plan with progress or mark items resolved.\n\n"
        "If you believe this assignment is incorrect, reply with 'reassign' and the proposed owner id."
    )
    return subject, body

def signoff_ack_email(plan_file: str, owner: str, signature_hash: str) -> Tuple[str, str]:
    subject = f"[Sign-off] Remediation plan acknowledged: {plan_file}"
    body = (
        f"Owner: {owner}\n"
        f"Plan: {plan_file}\n"
        f"Signature: {signature_hash}\n\n"
        "This acknowledges manual sign-off and will be appended to the intervention log for provenance."
    )
    return subject, body
