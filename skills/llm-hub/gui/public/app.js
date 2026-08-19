const $ = (s, r = document) => r.querySelector(s);
let ADMIN_KEY = localStorage.getItem("llmhub_admin_key") || "";
function authHeaders(extra) { const h = extra || {}; if (ADMIN_KEY) h.Authorization = "Bearer " + ADMIN_KEY; return h; }
async function api(path, body, method) {
  const opts = { method: method || (body ? "POST" : "GET"), headers: authHeaders(body ? { "content-type": "application/json" } : {}) };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  if (res.status === 401 || res.status === 403) { showLogin(res.status === 403 ? "That key is not an admin key." : ""); throw new Error("auth"); }
  return res.json();
}

let STATE = { providers: [] };
const byProvider = (p) => STATE.providers.find((x) => x.provider === p);
const testing = new Map(); // provider -> startTime(ms)
let ticker = null;

function ago(ts) {
  if (!ts) return "never";
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return s + "s ago";
  if (s < 3600) return Math.floor(s / 60) + "m ago";
  if (s < 86400) return Math.floor(s / 3600) + "h ago";
  return Math.floor(s / 86400) + "d ago";
}
const ledClass = (p, r) => (testing.has(p) ? "test" : !r ? "" : r.ok ? "ok" : "fail");
const isChat = (proto) => proto === "openai" || proto === "anthropic";
const GROUPS = ["official", "hub", "image"];

function statusLabel(r) {
  if (!r) return "";
  if (r.ok) return (r.mode === "check" ? "KEY OK" : "ONLINE") + " · " + r.status;
  if (r.status) return "HTTP " + r.status;
  return "FAILED";
}

function cardHTML(p) {
  const r = p.result;
  const empty = !p.configured;
  const isTesting = testing.has(p.provider);
  const stateColor = isTesting ? "var(--amber)" : !r ? "transparent" : r.ok ? "var(--signal)" : "var(--danger)";

  let resultHTML;
  if (isTesting) {
    resultHTML = `<span class="spin"></span><span class="testing-txt">checking… <b data-elapsed="${p.provider}">0.0s</b></span>`;
  } else if (empty) {
    resultHTML = `<span class="placeholder">no key · add to 1Password</span>`;
  } else if (!r) {
    resultHTML = `<span class="placeholder">untested</span><button class="btn primary small c-act" data-test="${p.provider}" data-mode="check">Check key</button>`;
  } else {
    const sub = r.ok && r.mode === "check" && r.models != null ? `${r.models} models` : (r.ok ? "" : (r.error || "").slice(0, 28));
    resultHTML = `
      <div class="lat">${r.latencyMs ?? "—"}<span class="u">ms</span></div>
      <div class="r-meta">
        <span class="r-status ${r.ok ? "ok" : "fail"}">${statusLabel(r)}</span>
        <span class="r-when">${sub ? sub + " · " : ""}${ago(r.ts)}</span>
      </div>
      <button class="btn ghost small c-act" data-test="${p.provider}" data-mode="check" title="Re-check key availability">↻ Check</button>`;
  }
  return `<article class="card ${empty ? "empty" : ""} ${isTesting ? "busy" : ""}" style="--state:${stateColor}" data-open="${p.provider}">
    <div class="c-top">
      <span class="led ${ledClass(p.provider, r)}" data-led="${p.provider}"></span>
      <span class="c-name">${p.provider}</span>
      <span class="c-proto">${p.protocol}</span>
    </div>
    <div class="c-base">${p.base_url}</div>
    <div class="c-meta">
      <span class="pill model">${p.model && p.model !== "-" ? p.model : "no model"}</span>
      <span class="pill ${empty ? "nokey" : "key"}">${empty ? "EMPTY" : "key ✓"}</span>
    </div>
    <div class="c-result">${resultHTML}</div>
  </article>`;
}

