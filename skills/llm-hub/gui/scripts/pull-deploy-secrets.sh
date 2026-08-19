#!/usr/bin/env bash
# Pull the deploy "access pair" from 1Password (item: "LLM Hub Deploy"):
#   • admin proxy key  -> deploy.env  (LLMHUB_ADMIN_KEY)
#   • private PEM       -> secrets/llmhub_private.pem  (decrypts keys.enc at runtime)
#   • public PEM        -> secrets/llmhub_public.pem   (used by encrypt-keys.sh)
# Run LOCALLY with `op` unlocked, then ship secrets/ + deploy.env to the server.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # gui/
SEC="${HERE}/secrets"; mkdir -p "$SEC"; chmod 700 "$SEC"

V="fyg24alzrp23y727yk5n6jt4cu"                 # Personal vault
I="ka3szv6zpubzxrz4e5zo4mavga"                 # item: LLM Hub Deploy
F_ADMIN="l74uvmrciahy6rgmw5zwj7ncci"
F_PRIV="vus5jd5mjgxmwi3ma5xg3dhkam"
F_PUB="zxfaljxw6hv3bbzpps5vaiopcq"

op read "op://$V/$I/$F_PRIV" > "$SEC/llmhub_private.pem"; chmod 600 "$SEC/llmhub_private.pem"
op read "op://$V/$I/$F_PUB"  > "$SEC/llmhub_public.pem";  chmod 644 "$SEC/llmhub_public.pem"
ADMIN="$(op read "op://$V/$I/$F_ADMIN")"

ENVF="${HERE}/deploy.env"
[[ -f "$ENVF" ]] || cp "${HERE}/deploy.env.example" "$ENVF"
if grep -q '^LLMHUB_ADMIN_KEY=' "$ENVF"; then
  # portable in-place replace (BSD + GNU sed)
  tmp="$(mktemp)"; sed "s|^LLMHUB_ADMIN_KEY=.*|LLMHUB_ADMIN_KEY=${ADMIN}|" "$ENVF" > "$tmp" && mv "$tmp" "$ENVF"
else
  printf '\nLLMHUB_ADMIN_KEY=%s\n' "$ADMIN" >> "$ENVF"
fi
chmod 600 "$ENVF"

echo "✓ pulled admin key -> deploy.env"
echo "✓ pulled private/public PEM -> secrets/"
echo "  next: scripts/encrypt-keys.sh  (seal provider keys -> keys.enc), then ship & docker compose up"
