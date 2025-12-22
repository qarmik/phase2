Intervention Log — Plain English Explanation (Day 28)

# Intervention Log — Plain English Explanation (Day 28)

Protocol: Qv Rev 7.1  
Scope: Human intervention accountability under EU AI Act Art. 73  
Audience: Auditors, regulators, compliance officers


(I) What this file is:-

1. This file is a permanent record of a human stepping in when an automated system could not be trusted to continue on its own.
2. It answers one question clearly: when something went wrong, did a human take responsibility, and is that decision traceable later?
3. It is not a technical log. It is an accountability record.


(II) When an entry is created:-

An entry is created only when a human intervenes in an AI-assisted decision.
For example: escalating a fraud case, overriding a model output, rolling back a decision, or stopping a system entirely.
If the AI runs normally, nothing is written. This log exists only for exceptions.


(III) Who is accountable:-

Accountability is assigned to a role, not a person.
Examples: Risk Officer, Compliance Lead, Incident Manager.
This ensures the organisation cannot hide behind “the system decided” or blame a nameless process.


(IV) What cannot be changed later:-

Once written, the following must never change:
1. intervention\_id – the unique reference auditors will cite
2. timestamp\_utc – when the human decision happened
3. human\_accountable – who took responsibility
4. decision\_summary – why the intervention occurred
5. eu\_single\_entry\_point – how the incident is routed to regulators

These are immutable because changing them would rewrite history.

(V) How an auditor would verify it:-

An auditor would:
1. Open the intervention log JSON file
2. Check that all required fields exist
3. Confirm the timestamp format is valid UTC
4. Verify the ENISA Single-Entry Point routing fields
5. Cross-reference evidence links (monitorability snapshot, public timestamp log)
6. Confirm the file is append-only and not rewritten





