// OpenAI-compatible gateway: one proxy key -> many providers.
// Route by model name: "provider:model" or "provider/model" (provider = first segment
// if it matches the registry). Bare model -> LLMHUB_DEFAULT_PROVIDER.
import { Readable } from "node:stream";
import { resolveKey } from "./keys.js";

export function parseModel(model, rows) {
  if (!model) throw httpErr(400, "missing 'model'");
  let provider, rest;
  const sep = model.includes(":") ? ":" : model.includes("/") ? "/" : null;
  if (sep) {
    const i = model.indexOf(sep);
    const head = model.slice(0, i);
    if (rows.some((r) => r.provider === head)) { provider = head; rest = model.slice(i + 1); }
  }
  if (!provider) {
    provider = process.env.LLMHUB_DEFAULT_PROVIDER;
    rest = model;
    if (!provider) throw httpErr(400, `model must be 'provider:model' (e.g. 'deepseek:deepseek-chat'). Known providers: ${rows.filter(r=>r.configured).map(r=>r.provider).join(", ")}`);
  }
  const row = rows.find((r) => r.provider === provider);
  if (!row) throw httpErr(404, `unknown provider '${provider}'`);
  if (!rest || rest === provider) rest = row.default_model;
  return { row, model: rest };
}

function httpErr(code, message) { const e = new Error(message); e.status = code; return e; }
function sendJSON(res, code, obj) { res.writeHead(code, { "content-type": "application/json", "cache-control": "no-store" }); res.end(JSON.stringify(obj)); }

// ---------- chat completions ----------
export async function handleChat(res, body, rows) {
  let route;
  try { route = parseModel(body.model, rows); }
  catch (e) { return sendJSON(res, e.status || 400, { error: { message: e.message, type: "invalid_request_error" } }); }
  const { row } = route;
  const realModel = route.model;

  if (row.protocol !== "openai" && row.protocol !== "anthropic")
    return sendJSON(res, 400, { error: { message: `provider '${row.provider}' (${row.protocol}) is not chat-routable through this gateway`, type: "invalid_request_error" } });

  let key;
  try { key = (await resolveKey(row)).key; }
  catch (e) { return sendJSON(res, 502, { error: { message: `provider '${row.provider}': ${e.message}`, type: "provider_key_error" } }); }

  const base = row.base_url.replace(/\/$/, "");
  const wantStream = !!body.stream;

  if (row.protocol === "anthropic") return forwardAnthropic(res, { base, key, body, realModel, provider: row.provider, wantStream });
  return forwardOpenAI(res, { base, key, body, realModel, provider: row.provider, wantStream });
}

async function forwardOpenAI(res, { base, key, body, realModel, provider, wantStream }) {
  const upstreamBody = { ...body, model: realModel };
  let up;
  try {
    up = await fetch(`${base}/chat/completions`, {
      method: "POST",
      headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
      body: JSON.stringify(upstreamBody),
    });
  } catch (e) { return sendJSON(res, 502, { error: { message: `upstream ${provider}: ${e.cause?.code || e.message}`, type: "upstream_error" } }); }

  if (wantStream && up.ok && up.body) {
    res.writeHead(up.status, { "content-type": up.headers.get("content-type") || "text/event-stream", "cache-control": "no-store", connection: "keep-alive" });
    Readable.fromWeb(up.body).pipe(res);
    return;
  }
  const text = await up.text();
  res.writeHead(up.status, { "content-type": up.headers.get("content-type") || "application/json", "cache-control": "no-store" });
  res.end(text);
}

