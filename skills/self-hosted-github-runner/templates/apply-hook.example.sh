#!/usr/bin/env bash
# apply-hook.example.sh · 项目钩子契约
#
# 代理调用：<hook> <image_ref> <release_id>
# 约定：
#   - 只在新版本已健康并且流量已切换到它之后返回 0；任何其他情况返回非零
#   - 钩子自己负责：起空闲槽、健康探针、写栅栏、切路由、旧槽降级
#   - 钩子是本机固定文件，由项目维护；代理从不修改它，也不从桶里取它
#   - 钩子不得访问 GitHub 或境外网络；需要的一切都在 image_ref 里
#
# 本仓库（vanahom-fb-hom01）的实现就是调用现有脚本，不重写切槽逻辑：
set -euo pipefail
IMAGE_REF="${1:?image_ref}"
RELEASE_ID="${2:?release_id}"

REMOTE_ROOT="${REMOTE_ROOT:-/srv/tableai-can01}"
cd "$REMOTE_ROOT"

# 现有的双槽发布脚本以环境变量接收镜像与版本；它内部完成：
#   起 idle 槽 → /api/live 与 /api/health 探针 → 写栅栏 → Traefik routes.yml 原子替换 → 旧槽 accept-writes 关闭
IMAGE="$IMAGE_REF" RELEASE="$RELEASE_ID" MODE=coolify POSTDEPLOY_SCOPE=code-only \
  bash scripts/can01-release-remote.sh

# 二次确认：活跃槽就是新版本且健康
active="$(cat "$REMOTE_ROOT/deploy/active-slot")"
docker inspect "tableai-can01-app-${active}" --format '{{.Config.Image}} {{.State.Health.Status}}' | grep -q "^${IMAGE_REF} healthy$"
