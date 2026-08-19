---
name: ksamint-macos-sign-release
description: Build, Developer ID sign, notarize, verify, and safely install ksamint MarkEdit for macOS. Use when working on its signed ARM64 local build, Universal release, Apple notarization failures or stalls, GitHub release-environment workflow, local App replacement, Homebrew readiness, signing certificates, provisioning profiles, bundled Helper/Finder/Quick Action extensions, or when checking whether the installed Mac app matches an exact commit.
---

# ksamint macOS signed release

Ship an exact repository commit without weakening Gatekeeper, exposing credentials, or overwriting an app that may contain unsaved work.

## Start here

1. Read [references/runbook.md](references/runbook.md) completely before signing, notarizing, installing, or changing the release workflow.
2. Work from the ksamint MarkEdit repository; default location on this Mac is `/Users/af/Documents/ksa-mdedit`.
3. Run `scripts/inspect-release-state.sh <repo> [candidate-app]` before and after the operation.
4. Preserve unrelated working-tree changes. Use an exact full commit SHA for every signed build.

## Select the artifact

- For an immediate local install on an Apple Silicon Mac, default to `arm64` unless the user requests Intel support.
- For a GitHub Release, Homebrew update, or public distribution, require a Universal `arm64 x86_64` artifact and all formal checks.
- Never describe an unstapled build as release-ready. It may be downloaded for inspection or later ticket stapling, but do not install it through the automatic safe-install path.

## Security rules

- Keep the Developer ID `.p12`, its password, App Store Connect `.p8`, Issuer ID, and Team ID in 1Password or GitHub release-environment secrets.
- Never print, paste, commit, upload as a normal artifact, or include secret values in a report. Redact command output and unset temporary secret variables.
- It is safe to report certificate names, Key IDs, Team IDs, profile names, submission IDs, workflow run IDs, versions, and commit SHAs.
- Do not disable hardened runtime, Gatekeeper, sandboxing, timestamping, or approval gates to make a build pass.
- Do not merge, publish Homebrew, or create a formal release merely because a local ARM64 build succeeds.

## Completion gates

Treat installation as complete only when all apply:

- Tests required for the selected artifact passed.
- The artifact embeds the exact requested commit.
- The main executable has the requested architecture.
- `codesign --verify --deep --strict`, `spctl --assess`, and `xcrun stapler validate` pass.
- The signing Team ID matches the configured release team.
- Conversation Capture Helper, Finder extension, Preview extension, and Quick Action extension are present and correctly signed when expected.
- The prior app was backed up, the new app launched, and the smoke test passed; otherwise rollback succeeded.

Report the installed version/build/commit, architecture, backup path, notarization status, and any remaining formal-release work. Never claim the local app is updated before verifying `/Applications/ksamint MarkEdit.app` directly.
