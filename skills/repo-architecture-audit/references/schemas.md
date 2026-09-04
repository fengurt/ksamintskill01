# Artifact schemas (column contracts)

All CSVs: UTF-8, header row, columns in this exact order, empty string for unknown, rows sorted
by (service, file, line) so diffs are stable. Paths are relative to the root passed to `audit.py`.
`line` is 1-based. Nothing is inferred: a value that could not be located is left empty.

## tree.csv — Structure
| column | meaning |
|---|---|
| service | service name |
| depth | 0 = service root, ≤ `--max-depth` |
| path | directory path |
| file_count | files under it (recursive, after exclusions) |
| loc | non-blank lines (recursive) |
| languages | top 3 extensions by loc, `ts:1200;py:300` |
| responsibility | one line. Filled only from a README first heading/line in that directory, or from `annotations.json`; otherwise empty |
| responsibility_source | `readme` / `annotation` / empty |

## routes.csv — Entry points
| column | meaning |
|---|---|
| service | |
| kind | `page` / `api` / `job` |
| method | HTTP verb(s) `;`-joined, `ANY`, `GRAPHQL`, or empty for pages/jobs |
| path | route path as written, with the file-level prefix (`APIRouter(prefix=)`, `@Controller`, `@RequestMapping`, `[Route]`) prepended when it is in the same file |
| handler | function/component/class name if captured |
| file | |
| line | line of the decorator / registration call |
| module | parent directory name of the file |
| auth_guard | guard names found on the registration line, on decorators directly above/below it, or in the handler signature (`;`-joined). A name prefixed `!` (e.g. `!AllowAnonymous`, `!Public`) is an explicit "no auth" marker and does not count as a guard |
| pattern_id | which pattern matched |
| note | annotation (from annotations.json) |

## models.csv — Data
| column | meaning |
|---|---|
| service | |
| source | `orm` / `migration` / `ddl` |
| table | table name as written (`__tablename__` / `@Table(name=)` win over the class name); the class name is kept as an alias for link matching |
| column | column name; empty for the table header row |
| type | type as written |
| nullable | `true`/`false`/empty |
| default | as written |
| pk | `true`/empty |
| fk_to | `table.column` or `table` if captured |
| file | |
| line | declaration line (inherited fields keep the base-class line) |
| pattern_id | |
| note | |

DTO / request schemas that are not persisted (Pydantic `BaseModel`, SQLModel without `table=True`,
TypeScript interfaces) are intentionally not rows here.

## permissions.csv — Access control
| column | meaning |
|---|---|
| service | |
| mechanism | `decorator` / `middleware` / `guard` / `const` / `policy` |
| name | guard or constant name |
| roles_or_perms | literal roles/permissions on the line (`;`-joined); route paths and HTTP verbs are excluded |
| applies_to | route path, handler name, or file |
| file | |
| line | |
| pattern_id | `route_line_guard` = found on/around a route registration; otherwise the guard pattern id |
| note | |

## audit_points.csv — Audit / observability
| column | meaning |
|---|---|
| service | |
| mechanism | `audit_table` / `logger` (warn/error level only) / `event` |
| function | enclosing function if captured |
| event_type | first string literal inside the call |
| fields_logged | identifiers inside the call parentheses, best effort |
| file | |
| line | |
| pattern_id | |
| note | |

Definitions of audit helpers (`def audit_log(...)`) are not rows; only call sites are.

## cross_calls.csv — Boundaries
| column | meaning |
|---|---|
| from_service | |
| to_service | resolved service name or empty |
| kind | `http` / `grpc` / `mq` / `shared_lib` / `db_shared` |
| endpoint_or_topic | URL, topic, package, or table |
| file / line | empty for `db_shared` rows (derived from P0-2) |
| to_service_confidence | `high` = URL host / package name equals a service name; `medium` = service name appears in the expression or in the 3 lines above; `low` = unresolved |
| pattern_id | |
| note | |

