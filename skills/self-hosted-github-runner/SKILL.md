---
name: self-hosted-github-runner
description: 为「代码托管在 GitHub、生产在中国大陆云（腾讯云 / 阿里云 / 华为云）」的项目设计、搭建、改造和排障 self-hosted GitHub Actions runner 与跨境发布链路。只要任务涉及 runs-on、runner 注册或标签、GitHub Actions 分钟额度 / 计费 / 消费上限、CI 从国内服务器跑得慢或超时、镜像仓库跨境推拉（TCR / ACR / SWR / ghcr / Docker Hub）、发布或部署工作流、COS / OSS / OBS 产物交接、生产端 apply 脚本或双槽切换，或者用户只是说「CI 很慢」「额度用完了」「runner」「部署脚本」「镜像推不上去」，都要先读本技能；在此类仓库里修改任何 .github/workflows、deploy/ 或发布脚本之前也必须先读。Use for self-hosted GitHub runners, cross-border CI/CD, deploying from GitHub to mainland-China production, Actions quota exhaustion, slow checkout / npm ci / docker push from a China host.
metadata:
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
---

# Self-hosted GitHub Runner · 跨境发布链路

## 0. 这个技能解决什么

### 先选择发布路线

- Public 仓库默认用 GitHub 托管 runner。PR 只做测试、lint 和构建验证，不接触生产 secrets，不执行部署；不要用 `pull_request_target` 执行 PR 代码。
- 部署只从受保护的 `main` 或显式选择的 main 提交触发，部署 job 绑定仅允许 main 的 GitHub Environment，使用最小权限凭据，并用 concurrency 防止同时发布。自建 runner 不是部署的前提。
- 用户要求 GitHub Actions 部署时，复用项目已有发布脚本。小型服务允许托管 Actions 调用现有 TAT / 云厂商 API；下面的对象存储复制与生产拉取方案用于确有跨境大文件瓶颈的项目，不要求先重建整套基础设施。
- 发布前固定远端 main 的完整 SHA，先测试候选版本的真实 API，再切换。失败则恢复已验证可启动的旧版本，并等待健康检查通过。命令提交成功、容器启动或 HTTP 首页 200 都不代表部署完成；必须确认发布 SHA、关键 API 和受影响功能。
- 异步云命令必须跟踪到终态；客户端超时不代表远端停止。发生新错误先定位原因，再修复重试，避免并行发布或反复改变传输方式。

以下跨境方案适用于需要该架构的项目；用户明确选择的既有发布路线优先。

仓库在 GitHub，生产在国内云。两边之间隔着一条慢且不稳定的跨境公网。所有典型故障都来自让**同一台机器同时面对两边**：国内的构建机去 GitHub 拉代码、去 npmjs 装依赖、往 ghcr 推镜像；或者境外的 runner 直接 SSH 进生产主机。前者慢到超时，后者把生产凭据放到了一台随时可能被 PR 代码控制的机器上。

三条铁律，所有决定都从这里推导：

1. **按网络亲和性切分工作。** 需要 GitHub、npm、PyPI、Docker Hub 的工作在境外做；需要生产资源的工作在境内做。一个 job 只能属于一边。
2. **字节只通过云厂商内部搬过境。** 对象存储的跨地域复制、镜像仓库企业版的实例同步都是云厂商在自己骨干网上搬。runner 自己的公网出口永远不承担跨境大流量。
3. **生产端只拉不推，控制面不入境。** 境外任何机器都不持有生产主机的 IP、密钥或访问路径。生产主机自己轮询对象存储，发现签过名的新清单再执行。

这三条不是风格偏好。第一条决定快慢，第二条决定是否超时，第三条决定 PR 里的一段恶意代码最坏能造成什么损失。

## 1. 先判断适用性

回答下面六个问题，全部为「是」才直接套用；有「否」的看第二列怎么调整。

