import { api, badge, esc, fmtTime } from "./util.js";

let studioKeyHandler = null;

function unbindStudioKeys() {
  if (!studioKeyHandler) return;
  window.removeEventListener("keydown", studioKeyHandler);
  studioKeyHandler = null;
}

function packBadge(pack) {
  if (!pack) return badge("warn", "无文件包");
  return pack.ready ? badge("ok", "文件包就绪") : badge("warn", "文件包未齐");
}

export async function renderProjects(root, parts) {
  unbindStudioKeys();
  if (parts[1] === "new") {
    root.classList.remove("studio-page");
    return renderNewProject(root);
  }
  if (parts[1]) return renderProjectDetail(root, parts[1], parts[2]);
  root.classList.remove("studio-page");

  root.innerHTML = `<p class="muted">Loading…</p>`;
  const [{ projects }, { templates }] = await Promise.all([
    api("/api/projects"),
    api("/api/templates"),
  ]);
  root.innerHTML = `
    <div class="row"><h1 style="margin:0">Projects</h1><span class="spacer"></span>
      <a class="btn" href="#/projects/new">New project</a></div>
    <p class="lede">每个项目完成长文档 → 可开发文件包。点进项目先看调用的 skill（含阶段）和最终产出。</p>
    <div class="grid grid-3">
      ${
        projects
          .map((p) => {
            const tpl = templates.find((t) => t.id === p.template);
            const skillNames = (tpl?.skills || []).map((s) => s.label || s.id).join(" · ");
            const counts = p.pack?.counts;
            return `<a class="card clickable" href="#/projects/${esc(p.id)}" style="text-decoration:none;color:inherit">
        <h3>${esc(p.name)}</h3>
        <div>${packBadge(p.pack)} ${badge("", p.template)}</div>
        <div class="muted" style="margin-top:.45rem">${esc(skillNames || p.template)}</div>
        <div class="mono muted" style="margin-top:.35rem">${
          counts
            ? `units ${counts.units ?? "—"} · pages ${counts.pages ?? "—"} · fill ${counts.fills ?? 0}`
            : "尚未产出"
        }</div>
      </a>`;
          })
          .join("") || `<div class="empty">No projects — create one to run a template.</div>`
      }
    </div>
    <h2>Templates</h2>
    <div class="grid grid-2">
      ${templates
        .map(
          (t) => `<div class="card">
        <h3>${esc(t.title)}</h3>
        <p class="muted">${esc(t.description)}</p>
        <div class="step-rail">${(t.skills || [])
          .map((s) => `<span class="step-pill">${esc(s.label || s.id)}</span>`)
          .join("")}</div>
      </div>`
        )
        .join("")}
    </div>
  `;
}

