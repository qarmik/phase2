#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEYS="$ROOT/keys"
ARCHIVE="$KEYS/archive"
mkdir -p "$ARCHIVE"

OLD_PRIV="$KEYS/indusv.pem"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
OLD_ARCHIVE="$ARCHIVE/indusv_${TIMESTAMP}.pem.gpg"

if [ -f "$OLD_PRIV" ]; then
  echo "Archiving existing private key to $OLD_ARCHIVE (GPG symmetric)..."
  gpg -c --cipher-algo AES256 -o "$OLD_ARCHIVE" "$OLD_PRIV"
  chmod 600 "$OLD_PRIV" || true
  echo "Existing private key archived."
else
  echo "No existing private key at $OLD_PRIV"
fi

# Generate new RSA 4096 keypair (PEM) non-interactively
NEW_PRIV="$KEYS/indusv.pem"
NEW_PUB="$KEYS/indusv.pub.pem"

echo "Generating new RSA 4096 keypair..."
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out "$NEW_PRIV"
openssl pkey -in "$NEW_PRIV" -pubout -out "$NEW_PUB"

chmod 600 "$NEW_PRIV" || true

# compute fingerprint
FPR=$(openssl pkey -pubin -in "$NEW_PUB" -outform DER 2>/dev/null | openssl dgst -sha256 | awk '{print $2}')
echo "New public key fingerprint (DER-SHA256): $FPR"

# update keys/key_index.json (append new entry)
INDEX="$KEYS/key_index.json"
if [ ! -f "$INDEX" ]; then
  cat > "$INDEX" <<JSON
{"keys": []}
JSON
fi

# create a minimal JSON object and append
python3 - <<PY
import json,sys,datetime
p = "$INDEX"
with open(p,'r',encoding='utf-8') as f:
    j = json.load(f)
entry = {
  "key_id": "indusv_${TIMESTAMP}",
  "role": "signing",
  "status": "active",
  "pub_path": "keys/indusv.pub.pem",
  "private_archive_path": "keys/archive/indusv_${TIMESTAMP}.pem.gpg",
  "fingerprint_der_sha256": "$FPR",
  "created_at": datetime.datetime.utcnow().isoformat()+'Z',
  "notes": "Automated rotation: archive created and new key generated."
}
# mark old active keys archived
for k in j.get("keys",[]):
    if k.get("status") == "active":
        k["status"] = "archived"
j["keys"].append(entry)
with open(p,'w',encoding='utf-8') as f:
    json.dump(j,f,indent=2)
print("Updated", p)
PY

echo "Rotation complete. Review keys/key_index.json, then commit public files (do NOT commit private key)."