| 问题 | 若为否 |
|---|---|
| 代码托管在 GitHub，CI 用 GitHub Actions？ | 用 GitLab / Gitea 时铁律不变，模板里的 runner 部分换成对应 runner |
| 生产在国内云，且该云的对象存储支持跨地域复制（腾讯 COS、阿里 OSS、华为 OBS 均支持）？ | AWS 中国是独立分区，S3 复制不能跨分区；见 `references/channels.md` 的 AWS 段 |
| 发布物是容器镜像或可打包的产物（tar、静态资源包）？ | git-push 型 PaaS 无法套用；k8s GitOps 改用镜像仓库企业版同步 + Argo 拉取，铁律三仍成立 |
| 你能在生产主机（或同 VPC 的一台小机）上跑一个 systemd 定时任务？ | 不能运行任何代理时，退化为「境外 publish + 人工在境内触发」，仍禁止境外直连 |
| 发布物里没有客户个人数据、数据库导出、密钥？ | 有则先剔除，跨境搬运的只能是代码和二进制 |
| 项目已有可复用的「起新版本、健康检查、切流量」脚本？ | 没有就先写这一段并在本地验证，apply 代理只负责调用它 |

不适用或需要重新设计的信号：多写者数据库要求双活切换；发布需要同时改境内多个地域；合规要求所有构建都在境内完成。

## 2. 给每个 job 分类：四种角色

先把仓库里每个 workflow 的每个 job 填进这张表，再动任何配置。

| 角色 | 跑在哪 | 做什么 | 持有什么凭据 | 绝不做什么 |
|---|---|---|---|---|
| **A 境外 CI runner** | 境外云或第三方，ephemeral，每 job 一个干净环境 | PR 门禁：checkout、装依赖、测试、lint、构建验证 | 仅 GitHub 为该 job 签发的临时 token | 不碰任何生产或云凭据；不部署 |
| **B 境外发布 job** | 与 A 同一台机也可，但只由 main 分支触发且绑定 GitHub Environment | 构建镜像、打包、签名、上传到境外对象存储的 inbox | 对象存储 inbox 前缀的只写密钥、签名私钥 | 不知道生产主机存在；不 SSH |
| **C 境内 apply 代理** | 生产主机或同 VPC 小机，systemd timer，**不是 GitHub runner** | 轮询境内桶、校验、`docker load`、调用项目自己的切流量脚本、写回结果 | 对象存储只读密钥、本机 docker、公钥 | 不执行来自桶里的任何脚本；不访问 GitHub |
| **D 境内构建 runner**（可选） | 境内独立机器，非生产主机 | 只有当构建必须用境内资源时才存在（只在境内镜像仓库有的基础镜像、境内大数据集） | 境内镜像仓库推送账号 | 不接 PR 触发的 job；不装生产密钥 |

分类规则：**需要 GitHub / npm / Docker Hub 就是 A 或 B，需要生产或境内资源就是 C 或 D，两者都需要就拆成两个 job。** 一个 job 同时需要两边，是设计错误而不是网络问题。

标签与开关约定：

```yaml
# 自建 runner 注册时的标签，缺一不可：角色和地域必须显式
--labels self-hosted,linux,x64,ci-ephemeral,ap-singapore

# 工作流里用仓库变量做开关，未设置时回落 GitHub 托管；随时可切回
runs-on: ${{ fromJSON(vars.PR_RUNNER_LABELS || '["ubuntu-24.04"]') }}
```

不要在自建 runner 上使用 `ubuntu-latest`、`ubuntu-24.04` 这类 GitHub 托管标签。GitHub 会优先把带这些标签的 job 派给托管 runner，你会在额度用光时看到 job 在两种 runner 之间行为不一致。

## 3. 跨境搬运通道

默认选第一行；只有它不可用时才往下看。详细机制、费用模型和坑见 `references/channels.md`。

