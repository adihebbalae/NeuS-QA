#!/usr/bin/env bash
# Copy EvalAI submission JSONs from run outputs into repo submissions/ using MANIFEST.json.
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
DEST="${REPO}/submissions"
MANIFEST="${DEST}/MANIFEST.json"

python3 << 'PY'
import json
import shutil
from pathlib import Path

repo = Path("/home/ah66742/NeuS-QA")
dest = repo / "submissions"
manifest = json.loads((dest / "MANIFEST.json").read_text())

for row in manifest["submissions"]:
    src = Path(row["source"])
    out = dest / row["file"]
    if not src.exists():
        print(f"skip {row['id']}: missing source {src}")
        continue
    shutil.copy2(src, out)
    data = json.loads(out.read_text())
    expected = 3000 if row.get("phase") == "test" else 2000
    if len(data) != expected:
        raise SystemExit(f"{out.name}: expected {expected} rows, got {len(data)}")
    print(f"copied {row['id']} -> {out.name} ({len(data)} rows)")

print(f"\nSynced manifest entries with existing sources to {dest}")
PY
