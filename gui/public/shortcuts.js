const GO = {
  h: "#/",
  s: "#/skills",
  p: "#/projects",
  r: "#/runs",
  e: "#/registry",
  j: "#/jobs",
};

const HELP = [
  ["?", "打开 / 关闭快捷键"],
  ["g h", "Home"],
  ["g p", "Projects"],
  ["g s", "Skills"],
  ["g r", "Runs"],
  ["g e", "Registry"],
  ["g j", "Jobs"],
  ["0–6", "项目阶段（与卡片编号一致）"],
  ["[ ]", "上一 / 下一阶段"],
  ["/", "搜索幻灯片 / 过滤目录"],
  ["j k", "目录上 / 下一项"],
  ["← → Space", "幻灯片上一 / 下一页"],
  ["页码", "预览栏输入后回车跳转"],
  ["t", "幻灯片铺满 / 退出"],
  ["Esc", "退出铺满"],
  ["Enter", "打开当前项"],
  ["o", "折叠 / 展开当前章"],
  ["d", "下载文件包"],
  ["S", "下载幻灯片评审包"],
];

function inField(el) {
  if (!el) return false;
  const tag = (el.tagName || "").toLowerCase();
  return tag === "input" || tag === "textarea" || tag === "select" || el.isContentEditable;
}

function ensureHelp() {
  let el = document.getElementById("kbd-help");
  if (el) return el;
  el = document.createElement("div");
  el.id = "kbd-help";
  el.hidden = true;
  el.innerHTML = `<div class="kbd-card">
    <div class="row"><h3 style="margin:0">快捷键</h3><span class="spacer"></span><span class="mono muted">? 关闭</span></div>
    <table><tbody>${HELP.map(([k, d]) => `<tr><td class="mono">${k}</td><td>${d}</td></tr>`).join("")}</tbody></table>
  </div>`;
  el.addEventListener("click", (e) => {
    if (e.target === el) el.hidden = true;
  });
  document.body.appendChild(el);
  document.getElementById("kbd-open")?.addEventListener("click", () => toggleHelp());
  return el;
}

export function toggleHelp() {
  const el = ensureHelp();
  el.hidden = !el.hidden;
}

export function installShortcuts() {
  ensureHelp();
  let pendingG = false;
  let gTimer = 0;
  window.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const help = document.getElementById("kbd-help");
    if (e.key === "?" || (e.key === "/" && e.shiftKey)) {
      if (inField(e.target) && e.key === "/") return;
      e.preventDefault();
      toggleHelp();
      pendingG = false;
      return;
    }
    if (e.key === "Escape") {
      if (help && !help.hidden) {
        help.hidden = true;
        e.preventDefault();
      }
      pendingG = false;
      return;
    }
    if (inField(e.target)) return;
    if (pendingG) {
      pendingG = false;
      clearTimeout(gTimer);
      e.preventDefault();
      const dest = GO[e.key];
      if (dest) location.hash = dest;
      return;
    }
    if (e.key === "g") {
      pendingG = true;
      gTimer = window.setTimeout(() => {
        pendingG = false;
      }, 800);
      e.preventDefault();
    }
  });
}
