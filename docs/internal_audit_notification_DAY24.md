> Scope: Internal audit communication template.  
> This document is not a canonical incident artifact.



Email/notification template to send to auditors / insurers



Subject: FRAUD-TSA — Day24 (Rev7) audit snapshot published — checksum \& verification



Dear \[Auditor / Insurer Team],



We have published the Day 24 (Rev7) authoritative audit snapshot for the FRAUD-TSA artifact family.



Release URL:

https://github.com/qarmik/phase2/releases/tag/EU-FRAUD-TSA-2025Q4-snapshot



Asset:

fraud\_audit\_export\_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip



SHA-256: <<ZIP\_SHA256>>



What’s included:

\- append-only NDJSON log: logs/public\_timestamp.ndjson

\- detached snapshot signatures: logs/public\_timestamp.ndjson.sig and logs/public\_timestamp.jsonld.sig

\- public key: keys/indusv.pub.pem

\- canonicalisation forensics attempt: logs/find\_canonical\_deep.txt

\- replay summary: logs/replay\_summary.csv

\- release note with canonicalisation \& key-rotation summary: docs/release\_note\_DAY24\_SNAPSHOT\_SIGNED.md



Verification steps:

1\. Download the ZIP from the Release URL and confirm the SHA-256 matches the value above.

2\. Verify detached signatures using `keys/indusv.pub.pem`. Example:

&nbsp;  `openssl dgst -sha256 -verify keys/indusv.pub.pem -signature public\_timestamp.ndjson.sig public\_timestamp.ndjson`



Notes:

\- We rotated the signing key during the Rev7 migration and attempted canonicalisation reproduction for historical `entry\_hash` values (see logs/find\_canonical\_deep.txt). No byte-for-byte reproduction was found for some legacy entries; detached snapshot signatures are the authoritative evidence for the published snapshot.



If you require a deeper forensic annex or assistance verifying specific entries, reply and we will escalate.



Regards,

Rohit Kumar (Cadet Q0)







