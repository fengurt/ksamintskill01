# Extractors — what is detected, where, and how to extend

The extractor is regex-based and stdlib-only so it runs anywhere. It is deliberately not an AST
parser: precision comes from narrow patterns plus evidence columns, not from language semantics.
Every hit records `file:line` and `pattern_id`, so a wrong row is cheap to spot and to suppress.

## Service discovery (merged, deduplicated by path)
1. `compose*.yml` / `docker-compose*.yml` — services with `build:` / `build.context:`; `context: .`
   plus `dockerfile: backend/Dockerfile` resolves to `backend/`. Base files win over `*override*`,
   `*deploy*`; when two compose services share a path, the one named like the directory wins.
2. `package.json` `workspaces` and `pnpm-workspace.yaml` globs.
3. Top-level directories holding a manifest (`package.json`, `pyproject.toml`, `go.mod`, `pom.xml`,
   `build.gradle(.kts)`, `composer.json`, `Gemfile`, `Cargo.toml`, `*.csproj`, `mix.exs`, `pubspec.yaml`)
   not already covered.
4. Nothing found → the root is one service.
Override with `--services name=path,...`; give hostnames/aliases with `--service-alias api=backend|gateway`.

## What each dimension is detected from

| Dimension | Language / framework | Pattern ids |
|---|---|---|
| routes (api) | Flask, FastAPI (+ `APIRouter(prefix=)`, `Blueprint(url_prefix=)`), Django `path()/url()` | `flask_route`, `flask_fastapi_verb`, `django_path`, `django_url` |
| | Express/Koa-style `app.get(...)`, `.route().get`, NestJS `@Get` + `@Controller` | `express_verb`, `express_route_chain`, `nest_verb`, `nest_controller` |
| | Spring `@GetMapping` + class `@RequestMapping` | `spring_mapping*`, `spring_class_prefix` |
| | Go gin/echo/chi/net-http | `go_gin_echo`, `go_chi`, `go_http_handle` |
| | Rails `routes.rb`, Laravel `Route::`, ASP.NET `[HttpGet]` + `[Route]` + minimal API, Actix, Axum | `rails_*`, `laravel_route`, `aspnet_*`, `rust_actix`, `rust_axum` |
| | GraphQL `type Query/Mutation` fields | `graphql_op` (method `GRAPHQL`) |
| routes (page) | React Router `<Route path>`, router objects `{ path: '/x', component }` (Vue/TanStack) | `react_router_route`, `router_object_path` |
| | File-based: Next.js `pages/` & `app/`, Nuxt `pages/`, SvelteKit `routes/`, Remix (needs `@remix-run` import) | `page_file_routing` block |
| routes (job) | `@scheduled`, `@Cron`, `cron.schedule`, Celery `@shared_task/periodic_task` | `cron_job` |
| models | SQL `CREATE TABLE` in any file, SQLAlchemy `Column/mapped_column`, SQLModel `table=True` (annotated fields, same-file base classes inherited), Django `models.Model`, Prisma, TypeORM, Sequelize, Mongoose, JPA `@Entity`, GORM structs (tagged), EF Core `DbSet<>`/POCO, Rails `create_table`, Laravel `Schema::create`, knex `createTable`, GraphQL types, protobuf messages | `sql_*`, `sqlalchemy_*`, `sqlmodel_table`, `py_annotated_field`, `django_*`, `prisma_*`, `typeorm_*`, `sequelize_*`, `mongoose_*`, `jpa_*`, `gorm_struct`, `go_struct_field`, `efcore_dbset`, `csharp_*`, `rails_*`, `laravel_*`, `knex_*`, `graphql_*`, `proto_*` |
| permissions | Python auth decorators, DRF `permission_classes`, Nest `@UseGuards/@Roles`, Spring `@PreAuthorize/@Secured/@RolesAllowed`, ASP.NET `[Authorize]`, Laravel `->middleware()` / Gate, Rails `before_action :authenticate…`; guard names on route lines; `ROLE_*`/`PERM_*` constants and `Role.X` enum members | `py_decorator_guard`, `py_permission_classes`, `nest_guard`, `spring_secured`, `aspnet_authorize`, `laravel_*`, `rails_before_action`, `route_line_guard`, `role_const`, `role_enum_member` |
| audit_points | `audit_log(...)`, `AuditLog.create`, `logActivity`, `trackEvent`, … ; logger warn/error/fatal; event bus emit/publish | `audit_call`, `logger_warn_error`, `event_publish` |
| cross_calls | HTTP clients (fetch/axios/requests/httpx/Go http/RestTemplate/HttpClient/Guzzle/Faraday…) with a URL literal or expression; gRPC stubs/channels; MQ publish/subscribe with a topic literal (only in files that mention kafka/rabbit/sqs/…); imports of another service's package | `http_client_url`, `grpc_client`, `mq_topic`, `*_import_pkg` |

