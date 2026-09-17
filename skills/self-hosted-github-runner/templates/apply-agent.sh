#!/usr/bin/env bash
# apply-agent.sh · 角色 C：境内 apply 代理
#
# 由 apply-agent.timer 每 60 秒触发，也可由操作员手工运行。
# 只读境内桶，只运行本机固定代码，只在全部校验通过后调用项目钩子。任何一步失败当前版本不变。
#
# 用法：
#   apply-agent.sh                      正常轮询，apply 最新且比当前更新的 release
#   apply-agent.sh --dry-run            走完校验，不 load、不 tag、不调用钩子
#   apply-agent.sh --release <id>       显式回滚或前进到指定 release（跳过单调性检查，其余校验照常）
#   apply-agent.sh --once               同正常，但只处理一个候选后退出（定时器模式的默认行为）
#
# 配置文件 /etc/release-agent/agent.env：
#   REPOSITORY=owner/repo
#   CHANNEL=production
#   INBOX_BUCKET={{INBOX_BUCKET_PROD}}
#   RCLONE_REMOTE=cn                      # rclone 配置名，endpoint 必须是内网端点
#   IMAGE_LOCAL_REF={{IMAGE_LOCAL_REF}}
#   APPLY_HOOK={{APPLY_HOOK}}             # 本机固定脚本：<hook> <image_ref> <release_id>
#   PUBKEY_DIR=/etc/release-agent/keys    # 一个或多个 *.pub，任一验证通过即可（用于轮换）
#   STATE_DIR=/var/lib/release-agent
#   HOOK_TIMEOUT=1200
#   KEEP_IMAGES=3
set -euo pipefail

CONF=/etc/release-agent/agent.env
# shellcheck disable=SC1090
. "$CONF"
: "${REPOSITORY:?}" "${CHANNEL:?}" "${INBOX_BUCKET:?}" "${RCLONE_REMOTE:?}" "${IMAGE_LOCAL_REF:?}" "${APPLY_HOOK:?}" "${PUBKEY_DIR:?}" "${STATE_DIR:?}"
HOOK_TIMEOUT="${HOOK_TIMEOUT:-1200}"
KEEP_IMAGES="${KEEP_IMAGES:-3}"

DRY_RUN=0; TARGET=""; VERBOSE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --release) TARGET="$2"; shift ;;
    --once) ;;
    --verbose) VERBOSE=1 ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
  shift
done

mkdir -p "$STATE_DIR"/{state,applied,tmp,outbox}
LOCK="$STATE_DIR/lock"
exec 9>"$LOCK"
if ! flock -n 9; then echo "another apply is running; exit"; exit 0; fi

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*"; }
dbg() { [ "$VERBOSE" = 1 ] && log "$*" || true; }
remote() { printf '%s:%s/%s' "$RCLONE_REMOTE" "$INBOX_BUCKET" "$1"; }
CURRENT="$(cat "$STATE_DIR/state/current" 2>/dev/null || echo "")"
STARTED="$(date -u +%FT%TZ)"

write_result() { # status reason release_id [hook_exit]
  local status="$1" reason="$2" rid="$3" hook_exit="${4:-null}"
  local host_digest; host_digest="sha256:$(hostname | sha256sum | cut -c1-16)"
  local f="$STATE_DIR/outbox/${rid}.result.json"
  cat > "$f" <<EOF
{ "schema_version": "release-result/v1", "release_id": "${rid}", "status": "${status}", "reason": $( [ "$reason" = null ] && echo null || printf '"%s"' "$reason" ),
  "previous_release_id": $( [ -n "$CURRENT" ] && printf '"%s"' "$CURRENT" || echo null ), "host": "${host_digest}",
  "started_at": "${STARTED}", "finished_at": "$(date -u +%FT%TZ)", "hook_exit_code": ${hook_exit}, "dry_run": $( [ "$DRY_RUN" = 1 ] && echo true || echo false ) }
EOF
  if [ "$DRY_RUN" = 0 ]; then
    rclone copyto "$f" "$(remote "release-outbox/${rid}/result.json")" >/dev/null 2>&1 || log "outbox write failed for $rid"
  fi
  log "result $rid $status ${reason}"
}

# ---- 1. 候选 ---------------------------------------------------------------
mapfile -t signed < <(rclone lsf "$(remote release-inbox/)" --recursive --files-only 2>/dev/null | grep '/manifest.json.sig$' | cut -d/ -f1 | sort -u)
if [ -n "$TARGET" ]; then
  candidate="$TARGET"
  printf '%s\n' "${signed[@]}" | grep -qx "$candidate" || { log "release $candidate has no signature in inbox"; exit 1; }
else
  candidate=""
  for rid in "${signed[@]}"; do
    [ -e "$STATE_DIR/applied/$rid" ] && continue
    if [ -z "$CURRENT" ] || [[ "$rid" > "$CURRENT" ]]; then
      if [ -z "$candidate" ] || [[ "$rid" > "$candidate" ]]; then candidate="$rid"; fi
    fi
  done
  if [ -z "$candidate" ]; then dbg "nothing newer than ${CURRENT:-<none>}"; exit 0; fi
fi
log "candidate $candidate (current ${CURRENT:-<none>}, dry_run=$DRY_RUN)"

