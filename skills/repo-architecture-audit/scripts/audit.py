#!/usr/bin/env python3
"""repo-architecture-audit — Stage 0 extractor.

Usage:
  python audit.py <root> [--out DIR] [--project-name NAME] [--services a=path,b=path]
                  [--service-alias api=backend,gateway] [--patterns local.json]
                  [--rules local.json] [--pr-url-template URL] [--max-depth 3] [--no-html]

Stdlib only. Regex-driven, evidence-first: every row has file+line, unknown cells stay empty.
"""
import argparse, csv, datetime, fnmatch, json, os, re, subprocess, sys
from collections import defaultdict, Counter

EXTRACTOR_VERSION = "1.0.0"
HERE = os.path.dirname(os.path.abspath(__file__))
CSV_COLUMNS = {
    "tree": ["service", "depth", "path", "file_count", "loc", "languages", "responsibility", "responsibility_source"],
    "routes": ["service", "kind", "method", "path", "handler", "file", "line", "module", "auth_guard", "pattern_id", "note"],
    "models": ["service", "source", "table", "column", "type", "nullable", "default", "pk", "fk_to", "file", "line", "pattern_id", "note"],
    "permissions": ["service", "mechanism", "name", "roles_or_perms", "applies_to", "file", "line", "pattern_id", "note"],
    "audit_points": ["service", "mechanism", "function", "event_type", "fields_logged", "file", "line", "pattern_id", "note"],
    "cross_calls": ["from_service", "to_service", "kind", "endpoint_or_topic", "file", "line", "to_service_confidence", "pattern_id", "note"],
    "links": ["kind", "from_service", "from", "to_service", "to", "confidence", "file", "line", "rule"],
    "priorities": ["level", "rule_id", "service", "subject", "evidence_file", "evidence_row", "detail", "suppressed"],
}
MANIFEST_FILES = ["package.json", "pyproject.toml", "requirements.txt", "setup.py", "go.mod", "pom.xml", "build.gradle",
                  "build.gradle.kts", "composer.json", "Gemfile", "Cargo.toml", "mix.exs", "pubspec.yaml"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def deep_merge(base, extra):
    for k, v in extra.items():
        if k == "patterns" and isinstance(v, list):
            byid = {p["id"]: p for p in base.get("patterns", [])}
            for p in v:
                byid[p["id"]] = p
            base["patterns"] = list(byid.values())
        elif isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        elif isinstance(v, list) and isinstance(base.get(k), list) and k != "patterns":
            base[k] = base[k] + [x for x in v if x not in base[k]]
        else:
            base[k] = v
    return base


def rel(root, p):
    return os.path.relpath(p, root).replace(os.sep, "/")


# ----------------------------------------------------------------------------- discovery
def discover_services(root, override, cfg):
    """Merge candidates from compose files, JS/pnpm workspaces and top-level manifest dirs; dedupe by path."""
    if override:
        out = {}
        for pair in override.split(","):
            name, path = pair.split("=", 1)
            out[name.strip()] = {"path": path.strip().strip("/") or ".", "detected_by": "cli"}
        return out
    found = {}  # path -> (name, detected_by)
    def add(name, path, by):
        path = path.strip("/") or "."
        if path == ".": return
        base = path.split("/")[-1]
        if path in found:
            if name == base and found[path][0] != base: found[path] = (name, by)   # prefer name == directory
            return
        found[path] = (name, by)
    # 1. compose files (all of them; infra services without build: are skipped naturally)
    compose_files = [fn for fn in os.listdir(root) if re.match(r"^(docker-)?compose[\w\.\-]*\.ya?ml$", fn)]
    compose_files.sort(key=lambda fn: (bool(re.search(r"override|deploy|prod|dev|test|local|ci", fn)), fn))   # base files first
    for fn in compose_files:
        text = open(os.path.join(root, fn), encoding="utf-8", errors="ignore").read()
        m = re.search(r"^services:\s*$(.*?)(?=^\w|\Z)", text, re.S | re.M)
        if not m: continue
        cur, ctx, dockerfile = None, {}, {}
        for line in m.group(1).splitlines():
            sm = re.match(r"^  ([\w\-\.]+):\s*$", line)
            if sm: cur = sm.group(1); continue
            if not cur: continue
            bm = re.match(r"^\s+build:\s*['\"]?([^'\"\s#]+)\s*$", line)
            cm = re.match(r"^\s+context:\s*['\"]?([^'\"\s#]+)", line)
            dm = re.match(r"^\s+dockerfile:\s*['\"]?([^'\"\s#]+)", line)
            if bm or cm: ctx[cur] = (bm or cm).group(1)
            if dm: dockerfile[cur] = dm.group(1)
        for name, c in ctx.items():
            cand = os.path.normpath(os.path.join(root, c))
            if cand == os.path.normpath(root) and name in dockerfile:
                cand = os.path.normpath(os.path.join(root, os.path.dirname(dockerfile[name])))
            if os.path.isdir(cand) and cand != os.path.normpath(root):
                add(name, rel(root, cand), fn)
    # 2. workspaces
    globs = []
    pj = os.path.join(root, "package.json")
    if os.path.exists(pj):
        try:
            ws = load_json(pj).get("workspaces")
            if isinstance(ws, dict): ws = ws.get("packages", [])
            globs += ws or []
        except Exception: pass
    pw = os.path.join(root, "pnpm-workspace.yaml")
    if os.path.exists(pw):
        globs += re.findall(r"^\s*-\s*['\"]?([^'\"\s#]+)", open(pw, encoding="utf-8", errors="ignore").read(), re.M)
    for g in globs:
        g = g.rstrip("/")
        if g.startswith("!"): continue
        base = g.split("*")[0].rstrip("/")
        bp = os.path.join(root, base)
        if "*" in g and os.path.isdir(bp):
            for d in sorted(os.listdir(bp)):
                dp = os.path.join(bp, d)
                if os.path.isdir(dp) and os.path.exists(os.path.join(dp, "package.json")):
                    add(d, rel(root, dp), "workspaces")
        elif os.path.isdir(bp):
            add(os.path.basename(bp), rel(root, bp), "workspaces")
    # 3. top-level dirs with a manifest not already covered
    for d in sorted(os.listdir(root)):
        dp = os.path.join(root, d)
        if d in cfg["exclude_dirs"] or not os.path.isdir(dp) or d.startswith("."): continue
        if any(p == d or p.startswith(d + "/") for p in found): continue
        has_manifest = any(os.path.exists(os.path.join(dp, m)) for m in MANIFEST_FILES) or any(x.endswith(".csproj") for x in os.listdir(dp))
        if has_manifest: add(d, d, "manifest-dir")
    if not found:
        return {os.path.basename(os.path.abspath(root)) or "root": {"path": ".", "detected_by": "single-root"}}
    out = {}
    for path, (name, by) in sorted(found.items(), key=lambda kv: kv[0]):
        n = name
        while n in out: n = n + "_" + path.split("/")[-1]
        out[n] = {"path": path, "detected_by": by}
    return out


# ----------------------------------------------------------------------------- file walking
def is_secret(name, cfg):
    return any(fnmatch.fnmatch(name, g) for g in cfg["secret_globs"])


def walk_service(root, svc_path, cfg, other_service_paths):
    base = os.path.join(root, svc_path)
    files, skipped = [], Counter()
    for dp, dns, fns in os.walk(base):
        rdp = rel(root, dp)
        dns[:] = [d for d in sorted(dns) if d not in cfg["exclude_dirs"] and not (d.startswith(".") and d != ".")
                  and not any(rel(root, os.path.join(dp, d)) == o for o in other_service_paths)]
        for fn in sorted(fns):
            fp = os.path.join(dp, fn)
            if is_secret(fn, cfg):
                skipped["secret"] += 1; continue
            if any(fnmatch.fnmatch(fn, g) for g in cfg["exclude_globs"]):
                skipped["excluded_glob"] += 1; continue
            ext = fn.rsplit(".", 1)[-1].lower() if "." in fn else ""
            lang = cfg["extensions"].get(ext)
            try:
                size = os.path.getsize(fp)
            except OSError:
                skipped["unreadable"] += 1; continue
            if size > 2_000_000:
                skipped["too_large"] += 1; continue
            files.append((fp, rel(root, fp), lang, ext))
    return files, skipped


def read_lines(fp):
    try:
        with open(fp, encoding="utf-8", errors="strict") as f:
            return f.read().splitlines()
    except UnicodeDecodeError:
        try:
            with open(fp, encoding="latin-1") as f:
                return f.read().splitlines()
        except Exception:
            return None
    except Exception:
        return None


# ----------------------------------------------------------------------------- helpers
DEF_RE = re.compile(r"^\s*(?:(?:export\s+)?(?:async\s+)?(?:default\s+)?(?:def|function|fn|func|class|public|private|protected|static|override|suspend|async|final|internal)\b[^=(]*?\b(\w+)\s*[\(<]|(?:const|let|var|val)\s+(\w+)\s*=|(\w+)\s*\([^)]*\)\s*(?::\s*[\w<>\[\]\|,\s]+)?\s*\{|(?:public|private|protected)\s+[\w<>\[\]]+\s+(\w+)\s*\()")
HTTP_VERBS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "ANY"}
IDENT_RE = re.compile(r"\b([A-Za-z_]\w{2,})\b")
STRING_RE = re.compile(r"['\"`]([^'\"`]{1,80})['\"`]")


