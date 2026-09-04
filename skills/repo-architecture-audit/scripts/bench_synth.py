#!/usr/bin/env python3
"""Generate a synthetic docs/audit directory at a chosen scale to benchmark build_html.py.
No real repo needed. Deterministic (seeded). Usage:
  python bench_synth.py <out_dir> --services 40 --routes-per-service 30 --tables-per-service 8
Then: python build_html.py <out_dir>   (and open index.html, or run the jsdom smoke test in the skill docs)
"""
import argparse, csv, json, os, random
from collections import Counter

COLS = {
    "tree": ["service", "depth", "path", "file_count", "loc", "languages", "responsibility", "responsibility_source"],
    "routes": ["service", "kind", "method", "path", "handler", "file", "line", "module", "auth_guard", "pattern_id", "note"],
    "models": ["service", "source", "table", "column", "type", "nullable", "default", "pk", "fk_to", "file", "line", "pattern_id", "note"],
    "permissions": ["service", "mechanism", "name", "roles_or_perms", "applies_to", "file", "line", "pattern_id", "note"],
    "audit_points": ["service", "mechanism", "function", "event_type", "fields_logged", "file", "line", "pattern_id", "note"],
    "cross_calls": ["from_service", "to_service", "kind", "endpoint_or_topic", "file", "line", "to_service_confidence", "pattern_id", "note"],
    "links": ["kind", "from_service", "from", "to_service", "to", "confidence", "file", "line", "rule"],
    "priorities": ["level", "rule_id", "service", "subject", "evidence_file", "evidence_row", "detail", "suppressed"],
}
WRITE = ["POST", "PUT", "PATCH", "DELETE"]
GUARDS = ["require_auth", "role_required", "CurrentUser", "AuthGuard", "Depends", ""]
ROLES = ["admin", "staff", "user", "auditor"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--services", type=int, default=40)
    ap.add_argument("--routes-per-service", type=int, default=30)
    ap.add_argument("--tables-per-service", type=int, default=8)
    ap.add_argument("--pages", type=int, default=60)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    svcs = [f"svc{i:02d}" for i in range(a.services)]
    rows = {k: [] for k in COLS}
    manifest_services = {}
    for si, s in enumerate(svcs):
        loc = rnd.randint(800, 40000)
        dirs = ["api", "models", "services", "jobs", "utils", "web"][: rnd.randint(2, 6)]
        rows["tree"].append({"service": s, "depth": 0, "path": f"services/{s}", "file_count": loc // 60, "loc": loc,
                             "languages": "py:%d;ts:%d" % (loc * 7 // 10, loc * 3 // 10), "responsibility": "", "responsibility_source": ""})
        rem = loc
        for d in dirs:
            l = rnd.randint(50, max(60, rem // 2)); rem -= l
            rows["tree"].append({"service": s, "depth": 1, "path": f"services/{s}/{d}", "file_count": max(1, l // 60), "loc": l,
                                 "languages": "py:%d" % l, "responsibility": "" if rnd.random() < .6 else f"{d} layer", "responsibility_source": "" if rnd.random() < .6 else "readme"})
            if l > 400:
                for sub in ("core", "impl"):
                    rows["tree"].append({"service": s, "depth": 2, "path": f"services/{s}/{d}/{sub}", "file_count": max(1, l // 120), "loc": l // 2,
                                         "languages": "py:%d" % (l // 2), "responsibility": "", "responsibility_source": ""})
        tables = [f"{s}_t{t}" for t in range(a.tables_per_service)]
        if si > 0 and rnd.random() < .3:  # shared table with previous service
            tables[0] = f"svc{si-1:02d}_t0"
        for t in tables:
            for c in ["id", "user_id" if rnd.random() < .5 else "userId", "status", "created_at", "amount"]:
                rows["models"].append({"service": s, "source": "orm", "table": t, "column": c, "type": rnd.choice(["int", "varchar(20)", "string", "numeric"]),
                                       "nullable": "", "default": "", "pk": "true" if c == "id" else "", "fk_to": "users.id" if c.lower() == "userid" or c == "user_id" else "",
                                       "file": f"services/{s}/models/{t}.py", "line": rnd.randint(1, 200), "pattern_id": "sqlalchemy_model", "note": ""})
        for r in range(a.routes_per_service):
            m = rnd.choice(WRITE + ["GET", "GET", "GET"])
            g = rnd.choice(GUARDS)
            path = f"/{s}/res{r % 9}" + ("/{id}" if r % 3 else "")
            f = f"services/{s}/api/res{r % 9}.py"
            rows["routes"].append({"service": s, "kind": "api", "method": m, "path": path, "handler": f"h{r}", "file": f, "line": r * 7 + 1,
                                   "module": "api", "auth_guard": g, "pattern_id": "flask_fastapi_verb", "note": ""})
            if g:
                rows["permissions"].append({"service": s, "mechanism": "decorator", "name": g, "roles_or_perms": rnd.choice(ROLES) if rnd.random() < .5 else "",
                                            "applies_to": f"h{r}", "file": f, "line": r * 7 + 1, "pattern_id": "guard", "note": ""})
            if m in WRITE and not g:
                rows["priorities"].append({"level": "P0", "rule_id": "P0-1", "service": s, "subject": f"{m} {path}", "evidence_file": "routes.csv",
                                           "evidence_row": f"{s}|{f}|{r*7+1}", "detail": "write route without guard", "suppressed": ""})
            if m in WRITE and rnd.random() < .5:
                rows["priorities"].append({"level": "P1", "rule_id": "P1-1", "service": s, "subject": f"{m} {path}", "evidence_file": "routes.csv",
                                           "evidence_row": f"{s}|{f}|{r*7+1}", "detail": "write route with no audit point in file", "suppressed": ""})
            elif m in WRITE:
                rows["audit_points"].append({"service": s, "mechanism": "call", "function": "audit_log", "event_type": f"{m.lower()}_res{r % 9}", "fields_logged": "user_id,id",
                                             "file": f, "line": r * 7 + 3, "pattern_id": "audit_call", "note": ""})
            t = rnd.choice(tables)
            rows["links"].append({"kind": "api_table", "from_service": s, "from": f"{m} {path}", "to_service": s, "to": t, "confidence": "medium", "file": f, "line": r * 7 + 1, "rule": "model_ref_in_handler_file"})
        # cross calls
        for _ in range(rnd.randint(1, 4)):
            to = rnd.choice(svcs)
            if to == s: continue
            conf = rnd.choice(["high", "high", "medium", "low"])
            rows["cross_calls"].append({"from_service": s, "to_service": to if conf != "low" else "", "kind": "http", "endpoint_or_topic": f"http://{to}/x",
                                        "file": f"services/{s}/services/client.py", "line": rnd.randint(1, 80), "to_service_confidence": conf, "pattern_id": "http_client_url", "note": ""})
            if conf == "low":
                rows["priorities"].append({"level": "P2", "rule_id": "P2-1", "service": s, "subject": f"http://{to}/x", "evidence_file": "cross_calls.csv", "evidence_row": "", "detail": "unresolved target service", "suppressed": ""})
        manifest_services[s] = {"path": f"services/{s}", "detected_by": "synthetic", "languages": {"py": loc}, "framework_hints": ["fastapi"], "version": "",
                                "version_source": "", "files_scanned": loc // 60, "files_skipped": rnd.randint(0, 40), "skip_reasons": {"unsupported_ext": 3, "binary": 1},
                                "rows_per_csv": {}}
    # pages
    web = "web"
    for p in range(a.pages):
        path = f"/page{p}"
        rows["routes"].append({"service": web, "kind": "page", "method": "", "path": path, "handler": "", "file": f"apps/web/pages{path}.tsx", "line": 1, "module": "pages", "auth_guard": "", "pattern_id": "nextjs_pages", "note": ""})
        for _ in range(rnd.randint(1, 4)):
            api = rnd.choice([r for r in rows["routes"] if r["kind"] == "api"])
            rows["links"].append({"kind": "page_api", "from_service": web, "from": path, "to_service": api["service"], "to": f'{api["method"]} {api["path"]}', "confidence": "medium", "file": f"apps/web/pages{path}.tsx", "line": 3, "rule": "url_literal_prefix"})
    rows["tree"].append({"service": web, "depth": 0, "path": "apps/web", "file_count": a.pages, "loc": a.pages * 40, "languages": "tsx:%d" % (a.pages * 40), "responsibility": "", "responsibility_source": ""})
    manifest_services[web] = {"path": "apps/web", "detected_by": "synthetic", "languages": {"tsx": a.pages * 40}, "framework_hints": ["nextjs"], "version": "", "version_source": "",
                              "files_scanned": a.pages, "files_skipped": 0, "skip_reasons": {}, "rows_per_csv": {}}
    # cycle + shared-table + naming priorities
    if len(svcs) > 2:
        rows["priorities"].append({"level": "P0", "rule_id": "P0-3", "service": svcs[0], "subject": f"{svcs[0]}->{svcs[1]}->{svcs[0]}", "evidence_file": "cross_calls.csv", "evidence_row": "", "detail": "call cycle", "suppressed": ""})
        rows["cross_calls"].append({"from_service": svcs[0], "to_service": svcs[1], "kind": "http", "endpoint_or_topic": f"http://{svcs[1]}/a", "file": f"services/{svcs[0]}/services/client.py", "line": 1, "to_service_confidence": "high", "pattern_id": "http_client_url", "note": ""})
        rows["cross_calls"].append({"from_service": svcs[1], "to_service": svcs[0], "kind": "http", "endpoint_or_topic": f"http://{svcs[0]}/b", "file": f"services/{svcs[1]}/services/client.py", "line": 1, "to_service_confidence": "high", "pattern_id": "http_client_url", "note": ""})
    tbl_svcs = {}
    for r in rows["models"]: tbl_svcs.setdefault(r["table"], set()).add(r["service"])
    for t, ss in tbl_svcs.items():
        if len(ss) > 1:
            ss = sorted(ss)
            rows["priorities"].append({"level": "P0", "rule_id": "P0-2", "service": ";".join(ss), "subject": t, "evidence_file": "models.csv", "evidence_row": "", "detail": f"table declared in {len(ss)} services", "suppressed": ""})
            for i in range(len(ss) - 1):
                rows["cross_calls"].append({"from_service": ss[i], "to_service": ss[i + 1], "kind": "db_shared", "endpoint_or_topic": t, "file": "", "line": "", "to_service_confidence": "high", "pattern_id": "shared_table", "note": ""})
    rows["priorities"].append({"level": "P1", "rule_id": "P1-2", "service": ";".join(svcs[:3]), "subject": "userid", "evidence_file": "models.csv",
                               "evidence_row": ";".join(f"{s}|{s}_t1|userId" for s in svcs[:3]), "detail": "spelling variants: userId / user_id", "suppressed": ""})
    for s in svcs[:5]:
        rows["priorities"].append({"level": "P2", "rule_id": "P2-2", "service": s, "subject": f"services/{s}/api", "evidence_file": "tree.csv", "evidence_row": f"{s}|services/{s}/api", "detail": "loc=3000, no responsibility line", "suppressed": ""})
    for k, c in COLS.items():
        with open(os.path.join(a.out, f"{k}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=c); w.writeheader()
            for r in rows[k]: w.writerow({x: r.get(x, "") for x in c})
    for s, m in manifest_services.items():
        m["rows_per_csv"] = {k: sum(1 for r in rows[k] if r.get("service") == s or r.get("from_service") == s) for k in ("routes", "models", "permissions", "audit_points", "cross_calls")}
    manifest = {"project": f"synthetic-{a.services}svc", "generated_at_utc": "2026-01-01T00:00:00Z", "generated_at_local": "2026-01-01T00:00:00+00:00", "extractor_version": "bench",
                "git": {"sha": "0" * 40, "sha_short": "0000000", "branch": "bench", "describe": "", "dirty_tree": False}, "pr": {"number": None, "source": "", "url": ""},
                "services": manifest_services, "totals": {"rows_per_csv": {k: len(v) for k, v in rows.items()},
                                                          "priorities": dict(Counter(p["level"] for p in rows["priorities"])),
                                                          "cross_calls_low_confidence": sum(1 for r in rows["cross_calls"] if r["to_service_confidence"] == "low")},
                "patterns": {"bundled": "synthetic"}}
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print(json.dumps({"services": len(svcs) + 1, **manifest["totals"]["rows_per_csv"]}))


if __name__ == "__main__":
    main()
