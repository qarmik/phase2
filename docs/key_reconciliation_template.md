\# Key Reconciliation Record





\*\*Artifact family:\*\* FRAUD-TSA

\*\*Repository:\*\* qarmik/phase2

\*\*Branch:\*\* stage1/fraud





\## 1. Summary

\- \*\*Event:\*\* Key rotation / reconciliation record

\- \*\*Date of record:\*\* {{UTC timestamp}}

\- \*\*Operator:\*\* {{your name / operator id}}





\## 2. Key inventory

| Key ID | Role | Fingerprint (DER-SHA256) | Public key file | Private key archive path (encrypted / offline) | Notes |

|--------|------|--------------------------:|-----------------|-----------------------------------------------:|-------|

| indusv\_v1 | signing (legacy) | {{fingerprint or UNKNOWN}} | {{keys/indusv\_v1.pub.pem if available}} | {{archive/indusv\_v1.pem.enc or 'missing'}} | e.g., used until 2025-11-05 10:15 UTC |

| indusv\_v2 | signing (current) | {{fingerprint}} | keys/indusv.pub.pem | keys/archive/indusv\_v2.pem.gpg | created during Rev7 migration |





\## 3. Chronology (events)

\- {{date}} — Generated key `indusv\_v2` (current). Fingerprint: {{fingerprint}}.

\- {{date earlier}} — Previous key `indusv\_v1` used to sign NDJSON entries up to entry\_hash {{hex}}.

\- {{date}} — Per-entry verification showed mismatch for entries with signer\_pub\_fingerprint matching {{fingerprint\_v1}}.

\- {{date}} — Created authoritative snapshot and detached signatures (files: `logs/public\_timestamp.ndjson.sig`, `logs/public\_timestamp.jsonld.sig`).





\## 4. Evidence \& location of artifacts

\- `logs/public\_timestamp.ndjson` — append-only chain (contains legacy signatures).

\- `logs/public\_timestamp.jsonld` — latest entry (authoritative snapshot reflected here).

\- Detached signatures: `logs/public\_timestamp.ndjson.sig`, `logs/public\_timestamp.jsonld.sig`.

\- Audit export: `dist/fraud\_audit\_export\_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip`.

\- Release/reconciliation note: `docs/release\_note\_DAY24\_SNAPSHOT\_SIGNED.md`.





\## 5. Action taken

\- Preserved historical NDJSON entries (append-only).

\- Created detached signature snapshot signed with current key `indusv\_v2`.

\- Documented rotation in `docs/release\_note\_DAY24\_SNAPSHOT\_SIGNED.md`.

\- Recommended: archive any old private keys offline (if found) and record fingerprint in `keys/key\_index.json`.





\## 6. Auditor instructions

\- Use `keys/indusv.pub.pem` to verify detached snapshot signatures.

\- If provider recovers `indusv\_v1` public key, compute its DER-SHA256 and cross-check against `public\_timestamp.ndjson` entries.





\## 7. Declaration

I declare that the above statements are accurate to the best of my knowledge.





Operator: Documented operator

Date 05/11/2025: 17:15 IST