| 通道 | 谁在搬 | 适合 | 费用 | 结论 |
|---|---|---|---|---|
| 对象存储跨地域复制（COS / OSS / OBS） | 云厂商内部 | 镜像 tar、产物包、清单、收据 | 按复制流量 GB 计费，每次发布不到 1 GB | **默认** |
| 镜像仓库企业版实例同步（TCR 企业版 / ACR 企业版） | 云厂商内部 | 团队已有企业版实例时 | 两个实例月费 | 有预算时可选 |
| 境外直接 `docker push` 到境内镜像仓库个人版 | 公网，但目标是云厂商自己的入口 | 小镜像、低频 | 免费 | 先 `time docker push` 实测一次再决定 |
| 云联网 CCN / 专线 | 云厂商私网 | 需要持续低延迟私网互通 | 跨境带宽按 Mbps 包月，远高于一台 runner | 发布场景不选 |
| 境外 SSH / rsync / scp 到境内主机 | 跨境公网 | 只允许小控制流量 | 免费但会超时 | 禁止承担大流量；控制面也应改为拉取 |

## 4. 发布协议：inbox → 复制 → apply → outbox

完整字段、上传顺序和校验顺序见 `references/release-protocol.md`，模板见 `templates/release-publish.yml` 与 `templates/apply-agent.sh`。这里只列不能省的部分。

```
release-inbox/<release_id>/image.tar.zst          镜像，zstd 压缩
release-inbox/<release_id>/image.tar.zst.sha256
release-inbox/<release_id>/receipts/*.json        PR 门禁 / preflight 收据
release-inbox/<release_id>/manifest.json          清单：仓库、commit、tree、镜像 ID、大小、过期时间
release-inbox/<release_id>/manifest.json.sig      最后上传；它的出现才代表这次发布完整
release-outbox/<release_id>/result.json           生产侧写回：applied / failed / skipped 与原因
```

- `release_id` 形如 `20260917T083000Z-dabd529`，按字符串排序即按时间排序。代理只接受比当前更新的 release，除非操作员显式指定回滚目标。
- 上传顺序固定：tar、sha256、receipts、manifest，**签名文件最后**。代理只对存在 `.sig` 的目录动手，所以复制未完成的目录永远不会被误用。
- 代理校验顺序固定：签名 → 仓库与通道匹配 → 未过期 → 单调递增 → 磁盘余量 → 下载 → sha256 与字节数 → `docker load` → 镜像 ID 与清单一致 → 调用项目钩子 → 写回。任何一步失败即停止，当前版本不变。
- 回滚就是显式指定一个旧的 `release_id` 重新 apply。inbox 保留最近 10 个版本，靠生命周期规则清理。
- GitHub Deployment 状态由境外侧回写：代理把结果写进 outbox，反向复制规则把 outbox 搬回境外桶，下一次 publish job 或一个每 10 分钟的境外定时 job 读取并调用 GitHub API。生产主机永远不需要连 GitHub。

## 5. 凭据与边界

| 持有者 | 应有 | 不应有 |
|---|---|---|
| A 境外 CI runner | job 临时 `GITHUB_TOKEN` | 任何云密钥、任何 SSH 私钥 |
| B 境外发布 job | inbox 前缀只写子账号、签名私钥（放 GitHub Environment secret） | 生产主机 IP、数据库口令、只读以外的桶权限 |
| C 境内 apply 代理 | 境内桶只读子账号、发布方公钥、本机 docker | GitHub 凭据、境外桶凭据、签名私钥 |
| 开发者笔记本 | 现有 SSH 密钥，仅作回退 | 不再是日常发布路径 |

优先用云厂商的 OIDC 角色让 GitHub Actions 免密拿临时凭据；不支持时用子账号密钥并按 90 天轮换，到期日写进仓库变量，工作流在到期前 14 天告警、到期后拒绝运行。签名密钥用 Ed25519，公钥固定在生产主机文件系统里，不从桶里读取。

## 6. 事故防线

改任何 workflow、runner 配置或发布脚本之前，逐条对照。每条的完整场景、损失和检测手段见 `references/risk-register.md`。

**Never（违反即停手并说明）**