function render() {
  const groups = { official: [], hub: [], image: [] };
  for (const p of STATE.providers) (groups[p.group] || (groups[p.group] = [])).push(p);
  for (const g of GROUPS) {
    const grid = $("#grid-" + g);
    if (!grid) continue;
    grid.innerHTML = (groups[g] || []).map((p) => cardHTML(p)).join("");
    [...grid.children].forEach((c, i) => (c.style.animationDelay = Math.min(i * 28, 400) + "ms"));
    $("#count-" + g).textContent = (groups[g] || []).length;
  }
  const ps = STATE.providers;
  const online = ps.filter((p) => p.result?.ok).length;
  const lats = ps.filter((p) => p.result?.ok && p.result.latencyMs).map((p) => p.result.latencyMs);
  const avg = lats.length ? Math.round(lats.reduce((a, b) => a + b, 0) / lats.length) : "—";
  $("#stat-online").textContent = online;
  $("#stat-config").textContent = ps.filter((p) => p.configured).length;
  $("#stat-empty").textContent = ps.filter((p) => !p.configured).length;
  $("#stat-latency").textContent = avg;
}

// ---- live elapsed ticker ----
function startTicker() {
  if (ticker) return;
  ticker = setInterval(() => {
    if (!testing.size) { clearInterval(ticker); ticker = null; return; }
    const now = performance.now();
    for (const [p, t0] of testing) {
      const el = document.querySelector(`[data-elapsed="${p}"]`);
      if (el) el.textContent = ((now - t0) / 1000).toFixed(1) + "s";
      if ($("#drawer").classList.contains("open") && $("#d-name").textContent === p) {
        const de = $("#d-elapsed"); if (de) de.textContent = ((now - t0) / 1000).toFixed(1) + "s";
      }
    }
  }, 100);
}

// ---- testing ----
async function runTest(provider, mode = "check", model) {
  if (testing.has(provider)) return;
  testing.set(provider, performance.now());
  startTicker();
  render();
  if (drawerFor() === provider) setDrawerBusy(true);
  const p = byProvider(provider);
  let res;
  try {
    res = await api("/api/test", { provider, mode, model: model ?? p?.model });
  } catch (e) {
    res = { provider, ok: false, status: 0, error: "request failed: " + e.message, ts: Date.now(), mode };
  }
  testing.delete(provider);
  if (p) p.result = res;
  render();
  if (drawerFor() === provider) { setDrawerBusy(false); fillDrawerResult(res); }
  return res;
}

async function testAll() {
  const btn = $("#btn-testall");
  btn.disabled = true;
  const orig = btn.dataset.label || btn.textContent;
  btn.dataset.label = orig;
  const targets = STATE.providers.filter((p) => p.configured);
  let done = 0;
  for (const p of targets) {
    btn.textContent = `▷ ${++done}/${targets.length}`;
    await runTest(p.provider, "check");
  }
  btn.disabled = false;
  btn.textContent = orig;
  toast(`checked ${targets.length} providers`);
}

