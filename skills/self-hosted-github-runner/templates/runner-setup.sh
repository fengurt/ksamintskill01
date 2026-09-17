#!/usr/bin/env bash
# runner-setup.sh · 把一台干净的 Debian 12 / Ubuntu 24.04 主机准备成 ephemeral GitHub Actions runner
#
# 用法（root）：
#   RUNNER_ROLE=ci-ephemeral RUNNER_REGION=ap-singapore NODE_VERSION=24.21.0 \
#   RUNNER_VERSION=2.330.0 RUNNER_SHA256=<官方发布页的 sha256> \
#   INSTALL_BROWSER=1 INSTALL_LIBREOFFICE=1 \
#   bash runner-setup.sh
#
# 之后：
#   install -m 0600 -o runner -g runner <fine-grained PAT 文件> /etc/github-runner/token
#   cp runner-loop.sh /opt/actions-runner/runner-loop.sh && chmod +x /opt/actions-runner/runner-loop.sh
#   cp github-runner@.service /etc/systemd/system/ && systemctl daemon-reload
#   systemctl enable --now github-runner@1        # 需要并行就再启 @2 @3，每个实例一个 _work 目录
#
# 原则：runner 用户无 sudo；工具链预装并锁版本；缓存持久化；生产密钥永不出现在这台机器上。
set -euo pipefail

: "${RUNNER_ROLE:?ci-ephemeral | publish | build-cn}"
: "${RUNNER_REGION:?例如 ap-singapore / ap-nanjing}"
: "${NODE_VERSION:?与仓库 .node-version 一致}"
: "${RUNNER_VERSION:?actions/runner 版本，例如 2.330.0}"
: "${RUNNER_SHA256:?对应 tar.gz 的 sha256，取自 GitHub 发布页}"
INSTALL_BROWSER="${INSTALL_BROWSER:-0}"
INSTALL_LIBREOFFICE="${INSTALL_LIBREOFFICE:-0}"
RUNNER_HOME=/opt/actions-runner
CACHE_ROOT=/srv/ci-cache

# ---- 1. 系统包 ------------------------------------------------------------
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl git jq zstd rclone openssl unzip xz-utils bc \
  fonts-noto-cjk fonts-noto-color-emoji
if [ "$INSTALL_BROWSER" = 1 ]; then
  apt-get install -y --no-install-recommends chromium
fi
if [ "$INSTALL_LIBREOFFICE" = 1 ]; then
  apt-get install -y --no-install-recommends libreoffice-calc-nogui libreoffice-impress
fi

# ---- 2. Docker（官方仓库，版本随基线）-------------------------------------
if ! command -v docker >/dev/null; then
  install -m 0755 -d /etc/apt/keyrings
  . /etc/os-release
  curl -fsSL "https://download.docker.com/linux/${ID}/gpg" -o /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# 境内 runner 才配 Docker Hub 加速镜像；境外直连即可
if [[ "$RUNNER_REGION" == ap-nanjing || "$RUNNER_REGION" == ap-shanghai || "$RUNNER_REGION" == ap-beijing || "$RUNNER_REGION" == ap-guangzhou ]]; then
  cat > /etc/docker/daemon.json <<'EOF'
{ "registry-mirrors": ["https://mirror.ccs.tencentyun.com"], "log-driver": "json-file", "log-opts": { "max-size": "50m", "max-file": "3" } }
EOF
else
  cat > /etc/docker/daemon.json <<'EOF'
{ "log-driver": "json-file", "log-opts": { "max-size": "50m", "max-file": "3" } }
EOF
fi
systemctl restart docker

