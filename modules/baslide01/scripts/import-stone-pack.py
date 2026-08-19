#!/usr/bin/env python3
"""Import the 合生汇 2026-06 reference pack into D03 and link pages to formulas."""
from __future__ import annotations

import csv
import json
import math
import re
import sqlite3
import statistics
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PACK = Path(
    "/Users/af/Public/APUCH/IPTrust/TableAI/education01/边江/石头先生/data/"
    "beijing-chaoyang-heshenghui-burger-2026-06"
)
SKU_DIR = Path("/Users/af/Public/APUCH/IPTrust/TableAI/education01/边江/石头先生/data/sku-catalog")
DATA_DIR = ROOT / "decks/stone-briefing/data"
DB_PATH = DATA_DIR / "pack.sqlite"
MD08 = ROOT / "ref/mds/08_北京西式快餐可参考品牌分析专项_B1.0.md"

STORE_FILES = {
    "city_beijing": "city_beijing.csv",
    "district_chaoyang": "district_chaoyang.csv",
    "ring_0_500m": "ring_0_500m.csv",
    "ring_500m_1km": "ring_500m_1km.csv",
    "ring_1km_3km": "ring_1km_3km.csv",
    "ring_3km_5km": "ring_3km_5km.csv",
    "ring_0_5km_all": "ring_0_5km_all.csv",
    "mall_heshenghui_inside": "mall_heshenghui_inside.csv",
    "mall_heshenghui_all_dining": "mall_heshenghui_all_dining.csv",
    "excluded_not_western": "excluded_not_western.csv",
    "included_despite_wrong_category": "included_despite_wrong_category.csv",
}

BRAND_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("麦当劳", re.compile(r"麦当劳|mcdonald", re.I)),
    ("肯德基", re.compile(r"肯德基|\bKFC\b", re.I)),
    ("必胜客", re.compile(r"必胜客|Pizza\s*Hut", re.I)),
    ("华莱士", re.compile(r"华莱士")),
    ("赛百味 SUBWAY", re.compile(r"赛百味|subway", re.I)),
    ("达美乐比萨", re.compile(r"达美乐")),
    ("塔斯汀", re.compile(r"塔斯汀")),
    ("汉堡王", re.compile(r"汉堡王|Burger\s*King", re.I)),
    ("比格比萨自助", re.compile(r"比格比萨|比格披萨")),
    ("萨莉亚", re.compile(r"萨莉亚")),
    ("牛约堡", re.compile(r"牛约堡")),
    ("超级碗 FOODBOWL", re.compile(r"超级碗|FOODBOWL", re.I)),
    ("Wagas 沃歌斯", re.compile(r"wagas|沃歌斯", re.I)),
    ("MURVEY 蔓味轻食", re.compile(r"MURVEY|蔓味", re.I)),
    ("棒约翰", re.compile(r"棒约翰|Papa\s*John", re.I)),
    ("轻遇三明治", re.compile(r"轻遇")),
    ("德克士", re.compile(r"德克士|dicos", re.I)),
    ("披萨革命", re.compile(r"披萨革命|比萨革命")),
    ("犇犇堡", re.compile(r"犇犇堡")),
    ("尊宝比萨", re.compile(r"尊宝比萨|尊宝披萨")),
    ("Tubestation 站点比萨", re.compile(r"Tubestation|站点比萨|站点披萨", re.I)),
    ("BAKER&SPICE", re.compile(r"BAKER\s*&?\s*SPICE", re.I)),
    ("Timefor 牛排意面", re.compile(r"Timefor", re.I)),
    ("KPRO 肯律轻食", re.compile(r"KPRO|肯律", re.I)),
    ("极度比萨", re.compile(r"极度比萨|极度披萨|极致·极度")),
    ("好伦哥", re.compile(r"好伦哥")),
    ("西十二街牛排", re.compile(r"西十二街")),
    ("bluefrog 蓝蛙", re.compile(r"bluefrog|蓝蛙", re.I)),
    ("油梨树 AVOCADO TREE", re.compile(r"油梨树|AVOCADO\s*TREE", re.I)),
    ("THE WOODS", re.compile(r"THE\s*WOODS", re.I)),
    ("gaga", re.compile(r"\bgaga\b", re.I)),
    ("沙野轻食", re.compile(r"沙野轻食")),
    ("Shake Shack", re.compile(r"Shake\s*Shack", re.I)),
    ("西堤牛排", re.compile(r"西堤牛排")),
    ("Papà Danilo", re.compile(r"Danilo|达尼罗", re.I)),
    ("墨纪 Mojí", re.compile(r"墨纪|Mojí|Moji", re.I)),
    ("京 A Taproom", re.compile(r"京\s*A|京A")),
    ("安妮意大利餐厅", re.compile(r"安妮意大利")),
    ("TACO BELL", re.compile(r"TACO\s*BELL|塔可钟", re.I)),
    ("左右手", re.compile(r"左右手")),
    ("SPACELAB 失重餐厅", re.compile(r"SPACELAB|失重餐厅", re.I)),
    ("品尝 SAVOR", re.compile(r"品尝SAVOR|品尝\s*SAVOR", re.I)),
    ("石头先生的烤炉", re.compile(r"石头先生的烤炉")),
    ("魏斯理", re.compile(r"魏斯理|Wesley\s*Burger", re.I)),
]

