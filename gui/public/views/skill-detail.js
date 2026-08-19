import { api, badge, copyText, esc, fmtTime } from "./util.js";

const COLOR_KEYS = ["surface", "ink", "muted", "grid", "accent", "positive", "negative", "warning"];
const EVIDENCE_TEMPLATES = new Set(["kpi", "roster", "chart", "chart-table", "matrix", "compare", "verdict"]);

function showcaseAssetUrl(kind, id, file) {
  return "/api/skills/showcase/" + encodeURIComponent(kind) + "/" + encodeURIComponent(id) + "?file=" + encodeURIComponent(file);
}

function treeHtml(nodes, depth = 0) {
  return (nodes || [])
    .map((node) => {
      const offset = depth * 12;
      if (node.type === "dir") {
        return '<div style="margin-left:' + offset + 'px">dir / ' + esc(node.name) + treeHtml(node.children || [], depth + 1) + "</div>";
      }
      return '<div style="margin-left:' + offset + 'px">' + esc(node.name) + ' <span class="muted">' + node.size + "b</span></div>";
    })
    .join("");
}

function themeCss(tokens) {
  const fontBody = String(tokens.fontBody || "sans-serif").replace(/[{};<>\r\n]/g, "").slice(0, 180);
  const fontNumber = String(tokens.fontNumber || "monospace").replace(/[{};<>\r\n]/g, "").slice(0, 180);
  return (
    ":root{" +
    "--gf-surface:" + tokens.surface + ";" +
    "--gf-ink:" + tokens.ink + ";" +
    "--gf-muted:" + tokens.muted + ";" +
    "--gf-grid:" + tokens.grid + ";" +
    "--gf-accent:" + tokens.accent + ";" +
    "--gf-positive:" + tokens.positive + ";" +
    "--gf-negative:" + tokens.negative + ";" +
    "--gf-warning:" + tokens.warning + ";" +
    "--gf-font-body:" + fontBody + ";" +
    "--gf-font-number:" + fontNumber + ";}"
  );
}

