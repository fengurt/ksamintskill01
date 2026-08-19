// LLM Hub — gateway + control panel.
//  • Gateway:  POST /v1/chat/completions, GET /v1/models  (any valid proxy key)
//  • Admin API: /api/*  (admin role)  — dashboard state, tests, key management
//  • Static control panel served from public/
import { createServer } from "node:http";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { createHmac, randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";
import { loadRegistry, publicRow } from "./lib/registry.js";
import { resolveKey } from "./lib/keys.js";
import { initAuth, requireRole, verify, listKeys, createKey, revokeKey } from "./lib/auth.js";
import { handleChat, handleModels } from "./lib/gateway.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = process.env.DATA_DIR || join(__dirname, "data");
const STATE_FILE = join(DATA_DIR, "state.json");
const PUBLIC = join(__dirname, "public");
const PORT = Number(process.env.PORT || 7878);

// ---------- state ----------
async function loadState() {
  if (!existsSync(STATE_FILE)) return { overrides: {}, results: {} };
  try { return JSON.parse(await readFile(STATE_FILE, "utf8")); } catch { return { overrides: {}, results: {} }; }
}
async function saveState(s) { await mkdir(DATA_DIR, { recursive: true }); await writeFile(STATE_FILE, JSON.stringify(s, null, 2)); }

// ---------- connectivity test ----------
async function testProvider(row, model, mode = "check") {
  const useModel = model || row.default_model;
  const out = { provider: row.provider, ts: Date.now(), model: useModel, base_url: row.base_url, mode };
  let key;
  try { key = (await resolveKey(row)).key; }
  catch (e) { return { ...out, ok: false, status: 0, error: e.message.startsWith("EMPTY") ? "EMPTY: no API key configured" : e.message }; }

  if (row.protocol === "liblib") return testLiblib(row, key, out);

  const base = row.base_url.replace(/\/$/, "");
  const isA = row.protocol === "anthropic";
  const headers = isA ? { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" }
                      : { authorization: `Bearer ${key}`, "content-type": "application/json" };
  let url, init, timeoutMs;
  if (mode === "check") {
    url = `${base}/${isA ? "v1/" : ""}models`; init = { method: "GET", headers }; timeoutMs = 18000;
  } else {
    if (!useModel || useModel === "-") return { ...out, ok: false, status: 0, error: "no model set — choose one and retry" };
    url = isA ? `${base}/v1/messages` : `${base}/chat/completions`;
    init = { method: "POST", headers, body: JSON.stringify({ model: useModel, max_tokens: 32, messages: [{ role: "user", content: "reply with one word: pong" }] }) };
    timeoutMs = 30000;
  }
  const ctrl = new AbortController(); const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const t0 = performance.now();
  try {
    const res = await fetch(url, { ...init, signal: ctrl.signal });
    const latency = Math.round(performance.now() - t0);
    const raw = await res.text();
    let sample = "", count, json;
    try {
      json = JSON.parse(raw);
      if (mode === "check") { const arr = Array.isArray(json) ? json : (json.data || json.models || []); count = Array.isArray(arr) ? arr.length : undefined; sample = count != null ? `key valid · ${count} models available` : "key valid"; }
      else sample = isA ? (json.content?.[0]?.text ?? "") : (json.choices?.[0]?.message?.content ?? "");
      if (!res.ok && json.error) sample = json.error.message || JSON.stringify(json.error);
    } catch { sample = raw.slice(0, 200); }
    return { ...out, ok: res.ok, status: res.status, latencyMs: latency, models: count, sample: (sample || "").trim().slice(0, 240), error: res.ok ? null : (sample || `HTTP ${res.status}`) };
  } catch (e) {
    const latency = Math.round(performance.now() - t0);
    const reason = e.name === "AbortError" ? `timeout (${timeoutMs / 1000}s) — endpoint unreachable (proxy/down?)` : (e.cause?.code || e.message);
    return { ...out, ok: false, status: 0, latencyMs: latency, error: reason };
  } finally { clearTimeout(timer); }
}

// liblib (image-gen) uses AccessKey+SecretKey HMAC-SHA1 request signing, not a
// bearer token. There's no /models endpoint, so we "check" by signing a query
// call: a valid signature returns a business error (model.notExist) instead of
// an auth/signature error. key format = "AK:SK".
function liblibSign(uri, sk) {
  const ts = Date.now().toString();
  const nonce = randomBytes(8).toString("hex");
  const sig = createHmac("sha1", sk).update(`${uri}&${ts}&${nonce}`).digest("base64")
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return `${uri}?AccessKey=__AK__&Signature=${sig}&Timestamp=${ts}&SignatureNonce=${nonce}`;
}
async function testLiblib(row, key, out) {
  const [ak, sk] = String(key).split(":");
  if (!ak || !sk) return { ...out, ok: false, status: 0, error: "liblib key must be 'AccessKey:SecretKey'" };
  const base = row.base_url.replace(/\/$/, "");
  const uri = "/api/model/version/get";
  const url = base + liblibSign(uri, sk).replace("__AK__", encodeURIComponent(ak));
  const ctrl = new AbortController(); const timer = setTimeout(() => ctrl.abort(), 15000);
  const t0 = performance.now();
  try {
    const res = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ versionUuid: "00000000000000000000000000000000" }), signal: ctrl.signal });
    const latency = Math.round(performance.now() - t0);
    const raw = await res.text();
    let code, msg = raw.slice(0, 160);
    try { const j = JSON.parse(raw); code = j.code; msg = j.msg || msg; } catch {}
    const authBad = /sign|签名|access\s*key|accesskey|鉴权|授权|unauthor|forbidden|invalid\s*key/i.test(msg);
    const ok = res.ok && !authBad; // any business reply with a good signature means the key pair works
    return { ...out, ok, status: res.status, latencyMs: latency, sample: ok ? `signature valid · ${msg}` : msg, error: ok ? null : (msg || `HTTP ${res.status}`) };
  } catch (e) {
    const latency = Math.round(performance.now() - t0);
    const reason = e.name === "AbortError" ? "timeout (15s) — endpoint unreachable" : (e.cause?.code || e.message);
    return { ...out, ok: false, status: 0, latencyMs: latency, error: reason };
  } finally { clearTimeout(timer); }
}

