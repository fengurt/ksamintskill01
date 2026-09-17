# 风险登记：意外怎么发生、损失是什么、怎么防、怎么发现

改动 workflow、runner 或发布脚本之前，把涉及的行逐条对照。写 PR 描述时，引用对应编号说明已经处理。

## A. 安全

| # | 风险 | 怎么发生 | 损失 | 防线 | 检测 |
|---|---|---|---|---|---|
| A1 | PR 代码在持有生产凭据的机器上执行 | 生产主机或部署机注册了接 `pull_request` 的 runner | 生产被接管，数据泄露 | 生产侧不注册 GitHub runner；PR 只落到角色 A 的 ephemeral runner | `lint-workflows.mjs` 报错；审计 runner 列表与主机对应关系 |
| A2 | Public 仓库的 fork PR 在自建 runner 上跑 | 仓库转 public 后未撤自建 runner | 任意人执行代码、窃取 runner 上的一切 | public 仓库不接自建 runner；private 仓库也用 ephemeral | 仓库可见性变更时的检查项 |
| A3 | 云主密钥或部署私钥进入 runner、镜像或仓库 | 图省事把根密钥写进 secret 或 `.env` 打进镜像 | 全账户资源可被操控与计费 | 子账号最小权限；OIDC 优先；publish job 跑密钥扫描；镜像构建 `.dockerignore` 排除 `.env` | 密钥扫描门禁；云侧异常调用告警 |
| A4 | apply 代理执行桶里的脚本 | 为「灵活」让清单携带 hook 命令 | 拿到 inbox 写权限等于拿到生产 root | 清单只是数据；钩子是本机固定文件；代理不解释任何字段为命令 | 代码审查；代理源码中不出现 `eval`、`sh -c "$field"` |
| A5 | 重放或降级 | 攻击者或误操作把旧清单重新放进 inbox | 已修漏洞被回滚 | 单调 release_id；`expires_at`；显式 `--release` 才能回滚且记录操作员 | outbox 里出现 `not_newer`、`expired` 的 skipped |
| A6 | 签名私钥泄露 | 私钥放在 runner 磁盘或日志里 | 任意人可发布 | 私钥只在 GitHub Environment secret，job 内写入内存文件系统并用完删除；定期轮换，多公钥并存过渡 | 轮换记录；公钥目录审计 |
| A7 | 复制链路被劫持或 DNS 污染 | 代理解析到伪造端点 | 拉到伪造 tar | 代理只用内网端点且启用 TLS；无论来源，签名与 sha256 必须通过 | 校验失败计数 |
| A8 | runner 二进制或 action 被供应链替换 | 用 `@main`、`@v4` 浮动引用；runner 自动更新失控 | 恶意代码进入 CI | action 全部 SHA 锁定；runner 版本与 sha256 固定在 setup 脚本；升级走 PR | 版本基线审计（本仓库已有 `versions:audit`） |
| A9 | 境外 runner 反过来 SSH 进生产 | 为「快速修复」给 runner 装了部署密钥 | 违反铁律三，A1 的变体 | 生产侧只拉；任何 runner 上不存在生产密钥 | 密钥清单；`authorized_keys` 审计 |

## B. 可用性与正确性

| # | 风险 | 怎么发生 | 损失 | 防线 | 检测 |
|---|---|---|---|---|---|
| B1 | 复制未完成就被 apply | 代理看到 manifest 先于 tar | 半个发布、load 失败或旧 tar 配新清单 | 签名文件最后上传；代理只认 `.sig`；sha256 与字节数校验 | `sha256_mismatch` skipped |
| B2 | 两个 apply 并发 | 定时器与手工触发重叠 | 双槽状态错乱、SQLite 双写者 | `flock`；钩子内部再检查写栅栏 | 锁等待日志 |
| B3 | 磁盘写满 | 连续失败的 tar 堆积 | 生产主机不可用 | 下载前检查 3 倍余量；临时目录 24 小时清理；镜像保留 3 个 | 磁盘告警 |
| B4 | `docker load` 得到的镜像不是清单里的 | 构建不可复现或 tar 被替换 | 部署了不是测过的版本 | 比对 `image_id` | `image_id_mismatch` |
| B5 | 时钟漂移 | 生产主机 NTP 失效 | 误判过期、签名 URL 失效 | 两侧 NTP；`expires_at` 留 14 天余量 | 时间偏差监控 |
| B6 | runner 离线，job 无限排队 | ephemeral 循环崩溃、注册 token 过期 | PR 门禁停摆 | systemd `Restart=always`；`vars.PR_RUNNER_LABELS` 一键回落托管 | 排队超过 10 分钟告警 |
| B7 | 标签不匹配 | 注册标签与 `runs-on` 拼写不一致 | job 永不开始 | 标签由 setup 脚本与工作流共用同一变量 | lint 校验标签集合 |
| B8 | 切流量脚本假设被打破 | 新镜像启动参数变化、健康探针路径变化 | 切到不健康槽 | 钩子只在健康探针通过后切换；失败即退出非零，代理不改 `current` | outbox `hook_exit_code` |
| B9 | 数据库迁移与镜像回滚不对称 | 回滚镜像但 schema 已前进 | 应用启动失败 | 迁移 expand-only；钩子在回滚时检查 schema 版本 | 启动日志 |
| B10 | 复制规则只配了一个方向 | 忘记 outbox 反向规则 | GitHub 状态永远 pending | 建桶时两条规则一起配，并在 dry-run 中验证 | 状态回写 job 长期无输入 |

