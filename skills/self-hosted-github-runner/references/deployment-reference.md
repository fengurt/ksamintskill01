# Self-hosted deployment: recovery and repeatable releases

Use this guide when a GitHub project deploys through a self-hosted runner and releases are stuck. Start with the current workflow; copying OPC Academy's labels, buckets or topology into another project is not a fix.

## Record the actual contract

Before changing anything, record:
- repository / visibility / trusted release branch;
- allowed runner provider, online runner name and full labels;
- runtime version file, test command, build command, deployment command;
- target environment(s), credential source, health endpoint and rollback procedure;
- full source SHA, CI workflow/run, release workflow/run, artifact digest where available.

The user's explicit self-hosted-only or no-TAT requirement takes precedence over template defaults. PR validation needs its own trust boundary; never send untrusted PR code to a persistent production deployment runner.

## Sharing one server across projects

A runner registration is not a whole server. Reuse hardware while separating job directories, runtime selection and credentials.

| Repository scope | Smallest setup |
| --- | --- |
| Several repositories in one organization | Organization runner pool with access limited to selected repositories |
| Repositories under a personal account | Separate repository-scoped runner registrations/processes on the same host, each with its own configuration and work directory |
| Untrusted PRs or projects with different trust | Disposable isolated worker environments; do not reuse a production runner's account, Docker socket or secrets |

Use versioned tool paths or pinned container images. Each job selects Node/Python/etc. from its project baseline; changing PATH for one job does not uninstall another project's tools. Share trusted read-only tool caches; namespace dependency caches by trust scope, OS/architecture, runtime and lockfile. Never reuse another project's node_modules or writable secrets.

Limit host-wide heavy work according to measured CPU/RAM. One organization worker can process queued jobs serially. Multiple per-repository workers need host-wide scheduling/resource controls: GitHub concurrency groups are repository-scoped and do not limit other repositories on the same machine. Separate work directories alone are not a security boundary.

A stopped runner can be started again; no project-specific VM snapshot is required. Idle runner processes normally have little work, but cloud server billing does not necessarily stop when the process stops. For on-demand workers, keep a clean image plus tool caches and create a fresh job environment when needed. An ephemeral runner deregisters after one job; the host/controller must still clean the environment, preserve logs and register a fresh runner. Do not snapshot job tokens or production secrets.

Start with the existing shared host and a small fixed worker count. Add autoscaling or orchestration only when queue times/resource measurements justify it. Repository transfers, new runner registrations, host services and credential redistribution are separate infrastructure changes, not implied by editing a project's release workflow.

