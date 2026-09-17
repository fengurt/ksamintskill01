#!/usr/bin/env node
/**
 * lint-workflows.mjs · 检查 .github/workflows 是否违反 self-hosted runner 技能的边界规则。
 *
 * 只用 Node 标准库；对 YAML 做缩进感知的轻量扫描，不做完整解析，够用来抓住下面这些错误：
 *
 *   E1  pull_request / pull_request_target 触发的 workflow 里，job 落到自建 runner，但标签不含允许的 ephemeral 标签
 *   E2  自建 runner 标签与 GitHub 托管标签（ubuntu-latest、ubuntu-24.04、windows-*、macos-*）混用
 *   E3  自建 runner 标签缺少角色或地域（默认要求同时出现 ci-ephemeral|publish|build-cn 之一 与 ap-* 地域）
 *   E4  名字含 release / publish / deploy 的 job 由 push 触发却没有 environment
 *   E5  PR 触发的 workflow 里引用了 secrets.*（GITHUB_TOKEN 除外）
 *   W1  PR 触发的 checkout 未设置 persist-credentials: false
 *   W2  自建 runner 的 job 没有 timeout-minutes
 *
 * 用法：node lint-workflows.mjs [.github/workflows] [--allow-pr-label=ci-ephemeral] [--roles=ci-ephemeral,publish,build-cn] [--region-prefix=ap-] [--json]
 * 退出码：有 E 级问题为 1，否则 0。
 */
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const opts = { dir: '.github/workflows', allowPrLabel: 'ci-ephemeral', roles: ['ci-ephemeral', 'publish', 'build-cn'], regionPrefix: 'ap-', json: false };
for (const a of args) {
  if (a.startsWith('--allow-pr-label=')) opts.allowPrLabel = a.split('=')[1];
  else if (a.startsWith('--roles=')) opts.roles = a.split('=')[1].split(',').filter(Boolean);
  else if (a.startsWith('--region-prefix=')) opts.regionPrefix = a.split('=')[1];
  else if (a === '--json') opts.json = true;
  else if (!a.startsWith('--')) opts.dir = a;
}

const HOSTED = /^(ubuntu-(latest|\d\d\.\d\d)(-arm)?|windows-(latest|\d{4})|macos-(latest|\d\d)(-large|-xlarge)?)$/i;
const findings = [];
const add = (level, code, file, job, message) => findings.push({ level, code, file, job, message });

function indentOf(line) { return line.match(/^ */)[0].length; }

