#!/usr/bin/env bash
# runner-loop.sh · ephemeral runner 循环：每接一个 job 就注销、清理、重新注册
#
# 为什么要 ephemeral：PR 代码跑过的环境不能留给下一个 job。--ephemeral 让 runner 跑完一个 job 自动注销，
# 这个脚本负责清空工作目录并用新的注册 token 再注册一次。由 github-runner@.service 以 runner 用户运行。
#
# 需要：
#   /etc/github-runner/env     由 runner-setup.sh 生成（RUNNER_LABELS 等）
#   /etc/github-runner/token   fine-grained PAT，仅本仓库，Actions + Administration 读写；或改用 GitHub App
#   环境变量 GITHUB_REPOSITORY  owner/repo
set -euo pipefail

: "${GITHUB_REPOSITORY:?owner/repo}"
RUNNER_HOME="${RUNNER_HOME:-/opt/actions-runner}"
INSTANCE="${INSTANCE:-1}"
WORK_DIR="${RUNNER_HOME}/_work-${INSTANCE}"
# shellcheck disable=SC1091
. /etc/github-runner/env
TOKEN_FILE=/etc/github-runner/token

registration_token() {
  curl -fsS -X POST \
    -H "Authorization: Bearer $(cat "$TOKEN_FILE")" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/runners/registration-token" \
    | jq -r .token
}

cleanup_workdir() {
  # 上一个 job 留下的 checkout、临时文件、docker 容器一律清掉；持久缓存在 /srv/ci-cache，不在这里
  rm -rf "${WORK_DIR:?}"/* 2>/dev/null || true
  docker ps -aq --filter "label=ci.ephemeral=${INSTANCE}" | xargs -r docker rm -f >/dev/null 2>&1 || true
}

cd "$RUNNER_HOME"
while true; do
  cleanup_workdir
  if ! token="$(registration_token)"; then
    echo "registration token failed; retry in 60s" >&2
    sleep 60
    continue
  fi
  ./config.sh --unattended --replace --ephemeral \
    --url "https://github.com/${GITHUB_REPOSITORY}" \
    --token "$token" \
    --name "$(hostname -s)-${RUNNER_ROLE}-${INSTANCE}" \
    --labels "${RUNNER_LABELS}" \
    --work "$WORK_DIR" \
    --disableupdate
  unset token
  # run.sh 在一个 job 结束并注销后返回；循环回到顶部重新注册
  ./run.sh || echo "run.sh exited $? ; re-registering" >&2
  sleep 2
done