// ---- drawer ----
const drawerFor = () => ($("#drawer").classList.contains("open") ? $("#d-name").textContent : null);
function setDrawerBusy(b) {
  $("#d-check").disabled = b; $("#d-chat").disabled = b;
  $("#d-spin").hidden = !b;
  $("#d-elapsed").hidden = !b;
}
function curlFor(p, model, mode) {
  const base = p.base_url.replace(/\/$/, "");
  if (p.protocol === "liblib")
    return `# liblib signs every request: HMAC-SHA1(SecretKey, "uri&ts&nonce")\n# query: ?AccessKey=..&Signature=..&Timestamp=..&SignatureNonce=..\ncurl -X POST "${base}/api/generate/webui/text2img?AccessKey=$AK&Signature=$SIG&Timestamp=$TS&SignatureNonce=$NONCE" \\\n  -H "content-type: application/json" -d '{"templateUuid":"...","generateParams":{...}}'`;
  if (mode === "check")
    return p.protocol === "anthropic"
      ? `curl ${base}/v1/models -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01"`
      : `curl ${base}/models -H "Authorization: Bearer $KEY"`;
  if (p.protocol === "anthropic")
    return `curl ${base}/v1/messages \\\n  -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" \\\n  -H "content-type: application/json" \\\n  -d '{"model":"${model}","max_tokens":32,"messages":[{"role":"user","content":"pong"}]}'`;
  return `curl ${base}/chat/completions \\\n  -H "Authorization: Bearer $KEY" -H "content-type: application/json" \\\n  -d '{"model":"${model}","messages":[{"role":"user","content":"pong"}]}'`;
}
function refreshCurl() {
  const p = byProvider($("#d-name").textContent); if (!p) return;
  $("#d-curl").value = curlFor(p, $("#d-model").value || "MODEL", $("#d-curl").dataset.mode || "check");
}
function fillDrawerResult(r) {
  const box = $("#d-result");
  if (!r) { box.className = "d-result"; box.textContent = "no test yet — run a check"; $("#d-led").className = "dled"; return; }
  $("#d-led").className = "dled " + (r.ok ? "ok" : "fail");
  box.className = "d-result " + (r.ok ? "ok" : "fail");
  const head = r.ok
    ? `✓ ${r.mode === "check" ? "KEY VALID" : "ONLINE"} · ${r.status} · ${r.latencyMs}ms${r.models != null ? " · " + r.models + " models" : ""}`
    : `✕ ${r.status ? "HTTP " + r.status : "FAILED"} · ${r.latencyMs ?? "—"}ms`;
  box.innerHTML = `<span class="big">${head}</span>${escapeHTML(r.ok ? (r.sample || "(ok)") : (r.error || "unknown error"))}`;
}
function openDrawer(provider) {
  const p = byProvider(provider); if (!p) return;
  $("#d-name").textContent = p.provider;
  $("#d-chips").innerHTML = `<span class="pill">${p.group}</span><span class="pill">${p.protocol}</span><span class="pill ${p.configured ? "key" : "nokey"}">${p.configured ? "key ✓" : "EMPTY"}</span>`;
  $("#d-base").textContent = p.base_url;
  const chat = isChat(p.protocol);
  $("#d-model").value = p.model && p.model !== "-" ? p.model : "";
  $("#d-model").disabled = !p.configured || !chat;
  $("#d-check").disabled = !p.configured;
  $("#d-check").textContent = chat ? "✓ Check key" : "✓ Check signature";
  $("#d-chat").disabled = !p.configured || !chat;
  $("#d-chat").hidden = !chat;
  $("#d-curl").dataset.mode = "check";
  refreshCurl();
  setDrawerBusy(testing.has(provider));
  fillDrawerResult(testing.has(provider) ? null : p.result);
  $("#drawer").classList.add("open");
  $("#scrim").hidden = false;
}
function closeDrawer() { $("#drawer").classList.remove("open"); $("#scrim").hidden = true; }

// ---- helpers ----
function escapeHTML(s) { return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }
let toastT;
function toast(msg, err) {
  let el = $(".toast"); if (!el) { el = document.createElement("div"); el.className = "toast"; document.body.appendChild(el); }
  el.textContent = msg; el.className = "toast show" + (err ? " err" : "");
  clearTimeout(toastT); toastT = setTimeout(() => (el.className = "toast"), 2600);
}

// ---- events ----
document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-test]");
  if (t) { e.stopPropagation(); runTest(t.dataset.test, t.dataset.mode || "check"); return; }
  const card = e.target.closest("[data-open]");
  if (card) openDrawer(card.dataset.open);
});
$("#drawer-close").onclick = closeDrawer;
$("#scrim").onclick = closeDrawer;
$("#btn-refresh").onclick = load;
$("#btn-testall").onclick = testAll;
$("#d-model").addEventListener("input", refreshCurl);
$("#d-check").onclick = () => { $("#d-curl").dataset.mode = "check"; refreshCurl(); runTest($("#d-name").textContent, "check", $("#d-model").value.trim()); };
$("#d-chat").onclick = () => { $("#d-curl").dataset.mode = "chat"; refreshCurl(); runTest($("#d-name").textContent, "chat", $("#d-model").value.trim()); };
$("#d-copy").onclick = () => { navigator.clipboard.writeText($("#d-curl").value); toast("curl copied"); };
document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeDrawer(); closeKeys(); } });

