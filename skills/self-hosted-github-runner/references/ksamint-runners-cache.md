# ksamint: organization runners and warm builds

## User-provided context, 2026-09-19

- Future repositories are intended to live under `https://github.com/ksamint/`.
- Promese01's new repository is `https://github.com/ksamint/promese01.git`.
- The reported slow phase is repeated container rebuilding without persistent cache, not an established cross-border transfer problem.
- The reported setup has two US ephemeral workers, still repository-scoped. Organization migration and cache optimization are requested directions, not verified completed infrastructure.

Inspect the actual owner, runner registrations, controller and builder storage before implementation. Do not change this skill repository's remote or mark every repository migrated from this note. Finish or reconcile an active exact-SHA release before a separate infrastructure change; never bypass a failed gate to complete migration.

## Organization pool, not one registration per repository

After migration is authorized:

1. Inspect `ksamint` Settings / Actions / Runners and Runner groups, group availability, repository access, current labels and controller credentials. Use an organization pool for eligible repositories rather than duplicating repository registrations.
2. Register replacements against `https://github.com/ksamint`, obtaining registration tokens from `POST /orgs/ksamint/actions/runners/registration-token`. Select an existing authorized group and role/OS/architecture labels; update workflows to target that group and matching labels. A repository transfer does not migrate its runner controller automatically.
3. Start with selected repositories. Adding all present/future repositories to a shared group is a separate access-policy choice. Separate untrusted PR workers from trusted build/release workers; labels and group membership alone do not isolate credentials or a Docker socket.
4. Drain active jobs, migrate one worker, test authorized repositories and verify exclusion of unauthorized ones, then migrate the second. Keep controller rollback available. Ephemeral workers must still deregister, clean the job environment and register replacements.

Check endpoint-specific permissions before requesting credentials. Organization registration supports a GitHub App or fine-grained token with organization `Self-hosted runners: write`; classic/OAuth tokens require `admin:org` and, for private repositories, `repo`. Ordinary repository `GITHUB_TOKEN` is not an organization administration credential. Group management has its own permission requirements. Keep controller credentials out of jobs; request missing authority rather than broadening access silently. [GitHub runner API](https://docs.github.com/en/rest/actions/self-hosted-runners#create-a-registration-token-for-an-organization), [group access](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access).

## Fix cold builds independently

Organization scope does not itself cause or cure cold builds. Inspect the builder driver, daemon lifetime, volume mounts and cleanup commands. An ephemeral runner registration is compatible with persistent cache; a throwaway nested Docker daemon loses its volumes unless its storage is retained deliberately.

- On a persistent host, retain a dedicated BuildKit state volume outside the disposable runner/workspace. With the `docker-container` driver, use a stable builder identity; if recreating that builder, `docker buildx rm --keep-state` preserves its state for recreation under the same name. Confirm the host Docker storage itself survives. [Docker persistence](https://docs.docker.com/build/builders/drivers/docker-container/#cache-persistence).
- Each of the two hosts has its own local volume. When scheduling across hosts causes cache misses, use an authorized private registry cache via `--cache-from type=registry,ref=<cache-ref>` and `--cache-to type=registry,ref=<cache-ref>,mode=max`. Keep the cache reference separate from the output image; confirm driver support and registry permissions. [Registry cache](https://docs.docker.com/build/cache/backends/registry/).
- Namespace builders/cache refs by repository, image target, platform and trust scope. Isolate concurrent writers with separate refs or serialization. Share only explicitly trusted inputs; PR jobs must not overwrite release caches. Never mount one raw BuildKit state directory into two active daemons.
- Keep dependency layers stable: copy lockfiles before changing application source, use locked installs, exclude irrelevant context and use suitable package cache mounts. Keep secret material in BuildKit secret mounts, not copied files or build arguments. [Cache optimization](https://docs.docker.com/build/cache/optimize/).
- Cleanup must remove job files, credentials and disposable execution state, while retaining only the allowlisted cache volumes. Avoid global volume/system pruning. Set cache size/age limits, garbage collection and disk headroom; never retain production secrets or treat caches as rollback artifacts.

## Acceptance before claiming speedup

Record cold and warm phase timings, cache hits, builder identity, storage usage and source SHA with identical pinned inputs. After job cleanup and runner re-registration, rebuild on the same host; test the second host separately and external cache import if configured. Report cache export/import overhead as well as build time. No fixed speedup is promised.

Verify a cold-cache build still works, a changed lockfile invalidates the correct layers, and untrusted jobs cannot read/write protected cache or credentials. Prefer deploying the tested immutable image by digest, not rebuilding it in production. Maintain host-wide CPU/RAM limits in addition to repository-level workflow concurrency.
