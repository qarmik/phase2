# Protocol Qv — Phase II Repository (Rev 7.1)

**Date:** 04 January 2026  
**Status:** **Complete (Public, Non-Product)**  
**Scope:** Post-incident AI accountability artifacts  
**Authority:** Protocol Qv Rev 7.1 (Frozen)

---

## Overview

This repository contains the **completed, artifact-based implementation of Protocol Qv Rev 7.1**, a post-incident accountability protocol for AI systems.

The work is **evidence-first and post-deployment**.  
It focuses on how incidents are **bounded, preserved, classified, explained, refused, and handed to regulators** without narrative distortion or speculative inference.

This is **not a software product**.  
It is a **completed accountability protocol**, expressed entirely through **concrete, runnable, auditable artifacts**.

No roadmap is implied.

---

## What Protocol Qv Rev 7.1 Is

Protocol Qv Rev 7.1 provides a **deterministic accountability spine** that operates **only after an incident has occurred**.

For any incident within scope, the protocol will:

- produce verifiable accountability artifacts, **or**
- explicitly record **why accountability could not proceed** (refusal, blockage, downgrade).

Both outcomes are **valid and auditable**.

---

## What This Repository Contains

- **Canonical incident artifacts** (JSON / Markdown) suitable for audit and regulatory review  
- **Deterministic tools** used to generate, freeze, verify, and replay those artifacts  
- **Append-only logs and timestamps** establishing integrity and non-repudiation  
- **Documentation that records enforced behavior, limits, and refusals** — without promises  

All executable artifacts adhere to strict constraints:

- ≤200 LOC per tool  
- Deterministic outputs  
- Append-only where applicable  
- Explainable to a regulator in ≤2 minutes  

---

## Implemented Accountability Mechanisms (Complete Set)

Protocol Qv Rev 7.1 **defines and enforces the following accountability mechanisms**.  
Each mechanism either **produces an artifact** or **emits an explicit refusal**.

---

### Incident Boundary Freezing (GAP 1)

- Hash-anchored boundary freezes incident scope at a specific time  
- In-scope and out-of-scope evidence explicitly declared  
- Retroactive scope expansion or contraction prevented  

**Artifacts:**  
`docs/incidents/*_boundary_freeze.json`

---

### Evidence Classification with Unknown Preservation (GAP 2)

- Evidence classified as:
  - `observed_fact`
  - `inferred_relation`
  - `unknown`
- Default classification is **unknown** unless justified  
- Uncertainty is preserved, not silently resolved  

**Artifacts:**  
`docs/incidents/*_evidence_classification.json`

---

### Counterfactual Typing & Rejection (GAP 3)

- Counterfactual claims are mechanically accepted or rejected  
- Rejections are bounded to explicit reasons (e.g. victim blame, institutional impossibility)  
- No moral or speculative reasoning  

**Artifacts:**  
`docs/incidents/*_counterfactuals.json`

---

### Responsibility Lattice (GAP 4)

- Explicit declaration of who could act, intervene, or halt  
- Responsibility boundaries recorded without blame  

**Artifacts:**  
`docs/incidents/*_responsibility_lattice.json`

---

### Unified Incident Record (GAP 5)

- Single canonical record aggregating all prior artifacts  
- Serves as the accountability anchor  

**Artifacts:**  
`docs/incidents/*_unified_incident_record.json`

---

### Unknowns Register (GAP 6)

- Explicit preservation of unresolved facts and gaps  
- Unknowns are not forced into resolution  

**Artifacts:**  
`docs/incidents/*_unknowns_register.json`

---

### Incident Severity Taxonomy — Hardened (GAP 7)

- Post-incident severity classification based on **observed outcomes only**  
- No prediction, no risk scoring  
- Aggregation operates only on observed effects and **does not infer causality or likelihood**  
- Confidence downgrade applied when inputs are incomplete  

**Artifacts:**  
`docs/incidents/*_severity.json`

---

### Regulator Handoff / Evidence Pack (GAP 8)

- Structured packaging for regulator review  
- Supports EU routing readiness (ENISA SEP)  

If notification is legally blocked, deferred, or constrained,  
**the protocol records that refusal explicitly rather than proceeding**.

**Artifacts:**  
`docs/incidents/*_regulator_handoff_pack.json`

---

### Cross-Incident Comparability (GAP 9)

- Enables comparison across schema-compatible incidents  
- No aggregation beyond observable fields  

**Artifacts:**  
`docs/incidents/cross_incident_index.json`

---

### Public Verifiability / Replay Path (GAP 10)

- Enables third-party recomputation of outcomes  
- Emits explicit refusal when replay is blocked  
- Refusal is a terminal, auditable outcome  

**Artifacts / Tools:**  
`tools/day38_public_replay_path.py`  
`docs/incidents/*_unified_incident_record.sha256.txt`

---

## Regulatory Routing (Readiness, Not Assertion)

EU-relevant incidents are prepared for routing compatibility with:

- AI Act (Article 73)  
- GDPR (Article 33)  
- NIS2  
- DORA  
- CER  

Routing readiness **does not imply notification has occurred** unless explicitly stated in an artifact.  
Where routing is legally blocked or deferred, the protocol records that refusal explicitly.

---

## What This Repository Explicitly Refuses to Do

This repository does **not**:

- predict harm or future risk  
- assign intent, blame, or liability  
- provide design-time governance  
- offer compliance guarantees  
- override legal, sovereign, or vendor constraints  

When such conditions exist, the protocol records a **refusal** rather than proceeding silently.

---

## Completion Status

Protocol Qv Rev 7.1 is **complete**.

A declared holding pattern documents known temporal limits without reopening doctrine (see `docs/boundaries/rev7_1_temporal_limits_and_holding_pattern.md`).

No further GAPs exist in this revision.  
No roadmap is implied.  
No future version is opened.

Rev 7.2 may be considered **only** under explicitly documented failure conditions.

---

## Contribution Model

Protocol Qv evolves **only through artifacts**.

External contributions, if any, must be:
- concrete,
- minimal,
- auditable,
- refusal-aware.

**No contribution may modify GAPs 1–10 or reinterpret Protocol Qv Rev 7.1.**

Proposals without executable or inspectable artifacts are out of scope.

---

## Integrity & Disclosure

- Key loss events are preserved as forensic facts  
- Legacy non-verifiable entries are disclosed, not corrected retroactively  
- Absence of an artifact means a mechanism is **not enforced**

---

## License

Documentation and code are provided for:
- research,
- regulatory examination,
- public scrutiny.

**No warranty is implied.**
