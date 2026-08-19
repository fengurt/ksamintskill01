(function (w) {
  "use strict";

  const INNER = {
    cover: "<b></b><em></em><s></s><u><i></i><i></i><i></i></u>",
    chapter: "<b></b><em></em><s></s>",
    statement: "<em></em><s></s>",
    quote: "<b>“</b><em></em><s></s>",
    question: "<b>?</b><em></em>",
    kpi: "<i></i><i></i><i></i><i></i><i></i><i></i>",
    chart: "<s></s><div class='bars'><i></i><i></i><i></i><i></i><i></i></div><em></em>",
    "chart-table": "<div class='bars'><i></i><i></i><i></i></div><u><i></i><i></i><i></i><i></i></u>",
    matrix: new Array(24).fill("<i></i>").join(""),
    roster: "<b></b><i></i><i></i><i></i><i></i><i></i>",
    compare: "<i></i><b></b><i></i>",
    timeline: "<i class='on'></i><s></s><i></i><s></s><i></i><s></s><i></i><s></s><i></i>",
    diagram: "<div class='nodes'><i></i><i></i><i></i></div>",
    "text-image": "<u><em></em><i></i><i></i><i></i></u><b></b>",
    "image-grid": "<i></i><i></i><i></i><i></i>",
    "image-hero": "<em></em>",
    verdict: "<i></i><i></i><i></i><i></i>"
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function previewHref(typeId, skin) {
    const q = new URLSearchParams({ type: typeId });
    if (skin) q.set("skin", skin);
    return "/preview/?" + q.toString();
  }

  function templateHref(href) {
    try {
      const u = new URL(href, location.origin);
      u.searchParams.set("chrome", "0");
      const out = u.pathname + u.search;
      // #region agent log
      fetch('http://127.0.0.1:7413/ingest/823441ad-59f6-4b3e-a911-72d56e2cb3ec',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'1a3c9c'},body:JSON.stringify({sessionId:'1a3c9c',runId:'pre-fix',hypothesisId:'H1',location:'baslide-catalog.js:templateHref',message:'template href built',data:{href:href,out:out,slide:u.searchParams.get('slide'),export:u.searchParams.get('export'),chrome:u.searchParams.get('chrome')},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      return out;
    } catch (e) {
      // #region agent log
      fetch('http://127.0.0.1:7413/ingest/823441ad-59f6-4b3e-a911-72d56e2cb3ec',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'1a3c9c'},body:JSON.stringify({sessionId:'1a3c9c',runId:'pre-fix',hypothesisId:'H1',location:'baslide-catalog.js:templateHref',message:'template href failed',data:{href:href,error:String(e)},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      return href;
    }
  }

  function thumbHTML(type, opts) {
    opts = opts || {};
    const href = opts.href || previewHref(type.id, opts.skin);
    const inner = INNER[type.id] || "<em></em>";
    // #region agent log
    if (!INNER[type.id]) fetch('http://127.0.0.1:7413/ingest/823441ad-59f6-4b3e-a911-72d56e2cb3ec',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'1a3c9c'},body:JSON.stringify({sessionId:'1a3c9c',runId:'pre-fix',hypothesisId:'H4',location:'baslide-catalog.js:thumbHTML',message:'missing thumb inner',data:{typeId:type && type.id},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    const capText = opts.caption === false ? "" : (typeof opts.caption === "string" ? opts.caption : type.id);
    const cap = capText ? "<span class='cap'>" + esc(capText) + "</span>" : "";
    return "<a class='thumb' data-thumb='" + esc(type.id) + "' href='" + esc(href) + "' aria-label='预览 " + esc(type.label) + "'>" + inner + cap + "</a>";
  }

  function skinLinks(type, skinsMeta, mode) {
    return Object.entries(type.skins || {}).map(function (entry) {
      const key = entry[0];
      const spec = entry[1];
      const label = (skinsMeta[key] && skinsMeta[key].label) || key;
      const href = mode === "template" ? spec.href : previewHref(type.id, key);
      return "<a href='" + esc(href) + "'>" + esc(label) + "</a>";
    }).join("");
  }

  function firstSkin(type) {
    return Object.keys(type.skins || {})[0] || "";
  }

  w.BaslideCatalog = {
    previewHref: previewHref,
    templateHref: templateHref,
    thumbHTML: thumbHTML,
    skinLinks: skinLinks,
    firstSkin: firstSkin
  };
})(window);
