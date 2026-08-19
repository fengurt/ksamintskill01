import { api, badge, bindCopyButtons, copyText, esc, fmtTime } from "./util.js";

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

function itemHay(it) {
  const pathText = Array.isArray(it.path) ? it.path.join(" ") : String(it.path || "");
  const chapters = Array.isArray(it.chapters) ? it.chapters.join(" ") : "";
  return `${it.id} ${it.label} ${it.sub || ""} ${it.meta || ""} ${it.page || ""} ${pathText} ${chapters}`.toLowerCase();
}

function deckPages(items) {
  return (items || []).filter((it) => it.kind === "html" && it.id !== "deck.html");
}

function deckMetaHtml(stats, viz) {
  const s = stats || {};
  const v = viz || {};
  const planned = s.vizPlanned ?? v.planned ?? 0;
  const drawn = s.vizDrawn ?? v.drawn ?? 0;
  const fillBits = Object.entries(s.fills || {})
    .filter(([, n]) => n)
    .map(([k, n]) => `${k} ${n}`)
    .join(" · ");
  return `<div class="deck-meta">
    <span>HTML <b>${s.slides ?? "—"}</b></span>
    <span>数据页 <b>${s.data ?? 0}</b><span class="muted">（kpi ${s.kpi ?? 0} · 表 ${s.tables ?? 0}）</span></span>
    <span>可视化 <b>${planned}</b> 规划 / <b>${drawn}</b> 绘制</span>
    ${fillBits ? `<span class="muted">${esc(fillBits)}</span>` : ""}
  </div>`;
}

function paintDeckFinder(pane, q) {
  const box = pane.querySelector("#deck-finder");
  if (!box) return;
  const pages = deckPages(pane._deckNav?.items);
  const needle = (q || "").trim().toLowerCase();
  if (needle) {
    const hits = pages.filter((it) => itemHay(it).includes(needle) || String(it.page) === needle);
    box.innerHTML = hits.length
      ? hits
          .slice(0, 80)
          .map(
            (it) =>
              `<button type="button" class="deck-hit" data-id="${esc(it.id)}"><span class="mono">${esc(String(it.page))}</span> ${esc(it.sub || it.label)}${it.meta ? ` <span class="muted">${esc(it.meta)}</span>` : ""}</button>`
          )
          .join("")
      : `<p class="muted">无匹配</p>`;
    box.hidden = false;
    return;
  }
  const groups = [];
  for (const it of pages) {
    const name = (it.chapters && it.chapters[0]) || "未分章";
    const last = groups[groups.length - 1];
    if (!last || last.name !== name) groups.push({ name, items: [it] });
    else last.items.push(it);
  }
  box.innerHTML = groups
    .map((g) => {
      const start = g.items[0]?.page;
      const end = g.items[g.items.length - 1]?.page;
      return `<button type="button" class="deck-ch" data-id="${esc(g.items[0].id)}">${esc(g.name)} <span class="mono muted">${start}–${end} · ${g.items.length}</span></button>`;
    })
    .join("");
}

