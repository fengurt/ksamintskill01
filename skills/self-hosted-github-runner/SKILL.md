---
name: self-hosted-github-runner
description: 为「代码托管在 GitHub、生产在中国大陆云（腾讯云 / 阿里云 / 华为云）」的项目设计、搭建、改造和排障 self-hosted GitHub Actions runner 与跨境发布链路。只要任务涉及 runs-on、runner 注册或标签、GitHub Actions 分钟额度 / 计费 / 消费上限、CI 从国内服务器跑得慢或超时、镜像仓库跨境推拉（TCR / ACR / SWR / ghcr / Docker Hub）、发布或部署工作流、COS / OSS / OBS 产物交接、生产端 apply 脚本或双槽切换，或者用户只是说「CI 很慢」「额度用完了」「runner」「部署脚本」「镜像推不上去」，都要先读本技能；在此类仓库里修改任何 .github/workflows、deploy/ 或发布脚本之前也必须先读。Use for self-hosted GitHub runners, cross-border CI/CD, deploying from GitHub to mainland-China production, Actions quota exhaustion, slow checkout / npm ci / docker push from a China host.
metadata:
  short-name: ship
  command-id: k028
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
---

# ship

Self-hosted GitHub Actions deployment and cross-border delivery. Canonical invocation: `$self-hosted-github-runner`.

## Choose the smallest working route

1. Read the project's release instructions, workflows and scripts. Record the user's runner and transport requirements, repository visibility, trusted branches, runner labels, deployment target, CI gate and rollback command.
2. User requirements override defaults and examples in every file of this skill. If self-hosted is required, deployment jobs must explicitly select self-hosted labels; no silent hosted fallback. If TAT is prohibited, remove it from the active deployment path. Actions such as checkout are software, not runner types: respect a separate prohibition on third-party actions if given.
3. For an existing static site or small service, reuse its self-hosted runner and existing deployment command. First try a bounded fetch of the exact Git commit. Measure checkout, dependency installation, build and publishing separately before changing architecture.
4. Only choose object-store handoff when the runner's network demonstrably cannot fetch the source reliably. Only introduce replication or a production pull agent when the existing delivery path has a measured limitation or a concrete isolation requirement.
5. Keep PR validation separate from production. Untrusted PR code must not run on persistent deployment machines. If hosted PR runners are also forbidden, an isolated disposable runner is required; report missing capacity rather than silently using hosted runners or claiming skipped checks passed.

For an existing deployment or a stuck project, start with [the reusable deployment guide](references/deployment-reference.md).
For multiple projects sharing a host or on-demand workers, use that guide's sharing section: distinguish runner registration scope, tool versions, trust isolation and host-wide concurrency before provisioning anything.
For runner/network failures, read [diagnostics](references/diagnostics.md).
For the optional cross-border pull architecture, read [advanced architecture](references/advanced-architecture.md), then only the channel/protocol references it routes to.
For `vanahom-fb-hom01` specifically, read [its mapping](references/vanahom-fb-hom01.md). Do not copy those hosts or commands into other projects.

## Source, checks and release identity

- Fetch the full target SHA with a read-only job token and bounded retries. Use a fresh job-scoped directory or a proven clean checkout. Verify `git rev-parse HEAD` equals the target before running repository code. Do not persist credentials in Git config.
- Bind source SHA, CI run SHA and published SHA. A checksum proves byte integrity, not Git identity. Changing the release label does not change the source.
- Enforce the CI gate in the workflow: the latest applicable run of the intended CI workflow for that SHA must be completed/success. An old successful run, another workflow, a PR merge SHA or a manually typed SHA is not sufficient.
- Check current remote main before publishing when the project releases current-main only. Serialize publishing with workflow concurrency and preserve existing rollback behavior.
- Prefer publishing the already-tested artifact where the project supports it. If rebuilding for production configuration, record that distinction, pin inputs and run production validation. Never describe two builds as one.
- Resolve tool versions from the repository baseline. A temporary signed tool URL must not become an undocumented permanent dependency. Cache verified tools; retain checksum verification for downloads.
- Infrastructure tools belong to infrastructure changes. Do not install or run OpenTofu for unrelated content/frontend changes.

### When object-store handoff is necessary

Use one repeatable producer, not shell snippets assembled during each release.

1. Freeze the final source commit; create its archive and record repository, commit, tree, byte length and SHA-256 in a manifest.
2. Upload to an immutable commit-scoped key. Await upload completion, verify object metadata, then test authenticated download and bytes. A URL string or upload command exit alone is not proof of availability.
3. Consumer verifies the manifest's origin/authenticity, repository, requested commit and tree, then archive size/hash before extraction. Use Git objects/bundles when commit identity cannot otherwise be verified.
4. Pass per-release metadata through the release interface. Do not commit a new archive digest into the workflow on every release: that changes HEAD after the archive was made.
5. Clean temporary credentials and objects only after all consumers have finished. Next release must regenerate its inputs automatically; retry/rollback artifacts need an explicit retention period. Test a second run after cleanup.

## Verify and report

- Follow asynchronous work to its terminal state. A client timeout does not prove remote work stopped; reconcile the existing run before retrying.
- Verify deployed SHA, important API responses and the affected feature. Static HTML 200 is not proof that React rendered, an image is correct, or clipboard behavior works.
- Record run URLs, runner labels, commit/artifact identity, step durations, checks and cleanup status in a durable project release note or job summary.
- Keep updates factual: a long step does not prove network congestion. Use timestamps and logs to locate the cause.
- State limitations explicitly: local checks, remote CI, live deployment and browser validation are different evidence.
- For user-authorized releases, continue through the established route. Do not add new approval loops or deploy unrelated projects.

## Workflow validation

Run:
```sh
node <skill>/scripts/lint-workflows.mjs .github/workflows
```
For existing `apuch-ci,nanjing` labels, pass
`--roles=apuch-ci,ci-ephemeral,publish --region-prefix=nanjing`.
The linter checks selected workflow patterns; it does not prove source identity, actual runner isolation, environment policy or CI gating. Verify those separately.

Template runner variables are required when used. Populate them with the authorized labels; absent configuration must fail instead of changing runner provider.

## Update checks

When updating this skill, validate frontmatter and local references; exercise the cases in [evals/evals.json](evals/evals.json). These are review scenarios, not evidence that production has passed.
