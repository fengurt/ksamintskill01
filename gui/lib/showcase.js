import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, extname, join, relative, resolve, sep } from "node:path";
import { DATA_DIR } from "./paths.js";

const MANIFEST_LIMIT = 256 * 1024;
const ASSET_LIMIT = 2 * 1024 * 1024;
const ALLOWED_ASSET_EXT = new Set([".html", ".css", ".md", ".json", ".txt"]);
const LOGO_TYPES = {
  "image/png": "png",
  "image/jpeg": "jpg",
  "image/webp": "webp",
};
const PRESETS_FILE = join(DATA_DIR, "showcase-presets.json");
const CONTROL_KEYS = ["theme", "logo", "template", "layout", "pack", "visualization"];

function cleanControls(controls) {
  if (controls == null) return null;
  if (!controls || typeof controls !== "object" || Array.isArray(controls)) throw new Error("invalid showcase controls");
  const out = {};
  for (const key of CONTROL_KEYS) {
    if (controls[key] == null) continue;
    if (!Array.isArray(controls[key]) || !controls[key].length || controls[key].length > 32) {
      throw new Error(`invalid showcase control: ${key}`);
    }
    out[key] = controls[key].map((value) => cleanText(value, `${key} option`, 80));
  }
  return out;
}

export const GF_THEME_DEFAULTS = {
  surface: "#f4f1e8",
  ink: "#17201d",
  muted: "#66716b",
  grid: "#c9cec7",
  accent: "#0e6b5c",
  positive: "#217a58",
  negative: "#b1473c",
  warning: "#9a671b",
  fontBody: "Arial, Helvetica, sans-serif",
  fontNumber: "ui-monospace, SFMono-Regular, Menlo, monospace",
};

function under(base, target) {
  const rel = relative(base, target);
  return rel === "" || (!rel.startsWith(`..${sep}`) && rel !== ".." && !rel.startsWith(sep));
}

function safeExisting(root, rel, limit = ASSET_LIMIT) {
  if (!rel || typeof rel !== "string" || rel.includes("\0")) throw new Error("showcase file required");
  const rootReal = realpathSync(root);
  const candidate = resolve(root, rel);
  if (!existsSync(candidate)) throw new Error(`showcase file missing: ${rel}`);
  const real = realpathSync(candidate);
  if (!under(rootReal, real)) throw new Error(`showcase path denied: ${rel}`);
  const st = statSync(real);
  if (!st.isFile() || st.size > limit) throw new Error(`showcase file too large or not a file: ${rel}`);
  return real;
}

function manifestFiles(manifest) {
  const files = new Set();
  if (manifest?.demo?.html) files.add(manifest.demo.html);
  if (manifest?.theme?.css) files.add(manifest.theme.css);
  if (manifest?.lab?.defaultSample) files.add(manifest.lab.defaultSample);
  for (const sample of manifest?.samples || []) if (sample?.file) files.add(sample.file);
  return files;
}

export function loadShowcase(skillDir, configured) {
  if (!configured) return null;
  const manifestAbs = safeExisting(skillDir, configured, MANIFEST_LIMIT);
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(manifestAbs, "utf8"));
  } catch {
    throw new Error("invalid showcase manifest JSON");
  }
  if (manifest?.version !== 1) throw new Error("unsupported showcase manifest version");
  const root = dirname(manifestAbs);
  for (const file of manifestFiles(manifest)) {
    if (!ALLOWED_ASSET_EXT.has(extname(file).toLowerCase())) throw new Error(`showcase file type denied: ${file}`);
    safeExisting(root, file);
  }
  return { ...manifest, controls: cleanControls(manifest.controls), path: configured };
}

