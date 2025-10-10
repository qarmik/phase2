# Indus V-ai — Phase II: Artifact Literacy Campaign (2025–2026)

This repository contains the training and artifact-building sequence for the Indus V-ai initiative — a boutique assurance and adversarial oversight lab.  
Phase II (Oct 2025 → Mar 2026) focuses on **artifact literacy**: building ≤ 200 LOC regulatory-grade Python artifacts mapped to EU AI Act / RBI compliance / insurer liability standards.

---

## 📜 Core Doctrine

- **Artifact Families:**  
  1. Fraud Red-Team Testbed (synthetic borrowers, mule scripts)  
  2. Compliance Audit Pack (RBI + EU AI Act checklists + DPIA/FRIA)  
  3. Consumer Trust Explainability Pack  
  4. Healthcare / Insurance Oversight Module  
  5. Compute / Energy Chokepoint Lens  

---

## ⚙️ Repository Layout
phase2/
├── fraud/ # Stage 1 – Fraud Red-Team Testbed
│ ├── fraud_simulator.py
│ ├── fraud_logger.py
│ ├── fraud_metrics.py
│ └── score_engine.py
│
├── compliance/ # Stage 2 – Compliance Audit Pack
│ ├── compliance_ingestor.py
│ ├── compliance_validator.py
│ └── output/compliance_checklist.md
│
├── artifacts/
│ └── evidence/ # DPIA / FRIA JSON outputs
│
├── docs/
│ ├── 42001-mapping.md # ISO 42001 alignment checklist
│ └── explaination.md
│
├── tests/ # pytest unit tests
│ └── test_score_engine.py
│
└── README.md

yaml
Copy code

---

## 🧩 Tools & Environment
- Python ≥ 3.10  
- Virtual env: `.venv/`  
- Libraries: `pytest`, `pandas`, `scikit-learn` (Stage 3+)  
- Logging and Integrity: `hashlib`, `json`, `pathlib`  
- CLI tested on Git Bash (Windows 10)

---

## 🧱 Stage Summary (progress)
| Stage | Artifact | Status |
|--------|-----------|---------|
| 1 | Fraud Red-Team Simulator + Immutable Intervention Log | ✅ Completed |
| 2 | Compliance Ingestor + Validator | ✅ Completed |
| 3 | Automated Scoring Stub + DPIA/FRIA Hook | 🚧 In progress |
| 4 | Healthcare / Insurance Oversight | ⏳ Scheduled |
| 5 | Compute / Energy Chokepoint Lens | ⏳ Pending deployment |

---

## 🧭 Licensing & Credits
© 2025 Indus V-ai Initiative — Rohit Kumar (Cadet Q0)  
Mission Advisor: Commander V (AI Strategist)  
Licensed for research and regulatory demonstration under Creative Commons BY-NC 4.0.

---

*Mantra:* _Not scale, but scars. Not speed, but sovereignty._