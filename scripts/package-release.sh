#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
sha=$(git rev-parse HEAD)
git bundle create "$stage/app.bundle" HEAD
# Keep Git maintenance synchronous while its objects are being packaged.
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0=maintenance.auto GIT_CONFIG_VALUE_0=false
export GIT_CONFIG_KEY_1=gc.auto GIT_CONFIG_VALUE_1=0
VENDOR_ROOT="$stage/vendor" python3 scripts/sync-vendor.py --production
tar -czf "$stage/vendor.tar.gz" -C "$stage/vendor" .
python3 - "$stage" "$sha" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1])
m={'sha':sys.argv[2], 'files':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['app.bundle','vendor.tar.gz']}}
(p/'release.json').write_text(json.dumps(m))
PY
tar -czf "${RUNNER_TEMP:-/tmp}/kskill-release.tar.gz" -C "$stage" app.bundle vendor.tar.gz release.json
