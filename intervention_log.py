#!/usr/bin/env python3
"""
Compatibility shim for legacy imports that expect a top-level
intervention_log module. Delegates to fraud.intervention_log.

Provides both legacy function signatures used by older tests:
 - append_intervention(artifact_id, model_version, input_dict, decision_summary, human_id, human_reason, output_dict)
 - append_intervention(entry_dict)  # new-style single-arg
And:
 - verify_record(record) -> bool

verify_record now performs integrity checks:
 - recomputes input_hash/output_hash from input/output if present
 - recomputes deterministic signature_hash (sha256 of artifact_id|model_version|input_hash|output_hash)
 - returns False on any mismatch (tamper detection)
"""
from __future__ import annotations
import json, hashlib
from typing import Dict, Any

# import the canonical implementation
try:
    from fraud.intervention_log import emit_intervention as _emit_intervention
except Exception as e:
    raise ImportError("Could not import fraud.intervention_log: " + str(e))

def _sha256_of_obj(obj: Any) -> str:
    j = json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False)
    return hashlib.sha256(j.encode('utf-8')).hexdigest()

def append_intervention(*args, **kwargs) -> Dict[str, Any]:
    """
    Backwards-compatible wrapper.

    Legacy signature (positional):
      append_intervention(artifact_id, model_version, input_dict, decision_summary, human_id, human_reason, output_dict)

    New signature:
      append_intervention(entry_dict)
    """
    # case 1: new style single dict
    if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
        return _emit_intervention(args[0])

    # case 2: legacy signature positional parsing
    if len(args) >= 6:
        artifact_id = args[0]
        model_version = args[1]
        input_obj = args[2]
        decision_summary = args[3]
        human_id = args[4]
        human_reason = args[5]
        output_obj = args[6] if len(args) > 6 else kwargs.get("output", None)
    else:
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

    extras = {k: v for k, v in kwargs.items() if k not in ("artifact_id", "model_version", "input", "decision_summary", "human_id", "human_reason", "output")}
    if extras:
        entry.setdefault("metadata", {}).update({"shim_extras": extras})

    return _emit_intervention(entry)

# alias for new name
emit_intervention = append_intervention

def verify_record(record: Dict[str, Any]) -> bool:
    """
    Perform tamper-detection and minimal schema checks.

    Steps:
    1. Ensure required keys exist.
    2. If 'input' present, recompute input_hash and compare to record['input_hash'] (if present).
    3. If 'output' present, recompute output_hash and compare to record['output_hash'] (if present).
    4. Recompute deterministic signature_hash = sha256(artifact_id|model_version|input_hash|output_hash)
       and compare to record['signature_hash'].
    Returns True if all checks pass, False otherwise.
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

    # recompute input/output hashes if possible and verify
    try:
        if "input" in record:
            recomputed_ih = _sha256_of_obj(record["input"])
            if record.get("input_hash") and recomputed_ih != record.get("input_hash"):
                return False
        if "output" in record:
            recomputed_oh = _sha256_of_obj(record["output"])
            if record.get("output_hash") and recomputed_oh != record.get("output_hash"):
                return False
    except Exception:
        # if JSON serialization fails, treat as tamper / invalid
        return False

    # recompute signature hash deterministically
    aid = str(record.get("artifact_id",""))
    mv = str(record.get("model_version",""))
    ih = str(record.get("input_hash",""))
    oh = str(record.get("output_hash",""))
    hid = str(record.get("human_id","") or "")
    hreason = str(record.get("human_reason","") or "")
    dsummary = str(record.get("decision_summary","") or "")
    sig_base = "|".join([aid, mv, ih, oh, hid, hreason, dsummary])
    expected_sig = hashlib.sha256(sig_base.encode("utf-8")).hexdigest()
    if expected_sig != record.get("signature_hash"):
        return False

    return True
