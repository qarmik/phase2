# compliance_validator.py
# PURPOSE: Convert structured compliance data into an audit checklist (Markdown)
# INPUT : output/compliance_ingest.json
# OUTPUT: output/compliance_checklist.md

import json
from pathlib import Path

INGEST_PATH = Path("output/compliance_ingest.json")
OUT_PATH    = Path("output/compliance_checklist.md")

def load_ingest(path=INGEST_PATH):
    """Load structured compliance data from JSON."""
    if not path.exists():
        print(f"❌ Ingest file not found: {path}")
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def build_checklist(data):
    """Create a Markdown checklist table from parsed regulation sections."""
    lines = [
        "# Compliance Audit Checklist",
        "",
        "| Section | Obligation | Evidence Available? | Notes |",
        "|----------|-------------|--------------------|--------|",
    ]
    for key, text in data.items():
        if not text:
            continue
        lines.append(f"| **{key.capitalize()}** | {text[:80]}... | [ ] Yes / [ ] No | |")
    return "\n".join(lines)

def save_md(content, out_path=OUT_PATH):
    out_path.write_text(content, encoding="utf-8")
    print(f"✅ Wrote audit checklist → {out_path}")

if __name__ == "__main__":
    data = load_ingest()
    if data:
        md = build_checklist(data)
        save_md(md)
