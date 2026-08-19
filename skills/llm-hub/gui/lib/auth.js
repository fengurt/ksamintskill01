// Proxy-key auth with roles. Clients call the gateway with a single bearer key.
// Roles: "admin" (manage keys + dashboard + gateway) and "user" (gateway only).
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { randomBytes, timingSafeEqual } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const APP_DIR = dirname(__dirname);
const DATA_DIR = process.env.DATA_DIR || join(APP_DIR, "data");
const KEYS_FILE = join(DATA_DIR, "keys.json");

let store = { keys: [] };

function genKey(role) {
  return (role === "admin" ? "sk-hub-admin-" : "sk-hub-") + randomBytes(24).toString("base64url");
}
async function persist() {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(KEYS_FILE, JSON.stringify(store, null, 2), { mode: 0o600 });
}

export async function initAuth() {
  if (existsSync(KEYS_FILE)) {
    try { store = JSON.parse(await readFile(KEYS_FILE, "utf8")); } catch { store = { keys: [] }; }
  }
  // Bootstrap an admin key. The env key is authoritative for the "admin-env"
  // slot: drop any stale entries under that id (e.g. a rotated key, or a dev
  // key accidentally shipped in data/keys.json) so rotation replaces rather
  // than duplicates, and weak/old keys never linger.
  const envAdmin = process.env.LLMHUB_ADMIN_KEY;
  if (envAdmin) {
    const canonical = store.keys.some((k) => k.id === "admin-env" && k.key === envAdmin);
    const stale = store.keys.some((k) => k.id === "admin-env" && k.key !== envAdmin);
    if (!canonical || stale) {
      store.keys = store.keys.filter((k) => k.id !== "admin-env");
      store.keys.push({ id: "admin-env", key: envAdmin, role: "admin", name: "admin (env)", created: Date.now() });
      await persist();
    }
  } else if (!store.keys.some((k) => k.role === "admin")) {
    const key = genKey("admin");
    store.keys.push({ id: "admin-" + randomBytes(4).toString("hex"), key, role: "admin", name: "admin (auto)", created: Date.now() });
    await persist();
    console.log("\n  ⚠  Generated admin key (save it, shown once):\n  " + key + "\n");
  }
  return store;
}

function eq(a, b) {
  const ba = Buffer.from(a), bb = Buffer.from(b);
  return ba.length === bb.length && timingSafeEqual(ba, bb);
}

export function bearer(req) {
  const h = req.headers["authorization"] || req.headers["x-api-key"] || "";
  return h.replace(/^Bearer\s+/i, "").trim();
}

export function verify(req) {
  const tok = bearer(req);
  if (!tok) return null;
  const k = store.keys.find((x) => eq(x.key, tok));
  if (!k) return null;
  k.lastUsed = Date.now();
  return { id: k.id, role: k.role, name: k.name };
}

export function requireRole(req, role) {
  const u = verify(req);
  if (!u) return { ok: false, code: 401, error: "missing or invalid API key" };
  if (role === "admin" && u.role !== "admin") return { ok: false, code: 403, error: "admin role required" };
  return { ok: true, user: u };
}

export function listKeys() {
  return store.keys.map((k) => ({
    id: k.id, role: k.role, name: k.name, created: k.created, lastUsed: k.lastUsed || null,
    masked: k.key.slice(0, 12) + "…" + k.key.slice(-4),
  }));
}
export async function createKey({ name, role }) {
  const key = genKey(role === "admin" ? "admin" : "user");
  const entry = { id: randomBytes(5).toString("hex"), key, role: role === "admin" ? "admin" : "user", name: name || "key", created: Date.now() };
  store.keys.push(entry);
  await persist();
  return { ...entry }; // returns full key once
}
export async function revokeKey(id) {
  const before = store.keys.length;
  store.keys = store.keys.filter((k) => k.id !== id);
  if (store.keys.length !== before) await persist();
  return store.keys.length !== before;
}