function loadPresets() {
  try {
    const parsed = JSON.parse(readFileSync(PRESETS_FILE, "utf8"));
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export function getShowcasePreset(key) {
  return loadPresets()[String(key)] || null;
}

export function saveShowcasePreset(key, input, showcase) {
  if (!showcase?.controls) throw new Error("showcase has no preset controls");
  const preset = { tokens: cleanTokens(input?.tokens) };
  for (const field of CONTROL_KEYS) {
    const options = showcase.controls[field];
    if (!options) continue;
    const value = String(input?.[field] || options[0]);
    if (!options.includes(value)) throw new Error(`invalid ${field} preset`);
    preset[field] = value;
  }
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  const all = loadPresets();
  all[String(key)] = preset;
  writeFileSync(PRESETS_FILE, JSON.stringify(all, null, 2) + "\n");
  return preset;
}

export function readShowcaseAsset(skillDir, showcase, file) {
  if (!showcase) throw new Error("skill has no showcase");
  if (!manifestFiles(showcase).has(file)) throw new Error("showcase file is not declared");
  const manifestAbs = safeExisting(skillDir, showcase.path, MANIFEST_LIMIT);
  const abs = safeExisting(dirname(manifestAbs), file);
  const ext = extname(abs).toLowerCase();
  if (!ALLOWED_ASSET_EXT.has(ext)) throw new Error("showcase file type denied");
  const types = {
    ".html": "text/html",
    ".css": "text/css",
    ".md": "text/markdown",
    ".json": "application/json",
    ".txt": "text/plain",
  };
  return { file, name: basename(abs), type: types[ext] || "text/plain", text: readFileSync(abs, "utf8") };
}

function cleanText(value, label, max = 160) {
  const out = String(value || "").trim();
  if (!out || out.length > max || /[\r\n\0]/.test(out)) throw new Error(`invalid ${label}`);
  return out;
}

function cleanUrl(value) {
  const raw = cleanText(value, "brand source", 500);
  let url;
  try {
    url = new URL(raw);
  } catch {
    throw new Error("invalid brand source URL");
  }
  if (url.protocol !== "https:" && url.protocol !== "http:") throw new Error("brand source must use http or https");
  return url.toString();
}

function cleanTokens(input = {}) {
  const out = { ...GF_THEME_DEFAULTS };
  for (const key of ["surface", "ink", "muted", "grid", "accent", "positive", "negative", "warning"]) {
    if (input[key] == null || input[key] === "") continue;
    const color = String(input[key]).trim();
    if (!/^#[0-9a-f]{6}$/i.test(color)) throw new Error(`invalid ${key} color`);
    out[key] = color.toLowerCase();
  }
  for (const key of ["fontBody", "fontNumber"]) {
    if (input[key] == null || input[key] === "") continue;
    const font = String(input[key]).trim();
    if (!font || font.length > 180 || /[{};<>\r\n\0]/.test(font)) throw new Error(`invalid ${key}`);
    out[key] = font;
  }
  return out;
}

function parseLogo(dataUrl) {
  if (!dataUrl) return null;
  const match = String(dataUrl).match(/^data:(image\/(?:png|jpeg|webp));base64,([a-z0-9+/=]+)$/i);
  if (!match || !LOGO_TYPES[match[1].toLowerCase()]) throw new Error("logo must be PNG, JPEG, or WebP");
  const data = Buffer.from(match[2], "base64");
  if (!data.length || data.length > ASSET_LIMIT) throw new Error("logo must be between 1 byte and 2 MB");
  return { data, ext: LOGO_TYPES[match[1].toLowerCase()] };
}

export function validateBrandSubskillInput(input = {}) {
  const brandName = cleanText(input.brandName, "brand name", 80);
  const skillId = cleanText(input.skillId, "skill id", 64).toLowerCase();
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*-gf4p2slides$/.test(skillId)) {
    throw new Error("skill id must be lowercase hyphenated and end with -gf4p2slides");
  }
  return {
    brandName,
    skillId,
    sourceUrl: cleanUrl(input.sourceUrl),
    sourceDate: String(input.sourceDate || "not supplied").trim().slice(0, 40),
    tokens: cleanTokens(input.tokens),
    logo: parseLogo(input.logoDataUrl),
  };
}

function themeCss(tokens) {
  return `:root {\n  --gf-surface: ${tokens.surface};\n  --gf-ink: ${tokens.ink};\n  --gf-muted: ${tokens.muted};\n  --gf-grid: ${tokens.grid};\n  --gf-accent: ${tokens.accent};\n  --gf-positive: ${tokens.positive};\n  --gf-negative: ${tokens.negative};\n  --gf-warning: ${tokens.warning};\n  --gf-font-body: ${tokens.fontBody};\n  --gf-font-number: ${tokens.fontNumber};\n}\n`;
}

export function assembleBrandSubskillStage(input) {
  const data = validateBrandSubskillInput(input);
  const stage = mkdtempSync(join(tmpdir(), "ksamint-brand-skill-"));
  const root = join(stage, data.skillId);
  const cleanup = () => rmSync(stage, { recursive: true, force: true });
  try {
    mkdirSync(join(root, "agents"), { recursive: true });
    mkdirSync(join(root, "assets"), { recursive: true });
    mkdirSync(join(root, "references"), { recursive: true });
    const logoName = data.logo ? `logo.${data.logo.ext}` : null;
    const description = `Create ${data.brandName} slides, responsive HTML, and print documents using the GF4p2slides presentation grammar and this brand's official tokens.`;
    writeFileSync(
      join(root, "SKILL.md"),
      `---\nname: ${data.skillId}\ndescription: ${JSON.stringify(description)}\nmetadata:\n  author: ksamint\n  origin: ksamint\n  repository: fengurt/ksamintskill01\n---\n\n# ${data.brandName} GF4p2slides\n\nCall the Skill tool with \"gf4p2slides\" for page classification, the page-plan interface, output-mode rules, and visualization selection. Then apply this brand pack's official tokens and assets.\n\nRead [references/brand-guide.md](references/brand-guide.md) before rendering. Use [assets/theme.css](assets/theme.css) for semantic tokens.${logoName ? ` Use \`assets/${logoName}\` as the official logo supplied for this pack.` : " No logo asset was supplied; do not invent one."}\n`,
      "utf8"
    );
    writeFileSync(
      join(root, "agents", "openai.yaml"),
      `interface:\n  display_name: ${JSON.stringify(`${data.brandName} GF4p2slides`)}\n  short_description: ${JSON.stringify(`Branded slides and documents for ${data.brandName}`)}\n  default_prompt: ${JSON.stringify(`Use $${data.skillId} to create a ${data.brandName} presentation from this material.`)}\n`,
      "utf8"
    );
    writeFileSync(join(root, "assets", "theme.css"), themeCss(data.tokens), "utf8");
    if (data.logo) writeFileSync(join(root, "assets", logoName), data.logo.data);
    writeFileSync(
      join(root, "references", "brand-guide.md"),
      `# ${data.brandName} brand source\n\n- Source: ${data.sourceUrl}\n- Publication or version date: ${data.sourceDate || "not supplied"}\n- Pack author: ksamint\n- Logo: ${logoName ? `\`assets/${logoName}\`, supplied by the user` : "not supplied"}\n\nThe source above is authoritative. Do not infer missing logo variants, colors, fonts, voice rules, or brand claims.\n`,
      "utf8"
    );
    return { stage, root, rootName: data.skillId, cleanup, data };
  } catch (error) {
    cleanup();
    throw error;
  }
}
