---
name: ksamint-githubaction-skill
description: Audit and optimize GitHub Actions triggers, job fan-out, schedules, hosted-runner usage, and failing workflows. Use when Actions minutes spike, workflows run twice, jobs fail before a runner starts, CI and deploy duplicate work, or a repository needs lower-cost CI/CD without weakening required checks.
---

# Ksamint GitHub Actions Optimizer

Reduce **billable fan-out**, not just the wall-clock duration shown on a workflow page. One workflow can allocate several runners, repeat setup in every job, and consume far more runner time than its visible duration suggests.

## Measure the real execution graph

1. Establish the repository visibility, default and protected branches, required check names, deployment path, runner types, workflow files, and relevant billing owner.
2. Inspect workflow runs and jobs over a representative period with `gh run list`, `gh run view`, and the GitHub Actions API. Group by repository, workflow, event, head SHA, conclusion, runner, and job.
3. Report observed job duration separately from estimated billable minutes. Fetch current GitHub billing rules from official documentation before applying rounding, operating-system multipliers, included quotas, or public-repository exceptions. Label estimates and state their assumptions.
4. Distinguish failures that never received a runner from failures inside a job. Account-level budget or payment blocks, missing runner capacity, invalid workflow configuration, and application test failures require different fixes.

Treat repository and deployment topology as evidence, not inference. A GitHub-hosted runner is an ephemeral build machine. Blue and green containers can run on one production server. Neither implies a second production server.

The measurement is complete when every active workflow is classified as necessary, duplicate, excessive, or unable to succeed.

## Remove work in this order

1. **Unable to succeed:** pause the trigger or make deployment manual until missing secrets, tools, artifacts, permissions, and build order are fixed. A repeatedly failing deploy is not a release gate.
2. **Duplicate triggers:** map which events run the same checks for the same commit. Keep distinct PR, merge, release, and scheduled guarantees only where each protects a real boundary.
3. **Stale work:** add branch-scoped `concurrency` and cancel superseded verification runs. Keep production deployment cancellation off unless the deployment is explicitly interruption-safe.
4. **Job fan-out:** combine short jobs when they repeat checkout, runtime setup, dependency installation, and cleanup. Keep jobs separate when they need distinct permissions, environments, services, or independently required checks.
5. **Matrices and schedules:** keep only supported combinations and a cadence tied to a decision. Move expensive or low-signal checks to manual or less frequent schedules.
6. **Setup cost:** reuse lockfile-aware caches and artifacts only when transfer time is lower than repeated work. Measure before and after.
7. **Runner placement:** use a self-hosted runner only after hosted minutes or queue time are measured constraints. Keep untrusted pull-request code away from production credentials, the Docker socket, and production hosts.

Preserve workflow and job names that back required checks. Path filters can leave required workflows pending when the workflow never starts, so verify the repository's branch-protection behavior before relying on them.

## Preserve release discipline

GitHub Actions is an executor, not the release contract. Local deployment, SSH scripts, a dedicated build host, or a provider-native Git integration are valid when they still provide:

- a tested immutable commit or image;
- failure stops before traffic changes;
- least-privilege secrets;
- health checks and rollback;
- production version verification; and
- an auditable release record.

Audit read-only by default. Edit workflows when the user requests optimization. Disabling workflows, changing budgets, rotating secrets, registering runners, or changing branch protection requires authorization for that action. Redact tokens, repository secrets, runner registration tokens, account identifiers, and billing details from reports.

## Verify one path, once

Run local equivalents and workflow syntax checks first. Inspect the final trigger graph and required-check names before spending runner time. When external verification is authorized, dispatch or observe the smallest single run that exercises the changed path. Do not re-run the same failure until its cause changed.

Return:

- a baseline by repository and workflow, including visibility, triggers, run count, job count, observed duration, estimated billable minutes, and failure class;
- a ranked waste ledger with evidence;
- the smallest changes made or proposed, expected savings, and preserved gates; and
- verification results plus any account-level blocker that code cannot fix.

The work is complete when the intended event produces exactly the expected checks, superseded verification cancels safely, deployment runs only from an authorized release boundary, and required gates still pass.
