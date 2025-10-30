#!/usr/bin/env python3
"""
release_checklist.py
Release preflight checks + timestamped evidence bundle.

- Verifies presence of required artifacts (notified-body package, manifest, key reports).
- Computes sha256 of package and writes timestamp file.
- Assembles release bundle: release_bundle_<ts>.zip containing:
    - notified-body package
    - manifest.json
    - timestamp.txt (with package sha256 + ISO ts)
Usage:
  python fraud/release_checklist.py --package artifacts/reports/notified_body_package_20251029T004318Z.zip --out-dir artifacts/reports --emit
"""
from __future__ import annotations
import argparse, os, json, hashlib, datetime, zipfile, sys
from typing import List, Dict

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sanity_checks(package: str, manifest: str, required_prefixes: List[str]) -> Dict[str, bool]:
    out = {"package_exists": os.path.exists(package), "manifest_exists": os.path.exists(manifest)}
    # check that manifest references the package
    if out["manifest_exists"]:
        try:
            m = json.load(open(manifest, "r", encoding="utf-8"))
            pkgs = [p.get("package") for p in m.get("packages", []) if isinstance(p, dict)]
            out["manifest_references_package"] = os.path.basename(package) in pkgs
        except Exception:
            out["manifest_references_package"] = False
    else:
        out["manifest_references_package"] = False
    # check for additional evidence files
    found = []
    repdir = os.path.dirname(manifest)
    for f in os.listdir(repdir):
        for p in required_prefixes:
            if f.startswith(p):
                found.append(f)
    out["evidence_count"] = len(found)
    out["evidence_examples"] = found[:10]
    return out

def write_timestamp_and_bundle(package: str, manifest: str, out_dir: str) -> Dict[str, str]:
    """
    Ensure manifest file exists (if not, try to extract it from the package zip),
    then write a timestamp file and a release bundle ZIP containing:
      - the package
      - the manifest file (on-disk)
      - the timestamp file
    Returns dict with keys: timestamp_file, bundle, sha256, ts
    """
    # if manifest file missing, attempt to extract it from the package zip
    if not os.path.exists(manifest):
        try:
            with zipfile.ZipFile(package, "r") as zf:
                if "manifest.json" in zf.namelist():
                    # extract into the same directory as `manifest`
                    extract_dir = os.path.dirname(manifest) or "."
                    zf.extract("manifest.json", path=extract_dir)
                    extracted = os.path.join(extract_dir, "manifest.json")
                    # if manifest path differs, move/rename
                    if os.path.abspath(extracted) != os.path.abspath(manifest):
                        os.replace(extracted, manifest)
                else:
                    raise FileNotFoundError(f"'manifest.json' not found inside package: {package}")
        except Exception as e:
            raise RuntimeError(f"Failed to obtain manifest for bundling: {e}")

    # compute package sha256
    sha = file_sha256(package)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    timestamp_text = f"package:{os.path.basename(package)}\nsha256:{sha}\ngenerated_at:{ts}\n"
    ts_fname = os.path.join(out_dir, f"timestamp_{ts}.txt")
    with open(ts_fname, "w", encoding="utf-8") as fh:
        fh.write(timestamp_text)

    # create release bundle containing package, manifest, and timestamp file
    bundle_name = os.path.join(out_dir, f"release_bundle_{ts}.zip")
    with zipfile.ZipFile(bundle_name, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(package, arcname=os.path.basename(package))
        zf.write(manifest, arcname=os.path.basename(manifest))
        zf.write(ts_fname, arcname=os.path.basename(ts_fname))

    return {"timestamp_file": ts_fname, "bundle": bundle_name, "sha256": sha, "ts": ts}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", required=True, help="Path to notified-body package zip")
    p.add_argument("--manifest", default=os.path.join(os.path.dirname(__file__), "../artifacts/reports/manifest.json"), help="Manifest path")
    p.add_argument("--out-dir", default=os.path.join(os.path.dirname(__file__), "../artifacts/reports"), help="Output directory")
    p.add_argument("--emit", action="store_true")
    args = p.parse_args()

    checks = sanity_checks(args.package, args.manifest, ["compliance_report_", "risk_matrix_", "sla_dashboard_"])
    print("Sanity checks:", checks)
    if not checks["package_exists"]:
        print("ERROR: package file missing:", args.package); sys.exit(2)
    if not checks["manifest_exists"]:
        print("ERROR: manifest missing:", args.manifest); sys.exit(2)
    if not checks["manifest_references_package"]:
        print("ERROR: manifest does not reference package; aborting."); sys.exit(2)

    result = write_timestamp_and_bundle(args.package, args.manifest, args.out_dir)
    print("Timestamp file written to:", result["timestamp_file"])
    print("Release bundle written to:", result["bundle"])
    print("Package sha256:", result["sha256"])

if __name__ == "__main__":
    main()
