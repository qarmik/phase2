#!/usr/bin/env python3
"""
tools/find_canonical_deep.py

Deeper canonical search for public_timestamp.ndjson entry_hashes.
Tries unicode normalization, utf-16 encodings, trimming, slash-normalization,
field-removals, separators, newline/no-newline, sort_keys, ensure_ascii.

Usage:
  python tools/find_canonical_deep.py
Outputs results to stdout. Recommended to redirect to logs/find_canonical_deep.txt
"""
from pathlib import Path
import json, hashlib, itertools, sys, copy, unicodedata

ROOT = Path(__file__).resolve().parents[1]
ND = ROOT / "logs" / "public_timestamp.ndjson"

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def normalize_strings(obj, form):
    if form is None:
        return obj
    def norm(v):
        if isinstance(v, str):
            return unicodedata.normalize(form, v)
        if isinstance(v, dict):
            return {k: norm(vv) for k, vv in v.items()}
        if isinstance(v, list):
            return [norm(x) for x in v]
        return v
    return norm(obj)

def trim_strings(obj):
    def trim(v):
        if isinstance(v, str):
            return v.strip()
        if isinstance(v, dict):
            return {k: trim(vv) for k, vv in v.items()}
        if isinstance(v, list):
            return [trim(x) for x in v]
        return v
    return trim(obj)

def slash_normalize(obj):
    def sn(v):
        if isinstance(v, str):
            return v.replace("\\", "/")
        if isinstance(v, dict):
            return {k: sn(vv) for k, vv in v.items()}
        if isinstance(v, list):
            return [sn(x) for x in v]
        return v
    return sn(obj)

def canonical_bytes(obj, sort_keys, ensure_ascii, separators_label, add_newline, encoding):
    # separators_label: 'default' or 'compact'
    if separators_label == 'compact':
        separators = (",", ":")
    else:
        separators = None
    # json.dumps uses default separators when separators is None
    j = json.dumps(obj, sort_keys=sort_keys, ensure_ascii=ensure_ascii, separators=separators)
    if add_newline:
        j = j + "\n"
    if encoding == "utf-8":
        return j.encode("utf-8")
    if encoding == "utf-16le":
        return j.encode("utf-16le")
    if encoding == "utf-16be":
        return j.encode("utf-16be")
    return j.encode("utf-8")

def variants():
    removals_list = [
        ["signature_b64"],
        ["signature_b64","signature_method"],
        ["signature_b64","entry_hash"],
        ["signature_b64","entry_hash","prev_entry_hash"],
        ["signature_b64","timestamp_utc"],
        ["signature_b64","bundle_path","qv_version","quantum_verification_hash"],
        [],  # try no removals too
    ]
    sort_keys_opts = [True, False]
    ensure_ascii_opts = [True, False]
    separators_opts = ['default', 'compact']
    newline_opts = [True, False]
    encoding_opts = ["utf-8", "utf-16le", "utf-16be"]
    normalize_opts = [None, "NFC", "NFD"]
    trim_opts = [False, True]
    slash_opts = [False, True]

    for removals in removals_list:
        for sort_keys in sort_keys_opts:
            for ensure_ascii in ensure_ascii_opts:
                for separators_label in separators_opts:
                    for add_newline in newline_opts:
                        for encoding in encoding_opts:
                            for norm in normalize_opts:
                                for trim in trim_opts:
                                    for slash in slash_opts:
                                        yield {
                                            "remove": removals,
                                            "sort_keys": sort_keys,
                                            "ensure_ascii": ensure_ascii,
                                            "separators": separators_label,
                                            "newline": add_newline,
                                            "encoding": encoding,
                                            "normalization": norm,
                                            "trim": trim,
                                            "slash_norm": slash
                                        }

def try_match(entry_obj, stored_hash, max_matches=3):
    matches = []
    tried = 0
    for v in variants():
        tried += 1
        # prepare candidate
        cand = copy.deepcopy(entry_obj)
        # normalization
        if v["normalization"]:
            cand = normalize_strings(cand, v["normalization"])
        # trimming
        if v["trim"]:
            cand = trim_strings(cand)
        # slash normalization
        if v["slash_norm"]:
            cand = slash_normalize(cand)
        # remove fields
        for key in v["remove"]:
            cand.pop(key, None)
        # compute bytes
        b = canonical_bytes(cand, v["sort_keys"], v["ensure_ascii"], v["separators"], v["newline"], v["encoding"])
        h = sha256_hex(b)
        if h == stored_hash:
            matches.append((v, h))
            if len(matches) >= max_matches:
                break
    return matches, tried

def main():
    if not ND.exists():
        print("ERROR: NDJSON file missing:", ND, file=sys.stderr)
        return 2
    lines = ND.read_text(encoding="utf-8").strip().splitlines()
    # default: examine last 20 (or fewer) entries
    start = max(0, len(lines) - 20)
    idxs = list(range(start, len(lines)))
    print("Examining entry indexes:", idxs)
    for i in idxs:
        try:
            e = json.loads(lines[i])
        except Exception as exc:
            print(f"Entry {i}: JSON parse error: {exc}")
            continue
        stored = e.get("entry_hash","")
        if not stored:
            print(f"Entry {i}: no stored entry_hash found.")
            continue
        print("\n--- Entry idx", i, "artifact_id:", e.get("artifact_id"))
        print(" stored entry_hash:", stored)
        # remove signature_b64 in a copy for matching (common)
        matches, tried = try_match(e, stored, max_matches=5)
        if not matches:
            print(" No matches found (tried", tried, "variants).")
        else:
            print(" Found match(es):")
            for v,h in matches:
                print("  MATCH -> computed:", h)
                print("    remove:", v["remove"])
                print("    sort_keys:", v["sort_keys"], "ensure_ascii:", v["ensure_ascii"],
                      "separators:", v["separators"], "newline:", v["newline"])
                print("    encoding:", v["encoding"], "normalization:", v["normalization"],
                      "trim:", v["trim"], "slash_norm:", v["slash_norm"])
            # stop after first entry match group to let you inspect
            return 0
    print("\nNo matches found for tested entries.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
