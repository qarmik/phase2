cat > docs/logbook_day25.md <<'MD'
# Day 25 — Monitorability Snapshot (Protocol Qv Rev7)

**Tag:** day25-monitor-snapshot-20251108T210705Z  
**Tag object:** fc6d54331b6f03d2b945a4ad4580437cc65bf072  
**Commit (peeled):** 2fba9b022ef4de6d2164eac54b025296ce47eacd  
**Branch:** stage1/fraud  
**Date (UTC):** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Summary
Created Day-25 monitor snapshot and executed monitorability CI: QVM trace, QVM scoring upgrade, incident simulator, TF-IDF faithfulness checks, monitorability verification. Auditor packet produced and detached-signed with current key.

## Artifacts
- dist/audit_packet_EU-FRAUD-TSA-2025Q4-snapshot_20251108T183603Z.zip  
  SHA-256: 3d54e907a79c6e9d6edbfb35640a22b97b225f238d0d58738fb37da46908c4f1
- logs/monitorability_snapshot.jsonld
- logs/monitorability_trace.jsonld
- logs/replay_summary.csv
- keys/key_index.json
- docs/forensic_annex_DAY24_REV7.md (legacy key declared)

## Forensic statement
The legacy signing key (indusv_v1) is missing from local archives and thus historical entries signed with it are non-verifiable. We preserve all historical entries and document the mismatches. Current authoritative artifacts are signed with indusv_v2 (fingerprint recorded in keys/key_index.json).

## Next (short)
- Day 26: Harden monitor daemon, extend incident simulator scenarios, and introduce external anchor automation (opt-in).
MD