Relative URLs (`/api/...`) and template URLs with unknown prefix (`${BASE}/x`, `{settings.API}/x`)
are treated as same-origin and go to `links.csv`, not here. Files under test directories are counted
in `tree.csv` but not extracted.

## links.csv — Derived relations
| column | meaning |
|---|---|
| kind | `page_api` (page file → API route), `api_api` (API handler file → API route in another file/service), `api_table` (API route → table referenced in its handler file) |
| from_service | |
| from | page path, file path (api_api), or `METHOD path` |
| to_service | |
| to | `METHOD path` or table |
| confidence | `high` = exact normalized path match; `medium` = prefix/parameter match or model name reference |
| file / line | where the reference was found |
| rule | `url_literal_prefix` / `model_ref_in_handler_file` |

Path normalization for matching: `<int:id>`, `:id`, `[id]`, `(?P<id>…)` all become `{id}`.
When the URL has a host that resolves to a service, only that service's routes are candidates.

## priorities.csv — Rule hits
| column | meaning |
|---|---|
| level | P0 / P1 / P2 |
| rule_id | see SKILL.md |
| service | one or `;`-joined |
| subject | route, table, normalized column (`#type` suffix for type drift), constant, cycle `a->b->a`, directory |
| evidence_file | which CSV |
| evidence_row | composite key(s) of the row(s), `;`-joined: `service|file|line` or `service|table|column` |
| detail | rule-specific detail (variants, explicit-public marker, …) |
| suppressed | `true` if annotations mark it as false positive |

## manifest.json
```json
{
  "project": "…",
  "generated_at_utc": "2026-09-04T10:22:11Z",
  "generated_at_local": "2026-09-04 06:22:11 -0400",
  "extractor_version": "1.0.0",
  "git": {"sha": "…", "sha_short": "…", "branch": "…", "describe": "…", "dirty_tree": false},
  "pr": {"number": null, "source": null, "url": null},
  "services": {
    "<name>": {
      "path": "…", "detected_by": "compose.yml | workspaces | manifest-dir | cli | single-root",
      "languages": {"py": 1200}, "framework_hints": ["fastapi", "sqlalchemy"],
      "version": "1.4.2", "version_source": "package.json",
      "files_scanned": 0, "files_skipped": 0,
      "skip_reasons": {"unsupported_ext": 3, "test_file_counted_not_extracted": 12, "secret": 1},
      "rows_per_csv": {"routes": 0, "models": 0, "permissions": 0, "audit_points": 0, "cross_calls": 0}
    }
  },
  "totals": {"rows_per_csv": {}, "priorities": {"P0": 0, "P1": 0, "P2": 0}, "cross_calls_low_confidence": 0},
  "patterns": {"bundled": "…/patterns.json", "local": null, "rules_local": null}
}
```
`pr.source` is `env:<VAR>` (PR_NUMBER, GITHUB_REF, CI_MERGE_REQUEST_IID, BITBUCKET_PR_ID, CHANGE_ID)
or `gh`; `null` locally is expected.

## annotations.json
```json
{
  "version": 1,
  "entries": {
    "routes|api|src/orders/routes.py|41": {"note": "…", "updated": "2026-09-04T…"},
    "tree|api|src/orders": {"responsibility": "Order lifecycle", "updated": "…"},
    "priorities|P1-2|user_id": {"note": "not a conflict", "false_positive": true}
  }
}
```
Key format per table: `tree|service|path`, `routes|service|file|line`, `models|service|table|column`,
`permissions|service|file|line`, `audit_points|service|file|line`, `cross_calls|from_service|file|line`,
`priorities|rule_id|subject`. Keys use the extracted values verbatim; renaming a file breaks the key on
purpose. In the HTML page a priorities note starting with `fp`, `false positive`, `not a conflict`,
`ok` or `ignore` sets `false_positive: true`. `audit.py` applies the same prefix rule, so a hand-edited
`annotations.json` with only a `note` also suppresses the row (`suppressed = true`; excluded from
`manifest.totals.priorities`).