## C. 成本

| # | 风险 | 怎么发生 | 损失 | 防线 | 检测 |
|---|---|---|---|---|---|
| C1 | 托管额度耗尽后全部停摆 | 消费上限为 0 | 数天无 CI，团队绕过门禁 | 设小额非零上限（例如 10 到 20 美元） | job 2 秒失败、`runner_id: 0` |
| C2 | 托管额度失控 | 上限设为无限 | 意外大账单 | 上限非零但有限；docs-only 跳过；定时任务放自建 | 月中检查用量 |
| C3 | 跨地域复制流量失控 | 复制规则覆盖了整个桶或大对象前缀 | 按 GB 的复制费叠加 | 仅 `release-inbox/`、`release-outbox/` 前缀；tar 大小预算 | 桶级流量账单 |
| C4 | 桶存储只增不减 | 无生命周期 | 每月存储费上涨 | inbox 14 天、outbox 30 天 | 对象数趋势 |
| C5 | 境外 runner 流量包超额 | 每个 job 都全量下载依赖与浏览器 | 超额流量按 GB 计 | 持久缓存、预装工具链、`--prefer-offline` | 月流量用量 |
| C6 | runner 全天空转 | 24 小时开机但只在工作时段用 | 机器费用翻倍 | 工作时段外关机或按量计费关机不收计算费 | 账单 |

## D. 数据与合规

| # | 风险 | 怎么发生 | 损失 | 防线 | 检测 |
|---|---|---|---|---|---|
| D1 | 客户数据跨境 | 测试夹具或数据库文件被 `COPY . .` 打进镜像 | 合规事故 | `.dockerignore` 排除数据目录；publish job 检查镜像内容清单 | 镜像层大小突变 |
| D2 | 日志泄露凭据 | 代理打印签名 URL、Authorization 头 | 凭据被日志聚合系统留存 | 日志只记 release_id 与摘要 | 日志扫描 |
| D3 | 清单泄露拓扑 | 清单写入主机名、内网 IP | 攻击面暴露 | 清单字段白名单；`host` 只写摘要 | 审查清单模板 |

## E. 流程

| # | 风险 | 怎么发生 | 损失 | 防线 | 检测 |
|---|---|---|---|---|---|
| E1 | 切 `runs-on` 与改测试同一个 PR | 想一次搞定 | CI 红了无法归因 | 一次只改一层 | PR 变更文件清单 |
| E2 | 新链路上线就删旧路径 | 过度自信 | 出问题无路可退 | 连续 5 次成功后再退役；退役是独立 PR | 发布记录 |
| E3 | 手工 SSH 继续使用，两条路径漂移 | 习惯 | 生产状态与清单不一致 | 手工路径仅回退；每次手工操作补写 outbox | outbox 与 `state/current` 对账 |
| E4 | 收据与实际构建不对应 | publish job 引用了错误 commit 的收据 | 未测代码上线 | 收据里带 tree_sha，publish 校验与当前 tree 一致 | 收据校验失败 |
| E5 | 必需检查因跳过而阻塞合并 | 用 `paths-ignore` 跳过了 required check | PR 无法合并 | 用 select job + `if` 让 job 以 success 快速结束，而不是不触发 | 合并页状态 |
