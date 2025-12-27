#!/usr/bin/env python3
import argparse, json, hashlib
from pathlib import Path

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_norm(obj):
    s = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(s).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intervention-log", required=True)
    ap.add_argument("--incident-id", required=True)
    ap.add_argument("--intervention-id", required=True)
    ap.add_argument("--actors", required=True, help="JSON file declaring actors")
    ap.add_argument("--out", default="docs/incidents")
    args = ap.parse_args()

    actors = load_json(Path(args.actors))
    failure_modes = []

    seen = set()
    has_authority = False
    has_override = False

    for a in actors:
        key = (a.get("actor_type"), a.get("role_name"))
        if key in seen:
            failure_modes.append("duplicate_actor_role")
        seen.add(key)

        if a.get("decision_authority"):
            has_authority = True
        if a.get("override_power") in ("limited", "full"):
            has_override = True

        cps = a.get("control_points", [])
        if not cps or any(not isinstance(x, str) or not x for x in cps):
            failure_modes.append("invalid_control_points")

    if not has_authority:
        failure_modes.append("no_decision_authority_declared")
    if not has_override:
        failure_modes.append("no_override_power_declared")

    lattice = {
        "schema_version": "qv_rev7_1",
        "artifact_type": "responsibility_lattice",
        "incident_id": args.incident_id,
        "intervention_id": args.intervention_id,
        "actors": actors,
        "validation_outcome": "valid" if not failure_modes else "invalid",
        "failure_modes": failure_modes
    }

    lattice["lattice_hash_sha256"] = sha256_norm(lattice)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{args.intervention_id}_responsibility_lattice.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(lattice, f, indent=2)

    print(f"[OK] Responsibility lattice written: {outpath.name}")

if __name__ == "__main__":
    main()
