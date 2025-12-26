> Scope: Draft explanatory note prepared for potential notified-body review.  
> Presence does not imply submission or regulatory notification.



\# For Notified Body — Submission Checklist \& Verification Guide



\## Purpose

This package (`dist/fraud\_audit\_export\_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip`) contains the authoritative audit snapshot for the FRAUD-TSA artifact family (Protocol Qv — Rev7). It includes an append-only publication log and detached signatures produced with the current RSA key `keys/indusv.pem` (private) / `keys/indusv.pub.pem` (public). This document shows exactly how to verify integrity and authenticity locally.



\## Delivered artifacts (inside ZIP)

\- `public\_timestamp.ndjson` — append-only chain of publication entries (logs/public\_timestamp.ndjson)

\- `public\_timestamp.ndjson.sig` — detached binary signature of the NDJSON snapshot (signed with current RSA private key)

\- `public\_timestamp.jsonld` — latest entry in JSON-LD form (logs/public\_timestamp.jsonld)

\- `public\_timestamp.jsonld.sig` — detached binary signature of the JSON-LD file

\- `fraud\_bundle.zip` — the bundled artifact that was timestamped

\- `42001-mapping.md` — ISO/IEC 42001 mapping (placeholder / mapping doc)

\- `intervention\_log\_sample.json` — human intervention sample (placeholder)

\- `release\_note\_DAY24\_SNAPSHOT\_SIGNED.md` — explanation of mismatch \& remediation

\- `keys/indusv.pub.pem` (provided separately; DO NOT request private key)



> Note: Historical NDJSON entries are preserved. Some earlier embedded per-entry signatures in `public\_timestamp.ndjson` do not verify against the current public key; remediation and an authoritative snapshot signature have been provided. See \*Release note\* for details.



---



\## High-level verification steps (recommended order)



1\. \*\*Unpack the audit ZIP (optional)\*\*  

&nbsp;  Inspect contents without extracting:

&nbsp;  ```bash

&nbsp;  unzip -l dist/fraud\_audit\_export\_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip




- Audit packet: https://github.com/qarmik/phase2/releases/download/EU-FRAUD-TSA-2025Q4-snapshot/audit_packet_EU-FRAUD-TSA-2025Q4-snapshot_20251108T183603Z.zip
  SHA-256: 3d54e907a79c6e9d6edbfb35640a22b97b225f238d0d58738fb37da46908c4f1