// ---------- http helpers ----------
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml" };
function send(res, code, data, type = "application/json") {
  const buf = typeof data === "string" || Buffer.isBuffer(data) ? data : JSON.stringify(data);
  res.writeHead(code, { "content-type": type, "cache-control": "no-store" }); res.end(buf);
}
function readBody(req) { return new Promise((resolve) => { let b = ""; req.on("data", (c) => (b += c)); req.on("end", () => { try { resolve(b ? JSON.parse(b) : {}); } catch { resolve({}); } }); }); }
function denied(res, g) { return send(res, g.code, { error: { message: g.error, type: "auth_error" } }); }

// ---------- routes ----------
const server = createServer(async (req, res) => {
  const u = new URL(req.url, `http://localhost:${PORT}`);
  const path = u.pathname;
  try {
    // health (public)
    if (path === "/api/health") return send(res, 200, { ok: true, ts: Date.now() });

    // ---- GATEWAY (any valid key) ----
    if (path === "/v1/chat/completions" && req.method === "POST") {
      const g = requireRole(req, "user"); if (!g.ok) return denied(res, g);
      return handleChat(res, await readBody(req), await loadRegistry());
    }
    if (path === "/v1/models" && req.method === "GET") {
      const g = requireRole(req, "user"); if (!g.ok) return denied(res, g);
      return handleModels(res, await loadRegistry());
    }

    // ---- ADMIN API ----
    if (path === "/api/me") { const us = verify(req); return send(res, 200, { user: us }); }

    if (path.startsWith("/api/")) {
      const g = requireRole(req, "admin"); if (!g.ok) return denied(res, g);

      if (path === "/api/state") {
        const [rows, state] = await Promise.all([loadRegistry(), loadState()]);
        const providers = rows.map((r) => ({ ...publicRow(r), model: state.overrides[r.provider] || r.default_model, result: state.results[r.provider] || null }));
        return send(res, 200, { providers, generatedAt: Date.now() });
      }
      if (path === "/api/test" && req.method === "POST") {
        const { provider, model, mode } = await readBody(req);
        const rows = await loadRegistry(); const row = rows.find((r) => r.provider === provider);
        if (!row) return send(res, 404, { error: "unknown provider" });
        const result = await testProvider(row, model, mode);
        const state = await loadState(); state.results[provider] = result; if (model) state.overrides[provider] = model; await saveState(state);
        return send(res, 200, result);
      }
      if (path === "/api/config" && req.method === "POST") {
        const { provider, model } = await readBody(req); const state = await loadState();
        if (model !== undefined) state.overrides[provider] = model; await saveState(state);
        return send(res, 200, { ok: true });
      }
      if (path === "/api/admin/keys" && req.method === "GET") return send(res, 200, { keys: listKeys() });
      if (path === "/api/admin/keys" && req.method === "POST") { const { name, role } = await readBody(req); return send(res, 200, await createKey({ name, role })); }
      if (path === "/api/admin/keys" && req.method === "DELETE") { const ok = await revokeKey(u.searchParams.get("id")); return send(res, ok ? 200 : 404, { ok }); }
      return send(res, 404, { error: "not found" });
    }

    // ---- static ----
    let p = path === "/" ? "/index.html" : path;
    const file = join(PUBLIC, p);
    if (!file.startsWith(PUBLIC) || !existsSync(file)) return send(res, 404, "not found", "text/plain");
    return send(res, 200, await readFile(file), MIME[extname(file)] || "application/octet-stream");
  } catch (e) {
    return send(res, 500, { error: String(e.message || e) });
  }
});

await initAuth();
server.listen(PORT, () => {
  console.log(`\n  LLM Hub  →  http://localhost:${PORT}`);
  console.log(`  gateway  →  POST /v1/chat/completions   GET /v1/models`);
  console.log(`  admin UI →  /  (login with an admin key)\n`);
});
