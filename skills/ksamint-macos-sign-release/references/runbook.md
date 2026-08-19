# Signed macOS release runbook

## Contents

1. Inspect and choose scope
2. Build through GitHub Actions
3. Monitor signing and notarization
4. Diagnose failures
5. Verify and install
6. Publish formally
7. Lessons preserved from the 2.4.0 signing incident

## 1. Inspect and choose scope

Run from the repository:

```sh
git status -sb
git rev-parse HEAD
git log -1 --oneline
scripts/inspect-release-state.sh "$(pwd)"
```

Inspect the version in the Xcode project and the installed App. Confirm the requested commit is pushed. Do not include unrelated dirty files in a signing commit.

Choose:

- `arm64`: local Apple Silicon installation; fastest useful path.
- `universal`: formal GitHub Release and Homebrew; requires ARM64 and Intel validation.

The current Mac may have only Command Line Tools. Do not require a macOS upgrade just to build. Use GitHub Actions with a compatible full Xcode image when local Xcode is unavailable.

## 2. Build through GitHub Actions

Primary workflow: `.github/workflows/signed-local-install.yml`.

Dispatch an immutable commit from the branch that contains it:

```sh
repo=fengurt/ksa-MarkEdit
sha="$(git rev-parse HEAD)"
branch="$(git branch --show-current)"
gh workflow run signed-local-install.yml \
  --repo "$repo" \
  --ref "$branch" \
  -f ref="$sha" \
  -f architecture=arm64
```

Verify the displayed input is the exact full SHA. If an incorrect input was dispatched, cancel it before approval and dispatch again.

The `release` environment may require approval. Approve only when the user requested this signed build and the run points at the exact intended commit. Inspect pending deployments first:

```sh
gh api "repos/$repo/actions/runs/$run_id/pending_deployments"
```

Do not bypass an approval requirement. Prefer the GitHub UI; the API is acceptable when the authenticated user is an authorized reviewer and the build is already authorized.

The workflow must:

1. Test CoreEditor, Web, and Cloud code.
2. Import the Developer ID identity into a temporary keychain.
3. Install the five active `MAC_APP_DIRECT` provisioning profiles.
4. Archive the selected architecture with hardened runtime.
5. Export with manual Developer ID signing and the exact certificate SHA-1.
6. Upload `ksamint-MarkEdit-signed-unstapled` before contacting the notary service.
7. Submit for notarization, poll by submission ID with transient-network retries, staple, verify, and upload `ksamint-MarkEdit-signed-local`.

Expected GitHub secret names are documented in the workflow. Inspect names, not values.

## 3. Monitor signing and notarization

Monitor the run without exposing secrets:

```sh
gh run view "$run_id" --repo "$repo" --json status,conclusion,jobs
gh pr checks "$pr_number" --repo "$repo"
```

Notary submission IDs are non-secret and should be recorded. A long `In Progress` state is not a rejection. Do not submit repeated copies while the existing request is still active.

The workflow submits with JSON output, extracts the submission ID, and polls `notarytool info`. Status lookup failures such as `NSURLErrorDomain -1009` are transient and must retry rather than discard the signed App.

If the CI status request fails after upload:

1. Confirm the Apple submission remains `In Progress` or becomes `Accepted`.
2. Preserve/download the `signed-unstapled` artifact for that exact run.
3. Once Accepted, staple that exact App locally, then run all verification gates.
4. Do not install while the request is still `In Progress`.

## 4. Diagnose failures

### Invalid notarization

Fetch the log by submission ID without printing credentials:

```sh
xcrun notarytool log "$submission_id" <credential-options>
```

Fix only the reported bundle or executable. Common incident findings:

- `ConversationCaptureHelper.app` lacked hardened runtime.
- `QuickActionExtension.appex` lacked hardened runtime.

Ensure `ENABLE_HARDENED_RUNTIME = YES` for Release and Debug where these targets are embedded and tested. Rebuild and resubmit an exact new commit.

### Archive/export signing failure

Check:

- A Developer ID Application G2 identity with private key is imported.
- `xcodebuild -exportArchive` uses `method=developer-id`, manual signing, expected Team ID, and the imported identity SHA-1.
- Each bundle identifier maps to its active Developer ID provisioning profile.
- The App Group is assigned to the main app, capture helper, Finder extension, and Quick Action extension as required.
- No native dynamic library or unsigned nested code is introduced accidentally.

### Notary queue stall

Apple may leave a valid first submission `In Progress` for hours. Keep one useful current request, retain its artifact, and report the external blocker honestly. Do not weaken the local installer or call the App notarized prematurely.

## 5. Verify and install

Download only the final artifact from a successful run:

```sh
gh run download "$run_id" \
  --repo "$repo" \
  --name ksamint-MarkEdit-signed-local \
  --dir "$temporary/artifact"
```

Extract into a `mktemp -d` directory. Verify:

```sh
/usr/libexec/PlistBuddy -c 'Print :KSAMINTBuildCommit' "$app/Contents/Info.plist"
lipo -archs "$app/Contents/MacOS/ksamint MarkEdit"
codesign --verify --deep --strict --verbose=2 "$app"
spctl --assess --type execute -vv "$app"
xcrun stapler validate "$app"
codesign -dvv "$app"
```

Also inspect the version/build and expected nested bundles. For ARM-only local installation, require `arm64`; do not require `x86_64`. For Universal publication, require both.

Prefer `Scripts/install-latest-local.sh --source auto --ref <sha> --arch arm64` only when the target commit is reachable through the workflow ref used by that script. The current script dispatches its workflow from `main`; for an unmerged PR commit, dispatch the branch workflow manually, download the successful exact-run artifact, and perform the same safe-install sequence.

Safe-install sequence:

1. Ask the App to quit normally.
2. If it remains open because of windows or unsaved documents, defer; never force-quit.
3. Move the old App to `/Applications/ksamint MarkEdit.backup-YYYYMMDD-HHMMSS.app`.
4. Copy with `ditto`; never use a broad recursive deletion target.
5. Re-run signature and Gatekeeper verification on the installed path.
6. Launch and confirm the process stays alive.
7. Confirm version, build, commit, architecture, Helper, Finder, and Quick Action bundles.
8. On any failure, restore the backup and relaunch it.

## 6. Publish formally

Local ARM success does not authorize release. Before merging and Homebrew:

- All required PR checks pass, including Universal/Intel checks.
- The sequential PR stack is merged in order.
- A Universal Developer ID signed and notarized artifact passes `Scripts/verify-universal.sh`.
- The DMG meets the repository size gate.
- GitHub Release assets, checksums, Apple signature, notarization, and recovery checks pass.
- Homebrew is updated only to the final signed/notarized Release asset.

## 7. Lessons preserved from the 2.4.0 signing incident

- A functional App can still fail notarization because one nested Helper/extension lacks hardened runtime.
- Xcode automatic cloud signing may fail even with the correct certificate; deterministic manual export plus explicit profiles is more reliable.
- A successful archive is not equivalent to a successful export, notarization, or install.
- `notarytool --wait` can terminate on a temporary runner network outage while Apple continues processing. Preserve the signed artifact before waiting and poll explicitly with retries.
- Always compare the signed artifact's embedded full commit to the requested commit.
- The local installed version must be read from `/Applications`; repository version or CI success is not proof of installation.
- ARM64-only is appropriate for an immediate Apple Silicon local install. Keep Universal validation for formal distribution rather than blocking local testing unnecessarily.