Sources: [runner registration scopes](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners), [repository-scoped concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency), [ephemeral runner lifecycle](https://docs.github.com/en/actions/reference/runners/self-hosted-runners), [stopping and restarting runners](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/remove-runners).

## Find the failing layer

```sh
gh run view RUN_ID --repo OWNER/REPO --json status,conclusion,jobs,headSha,url
gh api repos/OWNER/REPO/actions/runs/RUN_ID/jobs \
  --jq '.jobs[] | {name,runner_name,labels,conclusion,steps}'
gh run view RUN_ID --repo OWNER/REPO --log-failed
gh api repos/OWNER/REPO/actions/runners \
  --jq '.runners[] | {name,status,labels:[.labels[].name]}'
```

| Evidence | Check next | Avoid |
| --- | --- | --- |
| Job queued, no worker | All requested labels match an online runner; environment approval | Installing application dependencies locally |
| Empty source URL | Secret scope, environment and producer completion | Retrying an unchanged job |
| Source HTTP 404 | Exact bucket/key and completed upload; authenticated GET | Treating a signed URL as proof the object exists |
| HTTP 401/403 | Token permissions, secret scope, URL expiry, clock | Printing credentials or removing authentication |
| Git fetch times out | A bounded fetch from the actual runner | Concluding all China runners require a new architecture |
| Source hash passes, wrong code | Archive commit/tree against requested SHA | Relabeling an old archive with a new release SHA |
| Dependencies/build fail | Relevant error and repository runtime/lockfile | Changing deployment transport |
| Publish step is slow | Per-phase timestamps, object counts, retries | Calling it network congestion without evidence |
| HTTP 200 but broken page | Browser rendering, lazy assets, affected interaction | Treating SPA HTML as feature acceptance |

A GitHub API metadata failure does not prove a job stopped. Reconcile the existing run before launching another deployment.

## Smallest viable release

1. **Freeze a full commit SHA.** For current-main releases, resolve remote main. Fetch that commit into a fresh job-owned directory with a read-only job token; verify HEAD equals it.
2. **Run the intended checks.** The release workflow must enforce the latest applicable successful CI result for the same SHA, branch and CI workflow. Recheck remote main immediately before publishing if required.
3. **Build with repository versions.** Use the lockfile and version file. Cache verified tools instead of depending on expiring signed URLs. Prefer reusing the tested immutable artifact; document and validate a production rebuild if configuration differs.
4. **Publish through the existing self-hosted command.** Use least-privilege environment credentials, deployment concurrency and existing rollback. Keep static releases separate from API/database releases.
5. **Verify the outcome.** Check region release SHA/digest, real API behavior and the changed user-facing feature. For visual edits, inspect the rendered page; for copy buttons, test selection and clipboard.
6. **Verify repeatability.** Run checks a second time after temporary cleanup. Repeat deployment of the same healthy release should skip mutation. Keep known-good rollback artifacts under retention.

For Git fetch, pass authorization only to that command, never in the remote URL or persisted Git config. Use bounded timeouts/retries and mask any derived authorization value. Validate the target SHA before interpolation. Cleanup may delete only the job-owned temporary directory.

## Only if direct source fetching demonstrably fails

Automate a source handoff; do not create a new manual release ritual:
- archive the final commit, record repository/commit/tree/size/hash;
- upload an immutable commit-scoped object and await completion;
- verify HEAD metadata and authenticated download before dispatch;
- consumer verifies manifest origin, requested commit/tree, size/hash before execution;
- pass metadata per release instead of committing archive digests into workflows;
- generate fresh credentials for the next release and retain retry/rollback artifacts appropriately.

A checksum alone does not establish Git identity. An archive can be verified by rebuilding its Git tree and comparing it with the requested commit's tree fetched from the authenticated GitHub API, before executing project scripts. Missing/export-ignored files must fail this comparison. Otherwise use a Git bundle that proves identity. Never mark an archive of A as release B, even when their application files happen to match.

For a maintainer-triggered source bridge, expose one command that prepares immutable source, generates commit-scoped temporary credentials, verifies readback, dispatches CI, waits for its exact successful run, dispatches deployment and cleans up after terminal success. Explicitly document the trigger contract: CI must start after staging, not race an ordinary push. A second invocation must regenerate everything it needs. Keep the source bridge separate from production build/publish, which stays on the authorized runner.

## What to simplify

- Run OpenTofu only for infrastructure changes; inspect state ownership before retiring infrastructure code.
- Reuse deployment scripts and provider-supported caching; add replication/apply agents only for measured transport or isolation needs.
- Separate PR testing from production deployment; explicitly document any missing isolated runner instead of silently switching providers.
- Maintain one deployment runbook. Remove executable legacy instructions from current project notes; keep dated incident evidence clearly historical.
- Bound retries, print phase start/end timestamps and preserve rollback. Do not trade these away for shorter scripts.

## OPC Academy incident, 2026-09-19

The successful historical release was `072d7e9`, CI run `35422550278`, deployment run `35423108911`.
The runner was self-hosted; deployment took 7m49s, including a 69s build and 6m02s publishing phase. The phase duration alone did not prove a network bottleneck.

The first CI attempt had an empty source URL; the next got HTTP 404 because the object was absent. Upload and authenticated GET verification allowed the third attempt to pass.
The source archive came from `f2e66a9`, while the release label was `072d7e9`; only workflow digest edits differed, but exact source identity was not enforced.
Deleting the temporary source secret after success left both workflows unable to start the next release.

The corrections are exact Git checkout, an executable CI gate, no per-release workflow digest edit, repeatable tool setup, explicit static/API boundaries and documentation that distinguishes HTTP smoke from browser acceptance.

## Completion evidence

Record a concise release note:
```text
Source SHA / tree:
CI run / conclusion:
Deployment run / actual runner:
Artifact digest / rebuild policy:
Live release / API / affected-feature checks:
Rollback artifact:
Temporary cleanup / successful next-run check:
Outstanding limitations:
```
