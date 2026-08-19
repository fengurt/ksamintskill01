#!/usr/bin/env bash
# Resolve every configured provider key from 1Password and seal them into an
# ENCRYPTED store: secrets/keys.enc  (hybrid RSA-OAEP + AES-256-GCM).
# Nothing plaintext is written to disk. Run locally with `op` unlocked.
# Requires secrets/llmhub_public.pem (see gen-keypair.sh).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # gui/
REG="${HERE}/../registry.tsv"
PUB="${HERE}/secrets/llmhub_public.pem"
OUT="${HERE}/secrets/keys.enc"
[[ -f "$PUB" ]] || { echo "missing $PUB — run scripts/gen-keypair.sh first"; exit 1; }

# 1) resolve keys from 1Password into memory (supports AK|SK paired refs)
KEYS_JSON="$(python3 - "$REG" <<'PY'
import sys, json, subprocess
reg = sys.argv[1]; keys = {}
for line in open(reg, encoding="utf8"):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"): continue
    p = line.split("\t")
    if len(p) < 5: continue
    provider, ref = p[0], p[4]
    if not ref or ref == "EMPTY":
        print("  -", provider, "(EMPTY)", file=sys.stderr); continue
    try:
        vals = [subprocess.run(["op","read",r.strip()], capture_output=True, text=True, timeout=60, check=True).stdout.strip() for r in ref.split("|")]
        keys[provider] = ":".join(vals)
        print("  \u2713", provider, file=sys.stderr)
    except Exception:
        print("  \u2717", provider, "(failed)", file=sys.stderr)
print(json.dumps(keys))
PY
)"

# 2) encrypt to keys.enc with the public PEM (via lib/crypto.js)
cd "$HERE"
KEYS_JSON="$KEYS_JSON" PUB="$PUB" OUT="$OUT" node --input-type=module -e '
import { encryptToFile } from "./lib/crypto.js";
import { readFileSync } from "node:fs";
const obj = JSON.parse(process.env.KEYS_JSON || "{}");
await encryptToFile(obj, readFileSync(process.env.PUB, "utf8"), process.env.OUT);
console.log(`\n\u2713 sealed ${Object.keys(obj).length} keys -> ${process.env.OUT}`);
' 

echo "ship: secrets/keys.enc + secrets/llmhub_private.pem  (the PEM stays out of git/images)"
