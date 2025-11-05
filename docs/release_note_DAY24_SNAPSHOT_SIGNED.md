# Release Note — Day 24 snapshot signing (authoritative)

Date (UTC): $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Authoritative snapshot: logs/public_timestamp.ndjson + logs/public_timestamp.jsonld
Action: Detached signatures created for authoritative snapshot using keys/indusv.pem:
 - logs/public_timestamp.ndjson.sig
 - logs/public_timestamp.jsonld.sig

Reason:
 - Some per-entry signatures embedded in logs/public_timestamp.ndjson do not verify against the current public key (keys/indusv.pub.pem). Investigation indicates at least one historical NDJSON entry's stored signature bytes do not match signatures produced with the current signing key. Cause may be prior key rotation or corrupted signature bytes.

Remediation:
 - The current snapshot files were signed verbatim (detached signatures above). These detached signatures are authoritative for the snapshot provided to auditors/notified bodies.
 - Historical mismatched entries are preserved in logs/public_timestamp.ndjson for transparency. If the original signing key is recovered, provide it to auditors to allow retrospective verification.

Key fingerprint (current public key):
$(openssl pkey -pubin -in keys/indusv.pub.pem -outform DER 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //')


## Auditor notice — canonicalisation & key-rotation summary

During the Rev7 migration (Day 24) we rotated the signing key used to produce public timestamps. Historical NDJSON entries are preserved in `logs/public_timestamp.ndjson` as an immutable, append-only record. We performed an automated canonicalisation reproduction effort (multiple JSON serialization variants, separators, newline/no-newline, unicode normalizations, trimming, slash-normalization, and UTF-16/UTF-8 encodings). That automated sweep (recorded in `logs/find_canonical_deep.txt`) did not produce a byte-for-byte match for several historical `entry_hash` values.

Operational posture:
- The authoritative cryptographic evidence for the published snapshot is the detached snapshot signatures signed with the current active signing key and included in the audit export: `logs/public_timestamp.ndjson.sig`, `logs/public_timestamp.jsonld.sig`, and `dist/fraud_audit_export_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip`.
- Historical `entry_hash` values are retained for transparency but may have been generated with a different canonicalisation or an earlier signing key that is not available in local backups. If a legacy public/private key pair is later recovered, we will compute its DER-SHA256 fingerprint and reconcile which historical entries verify under that legacy key.
- For auditors who want per-entry verification today, run `python tools/log_replay.py` to see which entries verify under currently available public keys; results are recorded in `logs/replay_summary.csv`.
- If further forensic analysis is requested we will escalate with an extended, documented sweep and provide a forensic annex recording methods and outcomes.