work="$STATE_DIR/tmp/$candidate"
rm -rf "$work"; mkdir -p "$work"
trap '[ "$DRY_RUN" = 1 ] && rm -rf "$work" || true' EXIT

# ---- 2. 清单与签名 -----------------------------------------------------------
rclone copyto "$(remote "release-inbox/$candidate/manifest.json")"     "$work/manifest.json"
rclone copyto "$(remote "release-inbox/$candidate/manifest.json.sig")" "$work/manifest.json.sig"
sig_ok=0
for pub in "$PUBKEY_DIR"/*.pub; do
  if openssl pkeyutl -verify -pubin -inkey "$pub" -rawin -in "$work/manifest.json" -sigfile "$work/manifest.json.sig" >/dev/null 2>&1; then sig_ok=1; break; fi
done
[ "$sig_ok" = 1 ] || { write_result skipped signature_invalid "$candidate"; exit 1; }

m() { jq -r "$1" "$work/manifest.json"; }
[ "$(m .schema_version)" = "release-manifest/v1" ] || { write_result skipped schema_unsupported "$candidate"; exit 1; }
[ "$(m .release_id)" = "$candidate" ]             || { write_result skipped release_id_mismatch "$candidate"; exit 1; }
[ "$(m .repository)" = "$REPOSITORY" ]            || { write_result skipped repository_mismatch "$candidate"; exit 1; }
[ "$(m .channel)" = "$CHANNEL" ]                  || { write_result skipped channel_mismatch "$candidate"; exit 1; }
exp_epoch=$(date -u -d "$(m .expires_at)" +%s); now_epoch=$(date -u +%s)
[ "$now_epoch" -lt "$exp_epoch" ]                 || { write_result skipped expired "$candidate"; exit 1; }
if [ -z "$TARGET" ] && [ -n "$CURRENT" ] && ! [[ "$candidate" > "$CURRENT" ]]; then write_result skipped not_newer "$candidate"; exit 0; fi

# ---- 3. 磁盘与下载 -----------------------------------------------------------
tar_bytes=$(m .image.tar.bytes); tar_sha=$(m .image.tar.sha256); tar_path=$(m .image.tar.path); image_id=$(m .image.image_id)
avail=$(df --output=avail -B1 "$STATE_DIR" | tail -1)
[ "$avail" -gt $((tar_bytes * 3)) ] || { write_result skipped disk_low "$candidate"; exit 1; }
rclone copyto "$(remote "release-inbox/$candidate/$tar_path")" "$work/$tar_path" --s3-chunk-size 64M
actual_bytes=$(stat -c %s "$work/$tar_path")
[ "$actual_bytes" = "$tar_bytes" ] || { write_result failed size_mismatch "$candidate"; exit 1; }
echo "$tar_sha  $work/$tar_path" | sha256sum -c - >/dev/null || { write_result failed sha256_mismatch "$candidate"; exit 1; }
log "verified $tar_path ($tar_bytes bytes)"

if [ "$DRY_RUN" = 1 ]; then write_result skipped dry_run_ok "$candidate"; exit 0; fi

# ---- 4. load 与身份比对 -----------------------------------------------------
loaded=$(zstd -d -c "$work/$tar_path" | docker load | sed -n 's/^Loaded image ID: //p; s/^Loaded image: //p' | head -1)
actual_id=$(docker image inspect "$loaded" --format '{{.Id}}' 2>/dev/null || docker image inspect "$image_id" --format '{{.Id}}' 2>/dev/null || echo "")
if [ "$actual_id" != "$image_id" ]; then
  [ -n "$actual_id" ] && docker rmi -f "$actual_id" >/dev/null 2>&1 || true
  write_result failed image_id_mismatch "$candidate"; exit 1
fi
image_ref="${IMAGE_LOCAL_REF}:${candidate}"
docker tag "$image_id" "$image_ref"

# ---- 5. 项目钩子：起新版本、健康检查、切流量 -----------------------------------
set +e
timeout "$HOOK_TIMEOUT" "$APPLY_HOOK" "$image_ref" "$candidate"
hook_rc=$?
set -e
if [ "$hook_rc" -ne 0 ]; then
  write_result failed hook_failed "$candidate" "$hook_rc"
  # 临时目录保留 24 小时供排障（由 tmpfiles 或下一次运行清理）
  exit 1
fi

# ---- 6. 提交状态与清理 ---------------------------------------------------------
echo "$candidate" > "$STATE_DIR/state/current.next" && mv "$STATE_DIR/state/current.next" "$STATE_DIR/state/current"
touch "$STATE_DIR/applied/$candidate"
write_result applied null "$candidate" 0
rm -rf "$work"
# 只保留最近 KEEP_IMAGES 个 release 的镜像
docker images "$IMAGE_LOCAL_REF" --format '{{.Tag}}' | grep -E '^[0-9]{8}T[0-9]{6}Z-' | sort -r | tail -n +$((KEEP_IMAGES + 1)) \
  | xargs -r -I{} docker rmi "${IMAGE_LOCAL_REF}:{}" >/dev/null 2>&1 || true
# 清理超过 24 小时的失败临时目录
find "$STATE_DIR/tmp" -mindepth 1 -maxdepth 1 -type d -mmin +1440 -exec rm -rf {} + 2>/dev/null || true
log "applied $candidate"
