import json, os
from pathlib import Path
from fraud.timestamp_anchor import make_receipt, write_receipt, sha256_text

def test_make_receipt_and_write(tmp_path):
    # prepare a timestamp file
    rpt = tmp_path / "reports"
    rpt.mkdir()
    tsf = rpt / "timestamp_20250101T000000Z.txt"
    content = "package:example.zip\nsha256:deadbeef\ngenerated_at:20250101T000000Z\n"
    tsf.write_text(content, encoding="utf-8")
    receipt = make_receipt(str(tsf), "sim-test")
    assert receipt["provider"] == "sim-test"
    assert receipt["package"] == "example.zip"
    assert "receipt_id" in receipt and len(receipt["receipt_id"]) > 10
    out = write_receipt(receipt, str(rpt))
    assert os.path.exists(out)
    loaded = json.load(open(out, "r", encoding="utf-8"))
    assert loaded["signature"] == receipt["signature"]
    Path(out).unlink()
