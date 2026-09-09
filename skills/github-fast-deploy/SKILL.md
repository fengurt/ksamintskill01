---
name: github-fast-deploy
description: Route an explicitly authorized deployment between GitHub Actions and an existing local or provider-CLI fallback. Use when release speed, Actions quota, queue delay, checkout stalls, or safe automatic fallback affects a deployment.
---

# GitHub Fast Deploy

Choose the route before production mutation. Make at most one Actions attempt and one local attempt for the same repository, environment, and commit.

## Pin the release

1. Resolve the repository, production environment, default branch, and its remote 40-character SHA.
2. Resolve authorization from the current task. A request to fix, validate, and deploy covers the resulting commits and safe fallback within the same repository and environment. Pin each resulting SHA without asking again. Ask only when the repository/environment or requested scope changes, or when the user explicitly limited authorization to one SHA.
3. Find the repository's existing CI, deployment, smoke, rollback, and local/provider-CLI commands. Reuse them rather than creating an alternate deploy implementation.
4. Trace the command inside the workflow to its first production-mutating operation. Checkout, setup, dependency installation, tests, builds, and image uploads are pre-mutation. An umbrella step named Publish or Deploy may contain all of them. Prefer explicit phase markers and provider invocation IDs; if the boundary cannot be observed, treat its state as uncertain rather than claiming cutover has begun.
5. Check automatic triggers before merging or dispatching. A push/merge-triggered release counts as the one Actions attempt. Follow its run ID; do not dispatch a second copy.

Continue only when the target SHA is still the remote default-branch head and the working tree used for a local release is clean at that SHA.

## Choose and preflight the route

Follow the user's route choice or repository default first. Promese01 is local-first:
use its existing publisher after required CI and merge; hosted publishing is
manual-only and needs an explicit route choice. Keep this default scoped to
Promese01. Local-first runs check local readiness directly and skip hosted billing,
runner, and startup diagnostics.

For either route, verify the pinned release's required CI and protected-branch
checks, no active deployment for the same environment, and the existing runtime,
scoped credentials, target access, lock, rollback, and smoke checks. Reuse completed
validation when the tree and relevant build/test inputs are unchanged; rerun only
checks affected by changed inputs or a new failure. Local evidence never replaces
a required remote CI gate. Check automatic workflow triggers even on local-first
runs to prevent concurrent deployments.

For repositories without a selected route, assess Actions eligibility:

- The deployment workflow and GitHub API are enabled and reachable.
- Inspect hosted allowance only when existing permissions expose it; 403/404 means
  unknown. Prefer a ready local route when allowance is unknown and no release is
  active. An automatically triggered job advancing through useful work is direct
  evidence it can run; do not widen account scopes to read billing.
- Self-hosted jobs need an online, idle runner with the requested labels. Hosted
  minute allowance does not apply.
- Recent runs show no zero-step billing failure or repeated startup/checkout stall.

Use the ready local route when Actions is ineligible. Otherwise dispatch once for
the pinned SHA and capture the run ID and URL. Missing local readiness means
Actions-only, with fallback unavailable; it does not authorize new credentials or
broader access. If neither route is ready, report the concrete blocker.

## Actions startup and fallback

Inspect job and step state immediately. The following bounds are failure thresholds,
not mandatory waits before moving to the next step:

- Continue when checkout completes and work advances toward the mutation boundary.
  A build or upload making progress is not a startup stall.
- If the run is still queued or stalled in setup/checkout after 45 seconds and
  local is ready, request cancellation. Use step timestamps and logs as evidence.
- Confirm the run, all jobs, and child workflows are terminal, checking for up to
  30 seconds. Start local as soon as cancellation is confirmed everywhere and no
  mutating operation was dispatched.
- If provider state, cancellation, or the mutation boundary is uncertain, investigate
  the existing invocation. Never race routes. Once mutation is dispatched, diagnose,
  resume, repair, or roll back that release. A client timeout does not stop the host.

## Measure and shorten the critical path

When asked to optimize a slow release, inspect the actual log before editing:

- Separate queue/setup, dependency installation, compilation, image upload, remote pull/migration/readiness/cutover, and smoke timings. Inspect large or stalled layer uploads. An unchanged step name is not proof of progress or a reason for repeated reassuring updates.
- Reuse the deployed image digests for unchanged services. Determine affected services from their Dockerfile inputs and shared dependencies. Include old and new rename paths; an unavailable, truncated, or ambiguous diff requires a conservative rebuild. Read the actual deployed manifest, because a Web-only release may not create tags for the other services.
- Reuse intermediate build stages across ephemeral runners. Select cache storage close to the builder; exporting all intermediate layers to the same slow cross-region registry can make deployment slower. Keep dependency layers separate from application output, and bound cache growth.
- Keep digest pinning, migration gates, readiness checks, exclusive cutover, and rollback intact. Recheck the production baseline under the host lock so a slow build cannot apply a stale image-reuse plan over a newer release.
- Add timestamped phase boundaries and provider invocation IDs. Report a remote operation as dispatched only when the log supports it. Do not infer hours of remote execution from a workflow step that is still building locally.
- Verify selection, fallback-to-full-build, missing metadata, and failure-before-mutation with mocked orchestration; validate changed images with a real local build. A cold first run populates caches, so claim a speedup only after a measured follow-up release.

For Promese01, reuse `infra/lighthouse/publish-production.sh` and
`release-images.sh`. Read `release_phase=metadata`, `build-push:<service>`,
`production status=dispatching`, and `smoke`. The production marker precedes
the mutating TAT submission; the metadata TAT call is read-only. `BUILD_CACHE_DIR`
enables the intermediate local cache with a compatible Buildx builder; Actions
restores/saves that directory. `pnpm test:deploy` covers orchestration and A/B recovery.

## Local fallback

1. Acquire the repository's existing lock or provider-native exclusive control. Block if no race-free exclusivity mechanism exists.
2. While holding it, reconfirm the remote branch still points to the pinned SHA and no other deployment is active.
3. Read remote release metadata. If it already equals the pinned SHA, verify it and stop before building or publishing.
4. Use the existing validation evidence for unchanged tree and inputs; run only missing or invalidated checks. Required CI remains mandatory.
5. Build once with the pinned SHA, execute the existing local/provider deployment command, and run its release metadata and production smoke checks. Release the lock only after final verification or rollback completes.

Keep credentials in their existing runtime secret store. Pass them through ephemeral environment variables or standard input, unset them after use, and report only secret-free identifiers.
Do not print credential configuration to check readiness. Use a scoped read-only
provider call or inspect only whether required fields exist; redact before output,
not after a command has already printed secrets.

## Failure bounds

- One Actions dispatch and one local fallback are the maximum for a SHA.
- A failed pre-mutation Actions run may fall back only after confirmed termination.
- A failed post-mutation run follows the repository rollback or repair path; it never falls back concurrently.
- Missing rollback, smoke checks, exact-SHA proof, or exclusive execution is a blocker for production mutation.

## Complete the handoff

Finish as soon as release SHA/image digests, service health, and affected-flow
functional smoke checks pass. Reuse checks already performed by the publisher;
there is no fixed observation delay or repeated healthy-status update. Existing
alerts handle ongoing monitoring. Investigate further only for a specific anomaly,
an explicit monitoring request, or a release-specific requirement.

Readiness polling waits for an actual in-flight operation and stops when it is ready
or fails. Keep bounded provider polling and timeouts; do not replace a removed
observation window with another timer.

Report the route, SHA, workflow URL when applicable, measured phase durations,
verification result, and any rollback.
