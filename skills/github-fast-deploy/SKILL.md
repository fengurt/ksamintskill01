---
name: github-fast-deploy
description: Route an explicitly authorized deployment between GitHub Actions and an existing local or provider-CLI fallback. Use when release speed, Actions quota, queue delay, checkout stalls, or safe automatic fallback affects a deployment.
---

# GitHub Fast Deploy

Choose the route before production mutation. Make at most one Actions attempt and one local attempt for the same repository, environment, and commit.

## Pin the release

1. Resolve the repository, production environment, default branch, and its remote 40-character SHA.
2. Require explicit authorization to deploy that environment. The authorization also covers an automatic fallback for the same SHA and environment; any target change requires new authorization.
3. Find the repository's existing CI, deployment, smoke, rollback, and local/provider-CLI commands. Reuse them rather than creating an alternate deploy implementation.
4. Identify the workflow's first production-mutating step before dispatch. Checkout, setup, dependency installation, tests, and builds are pre-mutation.

Continue only when the target SHA is still the remote default-branch head and the working tree used for a local release is clean at that SHA.

## Preflight both routes

Treat Actions as eligible only when all applicable checks are green:

- GitHub API and the deployment workflow are enabled and reachable.
- The exact SHA has a successful required CI result, or an equivalent validation for the exact tree has already passed in the current task.
- No deployment for the same environment is queued or running.
- A GitHub-hosted job has provably available Actions allowance. Query the account billing endpoint when authorized. An unavailable, unsupported, or ambiguous result is `unknown`, which selects local deployment.
- A self-hosted job has an online, idle runner with every requested label; minute allowance does not apply, but queue and link health still do.
- Recent runs do not show a zero-step billing failure or repeated startup/checkout delay.
- The local fallback command, runtime, scoped credentials, target access, rollback, and smoke checks are ready without printing secrets.

Missing local readiness does not grant permission to install credentials or widen access. Actions may proceed only as Actions-only, with fallback explicitly reported unavailable. If neither route is eligible, block without dispatching.

## Route

Use local immediately when Actions is ineligible. Otherwise dispatch the workflow for the pinned SHA and capture its run ID and URL.

For 45 seconds, inspect job and step state rather than only the run state:

- Continue Actions when checkout completes and execution advances toward the repository-defined mutation boundary.
- If the run remains queued, in setup, or in checkout at 45 seconds, request cancellation.
- Wait up to 30 seconds until the run, every job, and every reusable or child workflow are terminal. Start local only after GitHub confirms cancellation everywhere and no mutating step started.
- Treat delayed or incomplete provider state, cancellation, API state, or mutation-boundary evidence as uncertain and stop. Composite actions and reusable workflows count as mutating when any nested step can cross the boundary. Never race the two routes.
- Once a mutating step starts, remain on Actions. Diagnose, resume, repair, or roll back that release instead of starting local.

## Local fallback

1. Acquire the repository's existing lock or provider-native exclusive control. Block if no race-free exclusivity mechanism exists.
2. While holding it, reconfirm the remote branch still points to the pinned SHA and no other deployment is active.
3. Read remote release metadata. If it already equals the pinned SHA, verify it and stop before building or publishing.
4. Reuse a successful exact-tree validation from the current task. Otherwise run the repository's required validation once.
5. Build once with the pinned SHA, execute the existing local/provider deployment command, and run its release metadata and production smoke checks. Release the lock only after final verification or rollback completes.

Keep credentials in their existing runtime secret store. Pass them through ephemeral environment variables or standard input, unset them after use, and report only secret-free identifiers.

## Failure bounds

- One Actions dispatch and one local fallback are the maximum for a SHA.
- A failed pre-mutation Actions run may fall back only after confirmed termination.
- A failed post-mutation run follows the repository rollback or repair path; it never falls back concurrently.
- Missing rollback, smoke checks, exact-SHA proof, or exclusive execution is a blocker for production mutation.

Finish with the selected route, SHA, workflow URL when applicable, phase durations, verification result, and whether any rollback occurred.
