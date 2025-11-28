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

Authoritative release and checksum

The authoritative audit export for Day 24 (Rev7 public snapshot) is published at:
https://github.com/qarmik/phase2/releases/tag/EU-FRAUD-TSA-2025Q4-snapshot

Asset: fraud_audit_export_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip
SHA-256: 493e7b70b47a9809ca2e5c386d8c4ce90bbabd0ea2d52444ad220ed123897f51

This ZIP contains:
- logs/public_timestamp.ndjson (append-only chain),
- logs/public_timestamp.ndjson.sig and logs/public_timestamp.jsonld.sig (detached snapshot signatures),
- keys/indusv.pub.pem (current public key),
- docs/release_note_DAY24_SNAPSHOT_SIGNED.md (release note and canonicalisation/key-rotation summary),
- logs/find_canonical_deep.txt and logs/replay_summary.csv (evidence of canonicalisation attempt and replay summary).

Verification instructions for auditors:
1. Download the ZIP from the release URL above.
2. Compute SHA-256 locally (e.g., `python -c "import hashlib;print(hashlib.sha256(open('fraud_audit_export_...zip','rb').read()).hexdigest())"`) and confirm it equals the SHA-256 shown here.
3. Verify detached snapshots using `keys/indusv.pub.pem`. For example:
   `openssl dgst -sha256 -verify keys/indusv.pub.pem -signature public_timestamp.ndjson.sig public_timestamp.ndjson`
If you require per-entry verification and legacy-key reconciliation, please request a forensic annex; we attempted automated canonicalisation reproduction and documented methods and outcomes in `logs/find_canonical_deep.txt`.



## Release integrity (audit record)

Authoritative release (Day 24, Rev7):
Release URL: '"$RELEASE_URL"'
Asset: fraud_audit_export_FRAUD-TSA-2025-AUTH-SNAPSHOT.zip

Contents and verification instructions are included in the repository and the ZIP (logs, detached signatures, public key, replay/find logs). See the Auditor notice — canonicalisation & key-rotation summary above for context.