def next_def_name(lines, i, maxlook=8):
    for j in range(i + 1, min(len(lines), i + 1 + maxlook)):
        m = DEF_RE.match(lines[j])
        if m:
            return next(g for g in m.groups() if g)
    return ""


def same_line_idents(line, after_index):
    seg = line[after_index:]
    ids = [x for x in IDENT_RE.findall(seg) if x not in ("async", "await", "function", "req", "res", "next", "ctx", "true", "false", "null")]
    return ids[-1] if ids else ""


def guard_names_on(line, cfg):
    line = re.sub(r"(['\"`])(?:\\.|(?!\1).)*\1", "''", line)   # drop string literals: path text is not a guard
    out = []
    for m in IDENT_RE.finditer(line):
        w = m.group(1)
        wl = w.lower()
        if any(wl == n or wl.startswith(n) for n in cfg["guard_negative"]):
            out.append("!" + w)          # explicit "public / anonymous" marker, kept visible but not counted as a guard
        elif any(k in wl for k in cfg["guard_keywords"]) and wl not in ("author", "authors"):
            out.append(w)
    return out


def norm_path(p):
    p = re.sub(r"<[^>:]*:?(\w+)>", r"{\1}", p)      # flask <int:id>
    p = re.sub(r":(\w+)", r"{\1}", p)                # express :id
    p = re.sub(r"\[\.?\.?\.?(\w+)\]", r"{\1}", p)    # next [id]
    p = re.sub(r"\(\?P<(\w+)>[^)]*\)", r"{\1}", p)   # django regex
    p = p.replace("^", "").replace("$", "")
    if not p.startswith("/"):
        p = "/" + p
    return re.sub(r"/{2,}", "/", p).rstrip("/") or "/"


