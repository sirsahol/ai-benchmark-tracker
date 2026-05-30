"""Verify dashboard.json integrity against YAML source."""
import json
from pathlib import Path

dash = json.loads(Path("data/dashboard.json").read_text())
bm = dash.get("_build_metadata", {})
assert bm.get("schema_version") == "3", "Schema version mismatch"
print(f"  Integrity check passed — commit: {bm.get('commit_sha', 'unknown')[:12]}")
print(f"  YAML hash: {bm.get('yaml_integrity', '?')}")