1. 不在生产主机上注册接 PR job 的 runner。PR 里的代码会在那台机器上执行。
2. 不让 `pull_request` 触发的 job 跑在带生产凭据或非 ephemeral 的 runner 上。仓库若是 public，自建 runner 上根本不能接 PR。
3. 不在自建 runner 上使用 GitHub 托管标签；不省略角色和地域标签。
4. 不让 apply 代理执行桶里下载的任何脚本或可执行文件。清单是数据，代理只运行自己磁盘上的固定代码。
5. 不跳过签名校验、sha256 校验、单调性校验中的任何一个。少一个就多一种攻击或误操作路径。
6. 不让两个 apply 同时运行；不让代理在磁盘余量不足 3 倍 tar 大小时开始下载。
7. 不把云根账号密钥、部署私钥写进仓库、镜像或 runner 环境变量。
8. 不用境外 runner 的公网出口承担跨境大流量；不用 SSH 把镜像推进境内。
9. 不在切换 `runs-on` 时同时改动测试内容。一次只改一层，否则 CI 变红时无法判断是网络、机器还是代码。
10. 不在旧路径稳定之前删除它。新链路连续 5 次成功发布后再退役手工 SSH 或旧 runner。

**成本护栏**

- GitHub 托管 runner 的消费上限设为一个小的非零值。0 意味着额度一到全部 job 在 2 秒内无 runner 失败，比超额付费的损失大得多。
- 文档类改动不跑完整门禁：先跑一个几十秒的 select job 判断受影响范围，再用 `needs` 加 `if` 决定重活是否执行。
- 定时任务、夜间基准、镜像构建放自建 runner，不消耗托管额度。
- inbox 前缀设 14 天生命周期；跨地域复制规则只覆盖 `release-inbox/` 与 `release-outbox/` 前缀；镜像 tar 用 zstd 压缩并设大小预算，超出即 publish 失败而不是默默付费。
- 境外 runner 选带流量包的轻量机型；给它持久化的包管理器缓存和预装的浏览器、办公套件、字体，把每个 job 的下载量从几百 MB 压到几 MB；工作时段外可以关机。

**数据与合规护栏**

- 跨境搬运的对象只能是代码、依赖、二进制和测试收据。镜像里不得打入 `.env`、数据库文件、客户导出；publish job 必须跑一次密钥扫描。
- 桶开启默认加密与版本化；日志里只记 release_id 和摘要，不记凭据和签名 URL。
- 生产端出站只允许云内网端点和镜像仓库；代理不解析境外域名。

## 7. 工作流程：拿到任务后怎么做

1. **先诊断再改动。** 用 `references/diagnostics.md` 的速查表判断问题属于额度、网络还是算力。看 job 对象的 `runner_id` 和耗时，看日志里 `pushing layers` 花了多久，看构建步骤各自的时间。一半以上的「runner 很慢」是网络，不是机器。
2. **填第 2 节的角色表。** 逐 job 分类，指出哪些 job 同时需要两边，那是要拆的地方。
3. **选通道。** 默认对象存储复制；如果团队坚持镜像仓库，先做一次实测并把数字写进 PR 描述。
4. **最小改动。** 一个 PR 只做一件事：切 `runs-on`、或加 publish job、或装代理。用仓库变量做开关，保证能一键回到 GitHub 托管。
5. **跑 lint。** `node <skill>/scripts/lint-workflows.mjs .github/workflows` 检查 PR job 是否落到自建 runner、标签是否完整、publish job 是否绑定 Environment。把它接进项目的 CI 前置检查。
6. **dry-run 代理。** `apply-agent.sh --dry-run` 走完全部校验但不 load、不调用钩子；先在 canary 项目或空闲槽上真跑一次。
7. **留下证据。** 每一步写 JSON：runner 规格与标签、通道实测数字、publish 上传清单、代理结果。这些文件进 PR 或进 outbox，不只写在聊天里。
8. **写明回退。** PR 描述里必须有一句「出问题时怎么回到上一条路径」，并且那条路径此刻仍然可用。

## 8. 诊断速查

