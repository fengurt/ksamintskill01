import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { existsSync, lstatSync, readlinkSync, realpathSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { REPO_ROOT } from "./paths.js";
import { loadInstallMap } from "./skills.js";

const execFileAsync = promisify(execFile);

async function run(cmd, args, timeout = 120000) {
  try {
    const { stdout, stderr } = await execFileAsync(cmd, args, {
      cwd: REPO_ROOT,
      maxBuffer: 4 * 1024 * 1024,
      timeout,
    });
    return { ok: true, code: 0, stdout: stdout.trim(), stderr: stderr.trim() };
  } catch (e) {
    return {
      ok: false,
      code: e.code ?? 1,
      stdout: (e.stdout || "").toString().trim(),
      stderr: (e.stderr || e.message || "").toString().trim(),
    };
  }
}

export async function runLintSkills() {
  const r = await run("python3", [join(REPO_ROOT, "scripts/lint-skills.py")]);
  return { id: "lint-skills", ...r };
}

export async function runScanSecrets() {
  const r = await run("bash", [join(REPO_ROOT, "scripts/scan-secrets.sh"), join(REPO_ROOT, "skills")]);
  return { id: "scan-secrets", ...r };
}

const TARGET_DIRS = {
  cursor: () => join(homedir(), ".cursor/skills"),
  claude: () => join(homedir(), ".claude/skills"),
  codex: () => join(homedir(), ".codex/skills"),
};

export function symlinkIntegrity() {
  const map = loadInstallMap();
  const rows = [];
  for (const [name, targets] of Object.entries(map)) {
    const src = join(REPO_ROOT, "skills", name);
    for (const t of targets) {
      const base = TARGET_DIRS[t]?.();
      if (!base) {
        rows.push({ name, target: t, status: "unknown_target", path: null });
        continue;
      }
      const link = join(base, name);
      if (!existsSync(link) && !existsSync(join(base, `${name}`))) {
        // existsSync follows symlinks; broken links need lstat
        let broken = false;
        try {
          lstatSync(link);
          broken = true;
        } catch {
          broken = false;
        }
        rows.push({
          name,
          target: t,
          status: broken ? "broken" : "missing",
          path: link,
          expected: src,
        });
        continue;
      }
      try {
        const st = lstatSync(link);
        if (!st.isSymbolicLink()) {
          rows.push({ name, target: t, status: "foreign", path: link, note: "not a symlink" });
          continue;
        }
        const dest = realpathSync(link);
        if (dest === realpathSync(src) || dest.startsWith(REPO_ROOT)) {
          rows.push({ name, target: t, status: "ok", path: link, resolves: dest });
        } else {
          rows.push({
            name,
            target: t,
            status: "foreign",
            path: link,
            resolves: dest,
            expected: src,
            link: readlinkSync(link),
          });
        }
      } catch (e) {
        rows.push({ name, target: t, status: "broken", path: link, error: e.message });
      }
    }
  }
  const summary = { ok: 0, missing: 0, foreign: 0, broken: 0, unknown_target: 0 };
  for (const r of rows) summary[r.status] = (summary[r.status] || 0) + 1;
  return { rows, summary };
}

export async function healthSnapshot() {
  const [lint, secrets] = await Promise.all([runLintSkills(), runScanSecrets()]);
  const links = symlinkIntegrity();
  return {
    lint,
    secrets,
    links,
    at: Date.now(),
  };
}