BANDS = [
    ("< 25 元", 0, 25),
    ("25–35 元", 25, 35),
    ("35–45 元", 35, 45),
    ("45–55 元", 45, 55),
    ("55–65 元", 55, 65),
    ("65–80 元", 65, 80),
    ("80–100 元", 80, 100),
    ("100 元以上", 100, 1e9),
]

WEB_GAPS = [
    {
        "id": "wesley-burger",
        "query": "魏斯理汉堡",
        "why": "08 §5.1：北京库 0 家，全国直营 80+ 的第一参照",
        "urls": [
            "https://www.weijia1999.com/html/brand/266.html",
            "https://36kr.com/p/3719738894463490",
            "https://erhainews.com/n23430.html",
        ],
    },
]


def to_float(cell: str | None) -> float | None:
    if cell is None:
        return None
    s = str(cell).strip().replace(",", "").replace("，", "")
    if s in {"", "None", "—", "-", "n/a", "N/A"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = [h.lstrip("\ufeff") for h in (reader.fieldnames or [])]
        rows = []
        for raw in reader:
            row = {k.lstrip("\ufeff"): (v if v is not None else "") for k, v in raw.items()}
            rows.append(row)
    return headers, rows


def canon_brand(name: str, brand: str) -> str:
    blob = f"{name} {brand}"
    for label, pat in BRAND_RULES:
        if pat.search(blob):
            return label
    raw = (brand or "").strip()
    if raw:
        return raw
    cut = re.split(r"[（(]", name or "", maxsplit=1)[0].strip()
    return cut or "(unnamed)"


def median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def stdev(xs: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    return statistics.pstdev(xs)


def create_schema(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        DROP TABLE IF EXISTS store;
        DROP TABLE IF EXISTS sku;
        DROP TABLE IF EXISTS brand_rule;
        DROP TABLE IF EXISTS formula;
        DROP TABLE IF EXISTS formula_row;
        DROP TABLE IF EXISTS page_link;
        DROP TABLE IF EXISTS web_source;
        DROP TABLE IF EXISTS pack_meta;
        CREATE TABLE pack_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE store (
            scope TEXT NOT NULL,
            id TEXT,
            source_restaurant_id TEXT,
            name TEXT,
            brand_raw TEXT,
            brand_canon TEXT,
            branch TEXT,
            district TEXT,
            business_district TEXT,
            address TEXT,
            category_l1 TEXT,
            category_l2 TEXT,
            category_l3 TEXT,
            restaurant_type TEXT,
            rating REAL,
            avg_spend REAL,
            review_count REAL,
            longitude REAL,
            latitude REAL,
            distance_m REAL,
            ring TEXT,
            in_heshenghui_mall TEXT,
            match_rules TEXT,
            database_version TEXT
        );
        CREATE INDEX idx_store_scope ON store(scope);
        CREATE INDEX idx_store_canon ON store(brand_canon);
        CREATE TABLE sku (
            sku_id TEXT PRIMARY KEY,
            category TEXT,
            seq INTEGER,
            name TEXT,
            kind TEXT,
            price REAL,
            gross_margin REAL,
            order_rate REAL,
            flavor TEXT,
            selling_point TEXT,
            recipe TEXT,
            station TEXT,
            notes TEXT,
            image_filename TEXT,
            image_path TEXT,
            image_url TEXT
        );
        CREATE TABLE brand_rule (
            canon TEXT PRIMARY KEY,
            pattern TEXT NOT NULL
        );
        CREATE TABLE formula (
            id TEXT PRIMARY KEY,
            name TEXT,
            expr TEXT,
            unit TEXT,
            value TEXT,
            n INTEGER,
            source_table TEXT,
            note TEXT
        );
        CREATE TABLE formula_row (
            formula_id TEXT,
            ord INTEGER,
            label TEXT,
            n REAL,
            spend REAL,
            rating REAL,
            extra TEXT
        );
        CREATE TABLE page_link (
            deck_id TEXT,
            page INTEGER,
            job TEXT,
            title TEXT,
            fill TEXT,
            formula_id TEXT,
            href TEXT,
            data_ok INTEGER
        );
        CREATE TABLE web_source (
            id TEXT,
            query TEXT,
            url TEXT,
            status INTEGER,
            excerpt TEXT,
            why TEXT,
            PRIMARY KEY (id, url)
        );
        """
    )


def insert_stores(con: sqlite3.Connection) -> None:
    for scope, filename in STORE_FILES.items():
        path = PACK / filename
        assert path.is_file(), path
        headers, rows = load_csv(path)
        assert "name" in headers, headers
        payload = []
        for row in rows:
            name = row.get("name", "")
            brand = row.get("brand", "")
            payload.append(
                (
                    scope,
                    row.get("id", ""),
                    row.get("source_restaurant_id", ""),
                    name,
                    brand,
                    canon_brand(name, brand),
                    row.get("branch", ""),
                    row.get("district", ""),
                    row.get("business_district", ""),
                    row.get("address", ""),
                    row.get("category_l1", ""),
                    row.get("category_l2", ""),
                    row.get("category_l3", ""),
                    row.get("restaurant_type", ""),
                    to_float(row.get("rating")),
                    to_float(row.get("avg_spend")),
                    to_float(row.get("review_count")),
                    to_float(row.get("longitude")),
                    to_float(row.get("latitude")),
                    to_float(row.get("distance_m")),
                    row.get("ring", ""),
                    row.get("in_heshenghui_mall", ""),
                    row.get("match_rules", ""),
                    row.get("database_version", ""),
                )
            )
        con.executemany(
            """INSERT INTO store VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            payload,
        )
        assert con.execute("SELECT COUNT(*) FROM store WHERE scope=?", (scope,)).fetchone()[0] == len(rows)


def insert_skus(con: sqlite3.Connection) -> None:
    path = SKU_DIR / "skus.csv"
    assert path.is_file(), path
    _, rows = load_csv(path)
    payload = []
    for row in rows:
        payload.append(
            (
                row.get("sku_id", ""),
                row.get("category", ""),
                int(to_float(row.get("seq")) or 0),
                row.get("name", ""),
                row.get("kind", ""),
                to_float(row.get("price")),
                to_float(row.get("gross_margin")),
                to_float(row.get("order_rate")),
                row.get("flavor", ""),
                row.get("selling_point", ""),
                row.get("recipe", ""),
                row.get("station", ""),
                row.get("notes", ""),
                row.get("image_filename", ""),
                row.get("image_path", ""),
                row.get("image_url", ""),
            )
        )
    con.executemany(
        """INSERT INTO sku VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        payload,
    )
    assert con.execute("SELECT COUNT(*) FROM sku").fetchone()[0] == len(rows)


def insert_rules(con: sqlite3.Connection) -> None:
    con.executemany(
        "INSERT INTO brand_rule(canon, pattern) VALUES (?,?)",
        [(label, pat.pattern) for label, pat in BRAND_RULES],
    )


def put_formula(
    con: sqlite3.Connection,
    fid: str,
    name: str,
    expr: str,
    unit: str,
    value: Any,
    n: int,
    source_table: str,
    note: str,
    rows: list[tuple[Any, ...]] | None = None,
) -> None:
    con.execute(
        "INSERT INTO formula VALUES (?,?,?,?,?,?,?,?)",
        (fid, name, expr, unit, str(value), n, source_table, note),
    )
    if not rows:
        return
    con.executemany(
        "INSERT INTO formula_row VALUES (?,?,?,?,?,?,?)",
        [
            (fid, i, str(label), n_v, spend, rating, extra)
            for i, (label, n_v, spend, rating, extra) in enumerate(rows)
        ],
    )


def compute_formulas(con: sqlite3.Connection) -> None:
    def count(scope: str) -> int:
        return int(con.execute("SELECT COUNT(*) FROM store WHERE scope=?", (scope,)).fetchone()[0])

    put_formula(con, "F01", "北京西式参考集", "COUNT(store WHERE scope=city_beijing)", "家", count("city_beijing"), count("city_beijing"), "store", "manifest.counts.city_beijing")
    put_formula(con, "F02", "朝阳区西式", "COUNT(store WHERE scope=district_chaoyang)", "家", count("district_chaoyang"), count("district_chaoyang"), "store", "manifest.counts.district_chaoyang")
    put_formula(con, "F03", "合生汇 5km 西式", "COUNT(store WHERE scope=ring_0_5km_all)", "家", count("ring_0_5km_all"), count("ring_0_5km_all"), "store", "四层环带并集")
    put_formula(con, "F04", "合生汇场内全餐饮", "COUNT(store WHERE scope=mall_heshenghui_all_dining)", "家", count("mall_heshenghui_all_dining"), count("mall_heshenghui_all_dining"), "store", "不限西式")
    put_formula(con, "F05", "合生汇场内西式", "COUNT(store WHERE scope=mall_heshenghui_inside)", "家", count("mall_heshenghui_inside"), count("mall_heshenghui_inside"), "store", "直接对手")

    city = con.execute(
        "SELECT name, brand_raw, brand_canon, rating, avg_spend, review_count, district, business_district, address FROM store WHERE scope='city_beijing'"
    ).fetchall()
    by_canon: dict[str, list[tuple[Any, ...]]] = {}
    for row in city:
        by_canon.setdefault(row[2], []).append(row)

    brand_rows = []
    for canon, rows in by_canon.items():
        spends = [r[4] for r in rows if r[4] and r[4] > 0]
        ratings = [r[3] for r in rows if r[3] and r[3] > 0]
        reviews = [r[5] for r in rows if r[5] is not None]
        n = len(rows)
        ge45 = sum(1 for x in ratings if x >= 4.5) / len(ratings) if ratings else None
        extra = json.dumps(
            {
                "review_median": median(reviews),
                "review_sum": sum(reviews) if reviews else 0,
                "cv": (stdev(spends) / (sum(spends) / len(spends))) if spends and len(spends) >= 2 and sum(spends) else None,
                "rating_sd": stdev(ratings),
                "share_4_5": ge45,
            },
            ensure_ascii=False,
        )
        brand_rows.append((canon, float(n), median(spends), (sum(ratings) / len(ratings)) if ratings else None, extra))
    brand_rows.sort(key=lambda x: -x[1])
    put_formula(
        con, "F06", "品牌归一化规模",
        "GROUP BY brand_canon; n=COUNT(*); spend=MEDIAN(avg_spend); rating=AVG(rating)",
        "品牌",
        sum(1 for r in brand_rows if r[1] >= 3),
        len(brand_rows),
        "store.city_beijing",
        "店名+品牌字段按 brand_rule 归一。CV=stdev(spend)/mean(spend)",
        brand_rows,
    )

    ge20 = [r for r in brand_rows if r[1] >= 20]
    put_formula(
        con, "F07", "北京门店 ≥ 20 家",
        "F06 WHERE n >= 20",
        "品牌",
        len(ge20),
        len(ge20),
        "formula_row F06",
        "对应 D03.1 图 2 / D05 图 2 清单",
        ge20,
    )

    ge3 = [r for r in brand_rows if r[1] >= 3 and r[2] is not None]
    band_rows = []
    for label, lo, hi in BANDS:
        hits = [r for r in ge3 if r[2] is not None and lo <= r[2] < hi]
        ge20n = sum(1 for r in hits if r[1] >= 20)
        mx = max(hits, key=lambda x: x[1]) if hits else None
        extra = json.dumps({"ge20": ge20n, "max_brand": mx[0] if mx else None, "max_n": mx[1] if mx else None}, ensure_ascii=False)
        band_rows.append((label, float(len(hits)), median([r[2] for r in hits if r[2] is not None]), median([r[3] for r in hits if r[3] is not None]), extra))
    put_formula(
        con, "F08", "价格带 × 规模天花板",
        "F06 WHERE n>=3 GROUP BY median_spend band; ge20=COUNT(n>=20)",
        "价格带",
        sum(json.loads(r[4])["ge20"] for r in band_rows),
        len(band_rows),
        "formula_row F06",
        "≥3 店品牌按人均中位分箱。对应 D03.1 图 1",
        band_rows,
    )

    burger_n = int(con.execute(
        "SELECT COUNT(*) FROM store WHERE scope='city_beijing' AND (name LIKE '%汉堡%' OR name LIKE '%Burger%' OR name LIKE '%BURGER%')"
    ).fetchone()[0])
    put_formula(con, "F09", "店名含汉堡/Burger", "COUNT(city_beijing WHERE name ~ 汉堡|Burger)", "家", burger_n, burger_n, "store", "06 声称 782；本包按店名复算")

    mall = con.execute(
        "SELECT name, brand_canon, rating, avg_spend, review_count FROM store WHERE scope='mall_heshenghui_all_dining'"
    ).fetchall()
    lt4 = sum(1 for r in mall if r[2] is not None and r[2] < 4.0)
    put_formula(con, "F10", "场内评分 < 4.0", "COUNT(mall_dining WHERE rating < 4) / COUNT(*)", "家", lt4, len(mall), "store", f"占比 {lt4}/{len(mall)}")

    inside = con.execute(
        "SELECT name, brand_canon, rating, avg_spend, review_count FROM store WHERE scope='mall_heshenghui_inside' ORDER BY review_count DESC"
    ).fetchall()
    put_formula(
        con, "F11", "场内西式九家",
        "SELECT * FROM mall_heshenghui_inside",
        "家",
        len(inside),
        len(inside),
        "store",
        "Shake Shack 合生汇店是价格锚",
        [(r[0], r[4] or 0, r[3], r[2], r[1]) for r in inside],
    )

    sister = con.execute(
        "SELECT name, brand_canon, rating, avg_spend, review_count, address FROM store WHERE name LIKE '%石头先生的烤炉%' OR brand_canon='石头先生的烤炉'"
    ).fetchall()
    put_formula(
        con, "F12", "兄弟店烤炉",
        "store WHERE name/brand 石头先生的烤炉",
        "店",
        len(sister),
        len(sister),
        "store",
        "同一老板，合生汇 B2",
        [(r[0], r[4] or 0, r[3], r[2], r[5]) for r in sister],
    )

    sku_n = int(con.execute("SELECT COUNT(*) FROM sku").fetchone()[0])
    sku_rows = con.execute("SELECT category, COUNT(*), AVG(price), AVG(gross_margin) FROM sku GROUP BY category").fetchall()
    put_formula(
        con, "F13", "客户 SKU 结构",
        "COUNT(sku); AVG(price); AVG(gross_margin) GROUP BY category",
        "SKU",
        sku_n,
        sku_n,
        "sku",
        "来自 sku-catalog/skus.csv，不是点评库",
        [(r[0], float(r[1]), r[2], r[3], "") for r in sku_rows],
    )

    pairs = [(r[3], r[2]) for r in mall if r[3] and r[2] and r[3] > 0]
    corr = None
    if len(pairs) >= 3:
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in pairs)
        den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
        corr = num / den if den else None
    put_formula(con, "F14", "场内客单×评分相关", "CORR(avg_spend, rating) on mall_dining", "r", corr, len(pairs), "store", "06 §3.1 声称 0.513")

    wesley = int(con.execute(
        "SELECT COUNT(*) FROM store WHERE scope='city_beijing' AND (name LIKE '%魏斯理%' OR name LIKE '%Wesley%' OR brand_canon='魏斯理')"
    ).fetchone()[0])
    put_formula(con, "F15", "魏斯理在北京库", "COUNT(city_beijing WHERE 魏斯理|Wesley)", "家", wesley, wesley, "store", "08 §5.1 声称 0；不足则走 web_source")

    spend_n = int(con.execute("SELECT COUNT(*) FROM store WHERE scope='city_beijing' AND avg_spend IS NOT NULL AND avg_spend>0").fetchone()[0])
    rate_n = int(con.execute("SELECT COUNT(*) FROM store WHERE scope='city_beijing' AND rating IS NOT NULL AND rating>0").fetchone()[0])
    put_formula(con, "F16", "有人均 / 有评分", "COUNT(avg_spend>0); COUNT(rating>0)", "家", f"{spend_n}/{rate_n}", spend_n, "store", "08 声称 5145 / 5173")


ZW = re.compile(r"[\u2060\u200b\u200c\u200d\ufeff]")


def clean_text(raw: str) -> str:
    return ZW.sub("", re.sub(r"<[^>]+>", "", raw or "")).strip()


def parse_slides(html_path: Path) -> list[dict[str, Any]]:
    text = html_path.read_text(encoding="utf-8")
    slides = []
    for i, block in enumerate(re.finditer(r"<section class=\"slide[^>]*>.*?</section>", text, re.S), start=1):
        chunk = block.group(0)
        job = re.search(r'data-job="([^"]+)"', chunk)
        fill = re.search(r'data-fill="([^"]+)"', chunk)
        title = re.search(r'class="sd-h2">(.*?)</div>', chunk, re.S)
        if not title:
            title = re.search(r'class="h-zh h1"[^>]*>(.*?)</div>', chunk, re.S)
        if not title:
            title = re.search(r"<h1[^>]*>(.*?)</h1>", chunk, re.S)
        chip = re.search(r'class="sd-chip">(.*?)</div>', chunk)
        quote = re.search(r'class="sd-quote">(.*?)</div>', chunk, re.S)
        lede = re.search(r'class="sd-lede">(.*?)</div>', chunk, re.S)
        slides.append({
            "page": i,
            "job": job.group(1) if job else "",
            "fill": fill.group(1) if fill else "",
            "title": clean_text(title.group(1) if title else ""),
            "chip": clean_text(chip.group(1) if chip else ""),
            "quote": clean_text(quote.group(1) if quote else ""),
            "lede": clean_text(lede.group(1) if lede else ""),
        })
    return slides


def pick_formula(slide: dict[str, Any]) -> str | None:
    title = slide["title"]
    chip = slide["chip"]
    t = f"{title} {chip}"
    body = " ".join([title, chip, slide.get("quote", ""), slide.get("lede", "")])
    if "魏斯理" in body or "Wesley" in body:
        return "F15"
    if "烤炉" in t:
        return "F12"
    if "门店数 ≥ 20" in t or "≥ 20 家" in t or "大于 20" in t:
        return "F07"
    if ("价格带" in t or "价格带" in title) and ("规模" in t or "天花板" in t):
        return "F08"
    if "275" in t or "商场全景" in t:
        return "F04"
    if "九家" in t or "9 家" in t or "场内西式九家" in t:
        return "F11"
    if "场内西式" in t:
        return "F05"
    if "合生汇" in t and ("相关" in t or "相关系数" in t):
        return "F14"
    if "汉堡" in t and any(k in t for k in ("店名", "2,060", "2060", "782", "关键词", "汉堡品类", "汉堡相关")):
        return "F09"
    if any(k in t for k in ("5km", "环带", "0–500", "0-500", "500m", "1km", "1–3km", "1-3km", "分环")):
        return "F03"
    if "朝阳" in t and "西式" in t:
        return "F02"
    if any(k in title for k in ("SKU", "产品结构", "档口", "毛利")):
        return "F13"
    if "5,145" in t or "5145" in t or "有人均" in t or "有评分" in t:
        return "F16"
    if "6,052" in t or "6052" in t or "参考集" in t:
        return "F01"
    if "全市西式" in t or "西式赛道" in t:
        return "F01"
    if "品牌" in t and any(k in t for k in ("规模", "总榜", "归一")):
        return "F06"
    if slide["job"] in {"chart", "chart-table"}:
        if "全市" in t:
            return "F01"
        if "合生汇" in t:
            return "F04"
        return "F06"
    if slide["job"] == "roster" and "清单" in t:
        if "≥ 20" in t or "≥20" in t:
            return "F07"
        if "275" in t:
            return "F04"
        if "价格带" in t and ("规模" in t or "天花板" in t):
            return "F08"
        if "汉堡" in t and any(k in t for k in ("相关", "2,060", "汉堡品类")):
            return "F09"
        if any(k in t for k in ("环带", "500m", "1km", "分环")):
            return "F03"
        if any(k in title for k in ("SKU", "档口")):
            return "F13"
        if "全市" in t:
            return "F01"
        return "F06"
    if slide["job"] in {"kpi", "matrix"}:
        return "F01"
    return None


def link_pages(con: sqlite3.Connection) -> None:
    decks = [
        ("D03.1", ROOT / "decks/stone-briefing/presentation.html", "/decks/stone-briefing/presentation.html"),
        ("D03.2", ROOT / "decks/stone-briefing/html-v1.html", "/decks/stone-briefing/html-v1.html"),
        ("D04", ROOT / "decks/stone-roadmap/presentation.html", "/decks/stone-roadmap/presentation.html"),
        ("D05", ROOT / "decks/stone-dossier/presentation.html", "/decks/stone-dossier/presentation.html"),
    ]
    for deck_id, path, href in decks:
        assert path.is_file(), path
        slides = parse_slides(path)
        assert slides, path
        for slide in slides:
            fid = pick_formula(slide)
            data_ok = 0
            if fid:
                val = con.execute("SELECT n FROM formula WHERE id=?", (fid,)).fetchone()
                data_ok = 1 if val and val[0] is not None else 0
            con.execute(
                "INSERT INTO page_link VALUES (?,?,?,?,?,?,?,?)",
                (
                    deck_id,
                    slide["page"],
                    slide["job"],
                    slide["title"],
                    slide["fill"],
                    fid,
                    f"{href}#p={slide['page']}",
                    data_ok,
                ),
            )


def fetch_web_gaps(con: sqlite3.Connection) -> None:
    wesley_n = int(con.execute("SELECT value FROM formula WHERE id='F15'").fetchone()[0])
    if wesley_n > 0:
        return
    for gap in WEB_GAPS:
        for url in gap["urls"]:
            status = 0
            excerpt = ""
            try:
                safe = quote(url, safe=":/?#[]@!$&'()*+,;=%")
                req = Request(safe, headers={"User-Agent": "baslide01-stone-pack/1.0"})
                with urlopen(req, timeout=12) as res:
                    status = res.status
                    raw = res.read(8000).decode("utf-8", errors="replace")
                    excerpt = re.sub(r"<[^>]+>", " ", raw)
                    excerpt = re.sub(r"\s+", " ", excerpt).strip()[:400]
            except (URLError, HTTPError, TimeoutError, OSError, UnicodeEncodeError) as exc:
                excerpt = f"fetch_failed: {exc}"
            con.execute(
                "INSERT OR REPLACE INTO web_source VALUES (?,?,?,?,?,?)",
                (gap["id"], gap["query"], url, status, excerpt, gap["why"]),
            )


def write_json(con: sqlite3.Connection) -> None:
    formulas = []
    for row in con.execute("SELECT * FROM formula ORDER BY id"):
        fid, name, expr, unit, value, n, source_table, note = row
        rows = [
            {"label": r[0], "n": r[1], "spend": r[2], "rating": r[3], "extra": r[4]}
            for r in con.execute(
                "SELECT label, n, spend, rating, extra FROM formula_row WHERE formula_id=? ORDER BY ord",
                (fid,),
            )
        ]
        formulas.append({
            "id": fid, "name": name, "expr": expr, "unit": unit,
            "value": value, "n": n, "source_table": source_table, "note": note, "rows": rows,
        })
    (DATA_DIR / "formulas.json").write_text(json.dumps(formulas, ensure_ascii=False, indent=2), encoding="utf-8")
    index = [
        {key: item[key] for key in ("id", "name", "expr", "unit", "value", "n", "source_table", "note")}
        for item in formulas
    ]
    (DATA_DIR / "formulas-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    links = []
    for row in con.execute("SELECT deck_id, page, job, title, fill, formula_id, href, data_ok FROM page_link ORDER BY deck_id, page"):
        links.append({
            "deck_id": row[0], "page": row[1], "job": row[2], "title": row[3],
            "fill": row[4], "formula_id": row[5], "href": row[6], "data_ok": bool(row[7]),
        })
    (DATA_DIR / "page-links.json").write_text(json.dumps(links, ensure_ascii=False, indent=2), encoding="utf-8")

    web = [
        {"id": r[0], "query": r[1], "url": r[2], "status": r[3], "excerpt": r[4], "why": r[5]}
        for r in con.execute("SELECT * FROM web_source")
    ]
    meta = {
        "pack": str(PACK),
        "sku": str(SKU_DIR),
        "db": str(DB_PATH.relative_to(ROOT)),
        "generated_for": ["D03", "D04", "D05"],
        "web_sources": web,
    }
    for key, val in con.execute("SELECT key, value FROM pack_meta"):
        meta[key] = val
    (DATA_DIR / "import-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_provenance() -> None:
    dest = DATA_DIR / "provenance"
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("manifest.json", "anchor.json", "taxonomy-rules.json"):
        src = PACK / name
        (dest / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    assert PACK.is_dir(), PACK
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    copy_provenance()
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    create_schema(con)
    manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    con.execute("INSERT INTO pack_meta VALUES (?,?)", ("pack_id", manifest["pack_id"]))
    con.execute("INSERT INTO pack_meta VALUES (?,?)", ("generated_at", manifest["generated_at"]))
    con.execute("INSERT INTO pack_meta VALUES (?,?)", ("source_file", manifest["dataset"]["source_file"]))
    con.execute("INSERT INTO pack_meta VALUES (?,?)", ("source_sha256", manifest["dataset"]["source_sha256"]))
    insert_rules(con)
    insert_stores(con)
    insert_skus(con)
    compute_formulas(con)
    link_pages(con)
    fetch_web_gaps(con)
    write_json(con)
    con.commit()

    city = int(con.execute("SELECT value FROM formula WHERE id='F01'").fetchone()[0])
    chaoyang = int(con.execute("SELECT value FROM formula WHERE id='F02'").fetchone()[0])
    inside = int(con.execute("SELECT value FROM formula WHERE id='F05'").fetchone()[0])
    hualaishi = con.execute("SELECT n FROM formula_row WHERE formula_id='F06' AND label='华莱士'").fetchone()
    subway = con.execute("SELECT n FROM formula_row WHERE formula_id='F06' AND label='赛百味 SUBWAY'").fetchone()
    wagas = con.execute("SELECT n FROM formula_row WHERE formula_id='F06' AND label='Wagas 沃歌斯'").fetchone()
    ge20 = int(con.execute("SELECT n FROM formula WHERE id='F07'").fetchone()[0])
    linked = int(con.execute("SELECT COUNT(*) FROM page_link WHERE formula_id IS NOT NULL").fetchone()[0])
    pages = int(con.execute("SELECT COUNT(*) FROM page_link").fetchone()[0])
    assert city == 6052, city
    assert chaoyang == 1698, chaoyang
    assert inside == 9, inside
    assert hualaishi and hualaishi[0] == 210, hualaishi
    assert subway and subway[0] == 190, subway
    assert wagas and wagas[0] == 53, wagas
    assert ge20 >= 24, ge20
    assert linked >= 80, linked
    f04_pages = int(con.execute("SELECT COUNT(*) FROM page_link WHERE formula_id='F04'").fetchone()[0])
    assert f04_pages >= 2, f04_pages
    f275 = con.execute(
        "SELECT formula_id FROM page_link WHERE deck_id='D03.1' AND title LIKE '%275%' AND job='chart' LIMIT 1"
    ).fetchone()
    assert f275 and f275[0] == "F04", f275
    f15_pages = int(con.execute("SELECT COUNT(*) FROM page_link WHERE formula_id='F15'").fetchone()[0])
    assert f15_pages >= 3, f15_pages
    official = con.execute("SELECT status FROM web_source WHERE url LIKE '%weijia1999%'").fetchone()
    assert official and official[0] == 200, official
    con.close()
    print(json.dumps({
        "db": str(DB_PATH.relative_to(ROOT)),
        "city": city,
        "ge20": ge20,
        "pages": pages,
        "linked": linked,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