export function sandboxDocument(html, css = "", logoDataUrl = "", logoMode = "full", controls = {}) {
  const csp = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; font-src data:; connect-src \'none\'; form-action \'none\'; base-uri \'none\'; navigate-to \'none\'">';
  const style = "<style>" + css + "</style>";
  let out = String(html || "").replace(/<meta\s+[^>]*http-equiv=["']?refresh["']?[^>]*>/gi, "").replace(/<base\s+[^>]*>/gi, "");
  if (out.includes("<head>")) out = out.replace("<head>", "<head>" + csp).replace("</head>", style + "</head>");
  else out = "<!doctype html><html><head>" + csp + style + "</head><body>" + out + "</body></html>";
  if (logoDataUrl && logoMode !== "none") {
    const logo = '<img class="gf-live-logo" alt="Brand logo" src="' + esc(logoDataUrl) + '">';
    out = out.replace(/(<section class="slide"[^>]*>)/g, "$1" + logo);
    const width = logoMode === "compact" ? "7%" : "12%";
    out = out.replace("</head>", "<style>.gf-live-logo{position:absolute;right:5%;bottom:4%;z-index:2;max-width:" + width + ";max-height:7%;object-fit:contain}</style></head>");
  }
  if (controls.template) {
    const packPadding = controls.pack === "air" ? "7%" : controls.pack === "tight" ? "4.5%" : "6%";
    const columns = controls.layout === "full" || controls.layout === "table-full" ? "1fr" : controls.layout === "split-3" ? "repeat(3,1fr)" : "minmax(0,1fr) minmax(0,1fr)";
    const state = [controls.template, controls.layout, controls.pack, controls.visualization].filter(Boolean).map(esc).join(" · ");
    out = out.replace(/<div class="recipe">([\s\S]*?)<span>([^<]+)<\/span><\/div>/g, (_, art, name) => '<div class="recipe" data-viz="' + esc(name) + '">' + art + "<span>" + esc(name) + "</span></div>");
    out = out.replace("<body>", '<body data-gf-layout="' + esc(controls.layout || "full") + '"><div class="gf-control-state">' + state + "</div>");
    out = out.replace("</head>", "<style>.gf-control-state{position:fixed;z-index:20;top:8px;right:12px;padding:6px 9px;background:var(--gf-ink);color:var(--gf-surface);font:11px var(--gf-font-number)}.slide{padding:" + packPadding + "}.contract{grid-template-columns:" + columns + "}.recipe{opacity:.22}.recipe[data-viz=\"" + esc(controls.visualization || "") + "\"]{opacity:1;outline:3px solid var(--gf-accent);outline-offset:3px}</style></head>");
  }
  return out;
}

export function parseLabMarkdown(text) {
  const raw = String(text || "");
  const lines = raw.split(/\r?\n/);
  const title = (lines.find((line) => /^#\s+/.test(line)) || "").replace(/^#\s+/, "").trim();
  const quote = lines.filter((line) => /^>\s?/.test(line)).map((line) => line.replace(/^>\s?/, "").trim()).join(" ");
  const sourceLine = lines.find((line) => /^source\s*:/i.test(line.trim())) || "";
  const source = sourceLine.replace(/^source\s*:\s*/i, "").trim();
  const bullets = lines.filter((line) => /^\s*[-*]\s+/.test(line)).map((line) => line.replace(/^\s*[-*]\s+/, "").trim());
  const headings = lines.filter((line) => /^##\s+/.test(line)).map((line) => line.replace(/^##\s+/, "").trim());
  const pipeLines = lines.filter((line) => line.trim().startsWith("|") && line.trim().endsWith("|"));
  const separator = pipeLines.findIndex((line) => /^\|?[\s:|-]+\|$/.test(line.trim()));
  let table = [];
  if (separator > 0) {
    const split = (line) => line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
    const headers = split(pipeLines[0]);
    table = pipeLines.slice(separator + 1).map((line) => {
      const cells = split(line);
      return headers.map((header, index) => ({ header, value: cells[index] || "" }));
    });
  }
  const paragraphs = lines
    .map((line) => line.trim())
    .filter((line) =>
      line &&
      !/^#{1,6}\s/.test(line) &&
      !/^>\s?/.test(line) &&
      !/^[-*]\s+/.test(line) &&
      !/^source\s*:/i.test(line) &&
      !(line.startsWith("|") && line.endsWith("|"))
    );
  return { raw, title, quote, source, bullets, headings, table, paragraphs, malformedTable: pipeLines.length > 0 && separator < 1 };
}

export function labWarnings(parsed, template) {
  const warnings = [];
  if (!parsed.raw.trim()) warnings.push("Add Markdown to render a layout smoke test.");
  if (!parsed.title) warnings.push("Add one level-one heading for the slide title.");
  if (EVIDENCE_TEMPLATES.has(template) && !parsed.source) warnings.push("Evidence and decision pages should include a Source: line.");
  if (["roster", "chart-table", "matrix", "compare"].includes(template) && !parsed.table.length) {
    warnings.push("This template works best with a valid Markdown table.");
  }
  if (parsed.malformedTable) warnings.push("The Markdown table needs a separator row.");
  if (["chart", "chart-table", "kpi"].includes(template)) {
    const numeric = parsed.bullets.some((item) => /-?\d/.test(item)) || parsed.table.some((row) => row.some((cell) => /-?\d/.test(cell.value)));
    if (!numeric) warnings.push("Add numeric evidence for this template.");
  }
  if (parsed.raw.length > 2200 || parsed.bullets.length > 8 || parsed.table.length > 8) {
    warnings.push("Content may overflow. Split it into another page instead of shrinking type.");
  }
  return warnings;
}

function tableMarkup(parsed, limit = 8) {
  if (!parsed.table.length) return '<p class="empty-copy">Add a Markdown table to preview structured rows.</p>';
  const headers = parsed.table[0].map((cell) => cell.header);
  return (
    "<table><thead><tr>" +
    headers.map((header) => "<th>" + esc(header) + "</th>").join("") +
    "</tr></thead><tbody>" +
    parsed.table.slice(0, limit).map((row) => "<tr>" + row.map((cell) => "<td>" + esc(cell.value) + "</td>").join("") + "</tr>").join("") +
    "</tbody></table>"
  );
}

function listMarkup(items, ordered = false) {
  const tag = ordered ? "ol" : "ul";
  const rows = items.length ? items : ["Add list items to the Markdown sample."];
  return "<" + tag + ">" + rows.slice(0, 8).map((item) => "<li>" + esc(item) + "</li>").join("") + "</" + tag + ">";
}

function metricMarkup(parsed) {
  const metrics = parsed.bullets
    .map((item) => item.match(/^(-?\d+(?:\.\d+)?)\s*(.*)$/))
    .filter(Boolean)
    .slice(0, 6);
  if (!metrics.length) return '<p class="empty-copy">Start list items with numbers to render KPIs.</p>';
  return '<div class="metrics">' + metrics.map((match) => '<article><strong>' + esc(match[1]) + '</strong><span>' + esc(match[2] || "measure") + "</span></article>").join("") + "</div>";
}

function chartMarkup(parsed, withTable) {
  let rows = parsed.bullets
    .map((item) => item.match(/^(-?\d+(?:\.\d+)?)\s*(.*)$/))
    .filter(Boolean)
    .map((match) => ({ label: match[2] || "Measure", value: Number(match[1]) }));
  if (!rows.length && parsed.table.length) {
    rows = parsed.table.map((row) => {
      const numeric = row.find((cell) => /^-?\d+(?:\.\d+)?$/.test(cell.value));
      return { label: row[0]?.value || "Row", value: Number(numeric?.value || 0) };
    });
  }
  rows = rows.slice(0, 6);
  const max = Math.max(1, ...rows.map((row) => Math.abs(row.value)));
  const bars = rows.length
    ? '<div class="bars">' + rows.map((row) => '<div><span>' + esc(row.label) + '</span><i style="width:' + Math.max(4, Math.round(Math.abs(row.value) / max * 100)) + '%"></i><b>' + esc(row.value) + "</b></div>").join("") + "</div>"
    : '<p class="empty-copy">Add numeric bullets or a table to render bars.</p>';
  return withTable ? '<div class="chart-table">' + bars + tableMarkup(parsed) + "</div>" : bars;
}

function labSlideBody(parsed, template) {
  const title = esc(parsed.title || "Untitled page");
  const paragraph = esc(parsed.paragraphs[0] || "");
  const takeaway = esc(parsed.quote || parsed.paragraphs[0] || "Add a takeaway or supporting sentence.");
  if (template === "cover") return '<div class="accent-rule"></div><h1>' + title + "</h1><p class=\"subtitle\">" + paragraph + "</p>";
  if (template === "toc") return "<h2>" + title + "</h2>" + listMarkup(parsed.headings.length ? parsed.headings : parsed.bullets, true);
  if (template === "chapter") return '<div class="chapter"><span>Section</span><h1>' + title + "</h1><p>" + paragraph + "</p></div>";
  if (template === "readme") return "<h2>" + title + '</h2><div class="readme"><p>' + paragraph + "</p>" + listMarkup(parsed.bullets) + "</div>";
  if (template === "statement") return '<blockquote>"' + takeaway + '"</blockquote><h3>' + title + "</h3>";
  if (template === "verdict") return '<div class="verdict"><div><h2>' + title + "</h2><p>" + takeaway + '</p></div><aside><strong>NEXT ACTION</strong><p>' + esc(parsed.bullets[0] || "State the next action.") + "</p></aside></div>";
  if (template === "kpi") return "<h2>" + title + "</h2>" + metricMarkup(parsed);
  if (template === "roster") return "<h2>" + title + "</h2>" + (parsed.table.length ? tableMarkup(parsed) : listMarkup(parsed.bullets));
  if (template === "chart") return "<h2>" + title + "</h2>" + chartMarkup(parsed, false);
  if (template === "chart-table") return "<h2>" + title + "</h2>" + chartMarkup(parsed, true);
  if (template === "matrix") return "<h2>" + title + '</h2><div class="matrix">' + tableMarkup(parsed, 6) + "</div>";
  if (template === "compare") return "<h2>" + title + '</h2><div class="compare">' + tableMarkup(parsed, 5) + "</div>";
  return "<h2>" + title + "</h2>";
}

export function labDocument(parsed, template, tokens, logoDataUrl = "") {
  const logo = logoDataUrl ? '<img class="logo" alt="Brand logo" src="' + esc(logoDataUrl) + '">' : "";
  const source = parsed.source ? '<p class="source">Source: ' + esc(parsed.source) + "</p>" : "";
  const css = [
    themeCss(tokens),
    "*{box-sizing:border-box}",
    "html,body{margin:0;min-height:100%;background:#d9ddd8}",
    "body{padding:18px;color:var(--gf-ink);font-family:var(--gf-font-body)}",
    ".slide{position:relative;aspect-ratio:16/9;overflow:hidden;background:var(--gf-surface);padding:6.5%;box-shadow:0 12px 36px rgba(23,32,29,.15)}",
    "h1,h2,h3,p{margin:0}h1{max-width:12ch;font-size:7vw;line-height:.95;letter-spacing:-.055em}h2{max-width:17ch;font-size:4.5vw;line-height:1;letter-spacing:-.045em}",
    ".subtitle{max-width:48ch;margin-top:4%;color:var(--gf-muted);font-size:2vw;line-height:1.4}.accent-rule{width:14%;height:8px;margin-bottom:5%;background:var(--gf-accent)}",
    "ul,ol{display:grid;gap:1.1vw;margin:4% 0 0;padding-left:1.6em;font-size:1.8vw}blockquote{max-width:15ch;margin:8% 0 3%;font-size:4.8vw;line-height:1.05;letter-spacing:-.04em}",
    ".chapter{display:grid;align-content:end;height:100%}.chapter span{color:var(--gf-accent);font:600 1.2vw var(--gf-font-number)}.chapter p,.readme p{max-width:45ch;margin-top:3%;color:var(--gf-muted);font-size:1.6vw}",
    ".metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4%;margin-top:6%}.metrics article{padding-top:4%;border-top:2px solid var(--gf-ink)}.metrics strong{display:block;color:var(--gf-accent);font:600 6.5vw/.9 var(--gf-font-number)}.metrics span{display:block;margin-top:8%;color:var(--gf-muted);font-size:1.35vw}",
    "table{width:100%;margin-top:4%;border-collapse:collapse;font-size:1.25vw}th,td{padding:1.2vw .4vw;text-align:left;border-bottom:1px solid var(--gf-grid)}th{color:var(--gf-muted)}",
    ".bars{display:grid;gap:1.2vw;margin-top:5%}.bars>div{display:grid;grid-template-columns:8vw 1fr 3vw;gap:1vw;align-items:center;color:var(--gf-muted);font-size:1.2vw}.bars i{display:block;height:1.5vw;background:var(--gf-accent)}",
    ".chart-table{display:grid;grid-template-columns:1.1fr .9fr;gap:5%}.verdict{display:grid;grid-template-columns:1.35fr .65fr;gap:7%;align-items:end;height:100%}.verdict>div{padding-left:4%;border-left:8px solid var(--gf-accent)}.verdict>div p{margin-top:5%;color:var(--gf-muted);font-size:1.6vw}.verdict aside{padding:11%;background:var(--gf-ink);color:var(--gf-surface)}.verdict aside strong{font:600 1vw var(--gf-font-number)}.verdict aside p{margin-top:12%;font-size:1.5vw}",
    ".source{position:absolute;left:6.5%;right:6.5%;bottom:3.5%;padding-top:1%;border-top:1px solid var(--gf-grid);color:var(--gf-muted);font-size:1vw}.logo{position:absolute;right:5%;top:5%;max-width:13%;max-height:8%;object-fit:contain}.empty-copy{margin-top:5%;color:var(--gf-muted);font-size:1.6vw}",
  ].join("");
  return '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:"><style>' + css + "</style></head><body><section class=\"slide\">" + logo + labSlideBody(parsed, template) + source + "</section></body></html>";
}

function detailPanel(id, html, active = false) {
  return '<section class="skill-detail-panel" id="skill-panel-' + id + '" data-skill-panel="' + id + '"' + (active ? "" : " hidden") + ">" + html + "</section>";
}

function copyLocationsHtml(s) {
  if ((s.copies || []).length <= 1) return "";
  return '<h3>Copies</h3><ul>' + s.copies.map((copy) => '<li class="mono">' + esc(copy.path) + " / " + esc(copy.source || copy.sourceId || "") + "</li>").join("") + "</ul>";
}

function runtimeHtml(extras) {
  if (!extras.length) return "";
  return '<h3>ZIP runtime</h3><ul>' + extras.map((item) => '<li class="mono">' + esc(item.to) + ' <span class="muted">' + esc(item.why) + "</span></li>").join("") + "</ul>";
}

function overviewHtml(s) {
  const intro = s.showcase?.intro;
  const summary = intro?.summary || s.description;
  const highlights = intro?.highlights || [];
  const workflow = intro?.workflow || [];
  return [
    '<div class="skill-overview-grid">',
    '<div class="skill-intro">',
    "<h2>What it does</h2>",
    "<p>" + esc(summary) + "</p>",
    highlights.length ? '<div class="skill-highlight-list">' + highlights.map((item) => "<span>" + esc(item) + "</span>").join("") + "</div>" : "",
    "</div>",
    '<aside class="skill-facts">',
    '<div><span>Author</span><strong>' + esc(s.author || "not set") + "</strong></div>",
    '<div><span>Repository</span><strong>' + esc(s.repo || s.source || "not set") + "</strong></div>",
    '<div><span>Updated</span><strong>' + esc(s.updatedAt ? fmtTime(s.updatedAt) : "not set") + "</strong></div>",
    '<div><span>License</span><strong>' + esc(s.license || "not set") + "</strong></div>",
    "</aside>",
    "</div>",
    workflow.length
      ? '<div class="skill-workflow"><h2>Working loop</h2><ol>' + workflow.map((item) => "<li>" + esc(item) + "</li>").join("") + "</ol></div>"
      : '<div class="skill-workflow"><h2>Instructions</h2><pre class="skill-instructions">' + esc((s.body || "").trim()) + "</pre></div>",
  ].join("");
}

function filesHtml(s, extras) {
  return [
    '<div class="skill-files-grid">',
    '<div class="card skill-file-meta">',
    "<h3>Metadata</h3>",
    '<div class="mono">path: ' + esc(s.path) + "</div>",
    '<div class="mono">author: ' + esc(s.author || "not set") + "</div>",
    '<div class="mono">repo: ' + esc(s.repo || s.source || "not set") + "</div>",
    '<div class="mono">origin: ' + esc(s.origin || "not set") + (s.agent ? " / " + esc(s.agent) : "") + "</div>",
    '<div class="mono">version: ' + esc(s.version?.hash || s.version?.synced_commit || "not set") + (s.version?.dirty ? " " + badge("warn", "dirty") : "") + "</div>",
    s.showcaseError ? '<p class="inline-error">' + esc(s.showcaseError) + "</p>" : "",
    copyLocationsHtml(s),
    runtimeHtml(extras),
    "<h3>File tree</h3>",
    '<div class="mono skill-tree">' + treeHtml(s.tree || []) + "</div>",
    "</div>",
    '<div class="card"><h3>SKILL.md</h3><pre class="pre light skill-raw">' + esc(s.raw) + "</pre></div>",
    "</div>",
  ].join("");
}

async function fetchShowcaseAsset(kind, id, file) {
  if (!file) return null;
  return api(showcaseAssetUrl(kind, id, file));
}

function themeFields(theme) {
  const labels = {
    surface: "Surface",
    ink: "Ink",
    muted: "Muted",
    grid: "Grid",
    accent: "Accent",
    positive: "Positive",
    negative: "Negative",
    warning: "Warning",
  };
  return (
    '<div class="theme-color-grid">' +
    COLOR_KEYS.map((key) => '<label><span>' + labels[key] + '</span><input type="color" data-theme-token="' + key + '" value="' + esc(theme[key]) + '"></label>').join("") +
    "</div>" +
    '<div class="theme-font-grid">' +
    '<label><span>Body font stack</span><input type="text" data-theme-token="fontBody" value="' + esc(theme.fontBody) + '"></label>' +
    '<label><span>Number font stack</span><input type="text" data-theme-token="fontNumber" value="' + esc(theme.fontNumber) + '"></label>' +
    "</div>"
  );
}

function presetFields(controls, preset = {}) {
  if (!controls) return "";
  return '<div class="theme-font-grid">' + Object.entries(controls).map(([key, options]) =>
    '<label><span>' + esc(key) + '</span><select data-showcase-control="' + esc(key) + '">' +
    options.map((value) => '<option value="' + esc(value) + '"' + (preset[key] === value ? " selected" : "") + ">" + esc(value) + "</option>").join("") +
    "</select></label>"
  ).join("") + '</div><div class="row"><button class="btn" type="button" id="preset-save">Save preset</button><button class="btn ghost" type="button" id="preset-export">Export preset JSON</button><span id="preset-status" class="muted" aria-live="polite"></span></div>';
}

function subskillFormHtml() {
  return [
    '<form id="brand-subskill-form" class="brand-subskill-form">',
    "<h3>Create a brand sub-skill</h3>",
    "<p>Use the latest published guide from apuch.art, or another official first-party source. The generated ZIP never changes this repository.</p>",
    '<div class="brand-form-grid">',
    '<label><span>Brand name</span><input id="brand-name" required maxlength="80" placeholder="Brand name"></label>',
    '<label><span>Skill id</span><input id="brand-skill-id" required maxlength="64" pattern="[a-z0-9]+(?:-[a-z0-9]+)*-gf4p2slides" placeholder="brand-gf4p2slides"></label>',
    '<label class="wide"><span>Official brand source URL</span><input id="brand-source" type="url" required placeholder="https://apuch.art/..."></label>',
    '<label><span>Publication or version date</span><input id="brand-source-date" type="date"></label>',
    '<label><span>Logo, optional</span><input id="brand-logo" type="file" accept="image/png,image/jpeg,image/webp"></label>',
    "</div>",
    '<div class="row"><button class="btn" type="submit">Download ZIP</button><span id="brand-status" class="muted"></span></div>',
    "</form>",
  ].join("");
}

export async function renderRichSkillDetail(root, kind, id) {
  root.classList.remove("studio-page");
  root.innerHTML = '<p class="muted">Loading skill...</p>';
  const s = await api("/api/skills/" + encodeURIComponent(kind) + "/" + encodeURIComponent(id));
  const extras = s.runtime || [];
  const showcase = s.showcase;
  let apuch = { themes: [], credentialConfigured: false, syncedAt: null };
  if (s.name === "gf4p2slides" && showcase?.theme) {
    try {
      apuch = await api("/api/apuch/themes");
    } catch {
      // The generic GF editor still works without the optional Apuch cache.
    }
  }
  let preset = null;
  if (showcase?.controls) {
    try {
      preset = (await api("/api/skills/" + encodeURIComponent(kind) + "/" + encodeURIComponent(id) + "/showcase-preset")).preset;
    } catch {
      preset = null;
    }
  }
  const assetEntries = [];
  if (showcase?.demo?.html) assetEntries.push(["demo", showcase.demo.html]);
  if (showcase?.theme?.css) assetEntries.push(["themeCss", showcase.theme.css]);
  if (showcase?.lab?.defaultSample) assetEntries.push(["defaultSample", showcase.lab.defaultSample]);
  for (const [index, sample] of (showcase?.samples || []).entries()) assetEntries.push(["sample-" + index, sample.file]);
  const assets = {};
  await Promise.all(
    assetEntries.map(async ([key, file]) => {
      try {
        assets[key] = await fetchShowcaseAsset(kind, id, file);
      } catch (error) {
        assets[key] = { error: error.message, text: "" };
      }
    })
  );

  const tabs = [{ id: "overview", label: "Overview" }];
  if (showcase?.demo || showcase?.samples?.length || showcase?.theme) tabs.push({ id: "guideline", label: "Guideline" });
  if (showcase?.lab) tabs.push({ id: "test", label: "Test" });
  tabs.push({ id: "files", label: "Files" });

  const sampleButtons = (showcase?.samples || [])
    .map((sample, index) => '<button type="button" data-sample-index="' + index + '"' + (index === 0 ? ' class="on"' : "") + '><strong>' + esc(sample.title) + "</strong><span>" + esc(sample.description || sample.file) + "</span></button>")
    .join("");
  const firstSample = assets["sample-0"];
  const theme = { ...(showcase?.theme?.tokens || {}), ...(preset?.tokens || {}) };
  const initialMarkdown = assets.defaultSample?.text || "";
  const templateOptions = (showcase?.lab?.templates || []).map((name) => '<option value="' + esc(name) + '">' + esc(name) + "</option>").join("");
  const apuchButtons = (apuch.themes || []).map((item) =>
    '<button type="button" data-apuch-theme="' + esc(item.slug) + '" style="--theme-swatch:' + esc(item.tokens?.accent || "#0e6b5c") + '"><i aria-hidden="true"></i><span>' + esc(item.name) + "</span></button>"
  ).join("");
  const themeEditor = showcase?.theme
    ? '<details class="guideline-theme" id="guideline-theme"><summary><span><strong>Theme and brand</strong><small>Switch a saved Apuch theme or edit the semantic tokens.</small></span><span class="guideline-theme-state">' + (apuch.syncedAt ? "Apuch connected" : "GF default") + '</span></summary><div class="guideline-theme-body">' +
      (s.name === "gf4p2slides" ? '<div class="apuch-theme-toolbar"><div class="saved-theme-switcher" role="group" aria-label="Saved themes"><button type="button" class="on" data-apuch-theme="" style="--theme-swatch:' + esc(theme.accent) + '"><i aria-hidden="true"></i><span>GF default</span></button>' + apuchButtons + '</div><div class="row"><button type="button" class="btn ghost" id="apuch-sync">Refresh from Apuch</button><span id="apuch-status" class="muted" aria-live="polite">' + (apuch.credentialConfigured ? "Admin credential stored locally. Public brand read active." : "Public brand read active.") + "</span></div></div>" : "") +
      '<div class="theme-workbench"><form id="theme-form">' + presetFields(showcase.controls, preset || {}) + themeFields(theme) + '<label class="theme-logo-field"><span>Preview logo</span><input id="theme-logo" type="file" accept="image/png,image/jpeg,image/webp"></label><div class="row"><button type="button" class="btn ghost" id="theme-reset">Reset to GF</button><span id="theme-status" class="muted" aria-live="polite"></span></div></form><aside class="apuch-theme-meta" id="apuch-theme-meta"><strong>GF default theme</strong><p>Local semantic-token baseline. The preview above updates as you edit.</p></aside></div>' +
      (s.name === "gf4p2slides" ? subskillFormHtml() : "") +
      "</div></details>"
    : "";
  const guidelinePanel = showcase?.demo || showcase?.samples?.length || showcase?.theme
    ? detailPanel(
        "guideline",
        '<div class="skill-panel-head"><div><h2>Reference guideline</h2><p>Rendered output, source examples, and brand controls in one working view.</p></div></div>' +
          (showcase?.demo ? (assets.demo?.error ? '<p class="inline-error">' + esc(assets.demo.error) + "</p>" : '<iframe id="showcase-frame" class="skill-showcase-frame" sandbox title="Rendered slide demo"></iframe>') : "") +
          (showcase?.samples?.length ? '<section class="guideline-samples"><div class="skill-panel-head"><div><h3>Reference inputs</h3><p>Inspect the contract or seed a layout test.</p></div></div><div class="skill-samples"><nav aria-label="Samples">' + sampleButtons + '</nav><pre id="sample-preview" class="pre light">' + esc(firstSample?.text || firstSample?.error || "") + "</pre></div></section>" : "") +
          themeEditor
      )
    : "";
  const testPanel = showcase?.lab
    ? detailPanel(
        "test",
        '<div class="skill-panel-head"><div><h2>Markdown layout smoke test</h2><p>Select the communication job. This checks layout and required content; it does not run a model.</p></div><button type="button" class="btn ghost" id="copy-test-prompt">Copy agent prompt</button></div>' +
          '<div class="skill-lab"><div class="lab-editor"><label><span>Page template</span><select id="lab-template">' + templateOptions + '</select></label><label><span>Markdown</span><textarea id="lab-markdown" spellcheck="false">' + esc(initialMarkdown) + '</textarea></label><div id="lab-warnings" class="lab-warnings" aria-live="polite"></div></div><iframe id="lab-frame" class="skill-lab-frame" sandbox title="Markdown slide preview"></iframe></div>'
      )
    : "";

  root.innerHTML = [
    '<div class="skill-detail-actions"><a class="btn ghost" href="#/skills">Back to gallery</a><span class="spacer"></span>',
    '<button type="button" class="star ' + (s.starred ? "on" : "") + '" id="star-one" aria-label="' + (s.starred ? "Unstar " : "Star ") + esc(s.name) + '" aria-pressed="' + Boolean(s.starred) + '">★</button>',
    badge("", s.origin || s.kind),
    s.agent ? badge("", s.agent) : "",
    s.zip ? '<a class="btn" href="' + esc(s.zip) + '">Export</a>' : "",
    "</div>",
    '<header class="skill-detail-hero"><p class="skills-kicker">' + esc(s.author || s.origin || "skill") + '</p><h1>' + esc(s.name) + '</h1><p>' + esc(s.description) + '</p><div class="skill-detail-byline"><span>' + esc(s.repo || s.source || "") + "</span><span>" + esc(s.updatedAt ? fmtTime(s.updatedAt) : "not dated") + "</span></div></header>",
    '<div class="skill-detail-tabs" role="tablist" aria-label="Skill detail sections">',
    tabs.map((tab, index) => '<button type="button" role="tab" data-skill-tab="' + tab.id + '" aria-controls="skill-panel-' + tab.id + '" aria-selected="' + (index === 0) + '">' + tab.label + "</button>").join(""),
    "</div>",
    detailPanel("overview", overviewHtml(s), true),
    guidelinePanel,
    testPanel,
    detailPanel("files", filesHtml(s, extras)),
  ].join("");

  const selectTab = (name) => {
    root.querySelectorAll("[data-skill-tab]").forEach((button) => {
      const on = button.dataset.skillTab === name;
      button.setAttribute("aria-selected", String(on));
      button.tabIndex = on ? 0 : -1;
    });
    root.querySelectorAll("[data-skill-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.skillPanel !== name;
    });
  };
  root.querySelectorAll("[data-skill-tab]").forEach((button, index, buttons) => {
    button.addEventListener("click", () => selectTab(button.dataset.skillTab));
    button.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const next = buttons[(index + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length];
      selectTab(next.dataset.skillTab);
      next.focus();
    });
  });

  root.querySelector("#star-one")?.addEventListener("click", async () => {
    const out = await api("/api/skills/star", { method: "POST", body: { id: s.id || s.name } });
    const button = root.querySelector("#star-one");
    button.classList.toggle("on", out.starred);
    button.setAttribute("aria-pressed", String(out.starred));
    button.setAttribute("aria-label", (out.starred ? "Unstar " : "Star ") + s.name);
  });

  const demoHtml = assets.demo?.text || "";
  const baseThemeCss = assets.themeCss?.text || themeCss(theme);
  const showcaseFrame = root.querySelector("#showcase-frame");
  if (showcaseFrame) showcaseFrame.srcdoc = sandboxDocument(demoHtml, baseThemeCss);

  root.querySelectorAll("[data-sample-index]").forEach((button) => {
    button.addEventListener("click", () => {
      root.querySelectorAll("[data-sample-index]").forEach((item) => item.classList.toggle("on", item === button));
      const sample = assets["sample-" + button.dataset.sampleIndex];
      root.querySelector("#sample-preview").textContent = sample?.text || sample?.error || "";
    });
  });

  let logoDataUrl = "";
  const themeInputs = [...root.querySelectorAll("[data-theme-token]")];
  const currentTokens = () => Object.fromEntries(themeInputs.map((input) => [input.dataset.themeToken, input.value]));
  const currentPreset = () => ({
    ...Object.fromEntries([...root.querySelectorAll("[data-showcase-control]")].map((input) => [input.dataset.showcaseControl, input.value])),
    tokens: currentTokens(),
  });
  const paintTheme = () => {
    const controls = currentPreset();
    const logoMode = controls.logo || "full";
    const frame = root.querySelector("#showcase-frame");
    if (frame) frame.srcdoc = sandboxDocument(demoHtml, baseThemeCss + themeCss(currentTokens()), logoDataUrl, logoMode, controls);
    const labFrame = root.querySelector("#lab-frame");
    if (labFrame) {
      const parsed = parseLabMarkdown(root.querySelector("#lab-markdown")?.value || "");
      labFrame.srcdoc = labDocument(parsed, root.querySelector("#lab-template")?.value || "cover", currentTokens(), logoMode === "none" ? "" : logoDataUrl);
    }
  };
  const savedThemes = new Map((apuch.themes || []).map((item) => [item.slug, item]));
  const selectSavedTheme = (slug) => {
    const selected = savedThemes.get(slug);
    const tokens = selected?.tokens || theme;
    for (const input of themeInputs) if (tokens[input.dataset.themeToken]) input.value = tokens[input.dataset.themeToken];
    logoDataUrl = selected?.logoDataUrl || "";
    const upload = root.querySelector("#theme-logo");
    if (upload) upload.value = "";
    root.querySelectorAll("[data-apuch-theme]").forEach((button) => {
      const on = button.dataset.apuchTheme === (selected?.slug || "");
      button.classList.toggle("on", on);
      button.setAttribute("aria-pressed", String(on));
    });
    const meta = root.querySelector("#apuch-theme-meta");
    if (meta) {
      meta.innerHTML = selected
        ? "<strong>" + esc(selected.name) + "</strong><p>Official tokens and canonical raster logo from apuch.art.</p><a href=\"" + esc(selected.sourceUrl) + "\" target=\"_blank\" rel=\"noreferrer\">Open brand source</a>"
        : "<strong>GF default theme</strong><p>Local semantic-token baseline. The preview above updates as you edit.</p>";
    }
    if (selected) {
      const name = root.querySelector("#brand-name");
      if (name) {
        brandIdEdited = false;
        name.value = selected.name;
        name.dispatchEvent(new Event("input"));
      }
      const source = root.querySelector("#brand-source");
      if (source) source.value = selected.sourceUrl;
      const date = root.querySelector("#brand-source-date");
      if (date) date.value = String(selected.version?.date || "").slice(0, 10);
    }
    paintTheme();
  };
  themeInputs.forEach((input) => input.addEventListener("input", paintTheme));
  root.querySelectorAll("[data-showcase-control]").forEach((input) => input.addEventListener("change", () => {
    if (input.dataset.showcaseControl === "theme") {
      const selected = showcase.theme?.presets?.[input.value] || {};
      for (const token of themeInputs) if (selected[token.dataset.themeToken]) token.value = selected[token.dataset.themeToken];
    }
    if (input.dataset.showcaseControl === "template") {
      const labTemplate = root.querySelector("#lab-template");
      if (labTemplate) labTemplate.value = input.value;
    }
    paintTheme();
  }));
  root.querySelector("#preset-save")?.addEventListener("click", async () => {
    const status = root.querySelector("#preset-status");
    try {
      await api("/api/skills/" + encodeURIComponent(kind) + "/" + encodeURIComponent(id) + "/showcase-preset", { method: "PUT", body: currentPreset() });
      status.textContent = "Preset saved locally.";
    } catch (error) {
      status.textContent = error.message;
    }
  });
  root.querySelector("#preset-export")?.addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(currentPreset(), null, 2) + "\n"], { type: "application/json" });
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = s.name + "-showcase-preset.json";
    link.click();
    URL.revokeObjectURL(href);
  });
  root.querySelectorAll("[data-apuch-theme]").forEach((button) => button.addEventListener("click", () => selectSavedTheme(button.dataset.apuchTheme)));
  root.querySelector("#theme-reset")?.addEventListener("click", () => selectSavedTheme(""));
  root.querySelector("#apuch-sync")?.addEventListener("click", async () => {
    const status = root.querySelector("#apuch-status");
    status.textContent = "Syncing official themes...";
    try {
      await api("/api/apuch/themes/sync", { method: "POST", body: { slugs: ["tiansight", "opcglobal", "iptrust"] } });
      status.textContent = "Saved. Reloading...";
      window.location.reload();
    } catch (error) {
      status.textContent = error.message;
    }
  });
  root.querySelector("#theme-logo")?.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      logoDataUrl = "";
      paintTheme();
      return;
    }
    if (!["image/png", "image/jpeg", "image/webp"].includes(file.type) || file.size > 2 * 1024 * 1024) {
      event.target.value = "";
      root.querySelector("#theme-status")?.replaceChildren(document.createTextNode("Logo must be PNG, JPEG, or WebP under 2 MB."));
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      logoDataUrl = String(reader.result || "");
      paintTheme();
    };
    reader.readAsDataURL(file);
  });

  const paintLab = () => {
    const markdown = root.querySelector("#lab-markdown")?.value || "";
    const template = root.querySelector("#lab-template")?.value || "cover";
    const parsed = parseLabMarkdown(markdown);
    const warnings = labWarnings(parsed, template);
    const warningBox = root.querySelector("#lab-warnings");
    if (warningBox) warningBox.innerHTML = warnings.length ? "<ul>" + warnings.map((item) => "<li>" + esc(item) + "</li>").join("") + "</ul>" : '<p class="lab-ok">Ready for visual review.</p>';
    const frame = root.querySelector("#lab-frame");
    if (frame) frame.srcdoc = labDocument(parsed, template, currentTokens(), currentPreset().logo === "none" ? "" : logoDataUrl);
  };
  root.querySelector("#lab-markdown")?.addEventListener("input", paintLab);
  root.querySelector("#lab-template")?.addEventListener("change", paintLab);
  root.querySelector("#copy-test-prompt")?.addEventListener("click", async (event) => {
    const markdown = root.querySelector("#lab-markdown")?.value || "";
    const template = root.querySelector("#lab-template")?.value || "cover";
    await copyText('Use $gf4p2slides to classify and render this Markdown. Start by testing the "' + template + '" page job, preserve every factual claim, and report fit or source-fidelity problems.\\n\\n' + markdown);
    const old = event.currentTarget.textContent;
    event.currentTarget.textContent = "Copied";
    setTimeout(() => (event.currentTarget.textContent = old), 1200);
  });

  const brandName = root.querySelector("#brand-name");
  const brandId = root.querySelector("#brand-skill-id");
  let brandIdEdited = false;
  brandId?.addEventListener("input", () => (brandIdEdited = true));
  brandName?.addEventListener("input", () => {
    if (brandIdEdited) return;
    const slug = brandName.value.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    brandId.value = (slug || "brand") + "-gf4p2slides";
  });
  root.querySelector("#brand-subskill-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = root.querySelector("#brand-status");
    status.textContent = "Building ZIP...";
    const body = {
      brandName: brandName.value,
      skillId: brandId.value,
      sourceUrl: root.querySelector("#brand-source").value,
      sourceDate: root.querySelector("#brand-source-date").value,
      tokens: currentTokens(),
      logoDataUrl,
    };
    try {
      const response = await fetch("/api/skills/" + encodeURIComponent(s.kind) + "/" + encodeURIComponent(s.folder) + "/brand-subskill.zip", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || "ZIP generation failed");
      }
      const blob = await response.blob();
      const href = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = href;
      link.download = body.skillId + "-skill.zip";
      link.click();
      URL.revokeObjectURL(href);
      status.textContent = "ZIP downloaded.";
    } catch (error) {
      status.textContent = error.message;
    }
  });

  if (showcase?.theme) paintTheme();
  paintLab();
}
