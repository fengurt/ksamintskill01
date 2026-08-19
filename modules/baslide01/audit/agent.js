(function () {
  "use strict";

  const SKIP_HOST = /^(https?:)?\/\/(fonts\.googleapis|fonts\.gstatic|cdnjs\.cloudflare|unpkg\.com|cdn\.jsdelivr)/i;
  const SKIP_SCHEME = /^(data:|blob:|mailto:|javascript:)/i;

  const $ = (id) => document.getElementById(id);
  const out = $("out");

  function setKpi(id, value) {
    $(id).querySelector(".v").textContent = String(value);
  }

  function absUrl(href, base) {
    try { return new URL(href, base).href; } catch (e) { return null; }
  }

  async function ping(url) {
    try {
      const res = await fetch(url, { method: "GET", cache: "no-store" });
      return { ok: res.ok, status: res.status, url, body: res.ok ? await res.text() : "" };
    } catch (err) {
      return { ok: false, status: 0, url, body: "", error: String(err) };
    }
  }

  function collectRefs(html, pageUrl) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const refs = [];
    doc.querySelectorAll("script[src], img[src], source[src], image[href]").forEach((el) => {
      const raw = el.getAttribute("src") || el.getAttribute("href");
      if (!raw || SKIP_SCHEME.test(raw) || SKIP_HOST.test(raw)) return;
      const url = absUrl(raw, pageUrl);
      if (url) refs.push({ kind: el.tagName.toLowerCase(), raw, url });
    });
    doc.querySelectorAll("link[rel='stylesheet'][href]").forEach((el) => {
      const raw = el.getAttribute("href");
      if (!raw || SKIP_SCHEME.test(raw) || SKIP_HOST.test(raw)) return;
      const url = absUrl(raw, pageUrl);
      if (url) refs.push({ kind: "link", raw, url });
    });
    return { doc, refs };
  }

  function findingsFor(page, pinged, parsed) {
    const findings = [];
    const push = (level, code, text) => findings.push({ level, code, text });

    if (!pinged.ok) {
      push("fail", "HTTP", "页面无法打开（" + pinged.status + (pinged.error ? " " + pinged.error : "") + "）");
      return findings;
    }
    push("pass", "HTTP", "HTTP " + pinged.status);

    const title = (parsed.doc.querySelector("title") || {}).textContent || "";
    if (!title.trim()) push("warn", "TITLE", "缺少 <title>");
    else push("pass", "TITLE", title.trim());

    if (!parsed.doc.documentElement.getAttribute("lang")) {
      push("warn", "LANG", "html 未声明 lang");
    }

    const hasChrome = /baslide-chrome\.js/.test(pinged.body) || parsed.doc.getElementById("baslide-chrome");
    const homeLink = parsed.doc.querySelector('a[href="/"], a[href="/index.html"], a[href="#/"]');
    if (page.path === "/") {
      push("pass", "HOME", "首页自身");
    } else if (hasChrome || homeLink) {
      push("pass", "HOME", "可返回首页");
    } else {
      push("fail", "HOME", "没有返回首页的入口（需 首页 chrome 或 a[href=/]）");
    }

    const root =
      parsed.doc.querySelector("#deck") ||
      parsed.doc.querySelector(".slide") ||
      parsed.doc.querySelector("#app") ||
      parsed.doc.querySelector(".hero") ||
      parsed.doc.querySelector(".wrap");
    if (!root) push("warn", "ROOT", "未找到 #deck / .slide / #app 根节点");
    else push("pass", "ROOT", "根节点 " + (root.id ? "#" + root.id : "." + root.className.split(" ")[0]));

    const slides = parsed.doc.querySelectorAll(".slide");
    if (slides.length) push("pass", "SLIDES", slides.length + " 张 .slide");

    if (page.path.indexOf("/demos/TIANSIGHT") !== -1 || page.path.indexOf("/files (10)") !== -1) {
      const need = ["TIANSIGHT.registry.js", "TIANSIGHT.schema.js", "TIANSIGHT.viz.js", "TIANSIGHT.demo.js", "TIANSIGHT.app.js"];
      need.forEach((name) => {
        const hit = parsed.refs.some((r) => r.url.indexOf(name) !== -1);
        if (hit) push("pass", "JS", name);
        else push("fail", "JS", "缺少脚本 " + name);
      });
    }

    return findings;
  }

  async function auditPage(page) {
    const pageUrl = absUrl(page.path, location.origin);
    const pinged = await ping(pageUrl);
    if (!pinged.ok) {
      return { page, pinged, findings: findingsFor(page, pinged, { doc: document.implementation.createHTMLDocument(""), refs: [] }), broken: [] };
    }
    const parsed = collectRefs(pinged.body, pageUrl);
    const findings = findingsFor(page, pinged, parsed);
    const broken = [];
    for (const ref of parsed.refs) {
      if (ref.url.indexOf(location.origin) !== 0) continue;
      const r = await ping(ref.url);
      if (!r.ok) {
        broken.push(ref);
        findings.push({
          level: "fail",
          code: "ASSET",
          text: ref.kind + " 断链 " + ref.raw + " → " + r.status
        });
      }
    }
    if (!broken.length && parsed.refs.some((r) => r.url.indexOf(location.origin) === 0)) {
      findings.push({ level: "pass", code: "ASSET", text: "同源资源可解析" });
    }
    return { page, pinged, findings, broken };
  }

  function worst(findings) {
    if (findings.some((f) => f.level === "fail")) return "FAIL";
    if (findings.some((f) => f.level === "warn")) return "WARN";
    return "PASS";
  }

  function render(results) {
    out.innerHTML = "";
    let pass = 0, warn = 0, fail = 0;
    results.forEach((res) => {
      const grade = worst(res.findings);
      if (grade === "PASS") pass += 1;
      else if (grade === "WARN") warn += 1;
      else fail += 1;
      const card = document.createElement("article");
      card.className = "card";
      const h = document.createElement("h2");
      h.innerHTML = (res.page.id || res.page.path) +
        '<span class="status">' + grade + "</span>";
      card.appendChild(h);
      const meta = document.createElement("p");
      meta.className = "meta";
      meta.innerHTML = '<a href="' + res.page.path + '">' + res.page.path + "</a>";
      card.appendChild(meta);
      res.findings.forEach((f) => {
        const p = document.createElement("p");
        p.className = "find " + f.level;
        p.innerHTML = "<b>" + f.level.toUpperCase() + " " + f.code + "</b>" + f.text;
        card.appendChild(p);
      });
      out.appendChild(card);
    });
    setKpi("kPages", results.length);
    setKpi("kPass", pass);
    setKpi("kWarn", warn);
    setKpi("kFail", fail);
  }

  async function run() {
    $("runMeta").textContent = "审计中…";
    $("btnRun").disabled = true;
    try {
      const catRes = await ping(absUrl("/catalog.json", location.origin));
      if (!catRes.ok) throw new Error("无法读取 /catalog.json");
      const catalog = JSON.parse(catRes.body);
      const surfaces = catalog.surfaces || [];
      const results = [];
      for (const page of surfaces) {
        $("runMeta").textContent = "正在审计 " + page.path;
        results.push(await auditPage(page));
      }
      render(results);
      const fails = results.filter((r) => worst(r.findings) === "FAIL").length;
      $("runMeta").textContent = fails ? ("完成 · " + fails + " 页失败") : "完成 · 全部通过或仅警告";
    } catch (err) {
      $("runMeta").textContent = String(err);
    } finally {
      $("btnRun").disabled = false;
    }
  }

  $("btnRun").onclick = run;
  $("btnHome").onclick = () => { location.href = "/"; };
  if (new URLSearchParams(location.search).get("run") === "1") run();
})();