# ----------------------------------------------------------------------------- extraction
class Extractor:
    def __init__(self, root, cfg, service_names, aliases):
        self.root, self.cfg = root, cfg
        self.service_names = service_names
        self.aliases = aliases  # alias(lower) -> service
        self.compiled = []
        for p in cfg["patterns"]:
            try:
                p["_re"] = re.compile(p["regex"])
                for key in ("skip_if", "requires_in_scope", "require_context", "tablename_pattern", "table_from_var",
                            "pk_from_lookback", "nullable_from_lookback", "fk_from_lookback", "nullable_from_type"):
                    if key in p:
                        p["_" + key] = re.compile(p[key], re.I if key == "require_context" else 0)
                if "flags_from_rest" in p:
                    p["_ffr"] = {k: re.compile(v, re.I if p.get("source") == "ddl" else 0) for k, v in p["flags_from_rest"].items()}
                self.compiled.append(p)
            except re.error as e:
                print(f"[patterns] skipping {p['id']}: {e}", file=sys.stderr)
        self.byid = {p["id"]: p for p in self.compiled}
        self.hints = [(h["id"], set(h["langs"]), re.compile(h["regex"])) for h in cfg["framework_hints"]]
        self.rows = {k: [] for k in CSV_COLUMNS}
        self.file_refs = {}  # (service, rfile) -> {"urls": [...], "idents": set()}
        self.role_defs, self.role_uses = defaultdict(list), defaultdict(list)
        self.table_aliases = defaultdict(set)  # table -> {class/model names}

    def applies(self, p, lang):
        return "*" in p["langs"] or (lang in p["langs"])

    def resolve_service(self, text, from_service):
        t = text.lower()
        for name in self.service_names:
            if name == from_service: continue
            nl = name.lower()
            if re.search(r"(?<![\w\-])" + re.escape(nl) + r"(?![\w\-])", t):
                return name, "high"
        for alias, svc in self.aliases.items():
            if svc == from_service: continue
            if alias in t:
                return svc, "medium"
        return "", "low"

    def extract_file(self, service, fp, rfile, lang, ext, stats):
        lines = read_lines(fp)
        if lines is None:
            stats["skip"]["undecodable"] += 1; return
        stats["files"] += 1
        loc = sum(1 for l in lines if l.strip())
        stats["langs"][ext] += loc
        text = "\n".join(lines)
        for hid, hl, hre in self.hints:
            if lang in hl and hre.search(text):
                stats["frameworks"].add(hid)
        parts = rfile.split("/")
        if any(pt in self.cfg.get("test_dir_names", []) for pt in parts[:-1]) or re.search(r"(?:^|[._\-])(?:test|spec)s?[._\-]|_test\.\w+$|\.test\.\w+$|\.spec\.\w+$", parts[-1]):
            stats["skip"]["test_file_counted_not_extracted"] += 1
            return
        mod = rfile.split("/")
        module = mod[-2] if len(mod) > 1 else ""
        svc_rel = rfile
        refs = self.file_refs.setdefault((service, rfile), {"urls": [], "idents": set(), "tables_ref": set()})
        prefix = ""
        gql_scope = ""
        i = 0
        n = len(lines)
        while i < n:
            i0 = i
            line = lines[i]
            if line.count("(") > line.count(")") and re.match(r"^\s*(?:@|\[|\w[\w\.]*\.(?:get|post|put|patch|delete|route|Get|Post|Put|Patch|Delete|GET|POST|PUT|PATCH|DELETE|Map\w+)\s*\()", line):
                joined, depth = line, line.count("(") - line.count(")")
                for j in range(i + 1, min(n, i + 12)):
                    joined += " " + lines[j].strip()
                    depth += lines[j].count("(") - lines[j].count(")")
                    if depth <= 0: break
                line = joined
            if lang == "graphql":
                gm = re.match(r"^\s*type\s+(\w+)", line)
                if gm: gql_scope = gm.group(1)
            consumed = False
            for p in self.compiled:
                if not self.applies(p, lang): continue
                cat = p["category"]
                if cat == "model_column":
                    continue
                m = p["_re"].search(line)
                if not m: continue
                g = m.groupdict()
                if cat == "route_prefix":
                    prefix = g.get("path") or ""; continue
                if cat in ("route_api", "route_page", "route_job"):
                    if p.get("requires_scope") and gql_scope not in p["requires_scope"]:
                        continue
                    if p.get("require_on_route_line"): continue
                    path = g.get("path")
                    if path is None: path = p.get("path_default", "")
                    if p.get("path_prefix_slash"): path = "/" + path
                    if p.get("requires_scope"):
                        path = "/" + gql_scope + "/" + (g.get("handler") or "")
                    methods = g.get("methods")
                    if methods:
                        method = ";".join(sorted(x.strip(" '\"").upper() for x in methods.split(",") if x.strip()))
                    else:
                        method = (g.get("method") or p.get("default_method", "")).upper()
                        method = {"REQUEST": "ANY", "ALL": "ANY", "MATCH": "ANY", "RESOURCE": "ANY", "APIRESOURCE": "ANY"}.get(method, method)
                    hf = p.get("handler_from")
                    handler = g.get("handler") or ""
                    if hf == "group_last":
                        toks = [t.strip() for t in handler.split(",") if t.strip()]
                        handler = re.sub(r"[()]", "", toks[-1]) if toks else ""
                    if hf == "next_def": handler = handler or next_def_name(lines, i)
                    elif hf == "same_line_idents": handler = handler or same_line_idents(line, m.end())
                    elif hf == "same_line_component":
                        cm = re.search(r"(?:element|component)\s*[=:]\s*\{?\s*<?\s*(\w+)", line)
                        handler = cm.group(1) if cm else handler
                    guards = set(guard_names_on(line, self.cfg))
                    LB = self.cfg["guard_lookback_lines"]
                    for j in range(i - 1, max(-1, i - 1 - LB), -1):      # decorators above
                        if not lines[j].lstrip().startswith(("@", "[")): break
                        guards.update(guard_names_on(lines[j], self.cfg))
                    for j in range(i + 1, min(n, i + 1 + LB)):            # decorators below (Flask style)
                        if not lines[j].lstrip().startswith(("@", "[")): break
                        guards.update(guard_names_on(lines[j], self.cfg))
                    for j in range(i + 1, min(n, i + 1 + LB + 8)):        # function signature (FastAPI Depends, injected user)
                        if DEF_RE.match(lines[j]) and re.match(r"^\s*(?:async\s+)?(?:def|func|fn|function|public|private|protected)\b", lines[j]):
                            sig = lines[j]
                            for k in range(j + 1, min(n, j + 12)):
                                if re.search(r"\)\s*(?:->\s*[^:]+)?\s*[:{]\s*$", sig) or re.search(r"[:{]\s*$", sig): break
                                sig += " " + lines[k].strip()
                            guards.update(x for x in guard_names_on(sig, self.cfg) if x != handler)
                            break
                    for k in list(guards):
                        if k.lower() in ("route", "routes", "router", "require") or re.match(r"^(?:ROLE|PERM|PERMISSION|SCOPE)_", k):
                            guards.discard(k)
                    full = (prefix.rstrip("/") + "/" + path.lstrip("/")) if prefix and cat == "route_api" and not p.get("requires_scope") else path
                    self.rows["routes"].append({
                        "service": service, "kind": cat.split("_")[1], "method": method, "path": full,
                        "handler": handler, "file": rfile, "line": i + 1, "module": module,
                        "auth_guard": ";".join(sorted(guards)), "pattern_id": p["id"], "note": ""})
                    for gname in guards:
                        self.rows["permissions"].append({"service": service, "mechanism": "middleware" if lang in ("javascript", "typescript", "go", "php") else "decorator",
                                                         "name": gname, "roles_or_perms": ";".join(x for x in STRING_RE.findall(line) if not x.startswith("/") and x.upper() not in HTTP_VERBS)[:200], "applies_to": full,
                                                         "file": rfile, "line": i + 1, "pattern_id": "route_line_guard", "note": ""})
                elif cat == "model_table":
                    if p.get("skip_tables") and g.get("table") in p["skip_tables"]: continue
                    i = self.extract_model(service, p, g, lines, i, rfile, lang, module)
                    consumed = True
                    break
                elif cat == "guard":
                    if p.get("require_on_route_line"): continue
                    name = g.get("name") or p.get("name_const", "")
                    roles = g.get("roles") or ""
                    applies = next_def_name(lines, i) or ""
                    self.rows["permissions"].append({"service": service, "mechanism": p.get("mechanism", "guard"), "name": name,
                                                     "roles_or_perms": ";".join(x.strip() for x in re.split(r"[,;]", roles) if x.strip())[:200],
                                                     "applies_to": applies or rfile, "file": rfile, "line": i + 1, "pattern_id": p["id"], "note": ""})
                    for r in re.findall(r"\b((?:ROLE|PERM|PERMISSION|SCOPE)_[A-Z0-9_]+)\b", roles):
                        self.role_uses[r].append((service, rfile, i + 1))
                elif cat == "role_const":
                    name = g["name"]
                    if re.search(r"^\s*(?:export\s+)?(?:const|static|final|val|public|private|enum|class|\w+\s*=)|=\s*['\"]", line) and re.search(re.escape(name) + r"\s*[=:(]", line):
                        self.role_defs[name].append((service, rfile, i + 1))
                        self.rows["permissions"].append({"service": service, "mechanism": "const", "name": name,
                                                         "roles_or_perms": ";".join(STRING_RE.findall(line)[:3]), "applies_to": rfile,
                                                         "file": rfile, "line": i + 1, "pattern_id": p["id"], "note": ""})
                    else:
                        self.role_uses[name].append((service, rfile, i + 1))
                elif cat == "audit":
                    dm = DEF_RE.match(line)
                    if dm and next((x for x in dm.groups() if x), "") == g.get("name", ""): continue
                    seg = line[m.end():]
                    depth = 1 if seg.startswith("(") else 0
                    cut = len(seg)
                    for ci, ch in enumerate(seg):
                        if ch == "(": depth += 1
                        elif ch == ")":
                            depth -= 1
                            if depth <= 0: cut = ci; break
                    seg = seg[:cut]
                    strings = STRING_RE.findall(seg)
                    idents = [x for x in IDENT_RE.findall(seg) if not x[0].isupper() or "_" in x][:8]
                    func = self.enclosing_function(lines, i)
                    self.rows["audit_points"].append({"service": service, "mechanism": p.get("mechanism", "logger"), "function": func,
                                                      "event_type": strings[0] if strings else "", "fields_logged": ";".join(dict.fromkeys(idents)),
                                                      "file": rfile, "line": i + 1, "pattern_id": p["id"], "note": ""})
                elif cat in ("cross_http", "cross_grpc", "cross_mq"):
                    if p.get("_require_context") and not p["_require_context"].search(text):
                        continue
                    target = g.get("url") or g.get("url2") or g.get("topic") or ""
                    target = re.sub(r"^[fFrRbBu]{1,2}(?=['\"`])", "", target).strip("'\"` ")
                    if re.match(r"^(?:\$\{|\{)", target) and "://" not in target:
                        target = "/" + target        # template with unknown prefix: treat as same-origin, not a cross call
                    if cat == "cross_http":
                        if not target or target in ("req", "res", "url", "path", "options", "config"):
                            continue
                        hm0 = re.match(r"^[a-z][a-z0-9+\-.]*://([^/:'\"`\s]+)", target, re.I)
                        host_svc = self.resolve_service(hm0.group(1), service)[0] if hm0 else ""
                        refs["urls"].append((target, i + 1, host_svc))
                        if target.startswith("/"):
                            continue  # relative URL: intra-service or same-origin call → links.csv, not a cross call
                        hm = re.match(r"^[a-z][a-z0-9+\-.]*://([^/:'\"`\s]+)", target, re.I)
                        if hm:
                            to, conf = self.resolve_service(hm.group(1), service)   # host only
                        else:
                            to, conf = self.resolve_service(target, service)         # expression / variable name
                            if conf == "high": conf = "medium"
                    else:
                        to, conf = self.resolve_service(target, service)
                    if conf == "low":
                        ctx = " ".join(lines[max(0, i - 3):i + 1])
                        to2, conf2 = self.resolve_service(ctx, service)
                        if conf2 != "low": to, conf = to2, "medium"
                    self.rows["cross_calls"].append({"from_service": service, "to_service": to, "kind": cat.split("_")[1],
                                                     "endpoint_or_topic": target[:200], "file": rfile, "line": i + 1,
                                                     "to_service_confidence": conf, "pattern_id": p["id"], "note": ""})
                elif cat == "import_pkg":
                    pkg = g.get("pkg") or g.get("pkg2") or ""
                    to, conf = self.resolve_service(pkg, service)
                    if to and conf == "high":
                        self.rows["cross_calls"].append({"from_service": service, "to_service": to, "kind": "shared_lib",
                                                         "endpoint_or_topic": pkg, "file": rfile, "line": i + 1,
                                                         "to_service_confidence": "high", "pattern_id": p["id"], "note": ""})
            refs["idents"].update(x for x in IDENT_RE.findall(line) if x[0].isupper() or "_" in x)
            if consumed:
                for l2 in lines[i0:i]: refs["idents"].update(x for x in IDENT_RE.findall(l2) if x[0].isupper() or "_" in x)
                continue
            i += 1

    def enclosing_function(self, lines, i):
        for j in range(i, max(-1, i - 80), -1):
            m = DEF_RE.match(lines[j])
            if m and re.match(r"^\s*(?:export\s+)?(?:async\s+)?(?:def|function|fn|func|public|private|protected|static|suspend)\b", lines[j]):
                return next(g for g in m.groups() if g)
        return ""

    def extract_model(self, service, p, g, lines, i, rfile, lang, module):
        table = g.get("table") or ""
        start = i
        scope = p.get("column_scope")
        cp = self.byid.get(p.get("column_pattern", ""))
        if p.get("table_from_var"):
            for j in range(i, max(-1, i - 3), -1):
                vm = re.search(p["table_from_var"], lines[j])
                if vm: table = vm.group("table"); break
        if p.get("table_from_next_class"):
            for j in range(i, min(len(lines), i + 6)):
                cm = re.search(r"\b(?:class|struct)\s+(\w+)", lines[j])
                if cm: table = table or cm.group(1); i = j; break
        # find scope
        body_start = i + 1
        end = body_start
        if scope == "indent":
            base_indent = len(lines[start]) - len(lines[start].lstrip())
            j = body_start
            while j < len(lines):
                l = lines[j]
                if l.strip() and (len(l) - len(l.lstrip())) <= base_indent and not l.lstrip().startswith(("#", ")")):
                    break
                j += 1
            end = j
        elif scope in ("brace", "paren"):
            open_c, close_c = ("{", "}") if scope == "brace" else ("(", ")")
            depth, j, seen = 0, i, False
            while j < len(lines) and j < i + 400:
                depth += lines[j].count(open_c) - lines[j].count(close_c)
                if lines[j].count(open_c): seen = True
                if seen and depth <= 0:
                    break
                j += 1
            end = j + 1
            if not seen: end = body_start
        elif scope == "ruby_block":
            j = body_start
            while j < len(lines) and not re.match(r"^\s*end\b", lines[j]): j += 1
            end = j
        body = lines[body_start:end]
        if p.get("_requires_in_scope") and not p["_requires_in_scope"].search("\n".join(body)):
            return i + 1
        class_name = table
        if p.get("_tablename_pattern"):
            tm = p["_tablename_pattern"].search("\n".join(lines[max(0, start - 3):end]))
            if tm: table = tm.group("table")
        if class_name and class_name != table: self.table_aliases[table].add(class_name)
        if not table:
            return i + 1
        body = [(body_start + k, l) for k, l in enumerate(body)]
        if p.get("inherit_fields") and scope == "indent":
            bases = re.findall(r"\b([A-Z]\w+)\b", lines[start][lines[start].find("(") + 1:lines[start].rfind(")")])
            for b in bases:                                   # fields declared on same-file base classes (mixins, SQLModel bases)
                for bj, bl in enumerate(lines):
                    if re.match(r"^\s*class\s+" + re.escape(b) + r"\s*[\(:]", bl) and bj != start:
                        bind = len(bl) - len(bl.lstrip()); bk = bj + 1
                        while bk < len(lines) and (not lines[bk].strip() or (len(lines[bk]) - len(lines[bk].lstrip())) > bind): bk += 1
                        body = [(bj + 1 + k, l) for k, l in enumerate(lines[bj + 1:bk])] + body
                        break
        self.rows["models"].append({"service": service, "source": p.get("source", "orm"), "table": table, "column": "", "type": "",
                                    "nullable": "", "default": "", "pk": "", "fk_to": "", "file": rfile, "line": start + 1,
                                    "pattern_id": p["id"], "note": ""})
        if cp:
            seen_cols = set()
            for ln, l in body:
                if cp.get("_skip_if") and cp["_skip_if"].search(l): continue
                m = cp["_re"].search(l)
                if not m: continue
                cg = m.groupdict()
                col = cg.get("column") or ""
                typ = cg.get("type") or ""
                rest = cg.get("rest") or ""
                nullable, pk, fk, default = "", "", "", ""
                if cp.get("column_from_next_prop"):
                    for jj in range(ln + 1, min(len(lines), ln + 3)):
                        pm = re.match(r"^\s*(?:readonly\s+)?(\w+)\s*[\?!]?\s*:\s*([\w<>\[\]\|\s]+)", lines[jj])
                        if pm: col = pm.group(1); typ = typ or pm.group(2).strip(); break
                    if cp.get("pk_if_decorator") and cp["pk_if_decorator"] in l: pk = "true"
                if cp.get("_ffr"):
                    for key, rx in cp["_ffr"].items():
                        fm = rx.search(rest if key != "type" or not typ else "")
                        if key == "type" and not typ:
                            fm = rx.search(rest)
                            if fm: typ = fm.group("type")
                            continue
                        if not fm: continue
                        if key == "pk": pk = "true"
                        elif key == "nullable_false": nullable = "false"
                        elif key == "nullable_true": nullable = "true"
                        elif key == "fk":
                            fk = fm.group("fk") or ""
                            fc = fm.groupdict().get("fkcol")
                            if fc: fk = fk + "." + fc
                        elif key == "default": default = (fm.group("default") or "").strip()
                if cg.get("nullable_mark"):
                    nullable = "false" if cp.get("nullable_mark_means") == "not_null" else "true"
                if cp.get("fk_types") and typ in cp["fk_types"]: fk = fk or col
                if cp.get("pk_types") and typ in cp["pk_types"]: pk = "true"
                if cp.get("_pk_from_lookback") or cp.get("_nullable_from_lookback") or cp.get("_fk_from_lookback"):
                    lb = "\n".join(lines[max(body_start, ln - 4):ln])
                    if cp.get("_pk_from_lookback") and cp["_pk_from_lookback"].search(lb): pk = "true"
                    if cp.get("_nullable_from_lookback") and cp["_nullable_from_lookback"].search(lb): nullable = "false"
                    if cp.get("_fk_from_lookback"):
                        fm = cp["_fk_from_lookback"].search(lb)
                        if fm: fk = (fm.groupdict().get("fk") or typ)
                if cp.get("_nullable_from_type") and cp["_nullable_from_type"].search(typ): nullable = "true"
                if col.lower() in ("primary", "foreign", "constraint", "unique", "index", "key", "check"): continue
                if col in seen_cols: continue
                seen_cols.add(col)
                self.rows["models"].append({"service": service, "source": p.get("source", "orm"), "table": table, "column": col,
                                            "type": typ.strip(), "nullable": nullable, "default": default, "pk": pk, "fk_to": fk,
                                            "file": rfile, "line": ln + 1, "pattern_id": cp["id"], "note": ""})
        return max(end, i + 1)


