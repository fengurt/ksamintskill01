(function () {
  "use strict";
  if (window.__BASLIDE_CHROME__) return;
  window.__BASLIDE_CHROME__ = true;

  const params = new URLSearchParams(location.search);
  const exportMode = params.get("export") === "1" || params.get("chrome") === "0";
  let printLock = false;

  const path = (location.pathname || "/").replace(/index\.html$/i, "") || "/";
  const isHome = path === "/";
  const isTypes = path === "/types" || path === "/types/";
  const isAudit = path === "/audit" || path === "/audit/";
  const isDecks = path === "/decks" || path === "/decks/" || path.indexOf("/decks/") === 0;
  const isDeck = !!(document.getElementById("deck") || document.querySelector("section.slide"));
  const isStoneData = /\/decks\/stone-(briefing|roadmap|dossier)\/data\.html$/.test(path);
  const stoneDeckId = ({
    "/decks/stone-briefing/presentation.html": "D03.1",
    "/decks/stone-briefing/html-v1.html": "D03.2",
    "/decks/stone-roadmap/presentation.html": "D04",
    "/decks/stone-dossier/presentation.html": "D05"
  })[path] || "";
  const showStoneData = isStoneData || !!stoneDeckId || path === "/decks/stone-briefing/";
  function stoneDataPage() {
    if (path.indexOf("/decks/stone-roadmap/") === 0) return "/decks/stone-roadmap/data.html";
    if (path.indexOf("/decks/stone-dossier/") === 0) return "/decks/stone-dossier/data.html";
    return "/decks/stone-briefing/data.html";
  }

  if (isDeck) document.documentElement.classList.add("baslide-deck");
  function markDoc() {
    if (!isDeck && document.body) document.body.classList.add("baslide-doc");
  }
  markDoc();
  if (!document.body) document.addEventListener("DOMContentLoaded", markDoc);

  function isExporting() {
    return exportMode || printLock;
  }

  const stored = localStorage.getItem("baslideChrome");
  let hidden = exportMode || stored === "off";

  const bar = document.createElement("nav");
  bar.id = "baslide-chrome";
  bar.setAttribute("aria-label", "Baslide01 顶栏");
  bar.innerHTML =
    '<div class="links">' +
      '<a href="/" ' + (isHome ? 'aria-current="page"' : "") + ">首页</a>" +
      '<a href="/decks/" ' + (isDecks ? 'aria-current="page"' : "") + ">编号</a>" +
      '<a href="/types/" ' + (isTypes ? 'aria-current="page"' : "") + ">类型</a>" +
      '<a href="/audit/" ' + (isAudit ? 'aria-current="page"' : "") + ">审计</a>" +
      (showStoneData
        ? '<a id="baslide-chrome-data" href="' + stoneDataPage() + '" ' +
          (isStoneData ? 'aria-current="page"' : "") + ">库</a>" +
          '<a id="baslide-chrome-formula" hidden href="' + stoneDataPage() + '"></a>'
        : "") +
    "</div>" +
    '<span class="hint">H 隐藏 · 导出自动关</span>' +
    '<button type="button" id="baslide-chrome-hide">隐藏</button>';

  const restore = document.createElement("button");
  restore.id = "baslide-chrome-restore";
  restore.type = "button";
  restore.hidden = true;
  restore.textContent = "顶栏";
  restore.setAttribute("aria-label", "显示顶栏");

  function apply() {
    const exporting = isExporting();
    const off = hidden || exporting;
    document.documentElement.classList.toggle("baslide-chrome-off", off);
    document.documentElement.classList.toggle("baslide-chrome-on", !off);
    document.documentElement.classList.toggle("baslide-export", exporting);
    bar.hidden = off;
    restore.hidden = !hidden || exporting;
  }

  function setHidden(next) {
    hidden = next;
    if (!exportMode) localStorage.setItem("baslideChrome", hidden ? "off" : "on");
    apply();
  }

  bar.querySelector("#baslide-chrome-hide").addEventListener("click", function () { setHidden(true); });
  restore.addEventListener("click", function () { setHidden(false); });

  addEventListener("keydown", function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key !== "h" && e.key !== "H") return;
    const tag = (e.target && e.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || (e.target && e.target.isContentEditable)) return;
    e.preventDefault();
    setHidden(!hidden);
  });

  addEventListener("beforeprint", function () {
    printLock = true;
    apply();
  });
  addEventListener("afterprint", function () {
    printLock = false;
    apply();
  });

  document.documentElement.appendChild(bar);
  document.documentElement.appendChild(restore);
  apply();

  function pageFromHash() {
    const match = String(location.hash || "").match(/p=(\d+)/i);
    return match ? match[1] : "";
  }

  function esc(text) {
    return String(text == null ? "" : text)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  }

  function currentLink() {
    const rows = window.__BASLIDE_PAGE_LINKS__ || [];
    const page = pageFromHash() || "1";
    return rows.find(function (row) {
      return row.deck_id === stoneDeckId && String(row.page) === String(page);
    }) || null;
  }

  function dataHref(formulaId) {
    let href = stoneDataPage();
    if (stoneDeckId) href += "?deck=" + encodeURIComponent(stoneDeckId);
    const page = pageFromHash();
    if (page) href += (href.indexOf("?") >= 0 ? "&" : "?") + "p=" + page;
    if (formulaId) href += "#" + formulaId;
    return href;
  }

  function injectExplainFormula() {
    const body = document.getElementById("sd-explain-body");
    if (!body || !stoneDeckId) return;
    const old = body.querySelector("[data-formula-card]");
    if (old) old.remove();
    const hit = currentLink();
    const formulas = window.__BASLIDE_FORMULAS__ || [];
    const meta = hit && hit.formula_id
      ? formulas.find(function (row) { return row.id === hit.formula_id; })
      : null;
    const card = document.createElement("div");
    card.className = "sd-rail-card";
    card.setAttribute("data-formula-card", "1");
    if (meta) {
      card.innerHTML =
        "<div class='head'><span>库公式 · FORMULA</span><span class='sd-live live ready'>" +
        esc(meta.id) + "</span></div>" +
        "<div class='body'><div class='term'><b>" + esc(meta.id) + " · " + esc(meta.name) +
        "</b><br><span>" + esc(meta.expr) + " = " + esc(meta.value) + " " + esc(meta.unit || "") +
        "</span></div></div>" +
        "<div class='foot'><a href='" + dataHref(meta.id) + "'>打开本稿库</a></div>";
    } else {
      card.innerHTML =
        "<div class='head'><span>库公式 · FORMULA</span><span class='sd-live live degraded'>未挂接</span></div>" +
        "<div class='body'>本页无公式。封面 / 目录 / 章扉 / 纯论述不入库。</div>" +
        "<div class='foot'><a href='" + dataHref("") + "'>打开本稿库</a></div>";
    }
    body.insertBefore(card, body.firstChild);
  }

  function watchExplain() {
    const body = document.getElementById("sd-explain-body");
    if (!body || body.getAttribute("data-baslide-formula") === "1") return;
    body.setAttribute("data-baslide-formula", "1");
    new MutationObserver(function () {
      if (!body.querySelector("[data-formula-card]")) injectExplainFormula();
    }).observe(body, { childList: true });
    injectExplainFormula();
  }

  function syncStoneData() {
    const dataLink = bar.querySelector("#baslide-chrome-data");
    if (!dataLink) return;
    const hit = currentLink();
    const href = dataHref(hit && hit.formula_id);
    const chip = bar.querySelector("#baslide-chrome-formula");
    if (chip) {
      if (hit && hit.formula_id) {
        chip.hidden = false;
        chip.textContent = hit.formula_id;
        chip.href = href;
      } else {
        chip.hidden = true;
      }
    }
    dataLink.href = href;
    injectExplainFormula();
  }

  if (stoneDeckId) {
    Promise.all([
      fetch("/decks/stone-briefing/data/page-links.json").then(function (res) { return res.json(); }),
      fetch("/decks/stone-briefing/data/formulas-index.json").then(function (res) { return res.json(); })
    ]).then(function (pair) {
      window.__BASLIDE_PAGE_LINKS__ = pair[0];
      window.__BASLIDE_FORMULAS__ = pair[1];
      watchExplain();
      syncStoneData();
    }).catch(function () {});
    addEventListener("hashchange", syncStoneData);
    syncStoneData();
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", watchExplain);
    } else {
      watchExplain();
    }
  }
})();
