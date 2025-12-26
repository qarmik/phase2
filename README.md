# Protocol Qv — Phase II Repository (Rev 7.1)

**Date:** 26 December 2025  
**Status:** Active (Public, Non-Product)  
**Scope:** Post-incident AI accountability artifacts  
**Authority:** Protocol Qv Rev 7.1 (unchanged)

---

## Overview

This repository contains the **public, artifact-based development** of **Protocol Qv Rev 7.1**, a post-incident governance protocol for AI systems.  
The work here is **evidence-first** and **post-deployment**: it focuses on how incidents are bounded, preserved, classified, and handed to regulators without narrative distortion.

This is **not** a software product.  
It is a **doctrine under construction**, expressed through concrete, runnable artifacts.

---

## What This Repository Contains

- Canonical **incident artifacts** (JSON/Markdown) suitable for audit and regulatory review
- Deterministic **tooling** used to generate, freeze, and verify those artifacts
- Append-only **logs and timestamps** establishing integrity and non-repudiation
- Documentation that records **what is enforced today**, without promises

All artifacts adhere to the following constraints:
- ≤200 LOC per tool
- Deterministic outputs
- Append-only where applicable
- Explainable to a regulator in ≤2 minutes

---

## Implemented Controls (Protocol Qv Rev 7.1)

The following controls are **implemented and verifiable** in this repository.

### Incident Boundary Freezing (GAP 1)

- A hash-anchored boundary artifact freezes the incident scope at a specific time.
- In-scope and out-of-scope evidence are explicitly declared.
- Retroactive scope expansion or contraction is prevented.

**Artifacts:**  
`docs/incidents/*_boundary_freeze.json`

---

### Evidence Classification with Unknown Preservation (GAP 2)

- All evidence within a frozen boundary is classified as:
  - `observed_fact`
  - `inferred_relation`
  - `unknown`
- Default classification is `unknown` unless explicitly justified.
- Uncertainty is preserved rather than silently resolved.

**Artifacts:**  
`docs/incidents/*_evidence_classification.json`

---

## Regulatory Routing

All EU-relevant incidents are prepared for routing via the **ENISA Single Entry Point (SEP)**, with harmonized classification for:

- AI Act Article 73
- GDPR Article 33
- NIS2
- DORA
- CER

Routing readiness does not imply notification has occurred unless explicitly stated in an artifact.

---

## What This Repository Does Not Claim

- It does not guarantee safety, compliance, or correctness of AI systems.
- It does not provide predictive risk scoring or pre-deployment assurances.
- It does not claim completion of all Protocol Qv gaps.
- It does not include roadmaps, timelines, or future commitments.

Absence of an artifact implies the control is **not yet enforced**.

---

## Contribution Model

Protocol Qv evolves through **artifacts, not proposals**.  
External contributions are expected to be concrete, minimal, and auditable.

---

## Integrity and Disclosure

Key loss events are treated as forensic facts, not corrected retroactively.  
Legacy non-verifiable entries are explicitly disclosed where applicable.

---

## License

Documentation and code are provided for research, regulatory examination, and public scrutiny.  
No warranty is implied.
