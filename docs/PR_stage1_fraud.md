# PR Archive — Stage 1: Fraud Red-Team Merge
**Branch merged:** stage1/fraud-day9 → stage1/fraud  
**Author:** Cadet Q0 (Rohit Kumar)  
**Reviewed by:** Commander V (AI strategist)  
**Date (merge):** 2025-10-11

## Summary (one line)
Merge README + .gitignore + Day-9 scoring artifacts into Stage 1 main branch to complete Phase II Stage-1 audit loop (Simulator → Immutable Intervention Log → Metrics → Compliance Ingestor → Validator → Score Engine).

## What changed (concise)
- Added `README.md` (Phase II overview, doctrine-safe copy).  
- Added / updated `.gitignore` to exclude runtime logs and artifacts.  
- Integrated insurer-grade immutable intervention log usage across fraud logger.  
- Added `score_engine.py` (automated scoring stub) and unit tests.  
- Added docs mapping: `docs/42001-mapping.md`.  
- Added `compliance_ingestor.py` and `compliance_validator.py` (ingest → checklist loop).
- Added `intervention_summary.py` (audit summarizer).

## Why this merge (audit rationale)
- Aligns Stage 1 artifacts with **Insurance Alignment Clause**: every human or system intervention now produces an append-only, tamper-evident intervention record (JSONL).  
- Provides EU-ready compliance ingestion and checklist autogeneration for regulator demos.  
- Prepares the artifact for insurer pilots by producing DPIA/FRIA JSON outputs on demand.

## How to run (sanity & reproducibility)
From repo root (`phase2/`):

```bash
# activate venv
source .venv/Scripts/activate

# run a simulator + logger
python fraud/fraud_logger.py

# produce aggregate metrics
python fraud/fraud_metrics.py

# summarize interventions
python intervention_summary.py

# parse a sample regulation (place PDF in input/)
python compliance_ingestor.py
python compliance_validator.py

# run score engine (example)
python fraud/score_engine.py --input sample.json --append-log --fria
