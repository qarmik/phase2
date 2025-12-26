# This logbook records actions completed on Day 25 under Protocol Qv Rev 7.1.

# It is a factual execution record intended to support later audit review.



# 

# 

# Day 25 — Monitorability Snapshot (Protocol Qv Rev7)

**Tag:** day25-monitor-snapshot-20251108T210705Z  
**Tag object:** fc6d54331b6f03d2b945a4ad4580437cc65bf072  
**Commit (peeled):** 2fba9b022ef4de6d2164eac54b025296ce47eacd  
**Branch:** stage1/fraud  
**Date (UTC):** 2025-11-09T00:00:00Z

## Summary

Created Day-25 monitor snapshot and executed monitorability CI: QVM trace, QVM scoring upgrade, incident simulator, TF-IDF faithfulness checks, monitorability verification. Auditor packet produced and detached-signed with current key.

## Artifacts

* dist/audit\_packet\_EU-FRAUD-TSA-2025Q4-snapshot\_20251108T183603Z.zip  
  SHA-256: 3d54e907a79c6e9d6edbfb35640a22b97b225f238d0d58738fb37da46908c4f1
* logs/monitorability\_snapshot.jsonld
* logs/monitorability\_trace.jsonld
* logs/replay\_summary.csv
* keys/key\_index.json
* docs/forensic\_annex\_DAY24\_REV7.md (legacy key declared)

## Forensic statement

The legacy signing key (indusv\_v1) is missing from local archives and thus historical entries signed with it are non-verifiable. We preserve all historical entries and document the mismatches. Current authoritative artifacts are signed with indusv\_v2 (fingerprint recorded in keys/key\_index.json).

## Next (short)

* Day 26: Harden monitor daemon, extend incident simulator scenarios, and introduce external anchor automation (opt-in).
