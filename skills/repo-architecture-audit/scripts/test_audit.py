#!/usr/bin/env python3
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class AuditRegressionTest(unittest.TestCase):
    def test_excludes_secret_directories_and_escapes_project_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = Path(tmp) / "audit"
            (root / "src" / "secrets").mkdir(parents=True)
            (root / "src" / "credentials").mkdir(parents=True)
            (root / "app.py").write_text(
                'from flask import Flask\napp = Flask(__name__)\n@app.post("/orders")\ndef create_order(): pass\n',
                encoding="utf-8",
            )
            (root / "src" / "secrets" / "config.py").write_text(
                '@app.post("/leak")\ndef leak(): pass\n', encoding="utf-8"
            )
            (root / "src" / "credentials" / "config.py").write_text(
                '@app.post("/credentials-leak")\ndef credentials_leak(): pass\n', encoding="utf-8"
            )
            project = '</title><script>alert("x")</script>'
            subprocess.run(
                [sys.executable, str(HERE / "audit.py"), str(root), "--out", str(out), "--project-name", project],
                check=True,
                capture_output=True,
                text=True,
            )

            with (out / "routes.csv").open(encoding="utf-8", newline="") as handle:
                routes = list(csv.DictReader(handle))
            self.assertEqual([row["path"] for row in routes], ["/orders"])
            with (out / "priorities.csv").open(encoding="utf-8", newline="") as handle:
                priorities = list(csv.DictReader(handle))
            self.assertTrue(any(row["rule_id"] == "P0-1" for row in priorities))

            report = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn(
                '&lt;/title&gt;&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;</title>', report
            )
            self.assertNotIn(f"<title>Architecture Audit — {project}</title>", report)


if __name__ == "__main__":
    unittest.main()
