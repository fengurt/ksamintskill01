#!/usr/bin/env bash
# Installed as a forced SSH command. Only the main Environment holds its key.
set -euo pipefail
root=/opt/ksamint-skill-hub
exec 9>/var/lock/ksamint-skill-hub-deploy.lock
flock -w 180 9
stage=$(mktemp -d "$root/incoming.XXXXXX")
candidate=kskill-release-candidate
cleanup() { docker stop -t 1 "$candidate" >/dev/null 2>&1 || true; rm -rf "$stage"; }
trap cleanup EXIT
timeout 180 head -c 104857601 > "$stage/input.tar.gz"
test "$(stat -c %s "$stage/input.tar.gz")" -le 104857600
sha=$(python3 - "$stage" <<'PY'
import hashlib,json,pathlib,re,sys,tarfile
p=pathlib.Path(sys.argv[1])
with tarfile.open(p/'input.tar.gz') as t:
    members=t.getmembers()
    assert {m.name for m in members}=={'app.bundle','vendor.tar.gz','release.json'}
    assert len(members)==3 and all(m.isfile() and m.size<100*1024*1024 for m in members)
    t.extractall(p,filter='data')
m=json.loads((p/'release.json').read_text())
assert re.fullmatch('[0-9a-f]{40}',m['sha'])
for n in ['app.bundle','vendor.tar.gz']:
    assert hashlib.sha256((p/n).read_bytes()).hexdigest()==m['files'][n]
with tarfile.open(p/'vendor.tar.gz') as t:
    assert sum(m.size for m in t.getmembers())<200*1024*1024
    t.extractall(p/'vendor',filter='data')
print(m['sha'])
PY
)
next=$root/releases/$sha
old=$(readlink -f "$root/current")
if test -e "$next"; then
  test "$next" != "$old" || { echo "Already deployed $sha"; exit 0; }
  mv "$next" "$next.failed-$(date +%s)"
fi
git clone --quiet "$stage/app.bundle" "$next"
git -C "$next" checkout --quiet --detach "$sha"
git -C "$next" remote set-url origin https://github.com/fengurt/ksamintskill01.git
test "$(git -C "$next" rev-parse HEAD)" = "$sha"
python3 - "$next" "$stage/vendor" <<'PY'
import importlib.util,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1]); v=pathlib.Path(sys.argv[2])
s=importlib.util.spec_from_file_location('sync',p/'scripts/sync-vendor.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
sources=[s for s in m.parse_sources(m.SOURCES.read_text()) if s.get('publish')=='true']
assert sources and {d.name for d in v.iterdir()}=={s['id'] for s in sources}
for s in sources:
    assert subprocess.check_output(['git','-C',str(v/s['id']),'rev-parse','HEAD'],text=True).strip()==s['synced_commit']
PY
mkdir -p "$root/vendor-releases"
test ! -e "$root/vendor-releases/$sha"
mv "$stage/vendor" "$root/vendor-releases/$sha"
ln -s "$root/vendor-releases/$sha" "$next/vendor"
check() {
  local port=$1
  curl -fsS --max-time 15 "http://127.0.0.1:$port/api/status" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert sys.argv[1].startswith(d["repo"]["head"]["hash"]); assert d["skills"]["mattpocock"]>0' "$sha"
  for endpoint in projects runs registry jobs health; do
    curl -fsS --max-time 30 "http://127.0.0.1:$port/api/$endpoint" | python3 -c 'import json,sys; assert isinstance(json.load(sys.stdin),dict)'
  done
}
docker run -d --rm --name "$candidate" --network host --read-only --tmpfs /tmp:rw -e PORT=17979 -e DATA_DIR=/tmp/data -e PUBLIC_READ_ONLY=1 -e VENDOR_ROOT=/vendor -v "$next:/app:ro" -v "$next/vendor:/vendor:ro" -w /app node:20-bookworm node gui/server.js
ready=0
for attempt in $(seq 1 20); do if check 17979 2>/dev/null; then ready=1; break; fi; sleep 1; done
test "$ready" = 1
docker stop -t 1 "$candidate" >/dev/null
conf=$(grep -l 'server_name kskill.opcglobal.cn;' /etc/nginx/sites-enabled/* | head -1)
test -n "$conf"
cp -L "$conf" "$stage/nginx.before"
drop=/etc/systemd/system/ksamint-skill-hub.service.d/actions.conf
mkdir -p "$(dirname "$drop")"
if test -f "$drop"; then cp "$drop" "$stage/service.before"; fi
rollback() {
  cp "$stage/nginx.before" "$conf"
  if test -f "$stage/service.before"; then cp "$stage/service.before" "$drop"; else rm -f "$drop"; fi
  ln -s "$old" "$root/rollback.$$"; mv -Tf "$root/rollback.$$" "$root/current"
  systemctl daemon-reload; systemctl restart ksamint-skill-hub.service
  nginx -t && systemctl reload nginx
}
trap 'rollback; cleanup' ERR
python3 - "$conf" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]); s=p.read_text()
s=s.replace('location = /api/health { return 404; }','')
s=s.replace('location ~ ^/api/(jobs|projects|runs|file)(/|$) { return 404; }','location ~ ^/api/file(/|$) { return 404; }')
p.write_text(s)
PY
cat > "$drop" <<'SERVICE'
[Service]
ExecStart=
ExecStart=/usr/bin/docker run --rm --name ksamint-skill-hub --network host --read-only --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=256m -e PORT=7979 -e PUBLIC_READ_ONLY=1 -e VENDOR_ROOT=/vendor -v /opt/ksamint-skill-hub/current:/app:ro -v /opt/ksamint-skill-hub/current/vendor:/vendor:ro -v /opt/ksamint-skill-hub/data:/app/gui/data -v /usr/bin/zip:/usr/local/bin/zip:ro -w /app node:20-bookworm node gui/server.js
SERVICE
nginx -t
ln -s "$next" "$root/next.$$"; mv -Tf "$root/next.$$" "$root/current"
systemctl daemon-reload
systemctl restart ksamint-skill-hub.service
ready=0
for attempt in $(seq 1 30); do if check 7979 2>/dev/null; then ready=1; break; fi; sleep 1; done
test "$ready" = 1
systemctl reload nginx
echo "DEPLOYED $sha"
