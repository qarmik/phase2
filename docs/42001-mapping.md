\# 42001 Mapping — `fraud\_v1` (score\_engine.py)



\*\*Artifact\*\*: fraud\_v1 (Automated scoring stub)  

\*\*Model version\*\*: v0.2 (example)



\## Purpose

Provide minimal AIMS evidence mapping demonstrating alignment with selected ISO/IEC 42001 clauses:

\- Risk management

\- Data lineage

\- Human oversight \& intervention logging



\## Mapping (short)

\- \*\*Context of the organization (Clause 4)\*\*:

&nbsp; - EU-first deployment; synthetic demo data for DPIA; insurer-readiness.



\- \*\*Leadership \& accountability (Clause 5)\*\*:

&nbsp; - `artifact\_id` + `model\_version` in every log entry for traceability.



\- \*\*Planning (Clause 6)\*\*:

&nbsp; - DPIA generation hook (`--fria`) to capture fundamental-rights checks.



\- \*\*Support (Clause 7)\*\*:

&nbsp; - Evidence directory `artifacts/evidence/` stores DP(A)/FRIA JSONs.



\- \*\*Operation (Clause 8)\*\*:

&nbsp; - `automated\_score()` deterministic rules; `InterventionLog.append()` enforces append-only NDJSON with `signature\_hash` chaining.



\- \*\*Performance evaluation (Clause 9)\*\*:

&nbsp; - Unit tests in `tests/test\_score\_engine.py` validate expected behaviours and chaining.



\- \*\*Improvement (Clause 10)\*\*:

&nbsp; - DPIA includes `mitigations`; FRIA placeholder lists alternatives.



\## Evidence artifacts

\- `intervention\_log.ndjson` (append-only, signature chain)

\- `artifacts/evidence/dpia\_\*.json`

\- `tests/test\_score\_engine.py`

\- `docs/42001-mapping.md` (this file)



\## Notes for auditors

\- Logs contain: `timestamp`, `artifact\_id`, `model\_version`, `input\_hash`, `decision\_summary`, `human\_id`, `human\_reason`, `output\_hash`, `signature\_hash`.

\- Signature calculation: `SHA256(prev\_signature + input\_hash + output\_hash)`. This makes tampering of old entries evident.



