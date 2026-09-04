#!/usr/bin/env python3
"""Build docs/audit/index.html from the CSVs + manifest.json (+ annotations.json).
Single file, inline CSS/JS, no CDN. Every view is captioned with its source CSV and rule,
and falls back to the table if it cannot render. Usage: python build_html.py <audit_dir>
"""
import csv, json, os, sys

TABLES = ["priorities", "tree", "routes", "models", "permissions", "audit_points", "cross_calls", "links"]
EDITABLE = {"tree": ["responsibility"], "routes": ["note"], "models": ["note"], "permissions": ["note"],
            "audit_points": ["note"], "cross_calls": ["note"], "priorities": ["note"]}
KEYS = {"tree": ["service", "path"], "routes": ["service", "file", "line"], "models": ["service", "table", "column"],
        "permissions": ["service", "file", "line"], "audit_points": ["service", "file", "line"],
        "cross_calls": ["from_service", "file", "line"], "priorities": ["rule_id", "subject"], "links": ["kind", "from", "to"]}


def read_csv(p):
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build(out):
    data = {t: read_csv(os.path.join(out, f"{t}.csv")) for t in TABLES}
    for r in data["priorities"]: r.setdefault("note", "")
    manifest = json.load(open(os.path.join(out, "manifest.json"), encoding="utf-8"))
    ann_p = os.path.join(out, "annotations.json")
    annotations = json.load(open(ann_p, encoding="utf-8")) if os.path.exists(ann_p) else {"version": 1, "entries": {}}
    payload = json.dumps({"data": data, "manifest": manifest, "annotations": annotations, "editable": EDITABLE, "keys": KEYS},
                         ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__PAYLOAD__", payload).replace("__PROJECT__", manifest.get("project", ""))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.join(out, "index.html")


TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Architecture Audit — __PROJECT__</title>
<style>
:root{--bg:#fafaf9;--fg:#1c1917;--muted:#78716c;--line:#e7e5e4;--card:#fff;--p0:#b91c1c;--p1:#c2410c;--p2:#a16207;--p3:#57534e;--acc:#1d4ed8;--ok:#15803d;--warn:#fef3c7}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}
.banner{background:#7f1d1d;color:#fff;text-align:center;font-weight:700;letter-spacing:.12em;padding:6px;font-size:12px}
header{padding:14px 22px;border-bottom:1px solid var(--line);background:var(--card);display:flex;flex-wrap:wrap;gap:8px 22px;align-items:baseline}
header h1{font-size:18px;margin:0 12px 0 0}header .kv{color:var(--muted);font-size:12px}header .kv b{color:var(--fg);font-weight:600}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;background:#f5f5f4;padding:1px 4px;border-radius:3px}
.dirty{background:var(--warn);color:#92400e;padding:2px 8px;border-radius:4px;font-weight:600}
main{padding:16px 22px;max-width:1600px}
nav{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 14px;position:sticky;top:0;background:var(--bg);z-index:5;padding:6px 0}nav button{border:1px solid var(--line);background:var(--card);padding:6px 12px;border-radius:6px;cursor:pointer;font-size:13px}
nav button.on{background:var(--fg);color:#fff;border-color:var(--fg)}nav button .n{opacity:.6;margin-left:4px;font-size:11px}
.jump{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px;font-size:12px}.jump a{color:var(--acc);text-decoration:none;border:1px solid var(--line);border-radius:12px;padding:2px 10px;background:var(--card)}
.todo{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:16px}
.todo .c{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;cursor:pointer}
.todo .c .v{font-size:26px;font-weight:700}.todo .c .l{font-size:12px;color:var(--muted)}
.todo .c.p0 .v{color:var(--p0)}.todo .c.p1 .v{color:var(--p1)}.todo .c.p2 .v{color:var(--p2)}
.view{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px;margin-bottom:16px;scroll-margin-top:60px}
.view .vh{display:flex;align-items:baseline;gap:10px}.view h2{font-size:15px;margin:0 0 4px;flex:1}.view .vh button{font-size:11px;padding:2px 8px;border:1px solid var(--line);background:var(--card);border-radius:4px;cursor:pointer;color:var(--muted)}
.view .cap{font-size:11px;color:var(--muted);margin-bottom:10px}.view .cap code{font-size:11px}
.view .fallback{color:var(--muted);font-size:12px;padding:8px}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}.toolbar input,.toolbar select{padding:5px 8px;border:1px solid var(--line);border-radius:5px;font-size:13px}
.toolbar .cnt{color:var(--muted);font-size:12px}.toolbar button{padding:5px 10px;border:1px solid var(--line);background:var(--card);border-radius:5px;cursor:pointer;font-size:12px}
table{border-collapse:collapse;width:100%;font-size:12px;background:var(--card)}th,td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top;max-width:380px;overflow-wrap:anywhere}
th{position:sticky;top:0;background:#f5f5f4;cursor:pointer;white-space:nowrap;user-select:none}th.s::after{content:" ▲"}th.d::after{content:" ▼"}
td[contenteditable]{background:#fffbeb;outline:1px dashed #f59e0b;min-width:120px}td[contenteditable]:focus{outline:2px solid #f59e0b;background:#fff}
tr.P0 td:first-child{color:var(--p0);font-weight:700}tr.P1 td:first-child{color:var(--p1);font-weight:700}tr.P2 td:first-child{color:var(--p2);font-weight:700}tr.sup{opacity:.45}
svg text{font-family:inherit}.tw{overflow:auto;max-height:70vh;border:1px solid var(--line);border-radius:6px}.sw{overflow:auto;max-width:100%}
.legend{font-size:11px;color:var(--muted);margin-top:6px;display:flex;flex-wrap:wrap;gap:4px 14px;align-items:center}.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:4px}.legend b{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:middle;margin-right:4px}
.risk td{text-align:center;padding:4px 6px;min-width:40px;cursor:pointer}.risk th{position:static;text-align:center}.risk td.svc{text-align:left;font-weight:600;cursor:pointer}.risk td.tot{font-weight:700}
.risk td.z{color:#d6d3d1}
.node{cursor:pointer}.g-dim{opacity:.12}.g-hi rect,.g-hi ellipse{stroke-width:2.5}
.sk .lk{fill:none;transition:opacity .1s}.sk .lk.dim{opacity:.05}.sk .lk.hi{opacity:.85}.sk .nd{cursor:pointer}.sk .nd.dim{opacity:.2}.sk text.sm{display:none}.sk .nd:hover text.sm{display:block}
.chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.chip{font-size:11px;border:1px solid var(--line);border-radius:12px;padding:2px 8px;background:#f5f5f4}.chip i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;vertical-align:middle}
.cluster{border-top:1px solid var(--line);padding:8px 0}.cluster h4{margin:0 0 6px;font-size:13px}.cluster.sup{opacity:.45}.cluster .var{display:flex;gap:8px;align-items:flex-start;margin:3px 0;font-size:12px}.cluster .var b{min-width:160px;font-family:ui-monospace,Menlo,monospace;font-size:12px}
.cov .row{display:grid;grid-template-columns:120px 1fr 260px 1fr;gap:10px;align-items:center;font-size:12px;padding:5px 0;border-bottom:1px solid var(--line)}.cov .bar{height:12px;background:#f5f5f4;border-radius:3px;overflow:hidden;display:flex}.cov .bar i{height:100%;display:block}
.cov .mini{display:flex;gap:3px;align-items:flex-end;height:26px}.cov .mini i{display:block;width:14px;background:#a8a29e;border-radius:2px 2px 0 0}.cov .mini i.z{background:#fca5a5}
.detail{font-size:12px;margin-top:8px;padding:8px;background:#f5f5f4;border-radius:6px}.detail b{font-weight:600}
footer{color:var(--muted);font-size:11px;padding:14px 22px;border-top:1px solid var(--line)}
li.dim{opacity:.45}
</style></head><body>
<div class="banner">INTERNAL · ADMIN ONLY · DO NOT DISTRIBUTE</div>
<header id="hdr"></header>
<main>
<nav id="nav"></nav>
<section id="content"></section>
</main>
<footer>Generated by repo-architecture-audit. CSVs in this folder are the source of truth; every view states its source and derivation rule. Edits are saved locally in this browser and can be exported as <code>annotations.json</code>; place that file next to the CSVs and rebuild to merge.</footer>
<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
const P=JSON.parse(document.getElementById('payload').textContent);const D=P.data,M=P.manifest;
const ANN=P.annotations||{version:1,entries:{}};let dirtyAnn=false;
const $=(s,r=document)=>r.querySelector(s);const el=(t,a={},...c)=>{const e=document.createElement(t);for(const[k,v]of Object.entries(a)){if(v==null)continue;if(k==='class')e.className=v;else if(k.startsWith('on'))e.addEventListener(k.slice(2),v);else e.setAttribute(k,v)}for(const x of c){if(x==null)continue;e.append(x.nodeType?x:document.createTextNode(String(x)))}return e};
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cut=(s,n)=>{s=String(s??'');return s.length>n?s.slice(0,n-1)+'…':s};
function key(t,r){return t+'|'+P.keys[t].map(k=>r[k]??'').join('|')}
function annOf(t,r){return ANN.entries[key(t,r)]||{}}
// ---------- shared indexes
const WRITE=new Set(['POST','PUT','PATCH','DELETE','ANY']);const isWrite=r=>r.kind==='api'&&String(r.method||'').split(';').some(m=>WRITE.has(m));
const SVC=[...new Set([...Object.keys(M.services||{}),...D.routes.map(r=>r.service),...D.models.map(r=>r.service),...D.tree.map(r=>r.service)].filter(Boolean))];
const PAL=['#2563eb','#059669','#d97706','#7c3aed','#db2777','#0891b2','#65a30d','#ea580c','#4f46e5','#0d9488','#b45309','#9333ea','#0369a1','#15803d','#be123c'];
const col=s=>{const i=SVC.indexOf(s);return i<0?'#78716c':i<PAL.length?PAL[i]:'hsl('+((i*137)%360)+' 55% 42%)'};
const RULES=['P0-1','P0-2','P0-3','P1-1','P1-2','P1-3','P1-4','P2-1','P2-2'];const LV=r=>r.slice(0,2);
const PR=D.priorities.filter(p=>!p.suppressed);
const prBy={};for(const p of PR)for(const s of String(p.service).split(';')){prBy[s]=prBy[s]||{};prBy[s][p.rule_id]=(prBy[s][p.rule_id]||0)+1}
const cnt=(s,r)=>((prBy[s]||{})[r]||0);const cntL=(s,l)=>RULES.filter(r=>LV(r)===l).reduce((a,r)=>a+cnt(s,r),0);
const unguarded=new Set(PR.filter(p=>p.rule_id==='P0-1').map(p=>p.service+' · '+p.subject));
const unaudited=new Set(PR.filter(p=>p.rule_id==='P1-1').map(p=>p.service+' · '+p.subject));
const sharedTables=new Set(PR.filter(p=>p.rule_id==='P0-2').map(p=>p.subject));
const p22=new Set(PR.filter(p=>p.rule_id==='P2-2').map(p=>p.service+'|'+p.subject));
const locOf={};for(const r of D.tree)if(String(r.depth)==='0')locOf[r.service]=(locOf[r.service]||0)+(+r.loc||0);
const routesOf={};for(const r of D.routes)routesOf[r.service]=(routesOf[r.service]||0)+1;
const fmt=n=>n>=1e6?(n/1e6).toFixed(1)+'M':n>=1e3?(n/1e3).toFixed(n>=1e4?0:1)+'k':String(n);
// ---------- header
(function(){const g=M.git||{},pr=M.pr||{};const h=$('#hdr');
h.append(el('h1',{},M.project||'Architecture audit'));
const kv=(l,v)=>h.append(el('span',{class:'kv'},l+': ',el('b',{},v)));
kv('generated',(M.generated_at_utc||'')+' UTC ('+(M.generated_at_local||'')+')');
const sha=el('code',{title:'click to expand',style:'cursor:pointer'},g.sha_short||'—');let full=false;sha.onclick=()=>{full=!full;sha.textContent=full?(g.sha||'—'):(g.sha_short||'—')};
h.append(el('span',{class:'kv'},'commit: ',sha));kv('branch',g.branch||'—');kv('tag/describe',g.describe||'—');
const vers=Object.entries(M.services||{}).filter(([,s])=>s.version).map(([n,s])=>n+' '+s.version).join(' · ');if(vers)kv('versions',vers);
if(pr.number){const a=pr.url?el('a',{href:pr.url,target:'_blank'},'#'+pr.number):el('b',{},'#'+pr.number);h.append(el('span',{class:'kv'},'PR: ',a,' ('+(pr.source||'')+')'))}else kv('PR','null (only available in CI / via gh)');
kv('extractor','v'+(M.extractor_version||''));if(g.dirty_tree)h.append(el('span',{class:'dirty'},'⚠ dirty working tree — results include uncommitted changes'));})();
// ---------- tabs
const tabs=[['overview','Overview'],['priorities','Priorities'],['tree','Structure'],['routes','Routes'],['models','Models'],['permissions','Permissions'],['audit_points','Audit points'],['cross_calls','Cross calls'],['links','Links']];
let cur='overview',filterState={};
function go(tab,fs){cur=tab;filterState=fs||{};render();try{window.scrollTo(0,0)}catch(_){}}
function nav(){const n=$('#nav');n.innerHTML='';for(const[id,l]of tabs){const b=el('button',{class:id===cur?'on':'',onclick:()=>go(id)},l);if(D[id])b.append(el('span',{class:'n'},D[id].length));n.append(b)}n.append(el('button',{onclick:exportAnn,style:'margin-left:auto'},'Export annotations.json'+(dirtyAnn?' •':'')));const imp=el('input',{type:'file',accept:'.json',style:'display:none',onchange:importAnn});n.append(el('button',{onclick:()=>imp.click()},'Import'),imp)}
function render(){nav();const c=$('#content');c.innerHTML='';if(cur==='overview')overview(c);else table(c,cur)}
// ---------- overview
const VIEWS=[
['risk','Risk matrix — where the findings are','priorities.csv (suppressed rows excluded) · rows = services, columns = rule ids; a finding spanning several services is counted for each · click a cell to open the rows',riskMatrix],
['deps','Service dependency graph','cross_calls.csv · left→right = call direction after cycle-breaking (longest-path layering); node = service (LOC, routes), badge = P0 / P1 count; edge width = log₂(calls), red = cycle (P0-3), dashed = confidence low, dotted = shared table (P0-2) drawn as a cylinder; hover isolates neighbours, click opens the service routes · > 60 services switches to an adjacency matrix',svcGraph],
['tree','Code structure treemap','tree.csv · area = LOC (non-blank lines), outer box = service, inner = directories (depth ≤ 2); hatched red border = P2-2 (heavy directory with no responsibility line) · click opens the service in Structure',treemap],
['flow','Page → API → Table flow','links.csv (page_api: URL literal in page file matches API path prefix; api_table: model/table name referenced in handler file; api_api: dashed arcs) · node height = number of links, colour = service; API red outline = P0-1 unguarded write, orange dot = P1-1 no audit; table dashed outline = P0-2 shared · grey nodes have no link · click a node to trace its chain',flowView],
['perm','Permission matrix — which guard sits on which route','routes.csv auth_guard × permissions.csv roles (matched by handler) · rows = API routes, unguarded writes first (red); columns = guard mechanisms / role literals; "public!" = explicit no-auth marker · filled = declared in code, empty = nothing found (not the same as denied)',permMatrix],
['audit','Audit coverage per service','routes.csv × audit_points.csv · per service: write routes whose file contains an audit point (green) vs none (red) · rule P1-1 · click a bar to list its unaudited routes',auditBars],
['fields','Field naming & type drift','priorities.csv (P1-2) joined to models.csv · one block per normalized name; each spelling/type variant with the tables that use it, coloured by service · over-reports on purpose: write "fp …" in the note to suppress',fieldClusters],
['cov','Extractor coverage & skip reasons','manifest.json · scanned vs skipped files per service and rows per CSV; a zero bar under routes/models usually means the framework needs a patterns.local.json entry',coverage]];
function overview(c){const cntl=l=>PR.filter(p=>p.level===l).length;
const todo=el('div',{class:'todo'});for(const[l,t]of[['P0','P0 · unguarded writes, shared tables, call cycles'],['P1','P1 · missing audit, naming/type drift, dangling FKs, orphan roles'],['P2','P2 · unresolved calls, undocumented heavy dirs']]){todo.append(el('div',{class:'c '+l.toLowerCase(),onclick:()=>go('priorities',{level:l})},el('div',{class:'v'},cntl(l)),el('div',{class:'l'},t)))}
const svcs=Object.keys(M.services||{});todo.append(el('div',{class:'c',onclick:()=>go('tree')},el('div',{class:'v'},svcs.length),el('div',{class:'l'},'services · '+cut(svcs.map(s=>s+' ('+(M.services[s].files_scanned||0)+' files)').join(', '),160))));
const low=(M.totals||{}).cross_calls_low_confidence||0;todo.append(el('div',{class:'c',onclick:()=>go('cross_calls',{to_service_confidence:'low'})},el('div',{class:'v'},low),el('div',{class:'l'},'cross calls with unresolved target')));
const wr=D.routes.filter(isWrite);todo.append(el('div',{class:'c',onclick:()=>go('routes',{q:''})},el('div',{class:'v'},D.routes.filter(r=>r.kind==='api').length),el('div',{class:'l'},'API routes · '+wr.length+' write · '+wr.filter(r=>!r.auth_guard||/^!/.test(r.auth_guard)).length+' without guard')));
c.append(todo);
const j=el('div',{class:'jump'});for(const[id,t]of VIEWS)j.append(el('a',{href:'#v-'+id},t.replace(/ —.*/,'')));c.append(j);
for(const[id,t,cap,fn]of VIEWS)c.append(view(id,t,cap,fn));}
function view(id,title,cap,fn){const vh=el('div',{class:'vh'},el('h2',{},title));const v=el('div',{class:'view',id:'v-'+id},vh,el('div',{class:'cap'},cap));try{const r=fn();v.append(r||el('div',{class:'fallback'},'No data for this view.'));if(v.querySelector('svg'))vh.append(el('button',{title:'download this view as SVG',onclick:()=>dlSvg(v.querySelector('svg'),id)},'↓ svg'))}catch(e){v.append(el('div',{class:'fallback'},'View could not render ('+e.message+'); see the table tab instead.'))}return v}
function dlSvg(svg,name){const s=new XMLSerializer().serializeToString(svg);const b=new Blob(['<?xml version="1.0"?>'+s],{type:'image/svg+xml'});const a=el('a',{href:URL.createObjectURL(b),download:(M.project||'audit')+'-'+name+'.svg'});document.body.append(a);a.click();a.remove()}
function svgDiv(s,cls){const d=el('div',{class:cls||'sw'});d.innerHTML=s;return d}
function legend(...items){const l=el('div',{class:'legend'});for(const it of items){if(typeof it==='string')l.append(el('span',{},it));else l.append(el('span',{},el(it.line?'i':'b',{style:it.style}),it.t))}return l}
// ---------- 1. risk matrix
function riskMatrix(){if(!PR.length)return el('div',{class:'fallback'},'No open findings — every rule passed or every row is suppressed.');const svcs=SVC.filter(s=>prBy[s]);const max=Math.max(1,...svcs.flatMap(s=>RULES.map(r=>cnt(s,r))));
const t=el('table',{class:'risk'});const hr=el('tr',{},el('th',{},'service'));for(const r of RULES)hr.append(el('th',{title:r,style:'color:var(--'+LV(r).toLowerCase()+')'},r));hr.append(el('th',{},'total'));t.append(hr);
const shade=(r,n)=>{const c={P0:'185,28,28',P1:'194,65,12',P2:'161,98,7'}[LV(r)];return 'background:rgba('+c+','+(0.12+0.7*n/max).toFixed(2)+');color:'+(n/max>0.5?'#fff':'#1c1917')};
for(const s of svcs.sort((a,b)=>cntL(b,'P0')-cntL(a,'P0')||cntL(b,'P1')-cntL(a,'P1')||a.localeCompare(b))){const tr=el('tr',{},el('td',{class:'svc',onclick:()=>go('priorities',{service:s})},el('span',{style:'display:inline-block;width:10px;height:10px;border-radius:2px;background:'+col(s)+';margin-right:6px'}),s));let tot=0;for(const r of RULES){const n=cnt(s,r);tot+=n;tr.append(el('td',{class:n?'':'z',style:n?shade(r,n):'',title:s+' · '+r+' · '+n,onclick:()=>go('priorities',{service:s,rule:r})},n||'·'))}tr.append(el('td',{class:'tot'},tot));t.append(tr)}
const tf=el('tr',{},el('td',{class:'tot'},'all'));for(const r of RULES)tf.append(el('td',{class:'tot',onclick:()=>go('priorities',{rule:r})},PR.filter(p=>p.rule_id===r).length));tf.append(el('td',{class:'tot'},PR.length));t.append(tf);
const w=el('div',{class:'tw',style:'max-height:420px'},t);const d=el('div',{},w,legend('P0-1 unguarded write · P0-2 shared table · P0-3 call cycle · P1-1 no audit · P1-2 naming/type drift · P1-3 dangling FK · P1-4 orphan role const · P2-1 unresolved call · P2-2 heavy undocumented dir'));return d}
// ---------- 2. service dependency graph (layered)
function layered(nodes,edges){const n=nodes.length,idx=new Map(nodes.map((x,i)=>[x,i]));const adj=nodes.map(()=>[]);for(const e of edges){const u=idx.get(e.a),v=idx.get(e.b);if(u==null||v==null||u===v)continue;adj[u].push(v)}
const st=new Array(n).fill(0),back=new Set();const stack=[];function dfs(r){stack.push([r,0]);st[r]=1;while(stack.length){const top=stack[stack.length-1];const[u,i]=top;if(i<adj[u].length){top[1]++;const v=adj[u][i];if(st[v]===1)back.add(u+'>'+v);else if(st[v]===0){st[v]=1;stack.push([v,0])}}else{st[u]=2;stack.pop()}}}for(let i=0;i<n;i++)if(!st[i])dfs(i);
const out=nodes.map(()=>[]),ind=new Array(n).fill(0),deg=new Array(n).fill(0);for(const e of edges){let u=idx.get(e.a),v=idx.get(e.b);if(u==null||v==null||u===v)continue;deg[u]++;deg[v]++;if(back.has(u+'>'+v))[u,v]=[v,u];out[u].push(v);ind[v]++}
const level=new Array(n).fill(0);const q=[];const ind2=ind.slice();for(let i=0;i<n;i++)if(!ind2[i])q.push(i);while(q.length){const u=q.shift();for(const v of out[u]){level[v]=Math.max(level[v],level[u]+1);if(--ind2[v]===0)q.push(v)}}
const iso=[];for(let i=0;i<n;i++)if(!deg[i])iso.push(i);let L=Math.max(0,...level.filter((_,i)=>deg[i]))+1;const maxCols=Math.max(3,Math.min(9,Math.ceil(Math.sqrt(n*1.4))));if(L>maxCols){for(let i=0;i<n;i++)if(deg[i])level[i]=Math.round(level[i]*(maxCols-1)/(L-1));L=maxCols}for(const i of iso)level[i]=L;
const layers=[];for(let i=0;i<n;i++){(layers[level[i]]=layers[level[i]]||[]).push(i)}for(let i=0;i<layers.length;i++)layers[i]=layers[i]||[];const pos=new Array(n).fill(0);layers.forEach(l=>l.forEach((v,i)=>pos[v]=i));
const pred=nodes.map(()=>[]);for(let u=0;u<n;u++)for(const v of out[u])pred[v].push(u);
for(let it=0;it<4;it++){for(let l=1;l<layers.length;l++)bary(layers[l],pred);for(let l=layers.length-2;l>=0;l--)bary(layers[l],out)}
function bary(layer,nb){layer.sort((a,b)=>{const ba=nb[a].length?nb[a].reduce((s,x)=>s+pos[x],0)/nb[a].length:pos[a],bb=nb[b].length?nb[b].reduce((s,x)=>s+pos[x],0)/nb[b].length:pos[b];return ba-bb});layer.forEach((v,i)=>pos[v]=i)}
return{level,pos,layers,back:new Set([...back].map(k=>k.split('>').map(i=>nodes[+i]).join('\u0000'))),iso:new Set(iso.map(i=>nodes[i]))}}
function svcGraph(){const rows=D.cross_calls.filter(r=>r.to_service);const unresolved=D.cross_calls.length-rows.length;const svcs=[...new Set([...Object.keys(M.services||{}),...rows.flatMap(r=>[r.from_service,r.to_service])])].filter(Boolean);if(!svcs.length)return null;
if(svcs.length>60)return adjMatrix(svcs,rows,unresolved);
const E={};const tbl={};for(const r of rows){if(r.kind==='db_shared'){const t='⛁'+r.endpoint_or_topic;tbl[t]=tbl[t]||new Set();tbl[t].add(r.from_service);tbl[t].add(r.to_service);continue}const k=r.from_service+'\u0000'+r.to_service;E[k]=E[k]||{a:r.from_service,b:r.to_service,n:0,low:true,kinds:{}};E[k].n++;E[k].kinds[r.kind]=(E[k].kinds[r.kind]||0)+1;if(r.to_service_confidence!=='low')E[k].low=false}
const nodes=[...svcs,...Object.keys(tbl)];const edges=[...Object.values(E),...Object.entries(tbl).flatMap(([t,ss])=>[...ss].map(s=>({a:s,b:t,n:1,db:true})))];
const lay=layered(nodes,edges);const cyc=new Set(PR.filter(p=>p.rule_id==='P0-3').flatMap(p=>{const s=p.subject.split('->');return s.slice(0,-1).map((x,i)=>x+'\u0000'+s[i+1])}));
const NW=150,NH=44,CW=NW+70,RH=NH+22,maxRows=Math.max(...lay.layers.map(l=>l.length));const TOP=lay.back.size?70:25;const W=40+lay.layers.length*CW+40,H=maxRows*RH+TOP+25;const xy={};nodes.forEach((n,i)=>{const l=lay.level[i],rowsN=lay.layers[l].length;xy[n]=[40+l*CW,TOP+(maxRows-rowsN)*RH/2+lay.pos[i]*RH]});
let s='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" style="display:block"><defs><marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#57534e"/></marker><marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#b91c1c"/></marker></defs>';
if(lay.iso.size)s+='<text x="'+(40+(lay.layers.length-1)*CW)+'" y="14" font-size="10" fill="#78716c">not connected</text>';
for(const e of edges){if(e.a===e.b)continue;const[x1,y1]=xy[e.a],[x2,y2]=xy[e.b];const red=cyc.has(e.a+'\u0000'+e.b);const w=e.db?1.2:Math.min(8,1+Math.log2(e.n+1));const back=lay.back.has(e.a+'\u0000'+e.b);let d;
if(e.db){d='M'+(x1+NW)+','+(y1+NH/2)+' C'+(x1+NW+40)+','+(y1+NH/2)+' '+(x2-40)+','+(y2+NH/2)+' '+x2+','+(y2+NH/2)}
else if(x1===x2){const bx=x1+NW+55+Math.abs(y2-y1)/8;d='M'+(x1+NW)+','+(y1+NH/2-6)+' C'+bx+','+(y1+NH/2-6)+' '+bx+','+(y2+NH/2+6)+' '+(x2+NW)+','+(y2+NH/2+6)}
else if(!back){d='M'+(x1+NW)+','+(y1+NH/2)+' C'+(x1+NW+45)+','+(y1+NH/2)+' '+(x2-45)+','+(y2+NH/2)+' '+x2+','+(y2+NH/2)}
else{d='M'+(x1+NW/2)+','+(y1)+' C'+(x1+NW/2)+','+(y1-RH*0.9)+' '+(x2+NW/2)+','+(y2-RH*0.9)+' '+(x2+NW/2)+','+y2}
const kinds=Object.entries(e.kinds||{}).map(([k,n])=>k+' ×'+n).join(', ');s+='<path class="edge" data-a="'+esc(e.a)+'" data-b="'+esc(e.b)+'" d="'+d+'" fill="none" stroke="'+(red?'#b91c1c':e.db?'#78716c':back?'#c2410c':'#78716c')+'" stroke-width="'+w+'" '+(e.db?'stroke-dasharray="2 4"':e.low?'stroke-dasharray="6 5"':'')+' '+(e.db?'':'marker-end="url(#'+(red?'arr':'ar')+')"')+' opacity=".85"><title>'+esc(e.a)+' → '+esc(e.b)+(e.db?' (shared table)':': '+e.n+' call(s) · '+kinds+(e.low?' · confidence low':'')+(red?' · CYCLE':''))+'</title></path>'}
for(const n of nodes){const[x,y]=xy[n];if(n.startsWith('⛁')){const t=n.slice(1);s+='<g class="node" data-n="'+esc(n)+'"><ellipse cx="'+(x+NW/2)+'" cy="'+(y+NH/2)+'" rx="'+(NW/2-10)+'" ry="'+(NH/2-6)+'" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.2" stroke-dasharray="3 3"/><ellipse cx="'+(x+22)+'" cy="'+(y+NH/2-5)+'" rx="6" ry="2.5" fill="none" stroke="#b91c1c"/><path d="M'+(x+16)+','+(y+NH/2-5)+' v9 a6,2.5 0 0 0 12,0 v-9" fill="none" stroke="#b91c1c"/><text x="'+(x+34)+'" y="'+(y+NH/2+4)+'" font-size="11" fill="#b91c1c">'+esc(cut(t,14))+'</text><title>shared table '+esc(t)+' — '+[...tbl[n]].join(', ')+'</title></g>';continue}
const p0=cntL(n,'P0'),p1=cntL(n,'P1');const svc=M.services[n]||{};s+='<g class="node" data-n="'+esc(n)+'" data-svc="1"><rect x="'+x+'" y="'+y+'" width="'+NW+'" height="'+NH+'" rx="6" fill="#fff" stroke="'+col(n)+'" stroke-width="1.8"/><rect x="'+x+'" y="'+y+'" width="6" height="'+NH+'" rx="3" fill="'+col(n)+'"/><text x="'+(x+14)+'" y="'+(y+18)+'" font-size="12" font-weight="600">'+esc(cut(n,17))+'</text><text x="'+(x+14)+'" y="'+(y+34)+'" font-size="10" fill="#78716c">'+fmt(locOf[n]||0)+' loc · '+(routesOf[n]||0)+' routes</text>';
if(p0)s+='<circle cx="'+(x+NW-2)+'" cy="'+(y+2)+'" r="9" fill="#b91c1c"/><text x="'+(x+NW-2)+'" y="'+(y+5.5)+'" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">'+p0+'</text>';if(p1)s+='<circle cx="'+(x+NW-(p0?24:2))+'" cy="'+(y+2)+'" r="9" fill="#c2410c"/><text x="'+(x+NW-(p0?24:2))+'" y="'+(y+5.5)+'" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">'+p1+'</text>';
s+='<title>'+esc(n)+' · '+(svc.framework_hints||[]).join(', ')+' · P0 '+p0+' / P1 '+p1+' / P2 '+cntL(n,'P2')+' · click for routes</title></g>'}
s+='</svg>';const d=svgDiv(s);const svg=d.querySelector('svg');
svg.addEventListener('mouseover',e=>{const g=e.target.closest('.node');if(!g)return;const n=g.dataset.n;const nb=new Set([n]);svg.querySelectorAll('.edge').forEach(p=>{if(p.dataset.a===n||p.dataset.b===n){nb.add(p.dataset.a);nb.add(p.dataset.b);p.classList.remove('g-dim')}else p.classList.add('g-dim')});svg.querySelectorAll('.node').forEach(x=>x.classList.toggle('g-dim',!nb.has(x.dataset.n)))});
svg.addEventListener('mouseout',e=>{if(e.target.closest('.node')&&!svg.contains(e.relatedTarget?.closest?.('.node')))svg.querySelectorAll('.g-dim').forEach(x=>x.classList.remove('g-dim'))});
svg.addEventListener('click',e=>{const g=e.target.closest('.node[data-svc]');if(g)go('routes',{service:g.dataset.n})});
d.append(legend('edge width = log₂(calls)',{style:'background:#b91c1c',line:1,t:'cycle (P0-3)'},{style:'background:#c2410c',line:1,t:'back edge, not a P0-3 cycle (low confidence)'},{style:'border-top:2px dashed #78716c;height:0;background:none',line:1,t:'confidence low'},{style:'border-top:2px dotted #78716c;height:0;background:none',line:1,t:'shared table'},{style:'background:#b91c1c;border-radius:50%',t:'P0 count'},{style:'background:#c2410c;border-radius:50%',t:'P1 count'}));
if(!rows.length)d.append(el('div',{class:'legend'},'no resolved cross-service call found'+(unresolved?'; '+unresolved+' unresolved (to_service empty, confidence low) — see Cross calls tab or pass --service-alias':'')));else if(unresolved)d.append(el('div',{class:'legend'},unresolved+' call(s) with empty to_service are not drawn (P2-1)'));return d}
function adjMatrix(svcs,rows,unresolved){const E={};for(const r of rows){const k=r.from_service+'\u0000'+r.to_service;E[k]=(E[k]||0)+1}const outd={};for(const k in E)outd[k.split('\u0000')[0]]=(outd[k.split('\u0000')[0]]||0)+E[k];svcs=[...svcs].sort((a,b)=>(outd[b]||0)-(outd[a]||0)||a.localeCompare(b));
const cyc=new Set(PR.filter(p=>p.rule_id==='P0-3').flatMap(p=>{const s=p.subject.split('->');return s.slice(0,-1).map((x,i)=>x+'\u0000'+s[i+1])}));const C=13,G=120,W=G+svcs.length*C+10,H=G+svcs.length*C+10,max=Math.max(1,...Object.values(E));
let s='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'"><text x="'+(G-6)+'" y="'+(G-6)+'" text-anchor="end" font-size="9" fill="#78716c">from ↓ / to →</text>';svcs.forEach((n,i)=>{s+='<text transform="translate('+(G+i*C+C/2+3)+','+(G-6)+') rotate(-60)" font-size="8">'+esc(cut(n,18))+'</text><text x="'+(G-6)+'" y="'+(G+i*C+C/2+3)+'" text-anchor="end" font-size="8">'+esc(cut(n,18))+'</text>'});
svcs.forEach((a,i)=>{s+='<rect x="'+G+'" y="'+(G+i*C)+'" width="'+(svcs.length*C)+'" height="'+(C-1)+'" fill="'+(i%2?'#fafaf9':'#f5f5f4')+'"/><rect x="'+(G+i*C)+'" y="'+(G+i*C)+'" width="'+(C-1)+'" height="'+(C-1)+'" fill="#e7e5e4"/>'});svcs.forEach((a,i)=>svcs.forEach((b,j)=>{const n=E[a+'\u0000'+b]||0;if(!n)return;const red=cyc.has(a+'\u0000'+b);s+='<rect x="'+(G+j*C)+'" y="'+(G+i*C)+'" width="'+(C-1)+'" height="'+(C-1)+'" fill="rgba(29,78,216,'+(0.2+0.8*n/max).toFixed(2)+')" '+(red?'stroke="#b91c1c" stroke-width="1.5"':'')+'><title>'+esc(a)+' → '+esc(b)+': '+n+(red?' · CYCLE':'')+'</title></rect>'}));
s+='</svg>';const d=svgDiv(s,'tw');d.append(el('div',{class:'legend'},svcs.length+' services — adjacency matrix instead of a node graph (readability limit 60); cell = calls from row to column, red outline = P0-3 cycle; '+unresolved+' unresolved call(s) not shown'));return d}
// ---------- 3. treemap
function squarify(items,x,y,w,h){const out=[];items=items.filter(i=>i.v>0).sort((a,b)=>b.v-a.v);const tot=items.reduce((s,i)=>s+i.v,0);if(!tot||w<=0||h<=0)return out;const scale=w*h/tot;let row=[],rx=x,ry=y,rw=w,rh=h;
const worst=(row,len)=>{const s=row.reduce((a,i)=>a+i.v*scale,0);if(!s)return Infinity;let mx=0,mn=Infinity;for(const i of row){const a=i.v*scale;mx=Math.max(mx,a);mn=Math.min(mn,a)}return Math.max(len*len*mx/(s*s),s*s/(len*len*mn))};
const lay=(row)=>{const s=row.reduce((a,i)=>a+i.v*scale,0);if(rw>=rh){const cw=s/rh;let cy=ry;for(const i of row){const ch=i.v*scale/cw;out.push({...i,x:rx,y:cy,w:cw,h:ch});cy+=ch}rx+=cw;rw-=cw}else{const ch=s/rw;let cx=rx;for(const i of row){const cw=i.v*scale/ch;out.push({...i,x:cx,y:ry,w:cw,h:ch});cx+=cw}ry+=ch;rh-=ch}};
for(const it of items){const len=Math.min(rw,rh);if(!row.length||worst([...row,it],len)<=worst(row,len))row.push(it);else{lay(row);row=[it]}}if(row.length)lay(row);return out}
function treemap(){const T=D.tree;if(!T.length)return null;const byS={};for(const r of T){(byS[r.service]=byS[r.service]||[]).push(r)}
const svcItems=SVC.filter(s=>byS[s]).map(s=>({v:+(byS[s].find(r=>String(r.depth)==='0')||{}).loc||byS[s].reduce((a,r)=>a+(+r.loc||0),0),s}));if(!svcItems.some(i=>i.v>0))return null;
const W=1200,H=Math.min(720,Math.max(360,SVC.length*22));let s='<svg viewBox="0 0 '+W+' '+H+'" width="100%" style="height:auto"><defs>';for(const sv of SVC)s+='<pattern id="h-'+esc(sv)+'" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)"><rect width="6" height="6" fill="'+col(sv)+'" opacity=".18"/><line x1="0" y1="0" x2="0" y2="6" stroke="#b91c1c" stroke-width="1.5"/></pattern>';s+='</defs>';
const pad=2;const rects=squarify(svcItems,0,0,W,H);
const children=(sv,parent,depth)=>byS[sv].filter(r=>String(r.depth)===String(depth)&&r.path.startsWith(parent+'/')&&!r.path.slice(parent.length+1).includes('/'));
const draw=(sv,parentRow,x,y,w,h,depth)=>{const kids=children(sv,parentRow.path,depth);if(!kids.length||w*h<1800)return;const used=kids.reduce((a,r)=>a+(+r.loc||0),0);const rest=(+parentRow.loc||0)-used;const items=kids.map(r=>({v:+r.loc||0,r}));if(rest>0)items.push({v:rest,r:{path:parentRow.path+'/(files here)',loc:rest,file_count:'',languages:'',responsibility:'',depth}});
for(const c of squarify(items,x,y,w,h)){const r=c.r;const flag=p22.has(sv+'|'+r.path);const name=r.path.split('/').pop();const cw=Math.max(0,c.w-pad),ch=Math.max(0,c.h-pad);if(cw<2||ch<2)continue;const hasKids=depth<2&&!r.path.endsWith('(files here)')&&children(sv,r.path,depth+1).length>0&&cw*ch>=3600&&ch>30;
s+='<g class="node" data-svc="'+esc(sv)+'"><rect x="'+(c.x+pad/2).toFixed(1)+'" y="'+(c.y+pad/2).toFixed(1)+'" width="'+cw.toFixed(1)+'" height="'+ch.toFixed(1)+'" fill="'+(flag&&!hasKids?'url(#h-'+esc(sv)+')':col(sv))+'" fill-opacity="'+(flag&&!hasKids?'1':hasKids?'.06':depth===1?'.22':'.14')+'" stroke="'+(flag?'#b91c1c':'#fff')+'" stroke-width="'+(flag?'1.5':'1')+'" '+(flag?'stroke-dasharray="4 2"':'')+'/>';
if(hasKids)s+='<rect x="'+(c.x+pad/2).toFixed(1)+'" y="'+(c.y+pad/2).toFixed(1)+'" width="'+cw.toFixed(1)+'" height="14" fill="'+(flag?'url(#h-'+esc(sv)+')':col(sv))+'" fill-opacity="'+(flag?'1':'.3')+'"/>';
if(cw>44&&ch>14)s+='<text x="'+(c.x+5).toFixed(1)+'" y="'+(c.y+12).toFixed(1)+'" font-size="10" font-weight="'+(hasKids?'600':'400')+'" fill="'+(flag?'#b91c1c':'#1c1917')+'" stroke="#fff" stroke-width="3" paint-order="stroke">'+esc(cut(name+(hasKids?' · '+fmt(+r.loc||0):''),Math.floor(cw/6)))+'</text>';if(!hasKids&&cw>60&&ch>28)s+='<text x="'+(c.x+5).toFixed(1)+'" y="'+(c.y+24).toFixed(1)+'" font-size="9" fill="#57534e" stroke="#fff" stroke-width="3" paint-order="stroke">'+fmt(+r.loc||0)+' loc</text>';
s+='<title>'+esc(r.path)+'\n'+(+r.loc||0)+' loc · '+(r.file_count||'?')+' files · '+esc(r.languages||'')+'\n'+(r.responsibility?esc(r.responsibility)+' ('+esc(r.responsibility_source)+')':'no responsibility line')+(flag?'\nP2-2: heavy directory without responsibility':'')+'</title></g>';
if(hasKids)draw(sv,r,c.x+pad/2+1,c.y+pad/2+15,cw-2,Math.max(0,ch-16),depth+1)}};
for(const c of rects){const sv=c.s;const root=byS[sv].find(r=>String(r.depth)==='0')||{path:M.services?.[sv]?.path||sv,loc:c.v};s+='<g class="node" data-svc="'+esc(sv)+'"><rect x="'+c.x.toFixed(1)+'" y="'+c.y.toFixed(1)+'" width="'+c.w.toFixed(1)+'" height="'+c.h.toFixed(1)+'" fill="#fff" stroke="'+col(sv)+'" stroke-width="2"/><rect x="'+c.x.toFixed(1)+'" y="'+c.y.toFixed(1)+'" width="'+c.w.toFixed(1)+'" height="'+Math.min(16,c.h).toFixed(1)+'" fill="'+col(sv)+'"/>';if(c.w>30)s+='<text x="'+(c.x+5).toFixed(1)+'" y="'+(c.y+12).toFixed(1)+'" font-size="11" font-weight="600" fill="#fff">'+esc(cut(sv+' · '+fmt(c.v)+' loc',Math.floor(c.w/6.5)))+'</text>';s+='<title>'+esc(sv)+' · '+c.v+' loc · '+esc(root.path)+'</title></g>';draw(sv,root,c.x+pad,c.y+18,c.w-2*pad,c.h-18-pad,1)}
s+='</svg>';const d=svgDiv(s);d.querySelector('svg').addEventListener('click',e=>{const g=e.target.closest('.node');if(g)go('tree',{service:g.dataset.svc})});
d.append(legend('area = LOC · outer box = service · inner = directory (depth 1, then depth 2 when the cell is big enough) · hover for path, files, languages, responsibility',{style:'background:repeating-linear-gradient(45deg,#fecaca 0 2px,#fff 2px 5px);border:1px dashed #b91c1c',t:'P2-2 heavy directory, no responsibility'}));return d}
// ---------- 4. page → api → table flow (sankey)
function flowView(){const L=D.links;if(!L.length&&!D.routes.length)return null;const CAP=70;
const pages=new Map(),apis=new Map(),tables=new Map();const add=(m,id,svc,extra)=>{if(!m.has(id))m.set(id,{id,svc,deg:0,...extra});return m.get(id)};
for(const r of D.routes){if(r.kind==='page')add(pages,r.service+' · '+r.path,r.service,{label:r.path});else if(r.kind==='api')add(apis,r.service+' · '+r.method+' '+r.path,r.service,{label:r.method+' '+r.path,write:isWrite(r)})}
for(const r of D.models)add(tables,r.service+' · '+r.table,r.service,{label:r.table,shared:sharedTables.has(r.table)});
const links=[];for(const l of L){const a=l.from_service+' · '+l.from,b=l.to_service+' · '+l.to;if(l.kind==='page_api'){add(pages,a,l.from_service,{label:l.from});add(apis,b,l.to_service,{label:l.to,write:/^(POST|PUT|PATCH|DELETE|ANY)\b/.test(l.to)})}else if(l.kind==='api_table'){add(apis,a,l.from_service,{label:l.from,write:/^(POST|PUT|PATCH|DELETE|ANY)\b/.test(l.from)});add(tables,b,l.to_service,{label:l.to,shared:sharedTables.has(l.to)})}else if(l.kind==='api_api'){const isFile=/[\/\\]|\.\w{1,5}$/.test(l.from)&&!/^[A-Z]+ /.test(l.from);add(apis,a,l.from_service,{label:isFile?'↗ '+l.from.split(/[\/\\]/).slice(-2).join('/'):l.from,file:isFile});add(apis,b,l.to_service,{label:l.to,write:/^(POST|PUT|PATCH|DELETE|ANY)\b/.test(l.to)})}else continue;links.push({a,b,kind:l.kind,conf:l.confidence})}
for(const l of links){const A=pages.get(l.a)||apis.get(l.a),B=apis.get(l.b)||tables.get(l.b);if(A)A.deg++;if(B)B.deg++}
const capCol=(m,name)=>{let arr=[...m.values()];if(arr.length<=CAP)return arr;arr.sort((a,b)=>b.deg-a.deg);const keep=arr.slice(0,CAP),rest=arr.slice(CAP);const agg={id:'…'+name,svc:'',label:'… '+rest.length+' more '+name+' (lowest degree)',deg:rest.reduce((s,x)=>s+x.deg,0),agg:new Set(rest.map(x=>x.id))};return[...keep,agg]};
const cols=[capCol(pages,'pages'),capCol(apis,'APIs'),capCol(tables,'tables')];const remap=new Map();for(const c of cols)for(const n of c)if(n.agg)for(const id of n.agg)remap.set(id,n.id);const rid=id=>remap.get(id)||id;
for(const c of cols)c.sort((a,b)=>(a.agg?1:0)-(b.agg?1:0)||(b.deg>0)-(a.deg>0)||a.svc.localeCompare(b.svc)||a.label.localeCompare(b.label));
const byId=new Map();cols.forEach((c,ci)=>c.forEach(n=>{n.col=ci;n.val=Math.max(1,n.deg);byId.set(n.id,n)}));
const agL=new Map();for(const l of links){const a=rid(l.a),b=rid(l.b);const k=a+'\u0000'+b+'\u0000'+l.kind;const e=agL.get(k)||{a,b,kind:l.kind,n:0,low:true};e.n++;if(l.conf!=='low')e.low=false;agL.set(k,e)}const EL=[...agL.values()].filter(e=>byId.has(e.a)&&byId.has(e.b));
const n=Math.max(...cols.map(c=>c.length)),GAP=4,MINH=7;const H=Math.max(380,Math.min(1400,n*(MINH+GAP)+40));const W=1200,X=[30,W/2-80,W-190],NWd=12;
let unit=Infinity;for(const c of cols){const sum=c.reduce((s,x)=>s+x.val,0);if(sum)unit=Math.min(unit,(H-30-GAP*(c.length-1))/sum)}if(!isFinite(unit))unit=8;unit=Math.min(unit,16);
for(const c of cols){let y=15;const tot=c.reduce((s,x)=>s+x.val*unit+GAP,0)-GAP;y=Math.max(15,(H-tot)/2);for(const x of c){x.y=y;x.h=Math.max(MINH,x.val*unit);y+=x.h+GAP}}
const outO=new Map(),inO=new Map();EL.sort((p,q)=>byId.get(p.b).y-byId.get(q.b).y);const so=new Map();for(const e of EL){const A=byId.get(e.a);so.set(e,(outO.get(e.a)||0));outO.set(e.a,(outO.get(e.a)||0)+e.n)}EL.sort((p,q)=>byId.get(p.a).y-byId.get(q.a).y);const ti=new Map();for(const e of EL){ti.set(e,(inO.get(e.b)||0));inO.set(e.b,(inO.get(e.b)||0)+e.n)}
let s='<svg class="sk" viewBox="0 0 '+W+' '+H+'" width="100%" style="height:auto"><defs><marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0L10,5L0,10z" fill="#44403c"/></marker></defs>';['Pages','APIs','Tables'].forEach((t,i)=>s+='<text x="'+(X[i]+(i===2?NWd:0))+'" y="10" font-size="11" font-weight="600" fill="#78716c" '+(i===2?'text-anchor="end"':'')+'>'+t+' ('+cols[i].length+(cols[i].some(x=>x.agg)?'+':'')+')</text>');
for(const e of EL){const A=byId.get(e.a),B=byId.get(e.b);const ua=A.h/Math.max(A.val,outO.get(e.a)||0,1),ub=B.h/Math.max(B.val,inO.get(e.b)||0,1);const y1=A.y+so.get(e)*ua+e.n*ua/2,y2=B.y+ti.get(e)*ub+e.n*ub/2;const th=Math.max(1.2,Math.min(e.n*ua,e.n*ub));
if(e.kind==='api_api'){const x=X[1];const bx=x-50-Math.abs(y2-y1)/5;s+='<path class="lk" fill="none" data-a="'+esc(e.a)+'" data-b="'+esc(e.b)+'" d="M'+x+','+y1+' C'+bx+','+y1+' '+bx+','+y2+' '+x+','+y2+'" stroke="#44403c" stroke-width="'+Math.min(th,2).toFixed(1)+'" stroke-dasharray="4 3" opacity=".7" marker-end="url(#ar)"><title>'+esc(e.a)+' → '+esc(e.b)+' (api_api ×'+e.n+')</title></path>';continue}
const x1=X[A.col]+NWd,x2=X[B.col],mx=(x1+x2)/2;s+='<path class="lk" fill="none" data-a="'+esc(e.a)+'" data-b="'+esc(e.b)+'" d="M'+x1+','+y1.toFixed(1)+' C'+mx+','+y1.toFixed(1)+' '+mx+','+y2.toFixed(1)+' '+x2+','+y2.toFixed(1)+'" stroke="'+col(A.svc)+'" stroke-width="'+th.toFixed(1)+'" opacity=".35" '+(e.low?'stroke-dasharray="5 4"':'')+'><title>'+esc(e.a)+' → '+esc(e.b)+' ×'+e.n+(e.low?' · confidence low':'')+'</title></path>'}
cols.forEach((c,ci)=>{for(const x of c){const un=ci===1&&unguarded.has(x.id),na=ci===1&&unaudited.has(x.id);const fill=x.deg?col(x.svc)||'#a8a29e':'#d6d3d1';s+='<g class="nd" data-id="'+esc(x.id)+'"><rect x="'+X[ci]+'" y="'+x.y.toFixed(1)+'" width="'+NWd+'" height="'+x.h.toFixed(1)+'" fill="'+(x.agg?'#e7e5e4':fill)+'" '+(un?'stroke="#b91c1c" stroke-width="2.5"':x.shared?'stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="3 2"':x.write?'stroke="#1c1917" stroke-width="1"':'')+'/>';
if(na)s+='<circle cx="'+(X[ci]+NWd+5)+'" cy="'+(x.y+3).toFixed(1)+'" r="3" fill="#c2410c"/>';const big=x.h>=10;s+='<text class="'+(big?'':'sm')+'" x="'+(ci===2?X[ci]-4:X[ci]+NWd+(na?10:4))+'" y="'+(x.y+Math.min(x.h,12)/2+3.5).toFixed(1)+'" font-size="10" '+(ci===2?'text-anchor="end"':'')+' fill="'+(x.file?'#78716c':x.deg?'#1c1917':'#a8a29e')+'" '+(un?'font-weight="700"':x.file?'font-style="italic"':'')+'>'+esc(cut(x.label,ci===1?40:30))+'</text>';
s+='<title>'+esc(x.id)+' · '+x.deg+' link(s)'+(x.file?' · call-site file (api_api source is the file, not a route)':'')+(un?' · P0-1 unguarded write':'')+(na?' · P1-1 no audit point':'')+(x.shared?' · P0-2 shared table':'')+(x.deg?'':' · no link found')+'</title></g>'}});
s+='</svg>';const d=svgDiv(s);const svg=d.querySelector('svg');const det=el('div',{class:'detail',style:'display:none'});d.append(det);
const nb=new Map();for(const e of EL){(nb.get(e.a)||nb.set(e.a,new Set()).get(e.a)).add(e.b);(nb.get(e.b)||nb.set(e.b,new Set()).get(e.b)).add(e.a)}
let sel=null;function hl(id){const set=new Set();if(id){set.add(id);for(const x of nb.get(id)||[]){set.add(x);for(const y of nb.get(x)||[])set.add(y)}}svg.querySelectorAll('.lk').forEach(p=>{p.classList.toggle('dim',!!id&&!(set.has(p.dataset.a)&&set.has(p.dataset.b)));p.classList.toggle('hi',!!id&&(p.dataset.a===id||p.dataset.b===id))});svg.querySelectorAll('.nd').forEach(g=>g.classList.toggle('dim',!!id&&!set.has(g.dataset.id)))}
svg.addEventListener('mouseover',e=>{const g=e.target.closest('.nd');if(g&&!sel)hl(g.dataset.id)});svg.addEventListener('mouseout',e=>{if(e.target.closest('.nd')&&!sel)hl(null)});
svg.addEventListener('click',e=>{const g=e.target.closest('.nd');if(!g)return;const id=g.dataset.id;if(sel===id){sel=null;hl(null);det.style.display='none';return}sel=id;hl(id);const x=byId.get(id);const ups=EL.filter(l=>l.b===id).map(l=>l.a),dns=EL.filter(l=>l.a===id).map(l=>l.b);det.style.display='';det.innerHTML='';det.append(el('b',{},x.id),' — '+x.deg+' link(s). ',el('span',{},ups.length?'from: '+ups.join(', '):'no upstream'),el('br'),el('span',{},dns.length?'to: '+dns.join(', '):'no downstream'),el('br'),el('a',{href:'#',onclick:ev=>{ev.preventDefault();go('links',{q:x.label})}},'open in Links'),' · click the node again to clear')});
d.append(legend('node height = links · colour = service',{style:'border:2.5px solid #b91c1c;background:#fff',t:'P0-1 write route without guard'},{style:'background:#c2410c;border-radius:50%',t:'P1-1 no audit point'},{style:'border:1.5px dashed #b91c1c;background:#fff',t:'P0-2 table in ≥2 services'},{style:'background:#d6d3d1',t:'no link found'},'dashed ribbon = confidence low · dashed arc on the right of APIs = api → api'));return d}
// ---------- 5. permission matrix
function permMatrix(){const R=D.routes.filter(r=>r.kind==='api');if(!R.length)return null;
const roleByHandler=new Map();for(const p of D.permissions){if(!p.roles_or_perms||!p.applies_to)continue;for(const h of String(p.applies_to).split(';'))for(const ro of p.roles_or_perms.split(';')){const t=ro.trim();if(t)(roleByHandler.get(p.service+'|'+h.trim())||roleByHandler.set(p.service+'|'+h.trim(),new Set()).get(p.service+'|'+h.trim())).add('role:'+t)}}
const rows=R.map(r=>{const g=String(r.auth_guard||'').split(';').map(x=>x.trim()).filter(Boolean);const cells=new Set(g.map(x=>x.startsWith('!')?'public!':x));for(const ro of roleByHandler.get(r.service+'|'+r.handler)||[])cells.add(ro);const w=isWrite(r);const ung=w&&![...cells].some(c=>c!=='public!');return{r,cells,w,ung}});
const colCount={};for(const x of rows)for(const c of x.cells)colCount[c]=(colCount[c]||0)+1;let cols=Object.keys(colCount).sort((a,b)=>colCount[b]-colCount[a]);const truncC=cols.length>40;cols=cols.slice(0,40);
let state={svc:''};const box=el('div');const tb=el('div',{class:'toolbar'});const sel=el('select',{onchange:e=>{state.svc=e.target.value;draw()}},el('option',{value:''},'all services'));for(const sv of SVC.filter(s=>R.some(r=>r.service===s)))sel.append(el('option',{value:sv},sv));const info=el('span',{class:'cnt'});tb.append(sel,info);box.append(tb);const host=el('div',{class:'tw',style:'max-height:640px'});box.append(host);
function draw(){let rs=rows.filter(x=>!state.svc||x.r.service===state.svc).sort((a,b)=>(b.ung-a.ung)||(b.w-a.w)||a.r.service.localeCompare(b.r.service)||a.r.path.localeCompare(b.r.path));const total=rs.length;rs=rs.slice(0,200);
const C=17,GL=300,GT=96,W=GL+cols.length*C+60,H=GT+rs.length*C+6;let s='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" style="display:block">';
cols.forEach((c,j)=>s+='<text transform="translate('+(GL+j*C+C/2+3)+','+(GT-6)+') rotate(-60)" font-size="9" fill="'+(c==='public!'?'#b91c1c':c.startsWith('role:')?'#7c3aed':'#1c1917')+'"><title>'+esc(c)+' · '+colCount[c]+' routes</title>'+esc(cut(c,20))+'</text>');
s+='<text x="'+(GL+cols.length*C+8)+'" y="'+(GT-6)+'" font-size="9" fill="#78716c">#</text>';
rs.forEach((x,i)=>{const y=GT+i*C;const lab=x.r.method+' '+x.r.path;s+='<g><rect x="0" y="'+y+'" width="'+W+'" height="'+(C-1)+'" fill="'+(x.ung?'#fef2f2':i%2?'#fafaf9':'#fff')+'"/><rect x="0" y="'+y+'" width="4" height="'+(C-1)+'" fill="'+col(x.r.service)+'"/><text x="8" y="'+(y+12)+'" font-size="10" '+(x.w?'font-weight="600"':'')+' fill="'+(x.ung?'#b91c1c':'#1c1917')+'"><title>'+esc(x.r.service+' · '+lab+' · '+x.r.file+':'+x.r.line)+'</title>'+esc(cut(x.r.service+' · '+lab,46))+'</text>';
cols.forEach((c,j)=>{if(x.cells.has(c))s+='<rect x="'+(GL+j*C+2)+'" y="'+(y+2)+'" width="'+(C-5)+'" height="'+(C-5)+'" rx="2" fill="'+(c==='public!'?'#b91c1c':c.startsWith('role:')?'#7c3aed':'#15803d')+'"><title>'+esc(lab+' · '+c)+'</title></rect>'});
s+='<text x="'+(GL+cols.length*C+8)+'" y="'+(y+12)+'" font-size="9" fill="#78716c">'+x.cells.size+'</text></g>'});
s+='</svg>';host.innerHTML=s;info.textContent=total+' routes'+(total>200?' (first 200 shown; filter by service)':'')+' · '+rs.filter(x=>x.ung).length+' unguarded write'+(truncC?' · columns truncated to 40':'')}
draw();box.append(legend({style:'background:#15803d',t:'guard mechanism on route'},{style:'background:#7c3aed',t:'role/permission literal (permissions.csv)'},{style:'background:#b91c1c',t:'explicit public marker'},{style:'background:#fef2f2;border:1px solid #fecaca',t:'write route with no guard (P0-1)'},'bold = write method'));return box}
// ---------- 6. audit coverage
function auditBars(){const per={};for(const r of D.routes){if(!isWrite(r))continue;per[r.service]=per[r.service]||{w:0,a:0,miss:[]};per[r.service].w++;if(D.audit_points.some(a=>a.service===r.service&&a.file===r.file))per[r.service].a++;else per[r.service].miss.push(r.method+' '+r.path)}
const svcs=Object.keys(per).sort((a,b)=>(per[b].w-per[b].a)-(per[a].w-per[a].a)||a.localeCompare(b));if(!svcs.length)return null;const maxW=Math.max(...svcs.map(s=>per[s].w));const W=760,bh=22,GL=130,BW=460,H=svcs.length*bh+8;
let s='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" style="max-width:100%;height:auto">';svcs.forEach((n,i)=>{const{w,a}=per[n],y=i*bh+4,sw=BW*w/maxW,aw=sw*a/w;s+='<g class="node" data-svc="'+esc(n)+'"><rect x="'+(GL-8)+'" y="'+y+'" width="6" height="16" rx="2" fill="'+col(n)+'"/><text x="'+(GL-14)+'" y="'+(y+12)+'" font-size="11" text-anchor="end">'+esc(cut(n,18))+'</text><rect x="'+GL+'" y="'+y+'" width="'+aw.toFixed(1)+'" height="16" fill="#15803d"/><rect x="'+(GL+aw).toFixed(1)+'" y="'+y+'" width="'+(sw-aw).toFixed(1)+'" height="16" fill="#dc2626"/><text x="'+(GL+sw+6).toFixed(1)+'" y="'+(y+12)+'" font-size="11">'+a+'/'+w+' audited ('+Math.round(100*a/w)+'%)</text><title>'+esc(n)+' · '+(w-a)+' write route(s) without audit point — click to list</title></g>'});
s+='</svg>';const d=svgDiv(s);const det=el('div',{class:'detail',style:'display:none'});d.append(det);d.querySelector('svg').addEventListener('click',e=>{const g=e.target.closest('.node');if(!g)return;const n=g.dataset.svc;det.style.display='';det.innerHTML='';det.append(el('b',{},n+' — '+per[n].miss.length+' write route(s) without audit point: '),per[n].miss.slice(0,40).join(' · ')+(per[n].miss.length>40?' …':''),el('br'),el('a',{href:'#',onclick:ev=>{ev.preventDefault();go('priorities',{service:n,rule:'P1-1'})}},'open P1-1 rows'))});
d.append(legend({style:'background:#15803d',t:'write routes with an audit point in the same file'},{style:'background:#dc2626',t:'write routes with none (P1-1)'},'bar length ∝ number of write routes'));return d}
// ---------- 7. field naming clusters
function fieldClusters(){const rows=D.priorities.filter(p=>p.rule_id==='P1-2');if(!rows.length)return el('div',{class:'fallback'},'No naming or type variants detected across models.csv.');const typeOf=new Map();for(const m of D.models)typeOf.set(m.service+'|'+m.table+'|'+m.column,m.type||'');
const box=el('div');for(const r of rows.sort((a,b)=>(a.suppressed?1:0)-(b.suppressed?1:0)||a.subject.localeCompare(b.subject))){const isType=r.subject.includes('#type');const locs=String(r.evidence_row||'').split(';').map(x=>x.split('|')).filter(x=>x.length===3);const groups={};for(const[sv,tb,c]of locs){const k=isType?(typeOf.get(sv+'|'+tb+'|'+c)||'?'):c;(groups[k]=groups[k]||[]).push([sv,tb,c])}
const cl=el('div',{class:'cluster'+(r.suppressed?' sup':'')},el('h4',{},el('code',{},r.subject.replace('#type','')),' ',el('span',{style:'font-size:11px;color:var(--muted)'},isType?'type drift':'spelling drift',' · '+Object.keys(groups).length+' variants · '+locs.length+' columns'+(r.suppressed?' · suppressed':''))));
for(const[k,items]of Object.entries(groups)){const chips=el('div',{class:'chips'});for(const[sv,tb,c]of items)chips.append(el('span',{class:'chip',title:sv+' · '+tb+'.'+c+' : '+(typeOf.get(sv+'|'+tb+'|'+c)||'?')},el('i',{style:'background:'+col(sv)}),tb+'.'+c));cl.append(el('div',{class:'var'},el('b',{},k),chips))}
cl.append(el('div',{style:'font-size:11px;color:var(--muted);margin-top:4px'},r.detail));box.append(cl)}return box}
// ---------- 8. coverage
function coverage(){const S=Object.entries(M.services||{});if(!S.length)return null;const box=el('div',{class:'cov'});const maxF=Math.max(1,...S.map(([,s])=>(s.files_scanned||0)+(s.files_skipped||0)));const cs=['routes','models','permissions','audit_points','cross_calls'];const maxR=Math.max(1,...S.flatMap(([,s])=>cs.map(c=>(s.rows_per_csv||{})[c]||0)));
box.append(el('div',{class:'row',style:'color:var(--muted)'},el('span',{},'service'),el('span',{},'files scanned (grey) / skipped (amber), width ∝ total'),el('span',{},'rows: '+cs.join(' · ')),el('span',{},'detected by · frameworks · skip reasons')));
for(const[n,s]of S){const sc=s.files_scanned||0,sk=s.files_skipped||0,tot=sc+sk;const bar=el('div',{class:'bar',style:'width:'+Math.max(4,100*tot/maxF)+'%'},el('i',{style:'width:'+(tot?100*sc/tot:0)+'%;background:#a8a29e',title:sc+' scanned'}),el('i',{style:'width:'+(tot?100*sk/tot:0)+'%;background:#f59e0b',title:sk+' skipped'}));
const mini=el('div',{class:'mini'});for(const c of cs){const v=(s.rows_per_csv||{})[c]||0;mini.append(el('i',{class:v?'':'z',style:'height:'+Math.max(3,26*v/maxR)+'px',title:c+': '+v}))}
box.append(el('div',{class:'row'},el('span',{},el('span',{style:'display:inline-block;width:10px;height:10px;border-radius:2px;background:'+col(n)+';margin-right:6px'}),n),el('span',{},bar,el('span',{style:'font-size:11px;color:var(--muted)'},sc+' / '+sk)),mini,el('span',{style:'font-size:11px;color:var(--muted)'},(s.detected_by||'')+' · '+((s.framework_hints||[]).join(', ')||'no framework hint')+' · '+(Object.entries(s.skip_reasons||{}).map(([k,v])=>k+' '+v).join(', ')||'—'))))}
box.append(legend({style:'background:#fca5a5',t:'zero rows in that CSV'},'rows bars share one scale across services'));return box}
// ---------- tables
let sort={};
function table(c,t){const rows=D[t]||[];if(!rows.length){c.append(el('div',{class:'fallback'},'No rows in '+t+'.csv'));return}const cols=Object.keys(rows[0]);const ed=P.editable[t]||[];
const tb=el('div',{class:'toolbar'});const q=el('input',{placeholder:'filter (all columns)…',value:filterState.q||'',oninput:e=>{filterState.q=e.target.value;draw()}});tb.append(q);
const svcCol=cols.includes('service')?'service':cols.includes('from_service')?'from_service':null;if(svcCol){const s=el('select',{onchange:e=>{filterState[svcCol]=e.target.value;draw()}},el('option',{value:''},'all services'));for(const v of [...new Set(rows.flatMap(r=>String(r[svcCol]).split(';')))].sort())s.append(el('option',{value:v,selected:(filterState[svcCol]||filterState.service)===v?'':null},v));tb.append(s);if(filterState.service&&!filterState[svcCol])filterState[svcCol]=filterState.service}
if(t==='priorities'){const s=el('select',{onchange:e=>{filterState.level=e.target.value;draw()}},el('option',{value:''},'all levels'));for(const v of['P0','P1','P2'])s.append(el('option',{value:v,selected:filterState.level===v?'':null},v));tb.append(s);const s2=el('select',{onchange:e=>{filterState.rule=e.target.value;draw()}},el('option',{value:''},'all rules'));for(const v of RULES)s2.append(el('option',{value:v,selected:filterState.rule===v?'':null},v));tb.append(s2)}
if(t==='cross_calls'){const s=el('select',{onchange:e=>{filterState.to_service_confidence=e.target.value;draw()}},el('option',{value:''},'any confidence'));for(const v of['high','medium','low'])s.append(el('option',{value:v,selected:filterState.to_service_confidence===v?'':null},v));tb.append(s)}
const cnt=el('span',{class:'cnt'});tb.append(cnt,el('button',{onclick:()=>downloadCsv(t,rows)},'Download CSV'));c.append(tb);
const wrap=el('div',{class:'tw'});c.append(wrap);
function draw(){const q=(filterState.q||'').toLowerCase();let rs=rows.filter(r=>(!q||Object.values(r).join(' ').toLowerCase().includes(q))&&(!svcCol||!filterState[svcCol]||String(r[svcCol]).split(';').includes(filterState[svcCol]))&&(!filterState.level||r.level===filterState.level)&&(!filterState.rule||r.rule_id===filterState.rule)&&(!filterState.to_service_confidence||r.to_service_confidence===filterState.to_service_confidence));
if(sort.col){const k=sort.col,d=sort.dir;rs=[...rs].sort((a,b)=>{const x=a[k]??'',y=b[k]??'';const nx=+x,ny=+y;const c=(x!==''&&y!==''&&!isNaN(nx)&&!isNaN(ny))?nx-ny:String(x).localeCompare(String(y));return d==='s'?c:-c})}
cnt.textContent=rs.length+' / '+rows.length+' rows';const tbl=el('table');const hr=el('tr');for(const col of cols)hr.append(el('th',{class:sort.col===col?sort.dir:'',onclick:()=>{sort={col,dir:sort.col===col&&sort.dir==='s'?'d':'s'};draw()}},col));tbl.append(hr);
const frag=document.createDocumentFragment();for(const r of rs.slice(0,3000)){const tr=el('tr',{class:(r.level||'')+(r.suppressed?' sup':'')});for(const col of cols){const a=annOf(t,r);let v=r[col]??'';if(ed.includes(col)&&a[col]!=null)v=a[col];const td=el('td',{},v);if(ed.includes(col)){td.setAttribute('contenteditable','true');td.title='editable — stored in annotations';td.addEventListener('blur',()=>setAnn(t,r,col,td.textContent.trim()))}else if(col==='file'&&v)td.append(' ',el('code',{},':'+(r.line||'')));tr.append(td)}frag.append(tr)}tbl.append(frag);wrap.innerHTML='';wrap.append(tbl);if(rs.length>3000)wrap.append(el('div',{class:'fallback'},'showing first 3000 rows — narrow the filter'))}
draw()}
function setAnn(t,r,col,val){const k=key(t,r);const e=ANN.entries[k]||{};if((e[col]||'')===val)return;e[col]=val;e.updated=new Date().toISOString();if(t==='priorities'&&col==='note')e.false_positive=/^(fp|false positive|not a conflict|ok|ignore)/i.test(val);ANN.entries[k]=e;dirtyAnn=true;nav();try{localStorage.setItem('audit-ann:'+(M.project||''),JSON.stringify(ANN))}catch(_){}}
function exportAnn(){const b=new Blob([JSON.stringify(ANN,null,2)],{type:'application/json'});const a=el('a',{href:URL.createObjectURL(b),download:'annotations.json'});document.body.append(a);a.click();a.remove();dirtyAnn=false;nav()}
function importAnn(e){const f=e.target.files[0];if(!f)return;f.text().then(tx=>{const j=JSON.parse(tx);Object.assign(ANN.entries,j.entries||{});dirtyAnn=true;render()})}
function downloadCsv(t,rows){const cols=Object.keys(rows[0]);const csv=[cols.join(',')].concat(rows.map(r=>cols.map(c=>'"'+String(r[c]??'').replace(/"/g,'""')+'"').join(','))).join('\n');const b=new Blob([csv],{type:'text/csv'});const a=el('a',{href:URL.createObjectURL(b),download:t+'.csv'});document.body.append(a);a.click();a.remove()}
try{const saved=localStorage.getItem('audit-ann:'+(M.project||''));if(saved){const j=JSON.parse(saved);for(const[k,v]of Object.entries(j.entries||{}))if(!ANN.entries[k]||(v.updated||'')>(ANN.entries[k].updated||''))ANN.entries[k]=v}}catch(_){}
render();
</script></body></html>
"""

if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "docs/audit"))
