#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("normalize-source.py")
spec = importlib.util.spec_from_file_location("normalize_source", SCRIPT)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bundle = root / "bundle.zip"
        with zipfile.ZipFile(bundle, "w") as z:
            z.writestr("10_last.md", "# Last")
            z.writestr("02_first.md", "# First")
            z.writestr("tables/a.csv", "name,value\na,1\n")
        out = root / "work"
        manifest = mod.normalize(bundle, out)
        assert manifest["markdown"] == ["02_first.md", "10_last.md"]
        assert manifest["as_of"]
        assert len(manifest["files"]) == 3
        assert all(len(item["sha256"]) == 64 for item in manifest["files"])
        text = (out / "source.md").read_text(encoding="utf-8")
        assert text.index("# First") < text.index("# Last")
        assert (out / "assets/tables/tables/a.csv").is_file()
        (out / "original/stale.md").write_text("stale", encoding="utf-8")
        mod.normalize(bundle, out)
        assert not (out / "original/stale.md").exists()

        bad = root / "bad.zip"
        with zipfile.ZipFile(bad, "w") as z:
            z.writestr("../escape.md", "bad")
        try:
            mod.normalize(bad, root / "bad-work")
            raise AssertionError("zip traversal accepted")
        except ValueError as exc:
            assert "unsafe archive entry" in str(exc)

        directory = root / "directory"
        directory.mkdir()
        (directory / "1.md").write_text("one", encoding="utf-8")
        (directory / "2.md").write_text("two", encoding="utf-8")
        old_max = mod.MAX_FILES
        mod.MAX_FILES = 1
        try:
            mod.normalize(directory, root / "bounded-work")
            raise AssertionError("directory file bound ignored")
        except ValueError as exc:
            assert "too large" in str(exc)
        finally:
            mod.MAX_FILES = old_max


if __name__ == "__main__":
    main()
    print("test_normalize_source.py ok")
