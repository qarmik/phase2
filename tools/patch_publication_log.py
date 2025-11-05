#!/usr/bin/env python3
# safe patcher: replace sign_with_openssl and verify_with_openssl with robust file-based versions
import re
from pathlib import Path
p = Path("tools/publication_log.py")
bak = p.with_suffix(".py.bak")
if not p.exists():
    print("ERROR: tools/publication_log.py not found")
    raise SystemExit(1)
# create backup
p.copy = p.read_text(encoding="utf-8")
bak.write_text(p.copy, encoding="utf-8")
s = p.copy

# patterns to locate functions by def line; will replace whole def until next def at column 0 or EOF
def replace_func(text, func_name, new_body):
    # regex: match "def func_name(...):" up to next "\ndef " at start of line or end
    pat = re.compile(r"(def\s+" + re.escape(func_name) + r"\s*\(.*?\)\s*:\n)(?:[ \t].*?\n)*(?=(\ndef\s+)|\Z)", re.S)
    m = pat.search(text)
    if not m:
        return None
    start, end = m.span()
    # find insertion point: start of match (m.start()) then replace with header + new_body indented
    header = m.group(1)
    # ensure new body lines are indented
    new_lines = []
    for line in new_body.splitlines():
        if line.strip()=="":
            new_lines.append("\n")
        else:
            new_lines.append("    " + line.rstrip() + "\n")
    new_text = header + "".join(new_lines)
    new = text[:start] + new_text + text[end:]
    return new

new_sign = r'''
# File-based signing for cross-platform robustness
def sign_with_openssl(entry_bytes: bytes, signer_name: str):
    priv = KEYS / f"{signer_name}.pem"
    if not priv.exists():
        raise FileNotFoundError(f"Private key not found at {priv}. Generate with openssl or run keygen steps.")
    import tempfile
    from pathlib import Path as _P
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(entry_bytes)
        tf.flush()
        entry_path = tf.name
    sig_path = entry_path + ".sig"
    p = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(priv), "-out", str(sig_path), str(entry_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        try:
            _P(sig_path).unlink()
        except Exception:
            pass
        raise RuntimeError(f"OpenSSL sign failed: {p.stderr.decode().strip()}")
    sig_bytes = _P(sig_path).read_bytes()
    try:
        _P(sig_path).unlink()
        _P(entry_path).unlink()
    except Exception:
        pass
    return base64.b64encode(sig_bytes).decode()
'''

new_verify = r'''
# File-based verification for cross-platform robustness
def verify_with_openssl(entry_bytes: bytes, signature_b64: str, signer_name: str) -> bool:
    pub = KEYS / f"{signer_name}.pub.pem"
    if not pub.exists():
        raise FileNotFoundError(f"Public key not found at {pub}.")
    sig = base64.b64decode(signature_b64)
    import tempfile
    from pathlib import Path as _P
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(entry_bytes)
        tf.flush()
        entry_path = tf.name
    with tempfile.NamedTemporaryFile(delete=False) as ts:
        ts.write(sig)
        ts.flush()
        sig_path = ts.name
    try:
        p = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", str(pub), "-signature", sig_path, entry_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        ok = (p.returncode == 0)
    finally:
        try:
            _P(sig_path).unlink()
            _P(entry_path).unlink()
        except Exception:
            pass
    return ok
'''

# apply replacements
s2 = replace_func(s, "sign_with_openssl", new_sign)
if s2 is None:
    print("Failed: sign_with_openssl not found in file; aborting (backup preserved).")
    raise SystemExit(1)
s3 = replace_func(s2, "verify_with_openssl", new_verify)
if s3 is None:
    print("Failed: verify_with_openssl not found in file; aborting (backup preserved).")
    raise SystemExit(1)

p.write_text(s3, encoding="utf-8")
print("Patched tools/publication_log.py; backup saved as", bak.name)