# ----------------------------------------------------------------------------- file-based page routes
def file_based_routes(root, service, svc_path, cfg, files, stats):
    rows = []
    for rule in cfg.get("page_file_routing", []):
        if rule.get("requires_hint") and rule["requires_hint"] not in stats["frameworks"]:
            continue
        for _, rf, lang, ext in files:
            parts = rf.split("/")
            if rule["root_glob"] not in parts or ext not in rule["exts"]: continue
            idx = parts.index(rule["root_glob"])
            sub = parts[idx + 1:]
            if not sub: continue
            stem = sub[-1].rsplit(".", 1)[0]
            if any(seg.startswith("_") for seg in sub): continue
            kind = "page"
            if rule.get("page_file") or rule.get("api_file"):
                if stem == rule.get("api_file"): kind = "api"
                elif stem == rule.get("page_file"): kind = "page"
                else: continue
                segs = sub[:-1]
            else:
                if rule.get("api_subdir") and sub[0] == rule["api_subdir"]:
                    kind = "api"
                segs = sub[:-1] + ([] if stem == rule.get("index_file") else [stem])
            if rule.get("dot_routing"):
                segs = [s for seg in segs for s in seg.split(".")]
            segs = [s for s in segs if not (s.startswith("(") and s.endswith(")"))]
            path = norm_path("/" + "/".join(segs))
            rows.append({"service": service, "kind": kind, "method": "ANY" if kind == "api" else "", "path": path, "handler": stem,
                         "file": rf, "line": 1, "module": sub[0] if len(sub) > 1 else "", "auth_guard": "",
                         "pattern_id": rule["id"], "note": ""})
            stats["frameworks"].add(rule["id"])
    return rows


