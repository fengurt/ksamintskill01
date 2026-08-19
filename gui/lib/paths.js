import { existsSync, realpathSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, isAbsolute, join, normalize, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
export const GUI_ROOT = resolve(__dirname, "..");
export const REPO_ROOT = resolve(GUI_ROOT, "..");
export const DATA_DIR = process.env.DATA_DIR || join(GUI_ROOT, "data");
export const WORK_DIR = join(REPO_ROOT, ".work");
export const PORT = Number(process.env.PORT || 7979);

/** Extra roots allowed for source docs / HTML (fixtures outside the repo). */
export const ALLOWED_DOC_ROOTS = (
  process.env.ALLOWED_DOC_ROOTS ||
  [
    join(homedir(), "cpro01/0thebrain01/baslide01"),
    join(REPO_ROOT, "fixtures"),
  ].join(":")
)
  .split(":")
  .map((p) => p.trim())
  .filter(Boolean)
  .map((p) => resolve(p.replace(/^~/, homedir())));

const DENY_NAME_RE =
  /(^|\/)(\.env|\.env\..*|deploy\.env|.*\.pem|.*\.key|credentials\.json|keys\.enc|op-session.*|apihub-login\.txt)(\/|$)/i;
const DENY_DIR_RE = /(^|\/)(secrets|node_modules|\.git)(\/|$)/i;

export function expandHome(p) {
  if (!p) return p;
  if (p.startsWith("~/")) return join(homedir(), p.slice(2));
  if (p === "~") return homedir();
  return p;
}

export const BASLIDE_ROOT = resolve(
  expandHome(process.env.BASLIDE_ROOT || join(homedir(), "cpro01/0thebrain01/baslide01"))
);

export function underRoot(abs, root) {
  const a = normalize(abs) + sep;
  const r = normalize(root) + sep;
  return a === r || a.startsWith(r) || normalize(abs) === normalize(root);
}

export function isDeniedPath(abs) {
  const n = abs.replace(/\\/g, "/");
  return DENY_NAME_RE.test(n) || DENY_DIR_RE.test(n);
}

/**
 * Resolve a user/path arg. Must land inside REPO_ROOT or ALLOWED_DOC_ROOTS.
 * Returns absolute real path or throws.
 */
export function safeResolve(userPath, { mustExist = false } = {}) {
  if (!userPath || typeof userPath !== "string") throw new Error("path required");
  const expanded = expandHome(userPath.trim());
  const abs = isAbsolute(expanded) ? resolve(expanded) : resolve(REPO_ROOT, expanded);
  if (isDeniedPath(abs)) throw new Error(`path denied: ${userPath}`);
  let real = abs;
  try {
    if (existsSync(abs)) real = realpathSync(abs);
  } catch {
    /* keep abs */
  }
  const ok =
    underRoot(real, REPO_ROOT) ||
    ALLOWED_DOC_ROOTS.some((r) => underRoot(real, r) || underRoot(abs, r));
  if (!ok) throw new Error(`path outside allowed roots: ${userPath}`);
  if (mustExist && !existsSync(real)) throw new Error(`missing path: ${userPath}`);
  return real;
}

/** Work dirs must stay under .work/ */
export function safeWorkDir(runIdOrPath) {
  if (!runIdOrPath) throw new Error("work required");
  const raw = String(runIdOrPath).trim();
  let abs;
  if (raw.includes("/") || raw.startsWith(".")) {
    abs = isAbsolute(raw) ? resolve(raw) : resolve(REPO_ROOT, raw);
  } else {
    abs = join(WORK_DIR, raw.replace(/[^a-zA-Z0-9._-]/g, "_"));
  }
  if (!underRoot(abs, WORK_DIR) && abs !== WORK_DIR) {
    throw new Error(`work must be under .work/: ${runIdOrPath}`);
  }
  return abs;
}

export function relToRepo(abs) {
  const n = normalize(abs);
  const r = normalize(REPO_ROOT);
  if (n === r) return ".";
  if (n.startsWith(r + sep)) return n.slice(r.length + 1);
  return abs;
}
