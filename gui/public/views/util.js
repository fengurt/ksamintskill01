const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

export async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "content-type": "application/json", ...(opts.headers || {}) },
    ...opts,
    body: opts.body != null ? JSON.stringify(opts.body) : undefined,
  });
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!res.ok) throw new Error(data.error || res.statusText || "request failed");
  return data;
}

export function badge(status, label) {
  const cls =
    status === "ok" || status === true
      ? "ok"
      : status === "fail" || status === false || status === "foreign" || status === "broken"
        ? "fail"
        : status === "warn" || status === "missing" || status === "running"
          ? "warn"
          : "";
  return `<span class="badge ${cls}">${esc(label ?? status)}</span>`;
}

export function fmtTime(ts) {
  if (!ts) return "—";
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return String(ts);
  }
}

export function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstChild;
}

export { esc };
