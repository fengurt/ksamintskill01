# 诊断：先分清额度、网络、算力，再动手

「runner 很慢」有三种完全不同的原因，处置方式互不相干。先用下面的方法在十分钟内定性。

## 1. 三类原因的指纹

| 原因 | 指纹 | 处置方向 |
|---|---|---|
| 额度或计费 | job 创建后 2 到 5 秒 `failure`；日志 404 或空；job 对象 `runner_id: 0`、`runner_name: ""`、无 steps；同一时间所有 workflow 同样表现 | 账户 Billing → Actions 消费上限；不是代码问题 |
| 网络 | 某一步耗时占整个 job 八成以上；`pushing layers` 数分钟后 `TLS handshake timeout`；`npm ci` 或 checkout 十几分钟；同一步骤在托管 runner 上只要几十秒 | 换 runner 位置或换搬运通道；不是机器规格问题 |
| 算力 | 步骤时间均匀偏慢；测试 `killed`、exit 137；`docker build` 编译类步骤慢 | 加内存或核数；串行化重型测试 |

## 2. 从 GitHub API 取证据

```bash
# job 列表：看 runner_id、started_at 与 completed_at 的差
gh api repos/{owner}/{repo}/actions/runs/{run_id}/jobs --jq '.jobs[] | {name, conclusion, runner_id, runner_name, started_at, completed_at}'

# 单个 job 的步骤耗时：找出占比最大的一步
gh api repos/{owner}/{repo}/actions/jobs/{job_id} --jq '.steps[] | {name, conclusion, started_at, completed_at}'

# 日志尾部：找 pushing layers / TLS / ETIMEDOUT / ECONNRESET
gh api repos/{owner}/{repo}/actions/jobs/{job_id}/logs | tail -n 200
```

没有 `gh` 时用 GitHub MCP 工具的 `get_workflow_job`、`get_job_logs`。日志 404 且 job 只活了几秒，几乎必然是无 runner 而不是失败的测试。

## 3. 在候选 runner 上测网络

在打算放 runner 的机器上运行一次，把结果贴进 PR。

```bash
#!/usr/bin/env bash
# probe-network.sh · 各出口方向的吞吐与握手
set -u
t() { local label="$1"; shift; local s=$(date +%s.%N); "$@" >/dev/null 2>&1; local rc=$?; printf '%-32s %6.1fs rc=%d\n' "$label" "$(echo "$(date +%s.%N) - $s" | bc)" "$rc"; }

t "github.com handshake"        curl -sS --max-time 20 -o /dev/null https://api.github.com/meta
t "github clone shallow"        git clone --depth 1 -q https://github.com/{{OWNER}}/{{REPO}} /tmp/probe-clone
t "registry.npmjs.org 5MB"      curl -sS --max-time 60 -o /dev/null https://registry.npmjs.org/typescript/-/typescript-5.6.3.tgz
t "docker hub pull alpine"      docker pull alpine:3.24.1
t "ghcr.io handshake"           curl -sS --max-time 20 -o /dev/null https://ghcr.io/v2/
t "cn registry handshake"       curl -sS --max-time 20 -o /dev/null https://{{CN_REGISTRY}}/v2/
t "object store overseas HEAD"  curl -sS --max-time 20 -o /dev/null -I https://{{INBOX_BUCKET_OVERSEAS}}.cos.{{OVERSEAS_REGION}}.myqcloud.com/
rm -rf /tmp/probe-clone
```

判读：任一方向握手超过 5 秒或 5 MB 下载超过 30 秒，这台机器就不该承担那个方向的工作。这正是「按网络亲和性切分」的依据。

## 4. 在 runner 上定位慢步骤

- 持久 runner：看 `/opt/actions-runner/_diag/Worker_*.log`，每个 step 有时间戳。
- `npm ci`：加 `--loglevel=http` 一次，看是 fetch 慢还是解压慢；fetch 慢是网络，解压慢是磁盘。
- `docker build`：`--progress=plain`，`#N ... 12.3s` 的数字就是每层耗时；`exporting to image → pushing layers` 段是推送。
- Playwright / LibreOffice 测试：`free -m` 与 `dmesg | grep -i oom`，137 就是被 OOM killer 杀掉。

## 5. 估算托管额度用量

```
一次 PR 门禁计费分钟 ≈ Σ 各并行 job 的时长（向上取整到分钟）
月用量 ≈ PR 数 × 单次分钟 + main 推送次数 × 推送 job 分钟 + 定时任务次数 × 时长
```

用 `list_workflow_runs` 拉最近 100 次运行，按 workflow 与 event 分组求和。本仓库 2026-09 的实测：单次 PR 门禁中位 4.6 分钟 × 3 job ≈ 14 分钟，月用量 2,500 到 3,000 分钟。Free 套餐 2,000 分钟，Team 3,000 分钟。数字对不上时先看是否有夜间或每日定时任务。

## 6. 代理侧排障

```bash
journalctl -u apply-agent.service -n 200 --no-pager
cat /var/lib/release-agent/state/current
ls /var/lib/release-agent/applied/
rclone lsf cn:{{INBOX_BUCKET_PROD}}/release-inbox/ --dirs-only
sudo -u release-agent apply-agent.sh --dry-run --verbose
```

常见 `skip_reason` 与含义：

| skip_reason | 含义 | 处置 |
|---|---|---|
| `no_signature` | 复制未完成或 publish 失败在最后一步 | 等待复制；查 publish job 日志 |
| `signature_invalid` | 公钥不匹配或清单被改 | 检查公钥轮换；不要跳过 |
| `not_newer` | release_id 不大于当前 | 正常；回滚需显式 `--release` |
| `expired` | 超过 `expires_at` | 重新 publish |
| `repository_mismatch` | 桶被多个项目共用且配置不一致 | 检查代理配置 |
| `disk_low` | 可用空间不足 3 倍 tar | 清理镜像与临时目录 |
| `sha256_mismatch` | 复制损坏或 tar 被替换 | 删除该目录，重新 publish |
| `image_id_mismatch` | 构建不可复现 | 检查 publish job 是否 save 了正确镜像 |