# ----------------------------------------------------------------------------- derived links
def derive_links(ex, services):
    links = []
    api_routes = [r for r in ex.rows["routes"] if r["kind"] == "api"]
    api_by_norm = defaultdict(list)
    for r in api_routes:
        api_by_norm[norm_path(r["path"])].append(r)
    norms = sorted(api_by_norm.keys(), key=len, reverse=True)
    page_files = {(r["service"], r["file"]): r for r in ex.rows["routes"] if r["kind"] == "page"}
    for (svc, rf), refs in ex.file_refs.items():
        page = page_files.get((svc, rf))
        for url, line, host_svc in refs["urls"]:
            u = re.sub(r"https?://[^/]+", "", url)
            u = re.sub(r"\$\{[^}]*\}", "{x}", u)
            if not u.startswith("/"): continue
            nu = norm_path(u.split("?")[0])
            for cand in norms:
                if nu == cand or nu.startswith(cand.rstrip("/") + "/") or (cand.count("{") and re.fullmatch(re.sub(r"\{\w+\}", r"[^/]+", cand), nu)):
                    for r in api_by_norm[cand]:
                        if host_svc and r["service"] != host_svc: continue
                        frm = page["path"] if page else rf
                        links.append({"kind": "page_api" if page else "api_api", "from_service": svc, "from": frm, "to_service": r["service"],
                                      "to": f'{r["method"]} {r["path"]}', "confidence": "high" if nu == cand else "medium",
                                      "file": rf, "line": line, "rule": "url_literal_prefix"})
                    break
    tables = {}
    for m in ex.rows["models"]:
        if m["column"] == "": tables.setdefault(m["table"], []).append(m)
    for r in api_routes:
        refs = ex.file_refs.get((r["service"], r["file"]))
        if not refs: continue
        for t, defs in tables.items():
            if len(t) < 3: continue
            names = {t} | ex.table_aliases.get(t, set())
            lowered = {x.lower() for x in refs["idents"]}
            if any(nm in refs["idents"] or nm.lower() in lowered for nm in names):
                for d in defs:
                    links.append({"kind": "api_table", "from_service": r["service"], "from": f'{r["method"]} {r["path"]}',
                                  "to_service": d["service"], "to": t, "confidence": "medium" if d["service"] == r["service"] else "medium",
                                  "file": r["file"], "line": r["line"], "rule": "model_ref_in_handler_file"})
    seen, out = set(), []
    for l in links:
        k = (l["kind"], l["from_service"], l["from"], l["to_service"], l["to"])
        if k in seen: continue
        seen.add(k); out.append(l)
    return out


