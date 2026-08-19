import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { REPO_ROOT } from "./paths.js";

const execFileAsync = promisify(execFile);

async function git(args, { cwd = REPO_ROOT } = {}) {
  try {
    const { stdout } = await execFileAsync("git", args, {
      cwd,
      maxBuffer: 4 * 1024 * 1024,
      env: { ...process.env, GIT_TERMINAL_PROMPT: "0" },
    });
    return stdout.trim();
  } catch (e) {
    return { error: e.stderr?.toString?.() || e.message, code: e.code };
  }
}

export async function repoStatus() {
  const branch = await git(["rev-parse", "--abbrev-ref", "HEAD"]);
  const head = await git(["log", "-1", "--format=%h %cI %s"]);
  const porcelain = await git(["status", "--porcelain"]);
  const aheadBehind = await git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"]);
  let ahead = 0;
  let behind = 0;
  let tracking = null;
  if (typeof aheadBehind === "string" && aheadBehind.includes("\t")) {
    const [a, b] = aheadBehind.split(/\s+/);
    ahead = Number(a) || 0;
    behind = Number(b) || 0;
    tracking = await git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]);
  } else if (typeof aheadBehind === "object" && aheadBehind?.error) {
    tracking = null;
  }
  const dirty =
    typeof porcelain === "string" ? porcelain.split("\n").filter(Boolean) : [];
  const headParts =
    typeof head === "string" ? head.match(/^(\S+)\s+(\S+)\s+(.*)$/) : null;
  return {
    root: REPO_ROOT,
    branch: typeof branch === "string" ? branch : "?",
    head: headParts
      ? { hash: headParts[1], date: headParts[2], subject: headParts[3] }
      : { hash: "?", date: null, subject: String(head) },
    dirty: dirty.length > 0,
    dirtyFiles: dirty.slice(0, 40),
    ahead,
    behind,
    tracking: typeof tracking === "string" ? tracking : null,
    synced: ahead === 0 && behind === 0 && typeof tracking === "string",
  };
}

export async function pathVersion(relPath) {
  const log = await git(["log", "-1", "--format=%h\t%cI\t%s", "--", relPath]);
  const porcelain = await git(["status", "--porcelain", "--", relPath]);
  if (typeof log !== "string" || !log) {
    return { hash: null, date: null, subject: null, dirty: false };
  }
  const [hash, date, ...rest] = log.split("\t");
  return {
    hash,
    date,
    subject: rest.join("\t"),
    dirty: typeof porcelain === "string" && porcelain.trim().length > 0,
  };
}

export async function remoteHead(cwd, remote = "origin", ref = "HEAD") {
  const out = await git(["ls-remote", remote, ref], { cwd });
  if (typeof out !== "string" || !out) return { error: out?.error || "ls-remote failed" };
  const hash = out.split(/\s+/)[0];
  return { hash };
}