async function renderNewProject(root) {
  const [{ templates }, { themes }] = await Promise.all([api("/api/templates"), api("/api/themes")]);
  root.innerHTML = `
    <a class="btn ghost" href="#/projects">← projects</a>
    <h1>New project</h1>
    <div class="card" style="max-width:640px">
      <div class="field"><label>Name</label><input id="name" style="width:100%" /></div>
      <div class="field"><label>Template</label>
        <select id="template" style="width:100%">
          ${templates.map((t) => `<option value="${esc(t.id)}" ${t.id === "alongslides" ? "selected" : ""}>${esc(t.title)}</option>`).join("")}
        </select>
      </div>
      <div class="field"><label>Theme / skin（留给后续 Baslide01 开发）</label>
        <select id="theme" style="width:100%">
          ${(themes || [])
            .map(
              (t) =>
                `<option value="${esc(t.id)}">${esc(t.label)} · ${esc(t.canvas)}${t.mechanical ? "" : " · agent path"}</option>`
            )
            .join("")}
        </select>
      </div>
      <div class="field"><label>Gates</label>
        <label class="row"><input type="checkbox" id="std-fit" checked /> fit-overfull</label>
        <label class="row"><input type="checkbox" id="std-hop1" checked /> hop1 source fidelity</label>
      </div>
      <div class="field"><label>Source markdown (absolute or repo-relative)</label><input id="source" style="width:100%" placeholder="fixtures/local/doc.md" /></div>
      <div class="field"><label>Work id under .work/ (optional)</label><input id="work" style="width:100%" placeholder="my-run" /></div>
      <div class="field"><label>Notes</label><textarea id="notes"></textarea></div>
      <button class="btn" id="create">Create</button>
      <p id="err" class="muted" style="color:var(--fail)"></p>
    </div>
  `;
  root.querySelector("#create").addEventListener("click", async () => {
    try {
      const body = {
        name: root.querySelector("#name").value,
        template: root.querySelector("#template").value,
        theme: root.querySelector("#theme").value,
        standards: {
          "fit-overfull": root.querySelector("#std-fit").checked,
          hop1: root.querySelector("#std-hop1").checked,
          hop2: false,
        },
        source: root.querySelector("#source").value || undefined,
        work_id: root.querySelector("#work").value || undefined,
        notes: root.querySelector("#notes").value,
      };
      const p = await api("/api/projects", { method: "POST", body });
      location.hash = `#/projects/${p.id}`;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
}

function stageBadge(status) {
  if (status === "ok") return badge("ok", "done");
  if (status === "fail") return badge("fail", "fail");
  if (status === "warn") return badge("warn", "partial");
  if (status === "later") return badge("mech", "下一步");
  return badge("", "pending");
}

const CORE_STAGE_IDS = ["a-segment", "b-outline", "c-pagination", "d-emit"];
const REVIEW_STAGE_IDS = ["source", "hop1"];

function stageTabHtml(p, current, s, key) {
  return `<a class="stage-tab ${s.id === current ? "on" : ""} ${s.later ? "later" : ""}" role="tab" aria-selected="${s.id === current}" href="#/projects/${esc(p.id)}/${esc(s.id)}">
    <div class="row"><span class="stage-key">${key}</span><span class="stage-tab-label">${esc(s.label)}</span><span class="spacer"></span>${stageBadge(s.status)}</div>
    <span class="stage-tab-goal">${esc(s.goal)}</span>
  </a>`;
}

function bindJobButtons(root, p) {
  root.querySelector("#run-tpl")?.addEventListener("click", async () => {
    try {
      const job = await api("/api/jobs", {
        method: "POST",
        body: {
          template: p.template === "baslide-slides" ? "alongslides" : p.template,
          projectId: p.id,
          work: p.work,
          source: p.source,
          theme: p.theme,
          standards: { ...p.standards, hop2: false },
          genre: p.genre,
        },
      });
      location.hash = `#/jobs/${job.id}`;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
  root.querySelector("#run-slides")?.addEventListener("click", async () => {
    try {
      const job = await api("/api/jobs", {
        method: "POST",
        body: {
          template: "baslide-slides",
          projectId: p.id,
          work: p.work,
          theme: p.theme,
          genre: p.genre,
          standards: { hop2: true },
        },
      });
      location.hash = `#/jobs/${job.id}`;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
  root.querySelector("#del")?.addEventListener("click", async () => {
    if (!confirm("Delete project? (.work artifacts are kept)")) return;
    await api(`/api/projects/${encodeURIComponent(p.id)}`, { method: "DELETE" });
    location.hash = "#/projects";
  });
}

async function showPreview(pane, p, runId, item) {
  if (!item) {
    pane.innerHTML = `<div class="empty">从左边目录选一项预览。</div>`;
    return;
  }
  pane.innerHTML = `<p class="muted">Loading ${esc(item.label)}…</p>`;
  try {
    if (item.kind === "file") {
      const file = await api(`/api/file?path=${encodeURIComponent(item.path)}`);
      pane.innerHTML = `<div class="preview-head"><h3>${esc(file.name)}</h3><span class="mono muted">${esc(file.path)}</span></div><pre class="pre light preview-body">${esc(file.text)}</pre>`;
      return;
    }
    if (item.kind === "unit") {
      const unit = await api(`/api/runs/${encodeURIComponent(runId)}/units/${encodeURIComponent(item.id)}`);
      pane.innerHTML = `<div class="preview-head"><h3>${esc(unit.id)}</h3>${badge("", unit.kind || "unit")}</div><pre class="pre light preview-body">${esc(unit.text)}</pre>`;
      return;
    }
    if (item.kind === "page") {
      const page = await api(`/api/runs/${encodeURIComponent(runId)}/pages/${encodeURIComponent(item.id)}`);
      pane.innerHTML = `<div class="preview-head"><h3>${esc(item.id)}</h3><span class="muted">${esc(item.sub || "")}</span> ${item.meta ? badge("", item.meta) : ""}</div><pre class="pre light preview-body">${esc(page.markdown)}</pre>`;
      return;
    }
    if (item.kind === "audit") {
      const page = await api(`/api/runs/${encodeURIComponent(runId)}/audit/${encodeURIComponent(item.id)}`);
      const hop1 = (page.findings?.hop1 || [])
        .map((f) => `${f.severity} · ${f.kind || ""} · ${f.detail || f.note || ""}`)
        .join("\n");
      pane.innerHTML = `<div class="preview-head"><h3>${esc(item.id)}</h3>${stageBadge(item.meta === "hard" ? "fail" : item.meta === "warn" ? "warn" : "ok")}</div>
        ${hop1 ? `<pre class="pre light" style="max-height:160px">${esc(hop1)}</pre>` : `<p class="muted">这一页 hop1 无 finding。</p>`}
        <pre class="pre light preview-body">${esc(page.material || "")}</pre>`;
      return;
    }
    if (item.kind === "html") {
      pane.innerHTML = `<div class="preview-head"><h3>${esc(item.label)}</h3><a class="btn ghost" href="${esc(item.href)}" target="_blank">打开 HTML</a></div>
        <p class="muted">这是下一步 Baslide01 幻灯片，不是当前完成物。</p>
        <iframe class="preview-frame" src="${esc(item.href)}" title="deck"></iframe>`;
      return;
    }
    if (item.kind === "dir") {
      pane.innerHTML = `<div class="preview-head"><h3>${esc(item.label)}</h3></div><p class="muted">目录 ${esc(item.path)} · ${esc(item.sub || "")}。切到「3 · pages」逐页预览。</p>`;
      return;
    }
    pane.innerHTML = `<div class="empty">无法预览这一项。</div>`;
  } catch (e) {
    pane.innerHTML = `<p style="color:var(--fail)">${esc(e.message)}</p>`;
  }
}

async function renderProjectDetail(root, id, stageId) {
  root.classList.add("studio-page");
  root.innerHTML = `<p class="muted">Loading…</p>`;
  const p = await api(`/api/projects/${encodeURIComponent(id)}`);
  const runId = (p.work || "").replace(/^\.work\//, "");
  const stages = p.viewStages || [];
  const skills = [...new Set((p.skills || []).map((s) => s.label || s.id))];
  const current = stages.some((s) => s.id === stageId) ? stageId : "c-pagination";
  const active = stages.find((s) => s.id === current) || stages[0];
  const pack = p.pack;

  root.innerHTML = `
    <div class="row">
      <a class="btn ghost" href="#/projects">← projects</a>
      <span class="spacer"></span>
      <button class="btn" id="run-tpl">生成文件包</button>
      <a class="btn ghost" href="/api/projects/${esc(p.id)}/pack.zip" ${pack?.ready ? "" : "hidden"}>下载文件包</a>
      <button class="btn ghost" id="run-slides">下一步 · 开发幻灯片</button>
      <button class="btn danger ghost" id="del">Delete</button>
    </div>
    <h1>${esc(p.name)}</h1>
    <div class="goal-card card">
      <div class="row" style="align-items:flex-start">
        <div>
          <div class="stat-l">项目目标</div>
          <p class="goal-line">长文档 → 零损失页面素材（可开发文件包）。<b>现在还不是 slides。</b></p>
        </div>
        <span class="spacer"></span>
        <div>${packBadge(pack)} ${badge("", p.template)} ${badge("", p.theme || "TIANSIGHT")}</div>
      </div>
      <div class="muted" style="margin-top:.35rem">Skill：${
        skills.map((s) => `<span class="step-pill">${esc(s)}</span>`).join(" ") || "—"
      }</div>
      <div class="mono muted" style="margin-top:.35rem">${
        pack?.counts
          ? `${pack.counts.units ?? "—"} units · ${pack.counts.pages ?? "—"} pages · ${pack.counts.fills ?? 0} L3 fill`
          : "尚未产出"
      }</div>
    </div>

    <div class="stage-block">
      <div class="stat-l">四个阶段</div>
      <div class="stage-bar core" role="tablist">
        ${CORE_STAGE_IDS.map((id) => {
          const s = stages.find((x) => x.id === id);
          if (!s) return "";
          return stageTabHtml(p, current, s, stages.findIndex((x) => x.id === id));
        }).join("")}
      </div>
    </div>
    <div class="stage-block">
      <div class="stat-l">审阅</div>
      <div class="stage-bar review" role="tablist">
        ${REVIEW_STAGE_IDS.map((id) => {
          const s = stages.find((x) => x.id === id);
          if (!s) return "";
          return stageTabHtml(p, current, s, stages.findIndex((x) => x.id === id));
        }).join("")}
      </div>
    </div>
    <div class="stage-block">
      <div class="stat-l">全局优化</div>
      <div class="stage-bar optimize">
        ${(() => {
          const s = stages.find((x) => x.id === "slides");
          return s ? stageTabHtml(p, current, s, stages.findIndex((x) => x.id === "slides")) : "";
        })()}
        <div class="opt-list">
          ${(p.laterSkills || [])
            .map((s) => `<span class="step-pill" title="${esc(s.note || "")}">${esc(s.label || s.id)}</span>`)
            .join("") || `<span class="muted">暂无后续 skill</span>`}
        </div>
      </div>
    </div>

    <div class="studio-head">
      <h2>${esc(active?.label || "产出")}</h2>
      <p class="lede" style="margin:0">${esc(active?.goal || "")} · skill <span class="mono">${esc(active?.skill || "")}</span>
        ${active?.later ? " · 文件包完成之后才做" : ""}</p>
    </div>
    <div id="studio" class="studio">
      <div class="studio-nav">
        <input class="search" id="dir-q" placeholder="过滤目录…  /" />
        <div id="dir-count" class="dir-count">目录加载中…</div>
        <div id="dir" class="dir-list"><p class="muted">Loading…</p></div>
      </div>
      <div id="preview" class="studio-pane"><div class="empty">从左边目录选一项预览。</div></div>
    </div>
    <p id="err" style="color:var(--fail)"></p>
  `;

  bindJobButtons(root, p);

  const dirEl = root.querySelector("#dir");
  const pane = root.querySelector("#preview");
  const qEl = root.querySelector("#dir-q");
  let items = [];
  const collapsed = new Set();
  let selectedId = null;

  function chaptersOf(it) {
    if (Array.isArray(it.chapters)) return it.chapters.filter(Boolean);
    if (Array.isArray(it.path)) return it.path.filter(Boolean);
    return [];
  }

  function itemHay(it) {
    const pathText = Array.isArray(it.path) ? it.path.join(" ") : String(it.path || "");
    return `${it.id} ${it.label} ${it.sub || ""} ${it.meta || ""} ${pathText}`.toLowerCase();
  }

  function buildTree(list) {
    const tree = { name: "", key: "", children: [], leaves: [] };
    for (const it of list) {
      let node = tree;
      let key = "";
      for (const seg of chaptersOf(it)) {
        key = `${key}/${seg}`;
        let child = node.children.find((c) => c.name === seg);
        if (!child) {
          child = { name: seg, key, children: [], leaves: [] };
          node.children.push(child);
        }
        node = child;
      }
      node.leaves.push(it);
    }
    return tree;
  }

  function leafHtml(it) {
    return `<button type="button" class="dir-item ${it.id === selectedId ? "on" : ""}" data-id="${esc(it.id)}">
      <span class="dir-id">${esc(it.label)}${it.meta ? ` · ${esc(it.meta)}` : ""}</span>
      <span class="dir-sub">${esc(it.sub || "")}</span>
    </button>`;
  }

  function countLeaves(node) {
    return node.leaves.length + node.children.reduce((s, c) => s + countLeaves(c), 0);
  }

  function nodeHtml(node, depth) {
    if (!node.key) {
      const parts = [];
      if (node.leaves.length) parts.push(node.leaves.map(leafHtml).join(""));
      for (const child of node.children) parts.push(nodeHtml(child, 0));
      return parts.join("");
    }
    const open = !collapsed.has(node.key);
    const head = `<div class="dir-chapter" data-depth="${depth}">
      <button type="button" class="dir-twist" data-chapter="${esc(node.key)}" aria-expanded="${open}">${open ? "▼" : "▶"}</button>
      <button type="button" class="dir-chapter-name" data-chapter="${esc(node.key)}" title="${esc(node.name)}">${esc(node.name)} <span class="dir-n">${countLeaves(node)}</span></button>
    </div>`;
    if (!open) return head;
    const body = [];
    if (node.leaves.length) body.push(node.leaves.map(leafHtml).join(""));
    for (const child of node.children) body.push(nodeHtml(child, depth + 1));
    return `${head}<div class="dir-branch">${body.join("")}</div>`;
  }

  function collapseDeep(node, keepDepth, depth) {
    if (!node.key) {
      for (const c of node.children) collapseDeep(c, keepDepth, 0);
      return;
    }
    if (depth >= keepDepth) collapsed.add(node.key);
    for (const c of node.children) collapseDeep(c, keepDepth, depth + 1);
  }

  function chapterKeys(it) {
    const keys = [];
    let key = "";
    for (const seg of chaptersOf(it)) {
      key = `${key}/${seg}`;
      keys.push(key);
    }
    return keys;
  }

  function revealItem(it) {
    for (const key of chapterKeys(it)) collapsed.delete(key);
  }

  function walkVisibleLeaves(node, acc) {
    for (const it of node.leaves) {
      if (it.kind !== "dir") acc.push(it);
    }
    for (const child of node.children) {
      if (!collapsed.has(child.key)) walkVisibleLeaves(child, acc);
    }
    return acc;
  }

  function currentTree() {
    const q = (qEl?.value || "").trim().toLowerCase();
    return buildTree(q ? items.filter((it) => itemHay(it).includes(q)) : items);
  }

  function selectItem(id, { preview = true, reveal = true } = {}) {
    const item = items.find((it) => it.id === id);
    if (!item) return;
    selectedId = id;
    if (reveal) revealItem(item);
    if (!dirEl.querySelector(`.dir-item[data-id="${CSS.escape(id)}"]`)) paintDir(qEl?.value || "");
    dirEl.querySelectorAll(".dir-item").forEach((b) => b.classList.toggle("on", b.getAttribute("data-id") === id));
    dirEl.querySelector(".dir-item.on")?.scrollIntoView({ block: "nearest" });
    if (preview) showPreview(pane, p, runId, item);
  }

  function paintDir(filter) {
    const q = (filter || "").trim().toLowerCase();
    const shown = q ? items.filter((it) => itemHay(it).includes(q)) : items;
    const countEl = root.querySelector("#dir-count");
    const tree = buildTree(shown);
    const openCount = walkVisibleLeaves(tree, []).length;
    if (countEl) countEl.textContent = `${openCount} 可见 / ${shown.length} 匹配 / ${items.length} 项`;
    dirEl.innerHTML = nodeHtml(tree, 0) || `<p class="muted">这一阶段还没有目录。</p>`;
    dirEl.querySelectorAll(".dir-item").forEach((btn) => {
      btn.addEventListener("click", () => selectItem(btn.getAttribute("data-id")));
    });
    dirEl.querySelectorAll("[data-chapter]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-chapter");
        if (collapsed.has(key)) collapsed.delete(key);
        else collapsed.add(key);
        paintDir(qEl.value);
      });
    });
  }

  function bindStudioKeys() {
    unbindStudioKeys();
    const onKey = (e) => {
      if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
      const help = document.getElementById("kbd-help");
      if (help && !help.hidden) return;
      const tag = (e.target?.tagName || "").toLowerCase();
      const typing = tag === "input" || tag === "textarea" || tag === "select" || e.target?.isContentEditable;
      if (e.key === "/" && !typing) {
        e.preventDefault();
        qEl?.focus();
        qEl?.select();
        return;
      }
      if (e.key === "Escape" && typing) {
        qEl.blur();
        return;
      }
      if (typing) return;
      const ids = stages.map((s) => s.id);
      if (e.key >= "0" && e.key <= "6") {
        const next = ids[Number(e.key)];
        if (next) location.hash = `#/projects/${p.id}/${next}`;
        return;
      }
      if (e.key === "[" || e.key === "]") {
        const i = ids.indexOf(current);
        const next = ids[i + (e.key === "]" ? 1 : -1)];
        if (next) location.hash = `#/projects/${p.id}/${next}`;
        return;
      }
      if (e.key === "d") {
        if (pack?.ready) location.href = `/api/projects/${p.id}/pack.zip`;
        return;
      }
      const leaves = walkVisibleLeaves(currentTree(), []);
      if (e.key === "j" || e.key === "ArrowDown" || e.key === "k" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!leaves.length) return;
        const idx = leaves.findIndex((it) => it.id === selectedId);
        const start = idx < 0 ? (e.key === "k" || e.key === "ArrowUp" ? 0 : -1) : idx;
        const delta = e.key === "j" || e.key === "ArrowDown" ? 1 : -1;
        const next = leaves[(start + delta + leaves.length) % leaves.length];
        selectItem(next.id);
        return;
      }
      if (e.key === "Enter" && selectedId) {
        selectItem(selectedId);
        return;
      }
      if (e.key === "o") {
        const item = items.find((it) => it.id === selectedId);
        const keys = chapterKeys(item);
        if (!keys.length) return;
        const key = keys[keys.length - 1];
        if (collapsed.has(key)) collapsed.delete(key);
        else collapsed.add(key);
        paintDir(qEl.value);
        dirEl.querySelectorAll(".dir-item").forEach((b) => b.classList.toggle("on", b.getAttribute("data-id") === selectedId));
      }
    };
    studioKeyHandler = onKey;
    window.addEventListener("keydown", onKey);
  }

  try {
    const view = await api(`/api/projects/${encodeURIComponent(p.id)}/stage/${encodeURIComponent(current)}`);
    items = view.items || [];
    const tree = buildTree(items);
    collapseDeep(tree, 1, 0);
    paintDir("");
    const firstLeaf = items.find((it) => it.kind !== "dir");
    if (firstLeaf) selectItem(firstLeaf.id);
    else if (active?.later && !items.length) {
      pane.innerHTML = `<div class="empty">幻灯片还没做。当前完成物是左边「3 · pages」的页面素材。需要时点「下一步 · 开发幻灯片」。</div>`;
    }
  } catch (e) {
    dirEl.innerHTML = `<p style="color:var(--fail)">${esc(e.message)}</p>`;
  }
  qEl?.addEventListener("input", () => {
    collapsed.clear();
    paintDir(qEl.value);
  });
  bindStudioKeys();
}