# ----------------------------------------------------------------------------- priorities
def find_cycles(edges):
    graph = defaultdict(set)
    for a, b in edges:
        if a and b and a != b: graph[a].add(b)
    cycles, color, stack = [], {}, []
    def dfs(u):
        color[u] = 1; stack.append(u)
        for v in sorted(graph[u]):
            if color.get(v) == 1:
                cycles.append(stack[stack.index(v):] + [v])
            elif color.get(v) is None:
                dfs(v)
        stack.pop(); color[u] = 2
    for u in sorted(graph):
        if color.get(u) is None: dfs(u)
    uniq = {}
    for c in cycles:
        uniq[tuple(sorted(set(c)))] = c
    return list(uniq.values())


def compute_priorities(ex, rules, tree_rows, annotations):
    P = []
    wm = set(rules["write_methods"])
    def add(level, rid, service, subject, evf, evrow, detail):
        key = f"priorities|{rid}|{subject}"
        a = annotations.get(key, {})
        note = str(a.get("note", "")).strip().lower()
        fp_note = note.startswith(("fp", "false positive", "not a conflict", "ok", "ignore"))
        sup = "true" if (a.get("false_positive") or fp_note) else ""
        P.append({"level": level, "rule_id": rid, "service": service, "subject": subject, "evidence_file": evf,
                  "evidence_row": evrow, "detail": detail, "suppressed": sup})
    routes = ex.rows["routes"]
    if rules["P0-1"]["enabled"]:
        for r in routes:
            if r["kind"] != "api": continue
            ms = set(r["method"].split(";"))
            real = [g for g in r["auth_guard"].split(";") if g and not g.startswith("!")]
            if ms & wm and (r["method"] != "ANY" or rules["P0-1"]["treat_ANY_as_write"]) and not real:
                add("P0", "P0-1", r["service"], f'{r["method"]} {r["path"]}', "routes.csv", f'{r["service"]}|{r["file"]}|{r["line"]}',
                    "write route explicitly public (" + r["auth_guard"] + ")" if r["auth_guard"] else "write route without guard")
    if rules["P0-2"]["enabled"]:
        by_table = defaultdict(set)
        for m in ex.rows["models"]:
            if m["column"] == "" and m["table"] not in rules["P0-2"]["ignore_tables"]:
                by_table[m["table"].lower()].add((m["service"], m["file"], m["line"]))
        for t, locs in by_table.items():
            svcs = {s for s, _, _ in locs}
            if len(svcs) >= rules["P0-2"]["min_services"]:
                add("P0", "P0-2", ";".join(sorted(svcs)), t, "models.csv", ";".join(f"{s}|{f}|{l}" for s, f, l in sorted(locs)), f"table declared in {len(svcs)} services")
                for s in sorted(svcs):
                    for s2 in sorted(svcs):
                        if s < s2:
                            ex.rows["cross_calls"].append({"from_service": s, "to_service": s2, "kind": "db_shared", "endpoint_or_topic": t,
                                                           "file": "", "line": "", "to_service_confidence": "high", "pattern_id": "P0-2", "note": ""})
    if rules["P0-3"]["enabled"]:
        order = {"low": 0, "medium": 1, "high": 2}
        edges = [(c["from_service"], c["to_service"]) for c in ex.rows["cross_calls"]
                 if c["to_service"] and order[c["to_service_confidence"]] >= order[rules["P0-3"]["min_confidence"]] and c["kind"] != "db_shared"]
        for cyc in find_cycles(set(edges)):
            add("P0", "P0-3", cyc[0], "->".join(cyc), "cross_calls.csv", "", "call cycle")
    if rules["P1-1"]["enabled"]:
        audited = {(a["service"], a["file"]) for a in ex.rows["audit_points"]}
        audited_fn = {(a["service"], a["file"], a["function"]) for a in ex.rows["audit_points"] if a["function"]}
        for r in routes:
            if r["kind"] != "api": continue
            if not (set(r["method"].split(";")) & wm): continue
            ok = (r["service"], r["file"]) in audited if rules["P1-1"]["match_scope"] == "file" else (r["service"], r["file"], r["handler"]) in audited_fn
            if not ok:
                add("P1", "P1-1", r["service"], f'{r["method"]} {r["path"]}', "routes.csv", f'{r["service"]}|{r["file"]}|{r["line"]}', "write route with no audit point in file")
    if rules["P1-2"]["enabled"]:
        nz = rules["P1-2"]["normalize"]
        def normalize(c):
            x = c.lower() if nz.get("lowercase") else c
            for ch in nz.get("strip_chars", ""): x = x.replace(ch, "")
            for suf in nz.get("strip_suffixes", []):
                if x.endswith(suf): x = x[: -len(suf)]
            return x
        by_norm = defaultdict(lambda: defaultdict(set))   # norm -> raw -> locations
        by_raw_type = defaultdict(lambda: defaultdict(set))
        for m in ex.rows["models"]:
            if not m["column"] or m["column"] in rules["P1-2"]["ignore_columns"]: continue
            loc = f'{m["service"]}|{m["table"]}|{m["column"]}'
            by_norm[normalize(m["column"])][m["column"]].add(loc)
            if m["type"]: by_raw_type[m["column"]][re.sub(r"\s+", "", m["type"].lower())].add(loc)
        for nrm, raws in sorted(by_norm.items()):
            if len(raws) >= rules["P1-2"]["min_variants"]:
                add("P1", "P1-2", ";".join(sorted({l.split("|")[0] for s in raws.values() for l in s})), nrm, "models.csv",
                    ";".join(sorted(l for s in raws.values() for l in s)), "spelling variants: " + " / ".join(sorted(raws)))
        for raw, types in sorted(by_raw_type.items()):
            if len(types) >= 2:
                add("P1", "P1-2", ";".join(sorted({l.split("|")[0] for s in types.values() for l in s})), raw + "#type", "models.csv",
                    ";".join(sorted(l for s in types.values() for l in s)), "type variants: " + " / ".join(sorted(types)))
    if rules["P1-3"]["enabled"]:
        known = {m["table"].lower() for m in ex.rows["models"] if m["column"] == ""}
        known |= {re.sub(r"s$", "", t) for t in known} | {t + "s" for t in known}
        for m in ex.rows["models"]:
            if not m["fk_to"]: continue
            tgt = m["fk_to"].split(".")[0].lower()
            if tgt and tgt not in known and tgt != m["column"].lower():
                add("P1", "P1-3", m["service"], f'{m["table"]}.{m["column"]} -> {m["fk_to"]}', "models.csv", f'{m["service"]}|{m["table"]}|{m["column"]}', "fk target table not in inventory")
    if rules["P1-4"]["enabled"]:
        for name, defs in ex.role_defs.items():
            if len(ex.role_uses.get(name, [])) < rules["P1-4"]["min_ref_count"]:
                s, f, l = defs[0]
                add("P1", "P1-4", s, name, "permissions.csv", f"{s}|{f}|{l}", "role/permission constant defined but never referenced")
        for name, uses in ex.role_uses.items():
            if name not in ex.role_defs and re.match(r"^(?:ROLE|PERM|PERMISSION|SCOPE)_", name):
                s, f, l = uses[0]
                add("P1", "P1-4", s, name, "permissions.csv", f"{s}|{f}|{l}", f"referenced {len(uses)}x but no definition found")
    if rules["P2-1"]["enabled"]:
        for c in ex.rows["cross_calls"]:
            if c["to_service_confidence"] == "low":
                add("P2", "P2-1", c["from_service"], c["endpoint_or_topic"], "cross_calls.csv", f'{c["from_service"]}|{c["file"]}|{c["line"]}', "unresolved target service")
    if rules["P2-2"]["enabled"]:
        cands = [t for t in tree_rows if int(t["depth"]) <= rules["P2-2"]["max_depth"] and int(t["depth"]) > 0]
        if cands:
            cands.sort(key=lambda t: -int(t["loc"]))
            top = cands[: max(1, int(len(cands) * rules["P2-2"]["top_loc_fraction"]))]
            for t in top:
                if not t["responsibility"]:
                    add("P2", "P2-2", t["service"], t["path"], "tree.csv", f'{t["service"]}|{t["path"]}', f'loc={t["loc"]}, no responsibility line')
    order = {"P0": 0, "P1": 1, "P2": 2}
    P.sort(key=lambda p: (order[p["level"]], p["rule_id"], p["service"], p["subject"]))
    return P