### Guard attribution on a route
A route's `auth_guard` collects guard-keyword identifiers from: the registration line (Express/Go
middleware args), decorators directly above **and** below it (Flask puts `@login_required` after the
route decorator), and the handler signature up to the closing parenthesis (FastAPI `Depends(...)`,
`current_user: CurrentUser`). String literals are removed first, so `/login` in a path is not a guard.
Identifiers matching `guard_negative` (`Public`, `AllowAnonymous`, `permitAll`, …) are recorded as
`!Name` and do not count. Keywords live in `guard_keywords` — extend them locally when a project uses
its own vocabulary (e.g. `withSession`, `checkScope`).

### Multi-line declarations
A decorator or registration call with unbalanced parentheses is joined with up to 12 following lines
before matching; the row keeps the first line's number.

## Adding project patterns — `docs/audit/patterns.local.json`
Same shape as `scripts/patterns.json`; lists are appended, dict keys merged, patterns with an
existing `id` replace the bundled one. Minimal example:
```json
{
  "guard_keywords": ["withSession", "checkScope"],
  "framework_hints": [{"id": "hono", "langs": ["typescript"], "regex": "from ['\"]hono['\"]"}],
  "patterns": [
    {"id": "hono_verb", "category": "route_api", "langs": ["typescript"],
     "regex": "\\b(?:app|api)\\.(?P<method>get|post|put|patch|delete)\\(\\s*['\"](?P<path>[^'\"]+)['\"]",
     "handler_from": "same_line_idents"},
    {"id": "our_audit", "category": "audit", "langs": ["*"], "regex": "\\b(?P<name>recordAudit)\\s*\\(", "mechanism": "audit_table"}
  ]
}
```
Pattern keys:
- `category`: `route_api | route_page | route_job | route_prefix | model_table | model_column | guard | role_const | audit | cross_http | cross_grpc | cross_mq | import_pkg`
- `langs`: list of language names from `extensions`, or `["*"]`
- named groups by category — routes: `path`, `method` or `methods`, `handler`; models: `table`, then
  column patterns use `column`, `type`, `rest` (+ `flags_from_rest` sub-regexes for `pk`,
  `nullable_true/false`, `fk`, `default`, `type`); guards: `name`, `roles`; audit: `name`;
  cross calls: `url` / `topic` / `pkg`
- routes: `handler_from` = `next_def | same_line_idents | same_line_component | group | group_last`,
  `default_method`, `path_default`, `requires_scope` (GraphQL type names)
- models: `column_scope` = `indent | brace | paren | ruby_block`, `column_pattern`, `tablename_pattern`,
  `table_from_next_class`, `table_from_var`, `requires_in_scope`, `inherit_fields`, `skip_tables`
- column helpers: `skip_if`, `column_from_next_prop`, `pk_if_decorator`, `pk_types`, `fk_types`,
  `pk_from_lookback`, `nullable_from_lookback`, `fk_from_lookback`, `nullable_from_type`, `nullable_mark_means`
- cross calls: `require_context` (file must mention one of these words)

Rules thresholds: `docs/audit/rules.local.json` mirrors `scripts/rules.json`
(`write_methods`, `P0-2.min_services`, `P1-2.normalize`, `P2-2.max_depth`, `P2-2.top_loc_fraction`, per-rule `enabled`).

## Known limits (state them in the Stage 0 report when relevant)
- Route prefixes are only applied when the prefix and the route are in the **same file**;
  `app.include_router(r, prefix="/v1")` / `app.use("/v1", router)` in another file are not composed.
- Base-class field inheritance is same-file only; mixins imported from elsewhere are missed.
- Regex, not AST: a route registered in a loop, a guard applied via a wrapper function, or a URL built
  by string concatenation across lines is not seen. Check `skip_reasons` and `rows_per_csv` before
  trusting an empty column.
- `to_service` resolution relies on hostnames / package names equal to service names; otherwise use
  `--service-alias`.
- MQ topic → consumer mapping is not derived (topics rarely encode the consumer); it is Stage 2 work.
- Test files are counted in `tree.csv` but not extracted (`test_file_counted_not_extracted`).
