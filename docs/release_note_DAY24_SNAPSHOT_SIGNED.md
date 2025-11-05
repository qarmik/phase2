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