# ----------------------------------------------------------------------------- tree
def build_tree(root, service, svc_path, files, max_depth, annotations):
    base = svc_path if svc_path != "." else ""
    agg = defaultdict(lambda: {"files": 0, "loc": 0, "langs": Counter()})
    loc_of = {}
    for fp, rf, lang, ext in files:
        lines = read_lines(fp)
        loc = sum(1 for l in lines if l.strip()) if lines else 0
        loc_of[rf] = loc
        parts = rf.split("/")
        start = len(base.split("/")) if base else 0
        for d in range(start, len(parts)):
            key = "/".join(parts[:d]) if d else "."
            agg[key]["files"] += 1; agg[key]["loc"] += loc
            if ext: agg[key]["langs"][ext] += loc
    rows = []
    rootkey = base if base else "."
    for key, a in agg.items():
        depth = 0 if key == rootkey else len(key.split("/")) - (len(base.split("/")) if base else 0)
        if key != rootkey and key == ".": continue
        if depth > max_depth or depth < 0: continue
        resp, src = "", ""
        d = os.path.join(root, key) if key != "." else root
        for cand in ("README.md", "readme.md", "README", "README.rst", "README.txt"):
            rp = os.path.join(d, cand)
            if os.path.exists(rp):
                for l in read_lines(rp) or []:
                    l = l.strip().lstrip("#").strip()
                    if l and not l.startswith(("[", "<", "=", "-")) and len(l) <= 160:
                        resp, src = l, "readme"; break
                break
        ann = annotations.get(f"tree|{service}|{key}", {})
        if ann.get("responsibility"):
            resp, src = ann["responsibility"], "annotation"
        rows.append({"service": service, "depth": depth, "path": key, "file_count": a["files"], "loc": a["loc"],
                     "languages": ";".join(f"{k}:{v}" for k, v in a["langs"].most_common(3)), "responsibility": resp, "responsibility_source": src})
    rows.sort(key=lambda r: (int(r["depth"]), r["path"]))
    return rows


# ----------------------------------------------------------------------------- git / versions
def git(root, *args):
    try:
        return subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def service_version(root, svc_path):
    d = os.path.join(root, svc_path)
    checks = [("package.json", lambda t: re.search(r'"version"\s*:\s*"([^"]+)"', t)),
              ("pyproject.toml", lambda t: re.search(r'^version\s*=\s*"([^"]+)"', t, re.M)),
              ("Cargo.toml", lambda t: re.search(r'^version\s*=\s*"([^"]+)"', t, re.M)),
              ("composer.json", lambda t: re.search(r'"version"\s*:\s*"([^"]+)"', t)),
              ("pom.xml", lambda t: re.search(r"<version>([^<]+)</version>", t)),
              ("VERSION", lambda t: re.match(r"\s*(\S+)", t))]
    for fn, fnc in checks:
        p = os.path.join(d, fn)
        if os.path.exists(p):
            m = fnc(open(p, encoding="utf-8", errors="ignore").read())
            if m: return m.group(1), fn
    return "", ""


def pr_info(root, template):
    env = os.environ
    for k in ("PR_NUMBER", "GITHUB_PR_NUMBER", "CI_MERGE_REQUEST_IID", "BITBUCKET_PR_ID", "CHANGE_ID"):
        if env.get(k): return {"number": env[k], "source": "env:" + k}
    ref = env.get("GITHUB_REF", "")
    m = re.match(r"refs/pull/(\d+)/", ref)
    if m: return {"number": m.group(1), "source": "env:GITHUB_REF"}
    try:
        out = subprocess.run(["gh", "pr", "view", "--json", "number", "-q", ".number"], cwd=root, capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip().isdigit():
            return {"number": out.stdout.strip(), "source": "gh"}
    except Exception:
        pass
    return {"number": None, "source": None}


# ----------------------------------------------------------------------------- main
def write_csv(path, name, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS[name], extrasaction="ignore")
        w.writeheader()
        for r in rows: w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in CSV_COLUMNS[name]})


