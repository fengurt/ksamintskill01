// Provider-key resolution. Precedence:
//   1. env var  LLMHUB_KEY_<PROVIDER>   (PROVIDER uppercased, non-alnum -> _)
//   2. encrypted store  secrets/keys.enc  (decrypted with the local private PEM)
//   3. 1Password  op read <op_ref>      (local dev only; not on servers)
// op_ref may be a "|"-joined pair (e.g. AccessKey|SecretKey); resolved values are
// joined with ":" -> "AK:SK" (used by signed providers like liblib).
// Resolved keys are cached in memory; nothing plaintext is written to disk.
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { decryptSecrets } from "./crypto.js";

const execFileP = promisify(execFile);
const cache = new Map();

export function envVarName(provider) {
  return "LLMHUB_KEY_" + provider.toUpperCase().replace(/[^A-Z0-9]/g, "_");
}

let opAvailable = null;
async function hasOp() {
  if (opAvailable !== null) return opAvailable;
  try { await execFileP("op", ["--version"], { timeout: 5000 }); opAvailable = true; }
  catch { opAvailable = false; }
  return opAvailable;
}

async function opRead(ref) {
  // supports "refA|refB" -> "valA:valB"
  const parts = ref.split("|");
  const vals = [];
  for (const p of parts) {
    const { stdout } = await execFileP("op", ["read", p.trim()], { timeout: 60000 });
    vals.push(stdout.trim());
  }
  return vals.join(":");
}

export async function resolveKey(row) {
  if (cache.has(row.provider)) return cache.get(row.provider);

  // 1) env
  const ev = process.env[envVarName(row.provider)];
  if (ev) { const v = { key: ev, source: "env" }; cache.set(row.provider, v); return v; }

  // 2) encrypted store
  const enc = await decryptSecrets();
  if (enc[row.provider]) { const v = { key: enc[row.provider], source: "encrypted" }; cache.set(row.provider, v); return v; }

  // 3) 1Password (local)
  if (row.op_ref && row.op_ref !== "EMPTY" && (await hasOp())) {
    const key = await opRead(row.op_ref);
    if (key) { const v = { key, source: "1password" }; cache.set(row.provider, v); return v; }
  }

  if (!row.configured) throw new Error("EMPTY: no API key configured");
  throw new Error("no key: set " + envVarName(row.provider) + ", add to encrypted store, or unlock 1Password");
}

export function clearKeyCache() { cache.clear(); }
