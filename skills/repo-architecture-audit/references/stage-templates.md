# Stage 1–3 output templates

All three stages are written **from the CSVs**, not from re-reading source. Every claim cites a row
key (`routes|svc|file|line`, `models|svc|table|column`, …). Unknown stays "not in inventory".
Use the user's language for prose; keep the field names below as they are so cards are comparable.

## §1 Service card (one per service)

```
## Service: <name>   path: <path>   detected_by: <…>   version: <…|not found>   frameworks: <…>
Size: <files_scanned> files, <loc> LOC (tree.csv depth 0) · skipped: <n> (<top reasons>)
Responsibility: <from tree.csv responsibility, else "not in inventory">

Entry points (routes.csv)
- pages: <n>   api: <n> (<n> write)   jobs: <n>
- write routes without guard: <n>  → P0-1 rows: <keys>
- guard mechanisms seen: <distinct auth_guard names>

Data (models.csv)
- tables: <list, with column counts>   sources: orm/migration/ddl
- tables also declared elsewhere: <P0-2 subjects>   dangling FKs: <P1-3 subjects>

Access control (permissions.csv)
- mechanisms: <decorator|middleware|const…>   constants: <n> (<unused: P1-4 subjects>)

Audit (audit_points.csv)
- points: <n> (<by mechanism>)   write-route coverage: <a>/<w> (<%>) → P1-1 rows: <keys>

Boundaries (cross_calls.csv, links.csv)
- calls out: <to_service: count, kind>   calls in: <from_service: count>
- unresolved (low): <n> → P2-1 keys
- page → api links: <n>   api → table links: <n>

Open questions for the owner (max 5, each tied to a row key)
```

## §2 Cross-service reconciliation

### 2a Core chains (user supplies 5–8 business chains)
| chain | hop | from | via (links/cross_calls key) | to | tables touched (api_table keys) | guard | audit | gap? |
|---|---|---|---|---|---|---|---|---|
One row per hop. `gap? = yes` when the next hop cannot be found in `links.csv` / `cross_calls.csv`;
do not fill the hop from reading code. List gaps at the end as questions.

### 2b Field dictionary
| concept (normalized) | variants (raw names) | locations (service.table.column) | types | agree? | P1-2 key | reviewer note |
Start from P1-2 rows, then add single-spelling fields that appear in ≥2 tables. Conflicts (agree = no)
go to a second table with the same columns plus "proposed canonical" left blank for the owner.

### 2c Permission matrix
| role / permission | resource (route or handler) | operation (method) | source rows (permissions.csv keys) | status |
`status` ∈ `implemented` (guard found) / `declared-only` (constant exists, no guard uses it) /
`unguarded` (write route, no guard) / `contradiction` (doc says X, code says Y — only when the user
supplies the doc). Render as the heatmap in the HTML plus this table.

### 2d Audit coverage matrix
| service | write route | handler | guard | audit point (key) | event_type | fields_logged | missing? |
One row per write route (routes.csv, method ∈ write_methods). `missing? = yes` ⇔ P1-1 row exists.

## §3 Decision list

Ranked by (severity, change cost). Each item:

```
### D<n>. <one-line statement of the finding, with the number>   [P0|P1|P2] · cost: S|M|L
Evidence: <priority rule id> → <row keys>
Blast radius: <services / routes / tables affected, counted from links.csv>
Options
  A. <minimal change>        — pros / cons / what it does not fix
  B. <structural change>     — pros / cons / migration note
  C. <accept & document>     — when this is legitimate (e.g. intentional public signup route)
Recommendation left to the owner; note which option the evidence favours and why.
```
Severity = the rule level; cost = S (one file), M (one service), L (cross-service or data migration).
Do not merge findings from different rules into one item; MECE applies here too.