| 症状 | 最可能原因 | 一步确认 |
|---|---|---|
| job 创建后 2 到 5 秒失败，无日志，job 对象 `runner_id: 0` | 托管额度用尽或消费上限为 0；或标签无人匹配 | 看账户 Billing 的 Actions 用量；看标签是否与在线 runner 一致 |
| `pushing layers` 持续数分钟后 `TLS handshake timeout` | 境内 runner 往 ghcr / Docker Hub 推，跨境公网 | 把目标换成境内镜像仓库再推一次对比 |
| checkout 或 `npm ci` 在境内 runner 上要十几分钟 | 跨境拉取 | 用 `time` 分别测 GitHub、registry.npmjs.org、境内镜像源 |
| job 排队不开始，显示等待 runner | 标签不匹配、runner 离线、ephemeral 循环没重新注册 | `journalctl -u github-runner@*`，看注册日志 |
| 测试被 killed 或 137 | 内存不足，浏览器与办公套件测试同时跑 | 加 swap，或把需要浏览器的测试与其他测试串行 |
| 代理反复跳过某个 release | 缺 `.sig`、签名不匹配、release_id 不比当前新、磁盘不足 | 看代理日志的 `skip_reason`，看 outbox result |

## 9. 项目适配变量

模板里的占位符，接入新项目时逐一填写，并把这张填好的表放进项目文档。

| 占位符 | 含义 | 本仓库示例 |
|---|---|---|
| `{{OVERSEAS_REGION}}` | 境外 runner 与 inbox 桶所在地域 | `ap-singapore` |
| `{{PROD_REGION}}` | 生产与境内桶所在地域 | `ap-nanjing` |
| `{{INBOX_BUCKET_OVERSEAS}}` / `{{INBOX_BUCKET_PROD}}` | 两个桶名（含 APPID） | `tableai-release-inbox-sg-<appid>` / `tableai-release-inbox-nj-<appid>` |
| `{{PROD_INTERNAL_ENDPOINT}}` | 境内桶的内网端点 | `cos-internal.ap-nanjing.tencentcos.cn` |
| `{{IMAGE_LOCAL_REF}}` | 代理 load 后打的本地镜像名 | `tableai/can01-app` |
| `{{APPLY_HOOK}}` | 项目自己的起新版本 / 健康检查 / 切流量脚本 | `scripts/can01-release-remote.sh` |
| `{{RUNNER_LABELS_CI}}` / `{{RUNNER_LABELS_PUBLISH}}` | 两类 runner 的完整标签 | `self-hosted,linux,x64,ci-ephemeral,ap-singapore` |
| `{{NODE_VERSION}}` 等工具链版本 | 与仓库 `.node-version`、技术基线一致 | `24.21.0` |
| `{{SIGNER_PUBKEY_PATH}}` | 生产主机上固定的公钥路径 | `/etc/release-agent/publisher.pub` |

## 10. 文件索引

| 文件 | 什么时候读 |
|---|---|
| `references/channels.md` | 选搬运通道；换云厂商；估费用；实测直推 |
| `references/release-protocol.md` | 写或改 publish job、apply 代理、清单字段、回滚 |
| `references/risk-register.md` | 改动前的事故对照；写 PR 风险段 |
| `references/diagnostics.md` | 排障；判断额度 / 网络 / 算力；测速脚本 |
| `templates/runner-setup.sh` `runner-loop.sh` `github-runner@.service` | 搭一台 ephemeral runner |
| `templates/pr-runs-on.snippet.yml` | 给 PR 门禁加 runner 开关 |
| `templates/release-publish.yml` | 境外发布 job |
| `templates/apply-agent.sh` `apply-agent.service` `apply-agent.timer` `apply-hook.example.sh` | 境内代理与项目钩子契约 |
| `templates/cam-policy-*.json` `cos-lifecycle.xml` `manifest.example.json` | 桶、子账号、生命周期、清单示例 |
| `scripts/lint-workflows.mjs` | 每次改 workflow 后；接进 CI |
| `evals/evals.json` | 改进本技能时的测试提示 |

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
