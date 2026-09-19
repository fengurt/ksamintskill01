---
name: self-hosted-github-runner
description: Recover and improve GitHub Actions deployments to mainland China. Use for stuck releases, runner selection or sharing, source handoff, CI gates, release verification and rollback. Preserve the project's authorized hosted or self-hosted route; introduce cross-border infrastructure only for a measured need.
metadata:
  short-name: ship
  command-id: k028
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
---

# ship

Recover releases and make the next deployment repeatable. Shortcut: `ship` (`k028`). Canonical invocation: `$self-hosted-github-runner`.

## Choose the smallest working route

1. Read the project's release instructions, workflows and scripts. Record repository visibility, trusted branch, authorized runner provider and online labels, runtime baseline, test/build/deploy commands, target environments, credential source, health checks, CI gate and rollback command. Editing a workflow does not authorize runner registrations, repository transfers or redistribution of credentials.
2. User requirements override defaults and examples in every file of this skill. If self-hosted is required, deployment jobs must explicitly select self-hosted labels; no silent hosted fallback. If TAT is prohibited, remove it from the active deployment path. Actions such as checkout are software, not runner types: respect a separate prohibition on third-party actions if given.
3. For an existing static site or small service, reuse its authorized runner and deployment command. Preserve GitHub-hosted Actions when that is the project's established route. First try a bounded fetch of the exact Git commit. Measure checkout, dependency installation, build and publishing separately before changing architecture.
4. Only choose object-store handoff when the runner's network demonstrably cannot fetch the source reliably. Only introduce replication or a production pull agent when the existing delivery path has a measured limitation or a concrete isolation requirement.
5. Keep PR validation separate from production. Untrusted PR code must not run on persistent deployment machines. If hosted PR runners are also forbidden, an isolated disposable runner is required; report missing capacity rather than silently using hosted runners or claiming skipped checks passed.

For an existing deployment or a stuck project, start with [the reusable deployment guide](references/deployment-reference.md).
For multiple projects sharing a host or on-demand workers, read [Sharing one server](references/deployment-reference.md#sharing-one-server-across-projects). Organization pools may serve selected repositories; personal-account repositories need separate registrations and work directories. Work directories are not security isolation, and repository concurrency cannot limit other repositories. Select project-specific runtimes, namespace caches by trust/runtime/lockfile, and bound host-wide heavy work. An ephemeral registration still needs environment cleanup and replacement by its controller.
For `ksamint/*`, organization runner migration, or cold container builds, read [organization runners and persistent build caches](references/ksamint-runners-cache.md). The user's target organization is `ksamint`; `promese01` now belongs there. Verify each repository's actual owner before changing its remote. Organization registration enables sharing, not cache persistence: keep disposable job environments separate from trusted BuildKit cache storage.
For runner/network failures, read [diagnostics](references/diagnostics.md).
For the optional cross-border pull architecture, read [advanced architecture](references/advanced-architecture.md), then only the channel/protocol references it routes to.
For `vanahom-fb-hom01` specifically, read [its mapping](references/vanahom-fb-hom01.md). Do not copy those hosts or commands into other projects.

## Source, checks and release identity

- Validate the full target SHA before interpolation. Fetch with a read-only job token and bounded retries into a fresh job-owned directory or proven clean checkout. Verify `git rev-parse HEAD` equals the target before running repository code. Scope authorization to the fetch command, mask derived authorization values, and keep credentials out of remote URLs, persisted Git config and logs. Cleanup may remove only the job-owned temporary directory.
- Bind source SHA, CI run SHA and published SHA. A checksum proves byte integrity, not Git identity. Changing the release label does not change the source.
- Enforce the CI gate in the workflow: the latest applicable run of the intended CI workflow for that SHA must be completed/success. An old successful run, another workflow, a PR merge SHA or a manually typed SHA is not sufficient.
- Check current remote main before publishing when the project releases current-main only. Serialize publishing with workflow concurrency and preserve existing rollback behavior.
- Prefer publishing the already-tested artifact where the project supports it. If rebuilding for production configuration, record that distinction, pin inputs and run production validation. Never describe two builds as one.
- Resolve tool versions from the repository baseline. A temporary signed tool URL must not become an undocumented permanent dependency. Cache verified tools; retain checksum verification for downloads.
- Infrastructure tools belong to infrastructure changes. Do not install or run OpenTofu for unrelated content/frontend changes.

### When object-store handoff is necessary

Use one repeatable producer, not shell snippets assembled during each release.

1. Freeze the final source commit; create its archive and record repository, commit, tree, byte length and SHA-256 in a manifest.
2. Upload to an immutable commit-scoped key. Await upload completion, verify object metadata, then test authenticated download and bytes. A URL string or upload command exit alone is not proof of availability.
3. Consumer verifies the manifest's origin/authenticity, repository, requested commit and tree, then archive size/hash before safe extraction. Before executing project scripts, rebuild the archive's Git tree and compare it with the requested commit's tree obtained from authenticated GitHub metadata; missing/export-ignored files must fail. Otherwise use a Git bundle and verify its requested commit. A manifest's claimed tree or checksum alone is insufficient.
4. Pass per-release metadata through the release interface. Do not commit a new archive digest into the workflow on every release: that changes HEAD after the archive was made.
5. Clean temporary credentials and objects only after all consumers have finished. Next release must regenerate its inputs automatically; retry/rollback artifacts need an explicit retention period. Test a second run after cleanup.

For a maintainer-triggered bridge, expose one command: stage immutable source, verify authenticated readback, dispatch CI, await that exact successful run, dispatch deployment, then clean up after terminal success. Document trigger ordering so CI cannot race staging on an ordinary push. The bridge prepares source; production build/publish stays on the authorized runner.

## Verify and report

- Follow asynchronous work to its terminal state. A client timeout does not prove remote work stopped; reconcile the existing run before retrying.
- Verify deployed SHA, important API responses and the affected feature. Static HTML 200 is not proof that React rendered, an image is correct, or clipboard behavior works.
- Keep static, API and database release boundaries explicit. After temporary cleanup, rerun checks to prove the next release can obtain its inputs. Reapplying the same healthy release should verify and skip mutation; retain the known-good rollback artifact.
- Record run URLs, runner labels, commit/artifact identity, step durations, checks and cleanup status in a durable project release note or job summary.
- Keep updates factual: a long step does not prove network congestion. Use timestamps and logs to locate the cause.
- State limitations explicitly: local checks, remote CI, live deployment and browser validation are different evidence.
- For user-authorized releases, continue through the established route. Do not add new approval loops or deploy unrelated projects.

Use the guide's [completion evidence](references/deployment-reference.md#completion-evidence) for the release note. Its OPC Academy incident is historical evidence, not proof that a current deployment or its source identity passed.

## Workflow validation

Run:
```sh
node <skill>/scripts/lint-workflows.mjs .github/workflows
```
For existing `apuch-ci,nanjing` labels, pass
`--roles=apuch-ci,ci-ephemeral,publish --region-prefix=nanjing`.
The linter checks selected workflow patterns; it does not prove source identity, actual runner isolation, environment policy or CI gating. Verify those separately.

Template runner variables are required when used. Populate them with the authorized labels; absent configuration must fail instead of changing runner provider.

## Update checks

When updating this skill, validate frontmatter and local references; exercise the cases in [evals/evals.json](evals/evals.json). These are review scenarios, not evidence that production has passed.
