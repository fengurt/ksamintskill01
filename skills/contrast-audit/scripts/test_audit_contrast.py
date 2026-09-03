#!/usr/bin/env python3
"""Smoke test for the rendered contrast gate."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        html = root / "sample.html"
        report = root / "report.json"
        html.write_text(
            '<main style="background:#000"><span style="color:#000;font-size:20px">Unreadable</span>'
            '<span style="color:#fff;font-size:20px">Readable</span>'
            '<span style="color:#fff;font-size:20px;opacity:.2">Translucent</span></main>',
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("audit_contrast.py")), str(html), "--json-out", str(report)],
            capture_output=True,
            text=True,
        )
        payload = json.loads(report.read_text(encoding="utf-8"))
        assert result.returncode == 1, result.stderr
        assert payload["summary"]["failures"] == 1, payload["summary"]
        assert payload["summary"]["manual_review"] == 1, payload["summary"]
        assert payload["files"][0]["failures"][0]["text"] == "Unreadable"
        assert payload["files"][0]["manual_review"][0]["reason"] == "element-or-ancestor-opacity"

        html.write_text(
            '<main style="background:#000"><span style="color:#fff;opacity:.2">Review me</span></main>',
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("audit_contrast.py")), str(html), "--json-out", str(report)],
            capture_output=True,
            text=True,
        )
        payload = json.loads(report.read_text(encoding="utf-8"))
        assert result.returncode == 1, result.stderr
        assert payload["summary"]["failures"] == 0, payload["summary"]
        assert payload["files"][0]["status"] == "review"


if __name__ == "__main__":
    main()
