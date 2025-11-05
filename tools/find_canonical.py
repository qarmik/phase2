#!/usr/bin/env python3
"""
tools/find_canonical.py

Try many likely canonicalization/form variants for NDJSON entries and report matches
Usage:
  python tools/find_canonical.py     # will examine last 20 entries by default
  python tools/find_canonical.py 0   # exam entry idx 0 only
"""
from pathlib import Path
import json, hashlib, itertools, sys, copy

ROOT = Path(__file__).resolve().parents[1]
ND = ROOT / "logs" / "public_timestamp.ndjson"

def sha256_hex(b: bytes): return hashlib.sha256(b).hexdigest()

def walk_remove_fields(obj, remove_list):
    o = dict(obj)
    for k in remove_list:
        o.pop(k, None)
    return o

def normalize_backslashes(obj):
    # replace backslash with slash in all string values recursively
    def norm(v):
        if isinstance(v, str):
            return v.replace("\\", "/")
        if isinstance(v, dict):
            return {kk: norm(vv) for kk,vv in v.items()}
        if isinstance(v, list):
            return [norm(x) for x in v]
        return v
    return norm(obj)

def canonical_bytes(obj, sort_keys, ensure_ascii, separators, add_newline):
    j = json.dumps(obj, sort_keys=sort_keys, ensure_ascii=ensure_ascii, separators=separators)
    if add_newline:
        return (j + "\n").encode("utf-8")
    else:
        return j.encode("utf-8")

def variants_for_entry(e):
    # baseline: remove signature_b64 by default (most likely)
    candidate_removals = [
        ["signature_b64"],
        ["signature_b64","signature_method"],
        ["signature_b64","signature_method","signer_pub_fingerprint_sha256"],
        ["signature_b64","timestamp_utc"],
        ["signature_b64","entry_hash"],
        ["signature_b64","entry_hash","prev_entry_hash"],
        ["signature_b64","bundle_path"],
        ["signature_b64","bundle_path","qv_version","quantum_verification_hash"],
        # broad
        ["signature_b64","signature_method","signer_pub_fingerprint_sha256","timestamp_utc","bundle_path","entry_hash"],
    ]

    sort_keys_opts = [True, False]
    ensure_ascii_opts = [True, False]
    separators_opts = [None, (",", ":")]  # None means default
    newline_opts = [True, False]
    normalize_paths_opts = [False, True]

    for remove_list in candidate_removals:
        for sort_keys, ensure_ascii, separators, add_newline, normalize_paths in itertools.product(
                sort_keys_opts, ensure_ascii_opts, separators_opts, newline_opts, normalize_paths_opts):
            yield {
                "remove": remove_list,
                "sort_keys": sort_keys,
                "ensure_ascii": ensure_ascii,
                "separators": separators,
                "newline": add_newline,
                "normalize_paths": normalize_paths
            }

def try_match(entry_index, entry_obj, stored_hash):
    results = []
    tried = 0
    for v in variants_for_entry(entry_obj):
        tried += 1
        candidate = dict(entry_obj)
        # optionally normalize backslashes in all string values
        if v["normalize_paths"]:
            candidate = normalize_backslashes(candidate)
        # remove fields
        candidate = walk_remove_fields(candidate, v["remove"])
        # compute canonical bytes
        sep = v["separators"] if v["separators"] is not None else (",", ": ")  # default spacing
        b = canonical_bytes(candidate, sort_keys=v["sort_keys"], ensure_ascii=v["ensure_ascii"], separators=sep, add_newline=v["newline"])
        ch = sha256_hex(b)
        if ch == stored_hash:
            results.append((v, ch))
            # return first match (but continue could be used to find multiple)
            # we'll collect and return all matches up to some reasonable limit
            if len(results) >= 5:
                break
    return results, tried

def main():
    if not ND.exists():
        print("NDJSON not found:", ND); return 2
    lines = ND.read_text(encoding="utf-8").strip().splitlines()
    if len(sys.argv) > 1:
        idxs = [int(sys.argv[1])]
    else:
        # default: last 20 entries or all if fewer
        idxs = list(range(max(0, len(lines)-20), len(lines)))
    print("Examining entries:", idxs)
    for i in idxs:
        e = json.loads(lines[i])
        stored = e.get("entry_hash","")
        print("\n--- Entry idx", i, "artifact_id:", e.get("artifact_id"))
        print(" stored entry_hash:", stored)
        matches, tried = try_match(i, e, stored)
        if not matches:
            print(" No matches found (tried", tried, "variants).")
        else:
            print(" Found matches (showing up to 5):")
            for m, ch in matches:
                print("  MATCH -> computed:", ch)
                print("    remove:", m["remove"])
                print("    sort_keys:", m["sort_keys"], "ensure_ascii:", m["ensure_ascii"], "separators:", ("compact" if m["separators"] else "default"), "newline:", m["newline"], "normalize_paths:", m["normalize_paths"])
    return 0

if __name__ == "__main__":
    main()
