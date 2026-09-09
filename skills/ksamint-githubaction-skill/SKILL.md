---
name: ksamint-githubaction-skill
description: Audit and optimize GitHub Actions triggers, job fan-out, schedules, hosted-runner usage, and failing workflows. Use when Actions minutes spike, workflows run twice, jobs fail before a runner starts, CI and deploy duplicate work, a test or release path is too slow, or a repository needs lower-cost CI/CD without weakening required checks.
---

# Ksamint GitHub Actions Optimizer

Optimize the user's stated objective: elapsed time, runner cost, reliability, or a combination. Workflow duration and total runner time are different measurements; report the one relevant to the request without treating either as the universal target.

## Match evidence to scope

For a focused bottleneck fix, inspect the affected workflow, slow job or step, runner resources, and checks or release boundaries the change can affect. Use an existing representative run as the baseline. Do not require an unrelated billing review, runner migration assessment, or classification of every workflow before improving that path. Increase test workers within an existing job when resource capacity and test isolation support it; this does not require adding jobs.

For a repository-wide cost or execution audit, use the full graph procedure below. Expand a focused review only when evidence reveals a dependency or failure that affects the requested outcome.

## Measure the full execution graph when in scope

1. Establish the repository visibility, default and protected branches, required check names, deployment path, runner types, workflow files, and relevant billing owner.
2. Inspect workflow runs and jobs over a representative period with `gh run list`, `gh run view`, and the GitHub Actions API. Group by repository, workflow, event, head SHA, conclusion, runner, and job.
3. Report observed job duration separately from estimated billable minutes. Fetch current GitHub billing rules from official documentation before applying rounding, operating-system multipliers, included quotas, or public-repository exceptions. Label estimates and state their assumptions.
4. Distinguish failures that never received a runner from failures inside a job. Account-level budget or payment blocks, missing runner capacity, invalid workflow configuration, and application test failures require different fixes.

Treat repository and deployment topology as evidence, not inference. A GitHub-hosted runner is an ephemeral build machine. Blue and green containers can run on one production server. Neither implies a second production server.

A full audit is measured when every active workflow in scope is classified as necessary, duplicate, excessive, or unable to succeed. A focused review is measured when the affected path has a baseline and enough evidence to choose and validate the fix.

## Choose the smallest relevant change

For a full waste audit, prioritize the following sources of unnecessary work. For a focused latency or reliability request, address the measured bottleneck directly; this list is not a prerequisite checklist.

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

Reuse completed checks when the code tree, dependencies, configuration, and test inputs are unchanged. Run missing local equivalents and syntax checks relevant to the change, and inspect affected triggers and required-check names. Do not repeat a full suite merely because the work entered another review or release phase. Required CI on the exact release commit remains mandatory where repository policy requires it.

When external verification is authorized, dispatch or observe the smallest single run that exercises the changed path. Compare the relevant result with the baseline. Repeat checks only for changed inputs, a new failure, or an unresolved concern; do not re-run the same failure until its cause changed.

Return:

- the requested objective and affected path, its baseline, and the measured result or remaining uncertainty;
- the smallest changes made or proposed and preserved gates; and
- verification results plus any blocker that code cannot fix.

For a full cost audit, also include a baseline by repository and workflow with visibility, triggers, run and job counts, observed duration, estimated billable minutes, failure classes, and a ranked waste ledger. Billing estimates and this broader inventory are unnecessary for a focused latency fix unless the user requested them or they materially affect the decision.

The work is complete when the changed path has relevant verification evidence and its required gates still pass. For trigger, concurrency, or deployment changes, also verify the affected event produces the expected checks, superseded verification cancels safely, and deployment stays within its authorized release boundary.