// OpenAI <-> Anthropic translation (non-streaming upstream; can emit SSE-shaped output)
async function forwardAnthropic(res, { base, key, body, realModel, provider, wantStream }) {
  const sys = (body.messages || []).filter((m) => m.role === "system").map((m) => m.content).join("\n");
  const msgs = (body.messages || []).filter((m) => m.role !== "system").map((m) => ({ role: m.role === "assistant" ? "assistant" : "user", content: typeof m.content === "string" ? m.content : m.content }));
  const aReq = { model: realModel, max_tokens: body.max_tokens || 1024, messages: msgs };
  if (sys) aReq.system = sys;
  if (body.temperature != null) aReq.temperature = body.temperature;

  let up, json;
  try {
    up = await fetch(`${base}/v1/messages`, {
      method: "POST",
      headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify(aReq),
    });
    json = await up.json();
  } catch (e) { return sendJSON(res, 502, { error: { message: `upstream ${provider}: ${e.cause?.code || e.message}`, type: "upstream_error" } }); }

  if (!up.ok) return sendJSON(res, up.status, { error: json.error || json });

  const content = (json.content || []).filter((c) => c.type === "text").map((c) => c.text).join("");
  const finish = json.stop_reason === "max_tokens" ? "length" : "stop";
  const usage = { prompt_tokens: json.usage?.input_tokens || 0, completion_tokens: json.usage?.output_tokens || 0, total_tokens: (json.usage?.input_tokens || 0) + (json.usage?.output_tokens || 0) };
  const id = "chatcmpl-" + (json.id || Date.now());

  if (wantStream) {
    res.writeHead(200, { "content-type": "text/event-stream", "cache-control": "no-store", connection: "keep-alive" });
    const base0 = { id, object: "chat.completion.chunk", created: Math.floor(Date.now() / 1000), model: realModel };
    res.write(`data: ${JSON.stringify({ ...base0, choices: [{ index: 0, delta: { role: "assistant" }, finish_reason: null }] })}\n\n`);
    res.write(`data: ${JSON.stringify({ ...base0, choices: [{ index: 0, delta: { content }, finish_reason: null }] })}\n\n`);
    res.write(`data: ${JSON.stringify({ ...base0, choices: [{ index: 0, delta: {}, finish_reason: finish }] })}\n\n`);
    res.write("data: [DONE]\n\n");
    return res.end();
  }
  sendJSON(res, 200, { id, object: "chat.completion", created: Math.floor(Date.now() / 1000), model: realModel, choices: [{ index: 0, message: { role: "assistant", content }, finish_reason: finish }], usage });
}

// ---------- models ----------
let modelsCache = { ts: 0, data: null };
export async function handleModels(res, rows) {
  if (modelsCache.data && Date.now() - modelsCache.ts < 5 * 60 * 1000) return sendJSON(res, 200, modelsCache.data);
  const configured = rows.filter((r) => r.configured && (r.protocol === "openai" || r.protocol === "anthropic"));
  const lists = await Promise.all(configured.map((r) => fetchProviderModels(r)));
  const data = [];
  configured.forEach((r, i) => {
    const ids = lists[i];
    if (ids && ids.length) for (const id of ids) data.push({ id: `${r.provider}:${id}`, object: "model", owned_by: r.provider });
    else if (r.default_model && r.default_model !== "-") data.push({ id: `${r.provider}:${r.default_model}`, object: "model", owned_by: r.provider });
  });
  const payload = { object: "list", data };
  modelsCache = { ts: Date.now(), data: payload };
  sendJSON(res, 200, payload);
}

async function fetchProviderModels(row) {
  try {
    const { key } = await resolveKey(row);
    const base = row.base_url.replace(/\/$/, "");
    const isA = row.protocol === "anthropic";
    const url = `${base}/${isA ? "v1/" : ""}models`;
    const headers = isA ? { "x-api-key": key, "anthropic-version": "2023-06-01" } : { authorization: `Bearer ${key}` };
    const ctrl = new AbortController(); const t = setTimeout(() => ctrl.abort(), 8000);
    const r = await fetch(url, { headers, signal: ctrl.signal }); clearTimeout(t);
    if (!r.ok) return null;
    const j = await r.json();
    const arr = Array.isArray(j) ? j : (j.data || j.models || []);
    return arr.map((m) => m.id || m.name).filter(Boolean);
  } catch { return null; }
}

export function clearModelsCache() { modelsCache = { ts: 0, data: null }; }
