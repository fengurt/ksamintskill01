# 发布协议：inbox → 复制 → apply → outbox

境外发布 job（角色 B）与境内 apply 代理（角色 C）之间唯一的契约。两边只共享这份协议和一对签名密钥，不共享网络、凭据或代码。

## 1. 对象布局

```
release-inbox/
  <release_id>/
    image.tar.zst              docker save | zstd -T0 -19
    image.tar.zst.sha256       "<hex>  image.tar.zst"，sha256sum 格式
    receipts/
      pr-gate-<sha>.json       PR 门禁收据；来源由项目决定
      preflight-<sha>.json     本地或 CI preflight 收据
    manifest.json              见第 3 节
    manifest.json.sig          Ed25519 签名，最后上传
release-outbox/
  <release_id>/
    result.json                生产侧写回，见第 6 节
```

`release_id` 格式：`YYYYMMDDTHHMMSSZ-<commit 前 7 位>`，例如 `20260917T083000Z-dabd529`。UTC，零填充，因此字符串排序等于时间排序。代理用字符串比较判断「更新」。

## 2. 上传顺序

固定为：

1. `image.tar.zst`
2. `image.tar.zst.sha256`
3. `receipts/*`
4. `manifest.json`
5. `manifest.json.sig`

签名文件最后上传，它的存在就是「这个目录完整」的标记。跨地域复制不保证对象到达顺序，代理只对已有 `.sig` 的目录动手，所以永远不会读到半个发布。

上传后 publish job 必须回读每个对象的 ETag 或 sha256 与本地对照，再结束。上传成功的 HTTP 200 不等于内容正确。

## 3. manifest.json

```json
{
  "schema_version": "release-manifest/v1",
  "release_id": "20260917T083000Z-dabd529",
  "repository": "fengurt/vanahom-fb-hom01",
  "channel": "production",
  "commit_sha": "dabd529dab0c12fa04cc11ca09fd115844b2be45",
  "tree_sha": "8f2c…",
  "created_at": "2026-09-17T08:30:00Z",
  "expires_at": "2026-10-01T08:30:00Z",
  "image": {
    "local_ref": "tableai/can01-app",
    "image_id": "sha256:b12810e8915a33c6b22bb21c50dc75c746a316a74280981f6ef9b9fe0790ed9d",
    "tar": { "path": "image.tar.zst", "sha256": "…", "bytes": 312345678 }
  },
  "receipts": [
    { "path": "receipts/pr-gate-dabd529.json", "sha256": "…" }
  ],
  "publisher": { "workflow": "release-publish", "run_id": "35169925206", "key_id": "publisher-2026-09" },
  "notes": "optional free text, no secrets, no hostnames"
}
```

字段规则：

- `image_id` 是 `docker save` 前用 `docker image inspect --format '{{.Id}}'` 取到的配置摘要。它在 `docker load` 后保持不变，是两端唯一能对上的镜像身份。仓库 digest 在 save / load 后会丢失，不要写它。
- `expires_at` 默认创建后 14 天。过期的清单代理拒绝 apply，防止旧发布在很久以后被误触发。
- `repository` 与 `channel` 必须与代理配置完全一致。同一对桶服务多个项目时，这两个字段是隔离边界。
- 清单里不写主机名、IP、路径、凭据。它会被复制到两个地域并保留两周。
- 项目已有清单格式（如本仓库的 `contracts/release-manifest.schema.json`）时，把上面这些字段并入现有 schema，不并存两套。

## 4. 签名

Ed25519，用 OpenSSL 即可，生产主机不需要安装额外工具。

```bash
# 一次性，在离线机器上生成；私钥进 GitHub Environment secret，公钥进生产主机
openssl genpkey -algorithm ed25519 -out publisher.key
openssl pkey -in publisher.key -pubout -out publisher.pub

# publish job 签名
openssl pkeyutl -sign -inkey publisher.key -rawin -in manifest.json -out manifest.json.sig

# apply 代理校验
openssl pkeyutl -verify -pubin -inkey {{SIGNER_PUBKEY_PATH}} -rawin -in manifest.json -sigfile manifest.json.sig
```

