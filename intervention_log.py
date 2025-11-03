#!/usr/bin/env python3
"""
Compatibility shim for legacy imports that expect a top-level
intervention_log module. Delegates to fraud.intervention_log.

Provides both legacy function signatures used by older tests:
 - append_intervention(artifact_id, model_version, input_dict, decision_summary, human_id, human_reason, output_dict)
 - append_intervention(entry_dict)  # new-style single-arg
And:
 - verify_record(record) -> bool

Usage:
 - The shim maps legacy positional args into the new entry dict and calls
   fraud.intervention_log.emit_intervention(entry).
 - It also exposes emit_intervention alias for callers using the new name.
"""
from __future__ import annotations
import json
from typing import Dict, Any

# import the canonical implementation
try:
    from fraud.intervention_log import emit_intervention as _emit_intervention
except Exception as e:
    raise ImportError("Could not import fraud.intervention_log: " + str(e))

def append_intervention(*args, **kwargs) -> Dict[str, Any]:
    """
    Backwards-compatible wrapper.

    Legacy signature (positional):
      append_intervention(artifact_id, model_version, input_dict, decision_summary, human_id, human_reason, output_dict)

    New signature:
      append_intervention(entry_dict)

    Behavior:
      - If called with one positional arg and it's a dict, treat as new-style.
      - If called with legacy 6/7 positional args, map to entry dict.
      - If called with keyword args, accept artifact_id, model_version, input, decision_summary, human_id, human_reason, output.
    """
    # case 1: new style single dict
    if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
        return _emit_intervention(args[0])

    # case 2: legacy signature positional parsing
    # Accept len 6 or 7 (output optional)
    if len(args) >= 6:
        artifact_id = args[0]
        model_version = args[1]
        input_obj = args[2]
        decision_summary = args[3]
        human_id = args[4]
        human_reason = args[5]
        output_obj = args[6] if len(args) > 6 else kwargs.get("output", None)
    else:
        # also allow kwargs style: artifact_id=..., model_version=..., input=..., etc.
        artifact_id = kwargs.get("artifact_id")
        model_version = kwargs.get("model_version")
        input_obj = kwargs.get("input")
        decision_summary = kwargs.get("decision_summary") or kwargs.get("status")
        human_id = kwargs.get("human_id")
        human_reason = kwargs.get("human_reason")
        output_obj = kwargs.get("output")

    entry = {
        "artifact_id": artifact_id,
        "model_version": model_version,
        "input": input_obj,
        "decision_summary": decision_summary,
        "human_id": human_id,
        "human_reason": human_reason
    }
    if output_obj is not None:
        entry["output"] = output_obj

    # merge any extra kwargs into metadata if present
    extras = {k: v for k, v in kwargs.items() if k not in ("artifact_id", "model_version", "input", "decision_summary", "human_id", "human_reason", "output")}
    if extras:
        entry.setdefault("metadata", {}).update({"shim_extras": extras})

    return _emit_intervention(entry)

# keep alias for new name
emit_intervention = append_intervention

def verify_record(record: Dict[str, Any]) -> bool:
    """
    Lightweight verification used by tests:
    - checks presence of required keys from Rev7 schema
    - verifies input_hash/output_hash/signature_hash exist (non-empty)
    Returns True if minimal checks pass, else False.
    """
    required = ["timestamp", "artifact_id", "model_version", "input_hash", "output_hash", "signature_hash"]
    for k in required:
        if k not in record:
            return False
        v = record[k]
        if v is None:
            return False
        if isinstance(v, str) and v.strip() == "":
            return False
    return True
