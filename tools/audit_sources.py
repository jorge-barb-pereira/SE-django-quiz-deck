"""Audit public source hashes and forbidden publication artifacts."""

from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
items = json.loads((root / "archive/manifest.json").read_text(encoding="utf-8"))
for item in items:
    data = (root / item["published"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item["published_sha256"], item[
        "published"
    ]
for area in ["archive", "game", "quizgame", "docs", "tools", ".github"]:
    for path in (root / area).rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        assert path.suffix not in {".sqlite3", ".zip", ".docx", ".pptx"}, str(path)
        assert path.name != ".env", str(path)
        if path.suffix in {".py", ".html", ".md", ".json", ".yml"}:
            text = path.read_text(encoding="utf-8")
            assert not re.search(
                r"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}|[A-Za-z]:[\\/]+Users[\\/]", text
            ), str(path)
print(f"PASS: {len(items)} historical source hashes and publication checks")
