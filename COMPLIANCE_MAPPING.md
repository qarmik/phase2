# COMPLIANCE_MAPPING.md
Protocol-Version: Qv Rev 7 (Draft 0.1)
classification: EXTERNAL-INDUSTRY

This document maps key artifact fields to normative clauses in ISO 42001, NIST AI RMF 600-1, and the EU AI Act (Articles referenced).
Use this crosswalk when preparing notified-body packages, DPIA/FRIA, and incident reports.

---

## 1. Intervention Log (intervention_log.json schema)

- `timestamp`
  - ISO mapping: ISO 42001 §8.7 (incident & log timestamps)
  - NIST AI RMF: Monitor & Respond functions (time-series audit)
  - EU AI Act: Article 73 (serious incident reporting) — use absolute time in submissions.

- `artifact_id`
  - ISO: Clause on Record Identification & Traceability (ISO 42001 §7/§8)
  - NIST: ID fields for data lineage

- `model_version`
  - ISO: Configuration & Change Control (ISO 42001 §9)
  - NIST: Model management / lifecycle

- `input_hash` / `output_hash`
  - ISO: Evidence integrity (checksum)
  - NIST: Reproducibility / audit trails
  - Use SHA-256 canonicalization for both.

- `signature_hash`
  - ISO: Tamper-evident audit (append-only signing recommendation)
  - Use HMAC or asymmetric signature as local policy; include signer id in `metadata`.

- `human_id`, `human_reason`, `decision_summary`
  - ISO: Human oversight trace (ISO 42001 human oversight clauses)
  - EU AI Act: documentation of human intervention for high-risk systems.

- `quantum_verification_hash`
  - Rev 7: QVM augmentation field (nullable)
  - Normative note: include `quantum_verification_hash` when QVM verification performed; map to QVM module output digest.

- `incident_report_id`
  - EU AI Act: Article 73 report identifier (when reported to national market surveillance)
  - Store provider/EC submission ID here.

- `gpa_model_id`
  - GPAI / systemic-risk mapping: include when model classified as GPAI/systemic

- `joules_per_verified_operation`
  - Compute-aware design: record energy metric (Compute/Energy Audit Lens)
  - Useful for audit & notified-body energy impact assessment.

- `metadata.tool`, `metadata.version`, `metadata.run_id`
  - Provenance mapping: ISO/NIST evidence for toolchain and run context.

---

## 2. Evidence Package Manifest (evidence_package.json)

- `package_name`
  - Identifier for the evidence zip.

- `generated_at`
  - ISO timestamp for package generation (used in notarisation).

- `files[].sha256`
  - Per-file integrity checks for notified-body submission (preferred: SHA-256).

- `package_signature`
  - Combined package-level signature. Map to insurer evidence signature expectation (Lloyd’s-style requirement).

- `receipts[].receipt_id`
  - External timestamp provider receipt; map to external anchor evidence (store raw provider response).

- `quantum_verification_hash`
  - If available, attach QVM proof per package.

- `joules_total`
  - Aggregate energy cost for package generation.

- `evidence_owner`
  - Owner responsible for evidence; used by owner-assignment automation (SLA).

---

## 3. Notes & Operational Guidance

- Always include `Protocol-Version: Qv Rev 7 (Draft 0.1)` and `classification:` in top-level READMEs for the repo and in evidence package top-level metadata.
- When producing DPIA/FRIA artifacts, auto-fill the above fields where applicable and include references to the mapping lines above.
- For Article 73 incidents, populate `incident_report_id` with the EC/national authority submission id and mirror it into evidence package `receipts`.
- For insurer consumption, ensure `signature_hash` is computed with an agreed algorithm and key-management policy; document method in artifact README.

End of `COMPLIANCE_MAPPING.md`.
