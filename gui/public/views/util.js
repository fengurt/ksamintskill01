const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const SKILL_STARS_KEY = "kskill.starred.v1";

function skillStarId(skill) {
  return String(typeof skill === "object" ? skill.id || skill.name : skill || "").trim().toLowerCase();
}

export function localSkillStars() {
  try {
    const value = JSON.parse(localStorage.getItem(SKILL_STARS_KEY) || "[]");
    return new Set(Array.isArray(value) ? value.map(skillStarId).filter(Boolean) : []);
  } catch {
    return new Set();
  }
}

export function isLocalSkillStarred(skill) {
  return localSkillStars().has(skillStarId(skill));
}

export function toggleLocalSkillStar(skill) {
  const id = skillStarId(skill);
  const stars = localSkillStars();
  if (stars.has(id)) stars.delete(id);
  else stars.add(id);
  localStorage.setItem(SKILL_STARS_KEY, JSON.stringify([...stars]));
  return stars.has(id);
}

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

export function fmtBytes(n) {
  const v = Number(n) || 0;
  if (v < 1024) return `${v} B`;
  if (v < 1024 * 1024) return `${Math.round(v / 1024)} KB`;
  return `${(v / (1024 * 1024)).toFixed(1)} MB`;
}

export function fmtTime(ts) {
  if (!ts) return "—";
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return String(ts);
  }
}

export async function copyText(text) {
  const value = String(text || "");
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const ta = document.createElement("textarea");
  ta.value = value;
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  ta.remove();
}

export function bindCopyButtons(root) {
  root.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const text = btn.getAttribute("data-copy");
      const prev = btn.textContent;
      try {
        await copyText(text);
        btn.textContent = "已复制";
        setTimeout(() => {
          btn.textContent = prev;
        }, 1200);
      } catch {
        btn.textContent = text || prev;
      }
    });
  });
}

export function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstChild;
}

export { esc };
