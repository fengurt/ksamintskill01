#!/bin/sh
set -eu

repo=${1:-$(pwd)}
candidate=${2:-}
installed='/Applications/ksamint MarkEdit.app'

test -d "$repo/.git" || {
  echo "Not a git repository: $repo" >&2
  exit 2
}

echo "repository=$repo"
echo "branch=$(git -C "$repo" branch --show-current)"
echo "commit=$(git -C "$repo" rev-parse HEAD)"
if test -n "$(git -C "$repo" status --porcelain)"; then
  echo 'worktree=dirty'
else
  echo 'worktree=clean'
fi

inspect_app() {
  label=$1
  app=$2
  echo "$label.path=$app"
  if test ! -d "$app"; then
    echo "$label.present=false"
    return
  fi
  echo "$label.present=true"
  plist="$app/Contents/Info.plist"
  executable="$app/Contents/MacOS/ksamint MarkEdit"
  echo "$label.version=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$plist" 2>/dev/null || true)"
  echo "$label.build=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$plist" 2>/dev/null || true)"
  echo "$label.commit=$(/usr/libexec/PlistBuddy -c 'Print :KSAMINTBuildCommit' "$plist" 2>/dev/null || true)"
  if test -f "$executable"; then
    echo "$label.architectures=$(lipo -archs "$executable" 2>/dev/null || true)"
  fi
  echo "$label.team=$(codesign -dvv "$app" 2>&1 | sed -n 's/^TeamIdentifier=//p')"
  if codesign --verify --deep --strict "$app" >/dev/null 2>&1; then
    echo "$label.codesign=valid"
  else
    echo "$label.codesign=invalid"
  fi
  if xcrun stapler validate "$app" >/dev/null 2>&1; then
    echo "$label.staple=valid"
  else
    echo "$label.staple=missing-or-invalid"
  fi
}

inspect_app installed "$installed"
if test -n "$candidate"; then
  inspect_app candidate "$candidate"
fi