def apply_notes(rows, table, annotations, keyfn):
    for r in rows:
        a = annotations.get(f"{table}|{keyfn(r)}")
        if a and a.get("note"): r["note"] = a["note"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default=None)
    ap.add_argument("--project-name", default=None)
    ap.add_argument("--services", default=None)
    ap.add_argument("--service-alias", default="", help="svc=alias1|alias2,svc2=alias3")
    ap.add_argument("--patterns", default=None)
    ap.add_argument("--rules", default=None)
    ap.add_argument("--pr-url-template", default=None)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--no-html", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    out = os.path.abspath(a.out or os.path.join(root, "docs", "audit"))
    os.makedirs(out, exist_ok=True)
    cfg = load_json(os.path.join(HERE, "patterns.json"))
    local_patterns = a.patterns or (os.path.join(out, "patterns.local.json") if os.path.exists(os.path.join(out, "patterns.local.json")) else None)
    if local_patterns: deep_merge(cfg, load_json(local_patterns))
    rules = load_json(os.path.join(HERE, "rules.json"))
    local_rules = a.rules or (os.path.join(out, "rules.local.json") if os.path.exists(os.path.join(out, "rules.local.json")) else None)
    if local_rules: deep_merge(rules, load_json(local_rules))
    ann_path = os.path.join(out, "annotations.json")
    annotations = load_json(ann_path).get("entries", {}) if os.path.exists(ann_path) else {}

    services = discover_services(root, a.services, cfg)
    aliases = {}
    for pair in filter(None, a.service_alias.split(",")):
        svc, al = pair.split("=", 1)
        for x in al.split("|"): aliases[x.strip().lower()] = svc.strip()
    ex = Extractor(root, cfg, list(services), aliases)
    manifest_services, tree_rows = {}, []
    other_paths = [s["path"] for s in services.values() if s["path"] != "."]
    for name, s in services.items():
        stats = {"files": 0, "skip": Counter(), "langs": Counter(), "frameworks": set()}
        files, skipped = walk_service(root, s["path"], cfg, [p for p in other_paths if p != s["path"] and not s["path"].startswith(p)])
        stats["skip"].update(skipped)
        for fp, rf, lang, ext in files:
            if lang is None:
                stats["skip"]["unsupported_ext"] += 1; continue
            ex.extract_file(name, fp, rf, lang, ext, stats)
        ex.rows["routes"].extend(file_based_routes(root, name, s["path"], cfg, files, stats))
        tree_rows.extend(build_tree(root, name, s["path"], files, a.max_depth, annotations))
        ver, vsrc = service_version(root, s["path"])
        manifest_services[name] = {"path": s["path"], "detected_by": s["detected_by"], "languages": dict(stats["langs"].most_common()),
                                   "framework_hints": sorted(stats["frameworks"]), "version": ver, "version_source": vsrc,
                                   "files_scanned": stats["files"], "files_skipped": sum(stats["skip"].values()),
                                   "skip_reasons": dict(stats["skip"].most_common()), "rows_per_csv": {}}
    # dedupe & sort
    for k in ("routes", "models", "permissions", "audit_points", "cross_calls"):
        seen, uniq = set(), []
        for r in ex.rows[k]:
            key = tuple(str(r.get(c, "")) for c in CSV_COLUMNS[k] if c != "note")
            if key in seen: continue
            seen.add(key); uniq.append(r)
        ex.rows[k] = sorted(uniq, key=lambda r: (str(r.get("service", r.get("from_service", ""))), str(r.get("file", "")), int(r.get("line") or 0), str(r.get("path", r.get("table", "")))))
    ex.rows["links"] = derive_links(ex, services)
    ex.rows["priorities"] = compute_priorities(ex, rules, tree_rows, annotations)
    apply_notes(ex.rows["routes"], "routes", annotations, lambda r: f'{r["service"]}|{r["file"]}|{r["line"]}')
    apply_notes(ex.rows["models"], "models", annotations, lambda r: f'{r["service"]}|{r["table"]}|{r["column"]}')
    apply_notes(ex.rows["permissions"], "permissions", annotations, lambda r: f'{r["service"]}|{r["file"]}|{r["line"]}')
    apply_notes(ex.rows["audit_points"], "audit_points", annotations, lambda r: f'{r["service"]}|{r["file"]}|{r["line"]}')
    apply_notes(ex.rows["cross_calls"], "cross_calls", annotations, lambda r: f'{r["from_service"]}|{r["file"]}|{r["line"]}')

    write_csv(os.path.join(out, "tree.csv"), "tree", tree_rows)
    for k in ("routes", "models", "permissions", "audit_points", "cross_calls", "links", "priorities"):
        write_csv(os.path.join(out, f"{k}.csv"), k, ex.rows[k])
    for name in services:
        for k in ("routes", "models", "permissions", "audit_points"):
            manifest_services[name]["rows_per_csv"][k] = sum(1 for r in ex.rows[k] if r["service"] == name)
        manifest_services[name]["rows_per_csv"]["cross_calls"] = sum(1 for r in ex.rows["cross_calls"] if r["from_service"] == name)
    now = datetime.datetime.now(datetime.timezone.utc)
    pr = pr_info(root, a.pr_url_template)
    pr["url"] = a.pr_url_template.replace("{pr}", str(pr["number"])) if (a.pr_url_template and pr["number"]) else None
    manifest = {
        "project": a.project_name or os.path.basename(root),
        "generated_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_at_local": now.astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
        "extractor_version": EXTRACTOR_VERSION,
        "git": {"sha": git(root, "rev-parse", "HEAD"), "sha_short": git(root, "rev-parse", "--short", "HEAD"),
                "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD"), "describe": git(root, "describe", "--tags", "--always"),
                "dirty_tree": bool(git(root, "status", "--porcelain"))},
        "pr": pr, "services": manifest_services,
        "totals": {"rows_per_csv": {k: len(ex.rows[k]) for k in ("routes", "models", "permissions", "audit_points", "cross_calls", "links")},
                   "priorities": dict(Counter(p["level"] for p in ex.rows["priorities"] if not p["suppressed"])),
                   "cross_calls_low_confidence": sum(1 for c in ex.rows["cross_calls"] if c["to_service_confidence"] == "low")},
        "patterns": {"bundled": os.path.join(HERE, "patterns.json"), "local": local_patterns, "rules_local": local_rules},
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(json.dumps({"services": {k: {"path": v["path"], "detected_by": v["detected_by"], "frameworks": v["framework_hints"],
                                       "files_scanned": v["files_scanned"], "files_skipped": v["files_skipped"], "rows": v["rows_per_csv"]}
                                   for k, v in manifest_services.items()},
                      "totals": manifest["totals"], "out": out}, indent=2, ensure_ascii=False))
    if not a.no_html:
        sys.path.insert(0, HERE)
        import build_html
        build_html.build(out)
        print("html:", os.path.join(out, "index.html"))


if __name__ == "__main__":
    main()
