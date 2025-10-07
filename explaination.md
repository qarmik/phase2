\# Stage 1 — Fraud Red-Team

\_Timestamp: 2025-10-05\_



\## Purpose

To simulate simple transaction-level fraud detection rules that a junior compliance analyst could read and test.



\## Core Function

`is\_suspicious(tx)` flags:

1\. Transactions with amount > ₹ 1 Lakh  

2\. Cross-border transactions (country ≠ IN or US)  

3\. Activity from fake / emulator devices  



\## Unit Tests

3 tests confirm:

\- High amount → flagged ✅  

\- Foreign country → flagged ✅  

\- Clean transaction → not flagged ✅  



\## Defense Logic

These are not ML models; they are rule-based controls used for early triage before escalation.



\*Not speed, but sovereignty. Not scale, but scars.\*



## Insurance Alignment Note
Every flagged transaction now triggers an immutable, tamper-evident intervention log
(JSONL format with signed hashes). This design aligns with insurer and regulatory
audit standards for human-in-the-loop oversight.