/** 取顶层 `on:` 的触发器名集合 */
function triggersOf(lines) {
  const out = new Set();
  const i = lines.findIndex((l) => /^on:\s*(.*)$/.test(l));
  if (i < 0) return out;
  const inline = lines[i].match(/^on:\s*(.+)$/);
  if (inline && inline[1].trim()) {
    const v = inline[1].trim();
    if (v.startsWith('[')) v.slice(1, -1).split(',').forEach((t) => out.add(t.trim().replace(/['"]/g, '')));
    else out.add(v.replace(/['"]/g, ''));
    return out;
  }
  for (let k = i + 1; k < lines.length; k++) {
    const l = lines[k];
    if (!l.trim() || l.trim().startsWith('#')) continue;
    if (indentOf(l) === 0) break;
    if (indentOf(l) === 2) { const m = l.match(/^\s{2}-?\s*([A-Za-z_]+)\s*:?/); if (m) out.add(m[1]); }
  }
  return out;
}

/** 收集 jobs.<id> 块：起止行、runs-on 原文、environment、timeout、name */
function jobsOf(lines) {
  const jobs = [];
  const start = lines.findIndex((l) => /^jobs:\s*$/.test(l));
  if (start < 0) return jobs;
  let cur = null;
  for (let k = start + 1; k < lines.length; k++) {
    const l = lines[k];
    if (l.trim() && indentOf(l) === 0) break;
    const jm = l.match(/^\s{2}([A-Za-z0-9_-]+):\s*$/);
    if (jm) { cur = { id: jm[1], from: k, to: lines.length, runsOn: null, environment: null, timeout: null, text: '' }; jobs.push(cur); continue; }
    if (!cur) continue;
    const ro = l.match(/^\s{4}runs-on:\s*(.*)$/);
    if (ro) {
      let v = ro[1].trim();
      if (!v) { // 多行列表
        const items = [];
        for (let j = k + 1; j < lines.length && /^\s{6}-\s*/.test(lines[j]); j++) items.push(lines[j].replace(/^\s{6}-\s*/, '').trim());
        v = `[${items.join(',')}]`;
      }
      cur.runsOn = v;
    }
    const env = l.match(/^\s{4}environment:\s*(.+)$/); if (env) cur.environment = env[1].trim();
    const to = l.match(/^\s{4}timeout-minutes:\s*(\d+)/); if (to) cur.timeout = Number(to[1]);
    const cond = l.match(/^\s{4}if:\s*(.+)$/); if (cond) cur.if = cond[1].trim();
  }
  for (let i = 0; i < jobs.length; i++) { jobs[i].to = i + 1 < jobs.length ? jobs[i + 1].from : lines.length; jobs[i].text = lines.slice(jobs[i].from, jobs[i].to).join('\n'); }
  return jobs;
}

function labelsOf(runsOn) {
  if (!runsOn) return { labels: [], expression: false };
  if (runsOn.includes('${{')) {
    // 表达式：尝试从 fromJSON('...') 的默认值里提取标签，否则只标记为表达式
    const m = runsOn.match(/'(\[[^']*\])'/);
    if (m) { try { return { labels: JSON.parse(m[1]).map(String), expression: true }; } catch { /* ignore */ } }
    return { labels: [], expression: true };
  }
  const v = runsOn.trim();
  if (v.startsWith('[')) return { labels: v.slice(1, -1).split(',').map((s) => s.trim().replace(/['"]/g, '')).filter(Boolean), expression: false };
  return { labels: [v.replace(/['"]/g, '')], expression: false };
}

const dir = path.resolve(opts.dir);
const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => /\.ya?ml$/.test(f)).map((f) => path.join(dir, f)) : [];
for (const file of files) {
  const rel = path.relative(process.cwd(), file);
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  const triggers = triggersOf(lines);
  const prTriggered = triggers.has('pull_request') || triggers.has('pull_request_target');
  const pushTriggered = triggers.has('push');
  const jobs = jobsOf(lines);

  if (prTriggered) {
    // 只认表达式里的 secrets.X，避免把文件名 scan-secrets.mjs 当成引用
    const secretsIn = (text) => [...new Set([...text.matchAll(/\$\{\{[^}]*?\bsecrets\.([A-Za-z0-9_]+)/g)].map((m) => m[1]).filter((n) => n !== 'GITHUB_TOKEN'))];
    // job 级 if 明确排除 PR 事件时降级为 info：该 job 在 PR 下不会运行，但仍建议拆到独立的 workflow_dispatch 文件
    const excludesPr = (cond) => Boolean(cond) && /event_name\s*==\s*'(workflow_dispatch|push|schedule)'|event_name\s*!=\s*'pull_request'/.test(cond);
    for (const job of jobs) {
      const names = secretsIn(job.text);
      if (!names.length) continue;
      if (excludesPr(job.if)) add('info', 'I2', rel, job.id, `引用 secrets.${names.join(', secrets.')}，但 job 级 if 排除了 PR 事件；建议拆到只有 workflow_dispatch 的独立 workflow`);
      else add('error', 'E5', rel, job.id, `PR 触发的 job 引用了 secrets.${names.join(', secrets.')}；PR 代码可读到它们`);
    }
    lines.forEach((l, i) => {
      if (/uses:\s*actions\/checkout@/.test(l)) {
        const block = lines.slice(i, i + 6).join('\n');
        if (!/persist-credentials:\s*false/.test(block)) add('warn', 'W1', rel, null, `第 ${i + 1} 行的 checkout 未设置 persist-credentials: false`);
      }
    });
  }

  for (const job of jobs) {
    const { labels, expression } = labelsOf(job.runsOn);
    const selfHosted = labels.some((l) => /^self-hosted$/i.test(l)) || /self-hosted/.test(job.runsOn || '');
    const hosted = labels.filter((l) => HOSTED.test(l));

    if (selfHosted && hosted.length) add('error', 'E2', rel, job.id, `自建 runner 标签与托管标签混用：${hosted.join(', ')}`);
    if (selfHosted) {
      const hasRole = labels.some((l) => opts.roles.includes(l));
      const hasRegion = labels.some((l) => l.startsWith(opts.regionPrefix));
      if (!hasRole || !hasRegion) add('error', 'E3', rel, job.id, `自建 runner 标签缺少${!hasRole ? '角色' : ''}${!hasRole && !hasRegion ? '与' : ''}${!hasRegion ? '地域' : ''}：${labels.join(',') || job.runsOn}`);
      if (prTriggered && !labels.includes(opts.allowPrLabel)) add('error', 'E1', rel, job.id, `PR 触发的 job 落到自建 runner，但标签不含 ${opts.allowPrLabel}；PR 代码将在非 ephemeral 机器上执行`);
      if (job.timeout == null) add('warn', 'W2', rel, job.id, '自建 runner 上的 job 没有 timeout-minutes');
    }
    if (pushTriggered && /(release|publish|deploy)/i.test(job.id) && !job.environment) add('error', 'E4', rel, job.id, 'push 触发的发布类 job 没有绑定 environment，发布凭据缺少审批与作用域');
    if (expression && !selfHosted && labels.length === 0) add('info', 'I1', rel, job.id, `runs-on 为表达式 ${job.runsOn}，默认值无法静态判断`);
  }
}

const errors = findings.filter((f) => f.level === 'error');
if (opts.json) {
  process.stdout.write(`${JSON.stringify({ schema: 'self-hosted-runner-lint/v1', dir: opts.dir, files: files.length, findings }, null, 2)}\n`);
} else {
  console.log(`self-hosted runner lint · ${files.length} workflow(s) in ${opts.dir}`);
  for (const f of findings) console.log(`  ${f.level === 'error' ? '✗' : f.level === 'warn' ? '⚠' : 'ℹ'} ${f.code} ${f.file}${f.job ? ` [${f.job}]` : ''}: ${f.message}`);
  console.log(`  ${errors.length} error(s), ${findings.filter((f) => f.level === 'warn').length} warning(s)`);
}
process.exit(errors.length ? 1 : 0);
