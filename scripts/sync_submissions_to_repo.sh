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
        raise SystemExit(f"missing source for {row['id']}: {src}")
    shutil.copy2(src, out)
    data = json.loads(out.read_text())
    if len(data) != 2000:
        raise SystemExit(f"{out.name}: expected 2000 rows, got {len(data)}")
    print(f"copied {row['id']} -> {out.name} ({len(data)} rows)")

print(f"\nSynced {len(manifest['submissions'])} files to {dest}")
PY
