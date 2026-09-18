#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
sha=$(git rev-parse HEAD)
git bundle create "$stage/app.bundle" HEAD
VENDOR_ROOT="$stage/vendor" python3 scripts/sync-vendor.py --production
tar -czf "$stage/vendor.tar.gz" -C "$stage/vendor" .
python3 - "$stage" "$sha" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1])
m={'sha':sys.argv[2], 'files':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['app.bundle','vendor.tar.gz']}}
(p/'release.json').write_text(json.dumps(m))
PY
tar -czf "${RUNNER_TEMP:-/tmp}/kskill-release.tar.gz" -C "$stage" app.bundle vendor.tar.gz release.json
