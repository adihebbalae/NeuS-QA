#!/usr/bin/env bash
# Re-run Sub #7 NSVS for rows that failed with CUDA or KeyError in shard diags.
#
# Reads shard_*/diag.json under sub7 output, writes rerun_qids.json, re-runs
# run_timelogic.py on 2 GPU shards, then merges into merged/entries.json.
#
# Usage:
#   bash scripts/run_sub7_rerun_failed_nsvs.sh
#   nohup bash scripts/run_sub7_rerun_failed_nsvs.sh > .../nsvs_rerun/run.log 2>&1 &
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful}
NUM_SHARDS=${NUM_SHARDS:-2}
RERUN_ROOT="${BASE}/nsvs_rerun"
QID_FILE="${BASE}/rerun_qids.json"
MERGED="${BASE}/merged/entries.json"

cd "$REPO"
source .venv/bin/activate

export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True,max_split_size_mb:512}

if [[ ! -f "${BASE}/config.json" ]]; then
  echo "FATAL: missing ${BASE}/config.json" >&2
  exit 1
fi

read -r VIDEO_ROOT ANN SAMPLE_RATE PULS_MODEL PROP_MODEL <<<"$(python3 - <<'PY' "$BASE/config.json"
import json
import sys

cfg = json.load(open(sys.argv[1]))
prop = cfg.get("proposition_model", "OpenGVLab/InternVL2-8B")
if prop.startswith("OpenGVLab/"):
    prop = prop[len("OpenGVLab/") :]
print(
    cfg["video_root"],
    cfg["ann_path"],
    cfg.get("sample_rate", 3.0),
    cfg.get("puls_model", "gpt-4o"),
    prop,
)
PY
)"

echo "[sub7-rerun] BASE=$BASE"
echo "[sub7-rerun] extracting failed NSVS qids from shard_*/diag.json"

python3 - <<'PY' "$BASE" "$QID_FILE"
import json
import sys
from pathlib import Path

base = Path(sys.argv[1])
out = Path(sys.argv[2])

cuda_markers = (
    "cudacachingallocator",
    "internal assert",
    "cuda launch failure",
    "cuda driver error: unknown",
)

def nsvs_failed(row: dict) -> bool:
    nsvs = str(row.get("step_status", {}).get("nsvs", ""))
    tb = row.get("traceback") or ""
    blob = f"{nsvs}\n{tb}".lower()
    if "keyerror" in blob:
        return True
    return any(m in blob for m in cuda_markers)

failed: set[str] = set()
for diag_path in sorted(base.glob("shard_*/diag.json")):
    for row in json.loads(diag_path.read_text(encoding="utf-8")):
        if nsvs_failed(row):
            failed.add(str(row["question_id"]))

qids = sorted(failed, key=int)
out.write_text(json.dumps(qids, indent=2) + "\n", encoding="utf-8")
print(f"[sub7-rerun] failed_qids={len(qids)} -> {out}")
PY

FAILED_N=$(python3 -c "import json; print(len(json.load(open('$QID_FILE'))))")
if [[ "$FAILED_N" -eq 0 ]]; then
  echo "[sub7-rerun] no failed NSVS qids; nothing to do"
  exit 0
fi

mkdir -p "$RERUN_ROOT"
echo "[sub7-rerun] re-running NSVS for $FAILED_N qids on $NUM_SHARDS shards at $(date -Iseconds)"

pids=()
for i in $(seq 1 "$NUM_SHARDS"); do
  gpu=$((i - 1))
  out="${RERUN_ROOT}/shard_${i}"
  mkdir -p "$out"
  echo "[sub7-rerun] shard ${i}/${NUM_SHARDS} on GPU ${gpu} -> ${out}"
  CUDA_VISIBLE_DEVICES=$gpu python3 -u scripts/run_timelogic.py \
    --video-root "$VIDEO_ROOT" \
    --ann-path "$ANN" \
    --output-dir "$out" \
    --qid-file "$QID_FILE" \
    --qid-total-shards "$NUM_SHARDS" \
    --qid-current-shard "$i" \
    --device 0 \
    --proposition-model "$PROP_MODEL" \
    --puls-model "$PULS_MODEL" \
    --sample-rate "$SAMPLE_RATE" \
    --env-file "$HOME/.env" \
    > "${out}/run.log" 2>&1 &
  pids+=("$!")
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

echo "[sub7-rerun] all rerun shards exited at $(date -Iseconds)"

shard_dirs=$(python3 - <<PY
import os
base = "${RERUN_ROOT}"
n = int("${NUM_SHARDS}")
dirs = [f"{base}/shard_{i}" for i in range(1, n + 1)]
missing = [d for d in dirs if not os.path.isfile(os.path.join(d, "entries.json"))]
if missing:
    raise SystemExit(f"missing entries.json in: {missing}")
print(",".join(dirs))
PY
)

if [[ ! -f "$MERGED" ]]; then
  echo "FATAL: missing base merge file $MERGED" >&2
  exit 1
fi

python3 scripts/merge_nsvs_shards.py \
  --shard-dirs "$shard_dirs" \
  --into-entries "$MERGED" \
  --out-dir "${BASE}/merged"

echo "[sub7-rerun] merged rerun rows into ${BASE}/merged/entries.json"
echo "[sub7-rerun] done $(date -Iseconds)"
