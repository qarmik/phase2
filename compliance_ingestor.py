# compliance_ingestor.py
# PURPOSE: Extract structured text blocks from regulatory PDFs.
# OUTPUT: compliance_ingest.json (sectioned content for audit parsing)

import fitz  # PyMuPDF
import json
from pathlib import Path
import re

INPUT_PDF = Path("input/sample_regulation.pdf")
OUT_JSON = Path("output/compliance_ingest.json")

def extract_sections(pdf_path=INPUT_PDF):
    """Extract text and section it using simple regex anchors."""
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return {}

    with fitz.open(pdf_path) as doc:
        text = "\n".join(page.get_text("text") for page in doc)

    # naïve pattern anchors (tune later for RBI/EU docs)
    patterns = {
    "scope": r"(?i)(?:scope|application|applicability|coverage)[:\-]?\s*(.*?)\n\s*(?:obligation|responsibilit|penalt|sanction|$)",
    "obligations": r"(?i)(?:obligations?|responsibilit(?:y|ies)|requirements)[:\-]?\s*(.*?)\n\s*(?:penalt|sanction|enforcement|$)",
    "penalties": r"(?i)(?:penalt(?:y|ies)|sanction|non-?compliance|enforcement)[:\-]?\s*(.*)",
}

    result = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, flags=re.IGNORECASE | re.DOTALL)
        result[key] = (m.group(1).strip() if m else "")

    return result

def save_json(data, out_path=OUT_JSON):
    out_path.parent.mkdir(exist_ok=True, parents=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Wrote structured compliance data → {out_path}")

if __name__ == "__main__":
    sections = extract_sections()
    if sections:
        save_json(sections)
