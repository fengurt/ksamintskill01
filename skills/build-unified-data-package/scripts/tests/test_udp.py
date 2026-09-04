from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl
import pyarrow as pa
import pyarrow.parquet as pq
import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "udp.py"


class UnifiedDataPackageCLITest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "orders.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Orders"
        sheet.append(["Order ID", "Line ID", "Net Amount", "Note", "Event Time"])
        sheet.append(["000123", "01", 10.5, "正常", "2026-08-30T09:00:00+08:00"])
        sheet.append(["000124", "01", None, "=2+2", "2026-08-30T10:00:00+08:00"])
        workbook.save(self.source)
        self.asset = self.root / "evidence.bin"
        self.asset.write_bytes(b"evidence\x00payload")
        self.config = self.root / "build.yml"
        self.config.write_text(
            yaml.safe_dump(
                {
                    "package": {
                        "name": "test_orders_normalize_v1",
                        "version": "1.0.0",
                        "spec_version": "unified-data-package/v1",
                        "timezone": "Asia/Shanghai",
                        "purpose": "Test exact, traceable order packaging.",
                        "profiles": ["tabular/v1"],
                        "classification": "internal",
                        "license": None,
                        "conclusions": [],
                        "assumptions": [],
                        "limitations": [],
                    },
                    "sources": [
                        {
                            "source_id": "source_001",
                            "path": "./orders.xlsx",
                            "tables": [
                                {
                                    "selector": "Orders",
                                    "name": "sales_orders_order_line",
                                    "title_zh": "销售订单明细",
                                    "description": "Test order lines.",
                                    "grain": "一行=一个订单明细行",
                                    "header_row": 1,
                                    "source_row_number_start": 2,
                                    "primary_key": ["row_uid"],
                                    "business_keys": ["order_id", "line_id"],
                                    "foreign_keys": [],
                                    "csv_mode": "full",
                                    "source_null_tokens": [""],
                                    "columns": [
                                        {
                                            "source": "Order ID",
                                            "name": "order_id",
                                            "title_zh": "订单编号",
                                            "description": "Leading-zero order identifier.",
                                            "physical_type": "string",
                                            "logical_type": "identifier",
                                            "semantic_role": "identifier",
                                            "unit": None,
                                            "nullable": False,
                                            "null_means": None,
                                            "sensitivity": "internal",
                                            "derived": False,
                                        },
                                        {
                                            "source": "Line ID",
                                            "name": "line_id",
                                            "title_zh": "行号",
                                            "description": "Line identifier.",
                                            "physical_type": "string",
                                            "logical_type": "identifier",
                                            "semantic_role": "identifier",
                                            "unit": None,
                                            "nullable": False,
                                            "null_means": None,
                                            "sensitivity": "internal",
                                            "derived": False,
                                        },
                                        {
                                            "source": "Net Amount",
                                            "name": "net_amount_cny",
                                            "title_zh": "净额",
                                            "description": "Exact amount.",
                                            "physical_type": "decimal(18,2)",
                                            "logical_type": "monetary_amount",
                                            "semantic_role": "measure",
                                            "unit": "CNY",
                                            "nullable": True,
                                            "null_means": "Source cell was blank.",
                                            "sensitivity": "internal",
                                            "derived": False,
                                        },
                                        {
                                            "source": "Note",
                                            "name": "note_text",
                                            "title_zh": "备注",
                                            "description": "Source note.",
                                            "physical_type": "string",
                                            "logical_type": "text",
                                            "semantic_role": "text",
                                            "unit": None,
                                            "nullable": True,
                                            "null_means": "Source did not provide a note.",
                                            "sensitivity": "internal",
                                            "derived": False,
                                        },
                                        {
                                            "source": "Event Time",
                                            "name": "event_at",
                                            "title_zh": "发生时间",
                                            "description": "Order event timestamp.",
                                            "physical_type": "timestamp[ms,tz=Asia/Shanghai]",
                                            "logical_type": "event_time",
                                            "semantic_role": "timestamp",
                                            "unit": None,
                                            "nullable": False,
                                            "null_means": None,
                                            "sensitivity": "internal",
                                            "derived": False,
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                    "assets": [{"source_id": "asset_001", "path": "./evidence.bin", "title": "Evidence"}],
                    "asset_table": {
                        "name": "test_assets_asset",
                        "title_zh": "资产索引",
                        "grain": "一行=一个二进制资产",
                    },
                },
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != expected:
            self.fail(f"exit={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
        return result

    def test_end_to_end_build_validate_archive_and_tamper_detection(self) -> None:
        inspection = self.run_cli("inspect", str(self.source))
        inspection_json = json.loads(inspection.stdout)
        self.assertEqual(inspection_json["files"][0]["tables"][0]["rows"], 2)

        output_parent = self.root / "out"
        self.run_cli("build", "--config", str(self.config), "--output", str(output_parent))
        package = output_parent / "test_orders_normalize_v1"
        validation = self.run_cli("validate", str(package), "--json")
        self.assertEqual(json.loads(validation.stdout)["status"], "pass")

        rebuild_parent = self.root / "rebuilt"
        self.run_cli(
            "build",
            "--config",
            str(package / "src" / "build.yml"),
            "--output",
            str(rebuild_parent),
        )
        rebuilt_manifest = json.loads(
            (rebuild_parent / "test_orders_normalize_v1" / "manifest.json").read_text(encoding="utf-8")
        )
        original_manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [table["content_sha256"] for table in rebuilt_manifest["tables"]],
            [table["content_sha256"] for table in original_manifest["tables"]],
        )

        orders = pq.read_table(package / "data" / "sales_orders_order_line.parquet")
        self.assertEqual(orders.column("order_id").to_pylist(), ["000123", "000124"])
        self.assertEqual(orders.schema.field("net_amount_cny").type, pa.decimal128(18, 2))
        self.assertEqual(str(orders.column("net_amount_cny")[0].as_py()), "10.50")
        csv_text = (package / "data" / "sales_orders_order_line.csv").read_text(encoding="utf-8-sig")
        self.assertIn("'=2+2", csv_text)

        archive_a = self.root / "package-a.zip"
        archive_b = self.root / "package-b.zip"
        self.run_cli("archive", str(package), "--output", str(archive_a))
        self.run_cli("archive", str(package), "--output", str(archive_b))
        self.assertEqual(hashlib.sha256(archive_a.read_bytes()).hexdigest(), hashlib.sha256(archive_b.read_bytes()).hexdigest())

        original_manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        failed_manifest = dict(original_manifest)
        failed_manifest["validation"] = {"status": "fail", "errors_cnt": 1, "warnings_cnt": 0}
        (package / "manifest.json").write_text(json.dumps(failed_manifest), encoding="utf-8")
        self.run_cli("archive", str(package), "--output", str(self.root / "failed.zip"), expected=2)
        (package / "manifest.json").write_text(json.dumps(original_manifest), encoding="utf-8")

        unlisted = package / "unlisted.txt"
        unlisted.write_text("not in manifest", encoding="utf-8")
        failed = self.run_cli("validate", str(package), "--json", expected=1)
        self.assertIn("Unlisted artifact: unlisted.txt", json.loads(failed.stdout)["errors"])
        self.run_cli("archive", str(package), "--output", str(self.root / "unlisted.zip"), expected=2)
        unlisted.unlink()

        nested_manifest = package / "data" / "manifest.json"
        nested_manifest.write_text("{}", encoding="utf-8")
        failed = self.run_cli("validate", str(package), "--json", expected=1)
        self.assertIn("Unlisted artifact: data/manifest.json", json.loads(failed.stdout)["errors"])
        nested_manifest.unlink()

        readme = package / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
        failed = self.run_cli("validate", str(package), "--json", expected=1)
        errors = json.loads(failed.stdout)["errors"]
        self.assertTrue(any("checksum mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
