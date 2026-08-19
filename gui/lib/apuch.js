import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { get as httpsGet } from "node:https";
import { join } from "node:path";
import { DATA_DIR } from "./paths.js";
import { GF_THEME_DEFAULTS } from "./showcase.js";

const SAVED_FILE = join(DATA_DIR, "apuch-themes.json");
const BRAND_LIMIT = 4 * 1024 * 1024;
const LOGO_LIMIT = 2 * 1024 * 1024;
const LOGO_TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);

function apiBase() {
  const url = new URL(process.env.APUCH_API_BASE || "https://apuch.art");
  if (url.protocol !== "https:" || url.hostname !== "apuch.art") throw new Error("APUCH_API_BASE must be https://apuch.art");
  return url.origin;
}

function hex(value, fallback) {
  return /^#[0-9a-f]{6}$/i.test(String(value || "")) ? String(value).toLowerCase() : fallback;
}

function download(url, limit, hosts, redirects = 0) {
  const target = new URL(url);
  if (target.protocol !== "https:" || !hosts.has(target.hostname)) throw new Error("Apuch URL is not trusted");
  return new Promise((resolve, reject) => {
    const request = httpsGet(target, { headers: { accept: "application/json,image/*" } }, (response) => {
      if ([301, 302, 303, 307, 308].includes(response.statusCode) && response.headers.location && redirects < 3) {
        response.resume();
        resolve(download(new URL(response.headers.location, target), limit, hosts, redirects + 1));
        return;
      }
      if (response.statusCode !== 200) {
        response.resume();
        reject(new Error(`Apuch returned ${response.statusCode}`));
        return;
      }
      if (Number(response.headers["content-length"] || 0) > limit) {
        response.destroy(new Error("Apuch response is too large"));
        return;
      }
      const chunks = [];
      let size = 0;
      response.on("data", (chunk) => {
        size += chunk.length;
        if (size > limit) response.destroy(new Error("Apuch response is too large"));
        else chunks.push(chunk);
      });
      response.on("end", () => resolve({ bytes: Buffer.concat(chunks), type: String(response.headers["content-type"] || "").split(";")[0].toLowerCase() }));
      response.on("error", reject);
    });
    request.setTimeout(12_000, () => request.destroy(new Error("Apuch request timed out")));
    request.on("error", reject);
  });
}

async function canonicalLogo(data) {
  if (!data.logoUrl) return "";
  const url = new URL(data.logoUrl);
  if (url.protocol !== "https:" || url.hostname !== "media.apuch.art") throw new Error("Apuch logo host is not trusted");
  const { bytes, type } = await download(url, LOGO_LIMIT, new Set(["media.apuch.art"]));
  if (!LOGO_TYPES.has(type)) return "";
  if (!bytes.length || bytes.length > LOGO_LIMIT) throw new Error("Apuch logo is too large");
  return `data:${type};base64,${bytes.toString("base64")}`;
}

export function mapApuchBrand(data, requestedSlug, logoDataUrl = "") {
  const source = data.theme || {};
  return {
    slug: requestedSlug,
    assetKey: data.assetKey || data.slug || requestedSlug,
    name: data.mainName || data.name || requestedSlug,
    sourceUrl: `${apiBase()}/brand.html?brand=${encodeURIComponent(requestedSlug)}`,
    apiUrl: `${apiBase()}/api/brands/${encodeURIComponent(requestedSlug)}.json`,
    logoDataUrl,
    keywords: Array.isArray(source.keywords) ? source.keywords.slice(0, 12).map(String) : [],
    version: data.version || null,
    sourceTheme: source,
    tokens: {
      ...GF_THEME_DEFAULTS,
      surface: hex(source.paper || source.surface, GF_THEME_DEFAULTS.surface),
      ink: hex(source.ink, GF_THEME_DEFAULTS.ink),
      muted: hex(source.muted, GF_THEME_DEFAULTS.muted),
      grid: hex(source.surface, GF_THEME_DEFAULTS.grid),
      accent: hex(source.accent, GF_THEME_DEFAULTS.accent),
      warning: hex(source.secondary, GF_THEME_DEFAULTS.warning),
    },
  };
}

export function loadSavedApuchThemes() {
  let saved = { source: apiBase(), syncedAt: null, themes: [] };
  try {
    const parsed = JSON.parse(readFileSync(SAVED_FILE, "utf8"));
    if (parsed && Array.isArray(parsed.themes)) saved = parsed;
  } catch {
    // First run has no local theme cache.
  }
  return { ...saved, credentialConfigured: Boolean(process.env.APUCH_ADMIN_API_KEY) };
}

export async function syncApuchThemes(input = {}) {
  const slugs = [...new Set(input.slugs || [])];
  if (!slugs.length || slugs.length > 12 || slugs.some((slug) => !/^[a-z0-9-]{1,64}$/.test(String(slug)))) {
    throw new Error("invalid Apuch brand slugs");
  }
  const base = apiBase();
  const themes = await Promise.all(slugs.map(async (slug) => {
    const response = await download(`${base}/api/brands/${encodeURIComponent(slug)}.json`, BRAND_LIMIT, new Set(["apuch.art"]));
    const data = JSON.parse(response.bytes.toString("utf8"));
    return mapApuchBrand(data, slug, await canonicalLogo(data));
  }));
  const saved = { source: base, syncedAt: new Date().toISOString(), themes };
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(SAVED_FILE, JSON.stringify(saved, null, 2) + "\n", { mode: 0o600 });
  return { ...saved, credentialConfigured: Boolean(process.env.APUCH_ADMIN_API_KEY) };
}
