#!/usr/bin/env python3
"""
Compatibility shim for legacy imports that expect a top-level
intervention_log module. Delegates to fraud.intervention_log.

Provides:
 - append_intervention(entry)  -> wrapper around emit_intervention()
 - verify_record(record)      -> lightweight schema/check validator used by tests
"""
from __future__ import annotations
import json
from typing import Dict, Any

# import the canonical implementation
try:
    from fraud.intervention_log import emit_intervention as _emit_intervention
except Exception as e:
    raise ImportError("Could not import fraud.intervention_log: " + str(e))

def append_intervention(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backwards-compatible name used by older tests.
    Delegates to fraud.intervention_log.emit_intervention.
    """
    return _emit_intervention(entry)

def verify_record(record: Dict[str, Any]) -> bool:
    """
    Lightweight verification used by tests:
    - checks presence of required keys from Rev7 schema
    - verifies input_hash/output_hash/signature_hash exist (non-empty)
    Returns True if minimal checks pass, else False.
    """
    required = ["timestamp","artifact_id","model_version","input_hash","output_hash","signature_hash"]
    for k in required:
        if k not in record:
            return False
        if record[k] is None or (isinstance(record[k], str) and record[k].strip() == ""):
            return False
    return True

# Export the canonical function names too (if tests import them)
emit_intervention = append_intervention