# ---- 3. Node（官方 tar，锁版本；不用发行版包）-------------------------------
if ! command -v node >/dev/null || [ "$(node -v)" != "v${NODE_VERSION}" ]; then
  arch=$(uname -m); case "$arch" in x86_64) narch=x64;; aarch64) narch=arm64;; *) echo "unsupported arch $arch"; exit 1;; esac
  curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${narch}.tar.xz" -o /tmp/node.tar.xz
  curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" -o /tmp/node-shasums.txt
  (cd /tmp && grep " node-v${NODE_VERSION}-linux-${narch}.tar.xz\$" node-shasums.txt | sha256sum -c -)
  rm -rf /usr/local/lib/nodejs && mkdir -p /usr/local/lib/nodejs
  tar -xJf /tmp/node.tar.xz -C /usr/local/lib/nodejs --strip-components=1
  ln -sf /usr/local/lib/nodejs/bin/node /usr/local/bin/node
  ln -sf /usr/local/lib/nodejs/bin/npm /usr/local/bin/npm
  ln -sf /usr/local/lib/nodejs/bin/npx /usr/local/bin/npx
fi

# ---- 4. runner 用户与持久缓存 ----------------------------------------------
id runner >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash runner
usermod -aG docker runner
mkdir -p "$CACHE_ROOT"/npm "$CACHE_ROOT"/playwright /etc/github-runner
chown -R runner:runner "$CACHE_ROOT"
cat > /etc/github-runner/env <<EOF
RUNNER_ROLE=${RUNNER_ROLE}
RUNNER_REGION=${RUNNER_REGION}
RUNNER_LABELS=self-hosted,linux,x64,${RUNNER_ROLE},${RUNNER_REGION}
npm_config_cache=${CACHE_ROOT}/npm
npm_config_prefer_offline=true
npm_config_fund=false
npm_config_audit=false
PLAYWRIGHT_BROWSERS_PATH=${CACHE_ROOT}/playwright
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium
EOF
if [[ "$RUNNER_REGION" == ap-nanjing || "$RUNNER_REGION" == ap-shanghai || "$RUNNER_REGION" == ap-beijing || "$RUNNER_REGION" == ap-guangzhou ]]; then
  # lockfile 里的 resolved 指向 registry.npmjs.org，只改 registry 不够，必须同时替换主机名
  cat >> /etc/github-runner/env <<'EOF'
npm_config_registry=https://registry.npmmirror.com
npm_config_replace_registry_host=always
EOF
fi
chmod 0644 /etc/github-runner/env

# ---- 5. actions/runner 二进制（锁版本 + sha256）-----------------------------
mkdir -p "$RUNNER_HOME" && chown runner:runner "$RUNNER_HOME"
if [ ! -x "$RUNNER_HOME/run.sh" ] || ! grep -q "$RUNNER_VERSION" "$RUNNER_HOME/.runner-version" 2>/dev/null; then
  curl -fsSL "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" -o /tmp/runner.tgz
  echo "${RUNNER_SHA256}  /tmp/runner.tgz" | sha256sum -c -
  sudo -u runner tar -xzf /tmp/runner.tgz -C "$RUNNER_HOME"
  echo "$RUNNER_VERSION" > "$RUNNER_HOME/.runner-version"
  "$RUNNER_HOME/bin/installdependencies.sh"
fi

# ---- 6. 收尾 ---------------------------------------------------------------
cat <<EOF

runner 主机准备完成
  角色/地域 : ${RUNNER_ROLE} / ${RUNNER_REGION}
  标签      : self-hosted,linux,x64,${RUNNER_ROLE},${RUNNER_REGION}
  Node      : $(node -v)   npm: $(npm -v)   Docker: $(docker --version | cut -d' ' -f3)
  缓存      : ${CACHE_ROOT}/npm  ${CACHE_ROOT}/playwright

下一步：
  1. 放置注册用 fine-grained PAT（仅 Actions: read/write，Administration: read/write，且只授权本仓库）：
       install -m 0600 -o runner -g runner <token 文件> /etc/github-runner/token
  2. 安装 runner-loop.sh 与 github-runner@.service，启动 github-runner@1
  3. 这台机器上不得出现任何生产 SSH 私钥、云主账号密钥或数据库口令
EOF
