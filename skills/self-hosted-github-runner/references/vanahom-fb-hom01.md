# vanahom-fb-hom01 mapping

Historical project-specific evidence from 2026-09-17. Recheck current repository state before acting. These are not OPC Academy defaults.

## 11. 本仓库（vanahom-fb-hom01）的具体映射

- 生产：腾讯云南京三区单应用主机 `APUCH-cc001`，Traefik 双槽 `app-a / app-b`，SQLite 单写者加写栅栏；PostgreSQL 18 与 Neo4j 在同 VPC。切流量脚本是 `scripts/can01-release-remote.sh`，它就是 `{{APPLY_HOOK}}` 要调用的对象，不要重写它。
- 镜像：基础镜像已镜像到 TCR 个人版 `ccr.ccs.tencentyun.com/tableai/*`，从南京拉取 30 MB 只需 0.6 秒。应用镜像目前在南京本地构建，慢的只有 checkout 与 `npm ci` 两段输入。
- 已有自建 runner 标签 `[self-hosted, Linux, X64, apuch-ci, nanjing]`，属于角色 D。它往 ghcr.io 推镜像失败过（推层 672 秒后 TLS 超时）。`postgresql-migration-images.yml` 应改推 TCR，不再经过 ghcr。
- 契约测试 `scripts/test-ci-affected-selection.mjs` 明令三个 PR job 必须用 GitHub 托管 runner，且禁止 `APUCH_CI_DEPLOY_KEY` 出现在 PR 工作流。这条规则与本技能一致；引入角色 A 时把断言改为允许 `ci-ephemeral` 标签，而不是删除断言。
- COS：生产已用 `ap-nanjing` 私有桶，应用容器内解析到内网地址（见 `docs/architecture/tencent-cos-nanjing-storage-strategy.md`）。新建 inbox / outbox 桶时沿用同一套 CAM 与加密约定。
- 收据：`scripts/can01-release-evidence.mjs` 与 `contracts/release-manifest.schema.json` 已存在。publish job 复用它们生成清单，不另起一套格式。
- 托管额度：一次 PR 门禁约 14 计费分钟，月用量约 2,500 到 3,000 分钟，超出 Free 套餐。先设非零消费上限止血，再按第 6 节减量。
- 标签词汇：现有标签 `apuch-ci,nanjing` 不符合本技能的 `<角色>,<云地域 id>` 约定。过渡期跑 lint 时传 `--roles=apuch-ci,ci-ephemeral,publish --region-prefix=nanjing`；标准化时改注册为 `build-cn,ap-nanjing` 并同步所有 `runs-on`。
- 2026-09-17 对 `main` 的 lint 结果（处理顺序）：`postgresql-migration-images.yml` 的 `publish` 由 push 触发却无 `environment` 且无 `timeout-minutes`，补 `environment: image-publish` 与 `timeout-minutes: 30`；`pr.yml` 里 `sms-readiness` 引用 `secrets.OP_SERVICE_ACCOUNT_TOKEN`，虽有 `workflow_dispatch` 守卫，仍应拆成独立的只有 `workflow_dispatch` 的 workflow 文件；四处 checkout 补 `persist-credentials: false`。
