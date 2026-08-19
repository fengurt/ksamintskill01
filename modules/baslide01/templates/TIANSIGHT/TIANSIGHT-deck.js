/* 侍天 TIANSIGHT v2.0 — present, print, font packs. Not part of the slide. */
(function () {
  "use strict";

  var PACKS = [
    { id: "TIANSIGHT", label: "Noto Serif SC", href: "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" },
    { id: "songti", label: "宋体", href: "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" },
    { id: "kaiti", label: "楷体", href: "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" },
    { id: "fangsong", label: "仿宋", href: "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" },
    { id: "lxgw", label: "霞鹜文楷", href: "https://fonts.googleapis.com/css2?family=LXGW+WenKai:wght@400;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" },
    { id: "xiaowei", label: "小薇", href: "https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei&family=IBM+Plex+Mono:wght@400;500;600&display=swap" },
    { id: "roboto-mono", label: "Roboto Mono", href: "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Roboto+Mono:wght@400;500;600&display=swap" }
  ];

  var params = new URLSearchParams(location.search);
  var exportMode = params.get("export") === "1";
  var printMode = params.get("print") === "1";
  if (exportMode) document.documentElement.classList.add("sd-export");
  if (printMode) document.documentElement.classList.add("sd-printing");

  var slides = [].slice.call(document.querySelectorAll(".sd-slide"));
  var i = 0;
  var hash = location.hash.match(/p=(\d+)/);
  if (hash) i = Math.max(0, Math.min(slides.length - 1, parseInt(hash[1], 10) - 1));

  function show(n) {
    if (!slides.length) return;
    i = (n + slides.length) % slides.length;
    slides.forEach(function (el, idx) { el.classList.toggle("on", idx === i); });
    var hint = document.getElementById("sd-nav-hint");
    if (hint) hint.querySelector("[data-idx]").textContent = (i + 1) + " / " + slides.length;
    if (slides.length > 1) history.replaceState(null, "", "#p=" + (i + 1));
    syncExplain();
  }

  function fit() {
    var deck = document.getElementById("deck");
    var stage = document.getElementById("sd-stage");
    if (!deck || !stage || printMode) return;
    if (window.matchMedia && window.matchMedia("print").matches) return;
    var w = 2880;
    var h = 1620;
    var stageW = stage.clientWidth;
    var stageH = stage.clientHeight;
    var vv = window.visualViewport;
    if (vv) {
      stageW = Math.min(stageW, vv.width);
      stageH = Math.min(stageH, vv.height);
    }
    if (stageW < 1 || stageH < 1) return;
    var s = Math.min(stageW / w, stageH / h);
    var x = (stageW - w * s) / 2;
    var y = (stageH - h * s) / 2;
    deck.style.transform = "translate(" + x + "px," + y + "px) scale(" + s + ")";
  }

  var explainHidden = true;
  try {
    if (localStorage.getItem("TIANSIGHT-explain") === "on") explainHidden = false;
  } catch (e) {}

  function currentRail() {
    var slide = slides[i];
    if (!slide) return null;
    return slide.querySelector(".sd-rail");
  }

  function setExplainHidden(next) {
    explainHidden = next;
    try { localStorage.setItem("TIANSIGHT-explain", next ? "off" : "on"); } catch (e) {}
    syncExplain();
  }

  function syncExplain() {
    var panel = document.getElementById("sd-explain");
    var restore = document.getElementById("sd-explain-restore");
    var body = document.getElementById("sd-explain-body");
    var rail = currentRail();
    var has = !!(rail && rail.querySelector(".sd-rail-card"));
    var showPanel = has && !explainHidden && !exportMode;
    document.documentElement.classList.toggle("sd-explain-has", has);
    document.documentElement.classList.toggle("sd-explain-on", showPanel);
    if (body) body.innerHTML = has ? rail.innerHTML : "";
    if (panel) panel.hidden = !showPanel;
    if (restore) restore.hidden = !has || !explainHidden || exportMode;
    fit();
  }

  function mountExplain() {
    if (exportMode) return;
    if (document.getElementById("sd-explain")) return;
    var panel = document.createElement("aside");
    panel.id = "sd-explain";
    panel.hidden = true;
    panel.setAttribute("aria-label", "数据出处 术语解释 结论解释");
    panel.innerHTML =
      "<div id='sd-explain-bar'><span>解释</span>" +
      "<button type='button' data-explain-hide>隐藏</button></div>" +
      "<div id='sd-explain-body' class='sd-rail'></div>";
    document.body.appendChild(panel);
    panel.addEventListener("click", function (ev) {
      if (ev.target.closest("[data-explain-hide]")) setExplainHidden(true);
    });
    var restore = document.createElement("button");
    restore.id = "sd-explain-restore";
    restore.type = "button";
    restore.hidden = true;
    restore.textContent = "解释 · 数据出处 / 术语 / 结论 / 置信度";
    restore.setAttribute("aria-label", "显示解释");
    restore.addEventListener("click", function () { setExplainHidden(false); });
    document.body.appendChild(restore);
  }

  function packById(id) {
    return PACKS.filter(function (p) { return p.id === id; })[0] || PACKS[0];
  }

  function applyFont(id, persist) {
    var pack = packById(id);
    document.documentElement.setAttribute("data-font-pack", pack.id);
    var link = document.getElementById("sd-font-link");
    if (link) link.href = pack.href;
    document.querySelectorAll(".sd-font-ui [data-pack]").forEach(function (btn) {
      btn.classList.toggle("on", btn.getAttribute("data-pack") === pack.id);
    });
    if (persist !== false) {
      try { localStorage.setItem("TIANSIGHT-font-pack", pack.id); } catch (e) {}
    }
  }

  function cycleFont() {
    var cur = document.documentElement.getAttribute("data-font-pack") || "TIANSIGHT";
    var idx = PACKS.findIndex(function (p) { return p.id === cur; });
    applyFont(PACKS[(idx + 1) % PACKS.length].id);
  }

  function mountUi() {
    if (exportMode) return;
    if (document.querySelector(".sd-font-ui")) return;
    var ui = document.createElement("div");
    ui.className = "sd-font-ui";
    ui.innerHTML = "<span>FONT</span>" + PACKS.map(function (p) {
      return "<button type='button' data-pack='" + p.id + "'>" + p.label + "</button>";
    }).join("") + "<button type='button' data-print='1'>PDF / 打印</button>";
    document.body.appendChild(ui);
    ui.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button");
      if (!btn) return;
      if (btn.getAttribute("data-print")) {
        window.print();
        return;
      }
      var id = btn.getAttribute("data-pack");
      if (id) applyFont(id);
    });
    if (slides.length) {
      var hint = document.createElement("div");
      hint.className = "sd-nav-hint";
      hint.id = "sd-nav-hint";
      hint.innerHTML = "<span data-idx>1 / " + slides.length + "</span><span>← →</span><span>E 解释</span><span>F 字体</span><span>P 打印</span>";
      document.body.appendChild(hint);
    }
  }

  document.documentElement.classList.add("sd-present");
  mountUi();
  mountExplain();

  var stored = null;
  try { stored = localStorage.getItem("TIANSIGHT-font-pack"); } catch (e) {}
  applyFont(params.get("font") || stored || "TIANSIGHT", false);

  if (printMode) {
    slides.forEach(function (el) { el.classList.add("on"); });
    var printDeck = document.getElementById("deck");
    if (printDeck) printDeck.style.transform = "none";
  } else {
    if (slides.length) show(i);
    fit();
  }
  window.addEventListener("resize", fit);
  window.addEventListener("load", fit);
  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", fit);
    window.visualViewport.addEventListener("scroll", fit);
  }
  if (window.ResizeObserver) {
    var stageEl = document.getElementById("sd-stage");
    if (stageEl) new ResizeObserver(fit).observe(stageEl);
  }
  window.addEventListener("beforeprint", function () {
    document.documentElement.classList.add("sd-printing");
    slides.forEach(function (el) { el.classList.add("on"); });
    var deck = document.getElementById("deck");
    if (deck) deck.style.transform = "none";
  });
  window.addEventListener("afterprint", function () {
    if (printMode) return;
    document.documentElement.classList.remove("sd-printing");
    show(i);
    fit();
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var t = ev.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
    if (ev.key === "ArrowRight" || ev.key === " " || ev.key === "PageDown") { ev.preventDefault(); show(i + 1); }
    else if (ev.key === "ArrowLeft" || ev.key === "PageUp") { ev.preventDefault(); show(i - 1); }
    else if (ev.key === "Home") { ev.preventDefault(); show(0); }
    else if (ev.key === "End") { ev.preventDefault(); show(slides.length - 1); }
    else if (ev.key === "f" || ev.key === "F") { ev.preventDefault(); cycleFont(); }
    else if (ev.key === "e" || ev.key === "E") { ev.preventDefault(); if (document.documentElement.classList.contains("sd-explain-has")) setExplainHidden(!explainHidden); }
    else if (ev.key === "p" || ev.key === "P") { ev.preventDefault(); window.print(); }
  });
})();