公钥固定在生产主机 `{{SIGNER_PUBKEY_PATH}}`，权限 0644，属主 root，代理以只读方式使用。轮换时先在生产主机放入新公钥（代理支持一个目录下多把公钥，任一验证通过即可），再切换 publish job 的私钥，最后移除旧公钥。

## 5. 代理的 apply 规则

按顺序执行，任何一步失败即写 outbox 并退出，当前版本保持不变。

1. `flock` 独占锁。拿不到锁说明上一次还在跑，直接退出。
2. 列举境内桶 `release-inbox/`，只保留存在 `manifest.json.sig` 的 `release_id`。
3. 排除已经出现在本地 `applied/` 目录里的 `release_id`。
4. 读取本地 `state/current`。默认只考虑严格大于它的 `release_id`，取最大的一个。操作员传入 `--release <id>` 时跳过单调性检查，这是唯一的回滚入口。
5. 下载 `manifest.json` 与 `.sig`，用固定公钥校验。失败即记录 `signature_invalid`。
6. 校验 `repository`、`channel` 与代理配置一致，`expires_at` 未过。
7. 检查磁盘：可用空间至少为 `image.tar.bytes` 的 3 倍。不足即记录 `disk_low`，不下载。
8. 下载 tar 与 sha256 文件到临时目录，校验 sha256 与字节数。
9. `zstd -d < image.tar.zst | docker load`，读取输出的镜像 ID，与清单 `image.image_id` 比较。不一致即删除刚 load 的镜像并记录 `image_id_mismatch`。
10. `docker tag <image_id> {{IMAGE_LOCAL_REF}}:<release_id>`。
11. 调用 `{{APPLY_HOOK}} <image_ref> <release_id>`，带超时（默认 20 分钟）。钩子负责起新版本、健康检查、切流量、写栅栏，只在全部成功时返回 0。钩子是项目自己磁盘上的固定脚本，不来自桶。
12. 成功：写 `state/current`，写 `applied/<release_id>`，写 outbox `result.json`，按保留策略清理旧镜像（默认保留最近 3 个 release 的镜像）。
13. 失败：写 outbox `result.json`，`state/current` 不变，保留临时目录 24 小时供排障。

`--dry-run` 执行 1 到 8 步和 9 步的校验部分，不 load、不 tag、不调用钩子。上线前和每次改代理后都先 dry-run。

## 6. result.json

```json
{
  "schema_version": "release-result/v1",
  "release_id": "20260917T083000Z-dabd529",
  "status": "applied",
  "reason": null,
  "previous_release_id": "20260916T120000Z-79af575",
  "host": "sha256:<hostname 的摘要，不写明文>",
  "started_at": "2026-09-17T08:41:02Z",
  "finished_at": "2026-09-17T08:43:40Z",
  "hook_exit_code": 0,
  "checks": { "signature": "ok", "sha256": "ok", "image_id": "ok", "hook": "ok" }
}
```

`status` 取值：`applied`、`failed`、`skipped`。`skipped` 时 `reason` 为 `not_newer`、`expired`、`signature_invalid`、`disk_low`、`repository_mismatch` 之一。

## 7. 状态回写 GitHub

生产主机不连 GitHub。反向复制规则把 `release-outbox/` 搬回境外桶；境外一个每 10 分钟运行的小 job（或下一次 publish job 的第一步）读取新的 `result.json`，调用 GitHub Deployments API 写 `success` 或 `failure`，然后把该 result 标记为已回写。

## 8. 保留与清理

- inbox 前缀：生命周期 14 天后删除当前版本，历史版本 1 天后删除。至少保留最近 10 个 release 供回滚；若发布频率低于每两周一次，把 14 天调长而不是缩短保留数。
- outbox 前缀：30 天。
- 生产主机：`applied/` 标记永久保留（很小）；镜像保留最近 3 个 release；临时目录成功后立即删除，失败后 24 小时删除。
- 代理日志：journald，保留 30 天；不记录 URL 查询串与凭据。

## 9. 回滚

```bash
sudo -u release-agent apply-agent.sh --release 20260916T120000Z-79af575
```

它会跳过单调性检查，其余全部校验照常执行。回滚目标必须仍在 inbox 保留期内，这就是「至少保留 10 个」的原因。数据库迁移不在本协议范围内：镜像回滚不会回滚 schema，项目钩子需要自行判断是否允许。