function load() { return api("/api/state").then((s) => { STATE = s; render(); }); }

// ---- auth ----
function showLogin(msg) { $("#login").hidden = false; $("#login-err").textContent = msg || ""; $("#btn-logout").hidden = true; setTimeout(() => $("#login-key").focus(), 50); }
function hideLogin() { $("#login").hidden = true; }
async function doLogin() {
  const key = $("#login-key").value.trim();
  if (!key) return;
  ADMIN_KEY = key;
  try {
    const me = await fetch("/api/me", { headers: authHeaders() }).then((r) => r.json());
    if (me.user && me.user.role === "admin") {
      localStorage.setItem("llmhub_admin_key", key);
      hideLogin(); $("#btn-logout").hidden = false; await load();
    } else { $("#login-err").textContent = me.user ? "That key is not an admin key." : "Invalid key."; }
  } catch { $("#login-err").textContent = "Could not reach server."; }
}
function logout() { localStorage.removeItem("llmhub_admin_key"); ADMIN_KEY = ""; showLogin(); }

// ---- keys & gateway modal ----
function gatewaySnippet() {
  const o = location.origin;
  return `curl ${o}/v1/chat/completions \\\n  -H "Authorization: Bearer $LLMHUB_KEY" \\\n  -H "content-type: application/json" \\\n  -d '{"model":"deepseek:deepseek-chat",\n       "messages":[{"role":"user","content":"hello"}]}'`;
}
async function openKeys() {
  $("#gw-base").textContent = location.origin + "/v1";
  $("#gw-snippet").textContent = gatewaySnippet();
  $("#keys-modal").hidden = false; $("#keys-scrim").hidden = false;
  await renderKeys();
}
function closeKeys() { $("#keys-modal").hidden = true; $("#keys-scrim").hidden = true; $("#key-reveal").hidden = true; }
async function renderKeys() {
  const { keys } = await api("/api/admin/keys");
  $("#keys-list").innerHTML = keys.map((k) => `
    <div class="keyrow">
      <span class="kname">${escapeHTML(k.name)}</span>
      <span class="krole ${k.role}">${k.role}</span>
      <span class="kmask">${k.masked}</span>
      <button class="btn ghost small krevoke" data-revoke="${k.id}">Revoke</button>
    </div>`).join("") || `<div class="placeholder">no keys yet</div>`;
}
async function createKeyUI() {
  const name = $("#key-name").value.trim() || "key";
  const role = $("#key-role").value;
  const k = await api("/api/admin/keys", { name, role });
  $("#key-name").value = "";
  const rev = $("#key-reveal");
  rev.hidden = false;
  rev.innerHTML = `New ${k.role} key — copy now, shown once:<br><b>${escapeHTML(k.key)}</b>`;
  navigator.clipboard?.writeText(k.key).catch(() => {});
  toast("key created & copied");
  await renderKeys();
}

// ---- handlers ----
$("#login-go").onclick = doLogin;
$("#login-key").addEventListener("keydown", (e) => { if (e.key === "Enter") doLogin(); });
$("#btn-logout").onclick = logout;
$("#btn-keys").onclick = openKeys;
$("#keys-close").onclick = closeKeys;
$("#keys-scrim").onclick = closeKeys;
$("#key-create").onclick = createKeyUI;
$("#gw-copy").onclick = () => { navigator.clipboard.writeText(gatewaySnippet()); toast("example copied"); };
document.addEventListener("click", (e) => { const r = e.target.closest("[data-revoke]"); if (r && confirm("Revoke this key?")) api("/api/admin/keys?id=" + r.dataset.revoke, null, "DELETE").then(renderKeys); });

// ---- boot ----
async function boot() {
  if (!ADMIN_KEY) return showLogin();
  try {
    const me = await fetch("/api/me", { headers: authHeaders() }).then((r) => r.json());
    if (me.user && me.user.role === "admin") { hideLogin(); $("#btn-logout").hidden = false; await load(); }
    else showLogin(me.user ? "That key is not an admin key." : "");
  } catch { showLogin(); }
}
boot();
