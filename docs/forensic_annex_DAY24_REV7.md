\# Forensic Annex — Canonicalisation and Verification Attempt

\*\*Artifact Family:\*\* FRAUD-TSA  

\*\*Phase:\*\* Day 24 — Rev 7 Migration  

\*\*Repository:\*\* qarmik/phase2  

\*\*Branch:\*\* stage1/fraud  

\*\*Release Tag:\*\* EU-FRAUD-TSA-2025Q4-snapshot  

\*\*Author / Operator:\*\* Rohit Kumar (Cadet Q0)  

\*\*Date:\*\* 2025-11-05 UTC  

\*\*Checksum of release asset:\*\* ce27e42ef58c75c1b2c9421613e2abecc5db4e04a8055a0221d424c11da66643  



---



\## 1 — Purpose

To document the forensic process used to reproduce historical `entry\_hash` values within `logs/public\_timestamp.ndjson` after the Rev 7 key rotation and canonicalisation update.



---



\## 2 — Context

\- During Rev 7 migration, historical entries retained their stored `entry\_hash` values.

\- The active signing key (`indusv\_v2`, fingerprint f39e1f866e7e9a05368f292eefcacc6b598050821065d8275fef9dfe0e74378f) replaced a missing legacy key (`indusv\_v1`).

\- Objective: identify the original JSON serialisation parameters or field set that produced each stored `entry\_hash`.



---



\## 3 — Methodology

\### Tools Used

| Tool | Path | Description |

|------|------|-------------|

| `tools/find\_canonical.py` | commit 040a076 | First-stage 288-variant canonicalisation sweep. |

| `tools/find\_canonical\_deep.py` | commit 040a076 | Extended 4 032-variant sweep including UTF-16, Unicode NFC/NFD, trimming, slash-normalisation. |

| `tools/log\_replay.py` | current | Verified chain continuity and signature status. |



\### Procedure

1\. Extracted all NDJSON entries (`logs/public\_timestamp.ndjson`, 11 entries).  

2\. Removed `signature\_b64` field to isolate canonical content.  

3\. Executed both sweep scripts to test combinations of:

&nbsp;  - `ensure\_ascii` (True/False)  

&nbsp;  - `sort\_keys` (True/False)  

&nbsp;  - `separators` (default / compact)  

&nbsp;  - newline inclusion  

&nbsp;  - Unicode normalisation (NFC / NFD / raw)  

&nbsp;  - encoding (UTF-8 / UTF-16LE / UTF-16BE)  

&nbsp;  - field removals (timestamp, bundle\_path, etc.)  

&nbsp;  - trimming \& slash-normalisation  

4\. Logged all outcomes to:

&nbsp;  - `logs/find\_canonical\_results.txt`

&nbsp;  - `logs/find\_canonical\_deep.txt`

5\. Compared each recomputed SHA-256 against stored `entry\_hash` values.



---



\## 4 — Results

| Metric | Value |

|---------|------:|

| Entries analysed | 11 |

| Variants tested per entry | 4 032 |

| Matches found | 0 |

| Chain continuity (`prev\_entry\_hash`) | ✅ Intact |

| Detached snapshot signatures verification | ✅ OK |

| Reproduced per-entry signatures | ❌ Not reproducible (legacy key absent) |



Conclusion:  

No tested canonicalisation variant reproduced the historical `entry\_hash` values; therefore those values were produced using a legacy code path or signing routine no longer present.



---



\## 5 — Integrity Evidence

\- NDJSON file preserved unchanged (append-only).  

\- Detached signatures verified successfully with the active key (`indusv\_v2`).  

\- SHA-256 of audit export ZIP: `ce27e42ef58c75c1b2c9421613e2abecc5db4e04a8055a0221d424c11da66643`.  

\- Public key: `keys/indusv.pub.pem`.



---



\## 6 — Follow-Up Plan

1\. Maintain `logs/find\_canonical\_deep.txt` as permanent record.  

2\. If legacy key recovered, compute its DER-SHA256 and test verification retroactively.  

3\. Append new findings (if any) as Annex B in this file.  

4\. Continue using detached snapshot signatures as authoritative evidence.



---



\## 7 — Sign-Off

I certify that the above forensic reconstruction accurately reflects the procedures and results obtained on 2025-11-05 UTC.



\*\*Operator:\*\* Rohit Kumar (Cadet Q0)  

\*\*Repository:\*\* qarmik/phase2 @ commit 040a076  

\*\*Signature:\*\* \_GPG-signed in repository commit history (stage1/fraud branch)\_




- NOTE (Day25-Reconciliation): legacy public key indusv_v1 not present locally; see logs/verification_annotations.json for details. Recorded: 2025-11-08T12:36:16.517826Z

## Legacy verification status (summary)
- Date checked: 2025-11-11T00:00:00Z
- Finding: Several historical NDJSON entries contain detached signatures that do not verify with current key(s) in keys/.
- Evidence sample:
  - artifact_id: TEST-RELEASE-0002
  - stored entry_hash: 656c0902ef26...
  - computed canonical SHA256: c2abacd2696f...
  - stored signature length: 512 bytes
  - stored signature SHA256: 7fa5463c1c9d...
  - conclusion: stored signature was produced by a different private key (legacy key missing or different). Do not retro-sign.
- Remediation: keep entries as-is; publish new authoritative snapshot signed by current key `indusv_v2` and reference it here.
