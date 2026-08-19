#!/usr/bin/env bash
# Generate the RSA keypair used to encrypt the provider-key store.
#   secrets/llmhub_private.pem  -> keep LOCAL + on the server only (never git/image)
#   secrets/llmhub_public.pem   -> used by encrypt-keys.sh to seal keys.enc
# The private PEM is one half of the access pair (the other is the proxy API key).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # gui/
SEC="${HERE}/secrets"
mkdir -p "$SEC"; chmod 700 "$SEC"
PRIV="${SEC}/llmhub_private.pem"
PUB="${SEC}/llmhub_public.pem"

if [[ -f "$PRIV" && "${1:-}" != "--force" ]]; then
  echo "private key already exists: $PRIV  (pass --force to overwrite)"; exit 1
fi

# Optional passphrase: pass it as $1 (or set LLMHUB_PEM_PASSPHRASE) for an
# encrypted private key. Leave empty for an unencrypted PEM.
PASS="${LLMHUB_PEM_PASSPHRASE:-}"
if [[ -n "$PASS" ]]; then
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -aes-256-cbc -pass "pass:${PASS}" -out "$PRIV"
else
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out "$PRIV"
fi
chmod 600 "$PRIV"
openssl pkey -in "$PRIV" ${PASS:+-passin pass:${PASS}} -pubout -out "$PUB"
chmod 644 "$PUB"

echo "✓ wrote $PRIV (KEEP SECRET) and $PUB"
echo "  next: scripts/encrypt-keys.sh   then ship secrets/keys.enc + the private PEM to the server"