function bindDeckFinder(pane) {
  const q = pane.querySelector("#deck-q");
  const box = pane.querySelector("#deck-finder");
  const goId = (id) => pane._deckNav?.selectItem?.(id);
  q?.addEventListener("input", () => {
    const v = q.value;
    const left = pane._deckNav?.qEl;
    if (left && left.value !== v) {
      left.value = v;
      pane._deckNav.paintDir?.(v);
    }
    paintDeckFinder(pane, v);
  });
  q?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const first = box?.querySelector("[data-id]");
      if (first) goId(first.getAttribute("data-id"));
    }
    if (e.key === "Escape") {
      box.hidden = true;
      q.blur();
    }
  });
  q?.addEventListener("focus", () => paintDeckFinder(pane, q.value));
  pane.querySelector("[data-deck=finder]")?.addEventListener("click", () => {
    if (q) q.value = "";
    paintDeckFinder(pane, "");
    box.hidden = !box.hidden;
    if (!box.hidden) q?.focus();
  });
  box?.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-id]");
    if (!btn) return;
    goId(btn.getAttribute("data-id"));
    box.hidden = true;
  });
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
    <p class="lede">文件包 zip 分三栏：original/ 原文 · pages/ 逐页 md · audit/ 审阅。Baslide01 历史 HTML 会作为只读项目出现。</p>
    <div class="project-bulkbar row" aria-label="Project bulk actions">
      <label class="row"><input type="checkbox" id="project-select-all" /> 全选</label>
      <span id="project-selected" class="muted">0 selected</span>
      <span class="spacer"></span>
      <button type="button" class="btn ghost" id="copy-projects" disabled>Copy info</button>
      <button type="button" class="btn" id="export-project-pdfs" disabled>PDF ZIP</button>
      <span id="project-bulk-status" class="muted" aria-live="polite"></span>
    </div>
    <div class="grid grid-3">
      ${
        projects
          .map((p) => {
            const tpl = templates.find((t) => t.id === p.template);
            const skillNames = (tpl?.skills || []).map((s) => s.label || s.id).join(" · ");
            const counts = p.pack?.counts;
            const exportId = `${p.id} template=${p.template}`;
            return `<div class="card project-card ${p.history ? "" : "clickable"}" ${p.history ? "" : `data-href="#/projects/${esc(p.id)}"`}>
        <div class="row" style="align-items:flex-start">
          <input class="project-select" type="checkbox" value="${esc(p.id)}" aria-label="Select ${esc(p.name)}" />
          <h3 style="margin:0">${esc(p.name)}</h3>
          <span class="spacer"></span>
          <button type="button" class="id-copy" data-copy="${esc(exportId)}" title="复制导出 ID">${esc(p.id)}</button>
        </div>
        <div style="margin-top:.45rem">${p.history ? badge("ok", "history") : packBadge(p.pack)} ${badge("", p.template)} ${p.pdf ? badge("ok", "PDF") : ""}</div>
        <div class="muted" style="margin-top:.45rem">${esc(skillNames || p.template)}</div>
        <div class="mono muted" style="margin-top:.35rem">${
          p.history
            ? `HTML report · ${fmtTime(p.updated_at)}`
            : counts
            ? `units ${counts.units ?? "—"} · pages ${counts.pages ?? "—"} · fill ${counts.fills ?? 0}`
            : "尚未产出"
        }</div>
        <div class="row" style="margin-top:.5rem">
          ${p.report_href ? `<a class="btn ghost" href="${esc(p.report_href)}" target="_blank" rel="noopener">Open report</a>` : ""}
          ${p.pack?.ready ? `<a class="btn ghost" href="/api/projects/${esc(p.id)}/pack.zip">文件包</a>` : ""}
          ${p.pack?.slides ? `<a class="btn ghost" href="/api/projects/${esc(p.id)}/slides.zip">幻灯片评审包</a>` : ""}
        </div>
      </div>`;
          })
          .join("") || `<div class="empty">No projects — create one to run a template.</div>`
      }
    </div>
    <h2>Templates</h2>
    <div class="grid grid-2">
      ${templates
        .map(
          (t) => `<div class="card">
        <div class="row" style="align-items:flex-start">
          <h3 style="margin:0">${esc(t.title)}</h3>
          <span class="spacer"></span>
          <button type="button" class="id-copy" data-copy="${esc(t.id)}" title="复制模板 ID">${esc(t.id)}</button>
        </div>
        <p class="muted">${esc(t.description)}</p>
        <div class="step-rail">${(t.skills || [])
          .map((s) => `<span class="step-pill">${esc(s.label || s.id)}</span>`)
          .join("")}</div>
      </div>`
        )
        .join("")}
    </div>
  `;
  bindCopyButtons(root);
  const selected = new Set();
  const all = [...root.querySelectorAll(".project-select")];
  const selectAll = root.querySelector("#project-select-all");
  const count = root.querySelector("#project-selected");
  const copy = root.querySelector("#copy-projects");
  const pdfs = root.querySelector("#export-project-pdfs");
  const status = root.querySelector("#project-bulk-status");
  const updateSelection = () => {
    for (const box of all) box.closest(".project-card")?.classList.toggle("selected", box.checked);
    selected.clear();
    for (const box of all) if (box.checked) selected.add(box.value);
    count.textContent = `${selected.size} selected`;
    copy.disabled = pdfs.disabled = selected.size === 0;
    selectAll.checked = all.length > 0 && selected.size === all.length;
    selectAll.indeterminate = selected.size > 0 && selected.size < all.length;
  };
  for (const box of all) box.addEventListener("change", updateSelection);
  selectAll.addEventListener("change", () => {
    for (const box of all) box.checked = selectAll.checked;
    updateSelection();
  });
  copy.addEventListener("click", async () => {
    const picked = projects.filter((p) => selected.has(p.id));
    const text = picked.map((p) => [
      `Name: ${p.name}`,
      `ID: ${p.id}`,
      `Type: ${p.history ? "Baslide01 history" : "project"}`,
      `Template: ${p.template}`,
      p.source ? `Source: ${p.source}` : "",
      p.html ? `HTML: ${p.html}` : "",
      p.work ? `Work: ${p.work}` : "",
      `Updated: ${fmtTime(p.updated_at)}`,
    ].filter(Boolean).join("\n")).join("\n\n");
    await copyText(text);
    status.textContent = "Copied";
  });
  pdfs.addEventListener("click", async () => {
    status.textContent = "Building PDFs…";
    pdfs.disabled = true;
    try {
      const res = await fetch("/api/projects/export-pdfs.zip", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ids: [...selected] }),
      });
      if (!res.ok) throw new Error((await res.json()).error || "export failed");
      const href = URL.createObjectURL(await res.blob());
      const a = document.createElement("a");
      a.href = href;
      a.download = "projects-pdf.zip";
      a.click();
      URL.revokeObjectURL(href);
      status.textContent = "Downloaded";
    } catch (e) {
      status.textContent = e.message;
    } finally {
      pdfs.disabled = selected.size === 0;
    }
  });
  root.querySelectorAll("[data-href]").forEach((card) => {
    card.addEventListener("click", (e) => {
      if (e.target.closest("a, button, input, label, [data-copy]")) return;
      location.hash = card.getAttribute("data-href");
    });
  });
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
          ${templates.map((t) => `<option value="${esc(t.id)}" ${t.id === "long4hslides" ? "selected" : ""}>${esc(t.title)}</option>`).join("")}
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
      if (p.page_pack_approved) {
        await api(`/api/projects/${encodeURIComponent(p.id)}`, { method: "PATCH", body: { page_pack_approved: false } });
      }
      const job = await api("/api/jobs", {
        method: "POST",
        body: {
          template: "long4hslides",
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
  root.querySelector("#approve-pack")?.addEventListener("click", async () => {
    try {
      await api(`/api/projects/${encodeURIComponent(p.id)}`, { method: "PATCH", body: { page_pack_approved: true } });
      p.page_pack_approved = true;
      root.querySelector("#approve-pack").textContent = "文件包已批准";
      root.querySelector("#approve-pack").disabled = true;
      root.querySelector("#run-slides").disabled = false;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
  root.querySelector("#run-slides")?.addEventListener("click", async () => {
    try {
      const job = await api("/api/jobs", {
        method: "POST",
        body: {
          template: "long4hslides-slides",
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

function setDecking(pane, on) {
  pane.classList.toggle("decking", on);
  pane.closest("#studio")?.classList.toggle("decking", on);
  if (!on) pane.classList.remove("theater");
}

function injectSdGo(iframe) {
  const win = iframe?.contentWindow;
  const doc = iframe?.contentDocument;
  if (!win || !doc || win.sdGo) return;
  const script = doc.createElement("script");
  script.textContent = `(function () {
  var slides = [].slice.call(document.querySelectorAll(".sd-slide"));
  function idx() {
    var n = slides.findIndex(function (el) { return el.classList.contains("on"); });
    return n < 0 ? 0 : n;
  }
  function go(n) {
    if (!slides.length) return 0;
    var i = ((Number(n) % slides.length) + slides.length) % slides.length;
    slides.forEach(function (el, j) { el.classList.toggle("on", j === i); });
    var hint = document.querySelector("#sd-nav-hint [data-idx]");
    if (hint) hint.textContent = (i + 1) + " / " + slides.length;
    if (slides.length > 1) try { history.replaceState(null, "", "#p=" + (i + 1)); } catch (e) {}
    if (parent !== window) parent.postMessage({ type: "sd-page", page: i + 1, total: slides.length }, "*");
    return i + 1;
  }
  window.sdGo = function (page) { return go(Number(page) - 1); };
  document.addEventListener("keydown", function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    if (ev.target && (ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA")) return;
    if (ev.key === "ArrowRight" || ev.key === " " || ev.key === "PageDown") { ev.preventDefault(); ev.stopImmediatePropagation(); go(idx() + 1); }
    else if (ev.key === "ArrowLeft" || ev.key === "PageUp") { ev.preventDefault(); ev.stopImmediatePropagation(); go(idx() - 1); }
    else if (ev.key === "Home") { ev.preventDefault(); ev.stopImmediatePropagation(); go(0); }
    else if (ev.key === "End") { ev.preventDefault(); ev.stopImmediatePropagation(); go(slides.length - 1); }
  }, true);
})();`;
  doc.documentElement.appendChild(script);
}

function deckGo(pane, page) {
  const iframe = pane.querySelector("iframe.deck-frame");
  const win = iframe?.contentWindow;
  const doc = iframe?.contentDocument;
  if (!win || !doc) return 0;
  if (typeof win.sdGo === "function") return win.sdGo(page) || 0;
  const slides = [...doc.querySelectorAll(".sd-slide")];
  if (!slides.length) return 0;
  const i = ((Number(page) - 1) % slides.length + slides.length) % slides.length;
  slides.forEach((el, idx) => el.classList.toggle("on", idx === i));
  const hint = doc.getElementById("sd-nav-hint")?.querySelector("[data-idx]");
  if (hint) hint.textContent = `${i + 1} / ${slides.length}`;
  const input = pane.querySelector("#deck-page");
  if (input) input.value = String(i + 1);
  const total = pane.querySelector("#deck-total");
  if (total) total.textContent = String(slides.length);
  pane.dispatchEvent(new CustomEvent("deck-page", { detail: { page: i + 1 } }));
  return i + 1;
}

function bindDeckChrome(pane, startPage) {
  const iframe = pane.querySelector("iframe.deck-frame");
  const go = (delta) => {
    const cur = Number(pane.querySelector("#deck-page")?.value) || 1;
    deckGo(pane, cur + delta);
  };
  pane.querySelector("[data-deck=prev]")?.addEventListener("click", () => go(-1));
  pane.querySelector("[data-deck=next]")?.addEventListener("click", () => go(1));
  pane.querySelector("[data-deck=theater]")?.addEventListener("click", () => {
    pane.classList.toggle("theater");
  });
  const input = pane.querySelector("#deck-page");
  input?.addEventListener("change", (e) => deckGo(pane, e.target.value));
  input?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      deckGo(pane, e.target.value);
    }
  });
  if (!pane.dataset.deckMsg) {
    pane.dataset.deckMsg = "1";
    window.addEventListener("message", (e) => {
      const frame = pane.querySelector("iframe.deck-frame");
      if (!frame || e.source !== frame.contentWindow || e.data?.type !== "sd-page") return;
      const pageInput = pane.querySelector("#deck-page");
      if (pageInput) {
        pageInput.value = String(e.data.page);
        pageInput.max = String(e.data.total);
      }
      const total = pane.querySelector("#deck-total");
      if (total) total.textContent = String(e.data.total);
      pane.dispatchEvent(new CustomEvent("deck-page", { detail: { page: e.data.page } }));
    });
  }
  const arm = () => {
    injectSdGo(iframe);
    deckGo(pane, startPage);
  };
  if (iframe?.contentDocument?.readyState === "complete" && iframe.contentDocument.querySelector(".sd-slide")) arm();
  else iframe?.addEventListener("load", arm, { once: true });
}

async function showPreview(pane, p, runId, item) {
  if (!item) {
    setDecking(pane, false);
    pane.innerHTML = `<div class="empty">从左边目录选一项预览。</div>`;
    return;
  }
  if (item.kind !== "html") setDecking(pane, false);
  if (item.kind === "html") {
    const base = String(item.href || "").split("#")[0];
    const page = Number(item.page) || 1;
    const existing = pane.querySelector("iframe.deck-frame");
    if (existing && existing.dataset.deck === base) {
      const title = pane.querySelector(".preview-head h3");
      if (title) title.textContent = item.label;
      deckGo(pane, page);
      return;
    }
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
      const base = String(item.href || "").split("#")[0];
      const page = Number(item.page) || 1;
      const viz = item.viz || {};
      setDecking(pane, true);
      const vizNote =
        viz.drawn > 0
          ? badge("ok", `L3 ${viz.drawn} 已绘制`)
          : viz.planned > 0
            ? badge("warn", `L3 ${viz.planned} 已规划 · HTML 尚未画图`)
            : badge("", "无 L3");
      pane.innerHTML = `<div class="preview-head">
        <h3>${esc(item.label)}</h3>${vizNote}
        <span class="spacer"></span>
        <div class="deck-nav">
          <button type="button" class="btn ghost" data-deck="prev">←</button>
          <input id="deck-page" type="number" min="1" value="${page}" />
          <span class="mono muted">/ <span id="deck-total">…</span></span>
          <button type="button" class="btn ghost" data-deck="next">→</button>
        </div>
        <button type="button" class="btn ghost" data-deck="finder">大纲</button>
        <button type="button" class="btn ghost" data-deck="theater">铺满</button>
        <a class="btn ghost" href="${esc(base)}" target="_blank">整页打开</a>
        ${deckMetaHtml(item.stats, viz)}
        <input id="deck-q" class="search" type="search" placeholder="搜索页码 / 标题 / 图型…" />
      </div>
      <div id="deck-finder" class="deck-finder" hidden></div>
      <iframe class="preview-frame deck-frame" data-deck="${esc(base)}" src="${esc(`${base}#p=${page}`)}" title="deck"></iframe>`;
      bindDeckChrome(pane, page);
      bindDeckFinder(pane);
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
      <a class="btn ghost" href="/api/projects/${esc(p.id)}/slides.zip" ${pack?.slides ? "" : "hidden"}>下载幻灯片评审包</a>
      <button class="btn ghost" id="approve-pack" ${pack?.ready ? "" : "hidden"} ${p.page_pack_approved ? "disabled" : ""}>${p.page_pack_approved ? "文件包已批准" : "批准文件包"}</button>
      <button class="btn ghost" id="run-slides" ${pack?.ready && p.page_pack_approved ? "" : "disabled"}>下一步 · 开发幻灯片</button>
      <button class="btn danger ghost" id="del">Delete</button>
    </div>
    <div class="row" style="align-items:baseline">
      <h1 style="margin:0">${esc(p.name)}</h1>
      <button type="button" class="id-copy" data-copy="${esc(`${p.id} template=${p.template}`)}" title="复制导出 ID">${esc(p.id)}</button>
      <button type="button" class="id-copy" data-copy="${esc(p.template)}" title="复制模板 ID">${esc(p.template)}</button>
    </div>
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
          ${pack?.slides ? `<a class="btn ghost" href="/api/projects/${esc(p.id)}/slides.zip">幻灯片评审包</a>` : ""}
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
        <input class="search" id="dir-q" placeholder="${current === "slides" ? "大纲搜索：页码 / 标题 / 图型…" : "过滤目录…  /"}" />
        <div id="dir-count" class="dir-count">目录加载中…</div>
        <div id="dir" class="dir-list"><p class="muted">Loading…</p></div>
      </div>
      <div id="preview" class="studio-pane"><div class="empty">从左边目录选一项预览。</div></div>
    </div>
    <p id="err" style="color:var(--fail)"></p>
  `;

  bindCopyButtons(root);
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

  pane.addEventListener("deck-page", (e) => {
    const page = Number(e.detail?.page);
    const match = items.find((it) => it.kind === "html" && Number(it.page) === page && it.id !== "deck.html");
    if (match && match.id !== selectedId) selectItem(match.id, { preview: false });
  });

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
      if (e.key === "Escape" && pane.classList.contains("theater")) {
        pane.classList.remove("theater");
        e.preventDefault();
        return;
      }
      if (e.key === "/" && !typing) {
        e.preventDefault();
        const deckQ = pane.querySelector("#deck-q");
        (deckQ || qEl)?.focus();
        (deckQ || qEl)?.select();
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
      if (e.key === "S") {
        if (pack?.slides) location.href = `/api/projects/${p.id}/slides.zip`;
        return;
      }
      const leaves = walkVisibleLeaves(currentTree(), []);
      const deckPane = pane.classList.contains("decking") ? pane : null;
      if (deckPane && e.key === "t") {
        e.preventDefault();
        pane.classList.toggle("theater");
        return;
      }
      if (deckPane && (e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "PageUp" || e.key === "PageDown" || e.key === "Home" || e.key === "End" || e.key === " ")) {
        e.preventDefault();
        const cur = Number(deckPane.querySelector("#deck-page")?.value) || 1;
        const total = Number(deckPane.querySelector("#deck-total")?.textContent) || 1;
        if (e.key === "Home") deckGo(deckPane, 1);
        else if (e.key === "End") deckGo(deckPane, total);
        else deckGo(deckPane, cur + (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " " ? 1 : -1));
        return;
      }
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
    pane._deckNav = { items, selectItem, paintDir, qEl };
    const tree = buildTree(items);
    collapseDeep(tree, 1, 0);
    paintDir("");
    const firstLeaf =
      items.find((it) => it.kind === "html" && it.id !== "deck.html") || items.find((it) => it.kind !== "dir");
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
    const deckQ = pane.querySelector("#deck-q");
    if (deckQ && deckQ.value !== qEl.value) deckQ.value = qEl.value;
  });
  bindStudioKeys();
}
