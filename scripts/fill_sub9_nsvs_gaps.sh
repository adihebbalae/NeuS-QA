#!/usr/bin/env bash
# Fill missing NSVS rows for Sub9 after an interrupted or partial shard run.
# Merges gap results into each shard's entries.json (does not rerun full shards).
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
cd "$REPO"
source .venv/bin/activate

BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_test}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
TOTAL=${TOTAL:-8}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
PROP_MODEL=${PROP_MODEL:-InternVL2-8B}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}

PLAN="${BASE}/nsvs_gap_plan.json"
python3 scripts/sub9_shard_utils.py \
  --base "$BASE" \
  --ann "$ANN" \
  --video-root "$VIDEO_ROOT" \
  --total "$TOTAL" \
  --write-gap-plan "$PLAN" \
  --print-missing

if python3 scripts/sub9_shard_utils.py --base "$BASE" --ann "$ANN" --video-root "$VIDEO_ROOT" --total "$TOTAL" --check; then
  echo "[sub9-gap] all ${TOTAL} shards covered; nothing to fill"
  exit 0
fi

echo "[sub9-gap] filling missing NSVS rows at $(date -Iseconds)"

for i in $(seq 1 "$TOTAL"); do
  qids_json="${BASE}/shard_${i}/_gapfill_qids.json"
  python3 - <<PY
import json
plan = json.load(open("${PLAN}"))
qids = plan["by_shard"].get(str(${i}), [])
json.dump(qids, open("${qids_json}", "w"))
print(f"[sub9-gap] shard ${i}: {len(qids)} missing qids")
PY
  n=$(python3 -c "import json; print(len(json.load(open('${qids_json}'))))")
  if [[ "$n" -eq 0 ]]; then
    continue
  fi

  gpu=$((i + 1))
  gapdir="${BASE}/shard_${i}/_gapfill"
  rm -rf "$gapdir"
  mkdir -p "$gapdir"

  echo "[sub9-gap] shard ${i}: GPU ${gpu} -> ${gapdir}"
  CUDA_VISIBLE_DEVICES=$gpu python3 -u scripts/run_timelogic.py \
    --video-root "$VIDEO_ROOT" \
    --ann-path "$ANN" \
    --output-dir "$gapdir" \
    --qid-file "$qids_json" \
    --device 0 \
    --proposition-model "$PROP_MODEL" \
    --puls-model "$PULS_MODEL" \
    --sample-rate "$SAMPLE_RATE" \
    --env-file "$HOME/.env" \
    2>&1 | tee -a "${BASE}/shard_${i}/gapfill.log"

  python3 scripts/merge_nsvs_shards.py \
    --shard-dirs "$gapdir" \
    --into-entries "${BASE}/shard_${i}/entries.json" \
    --out-dir "${BASE}/shard_${i}"

  rm -rf "$gapdir" "${qids_json}"
done

if ! python3 scripts/sub9_shard_utils.py --base "$BASE" --ann "$ANN" --video-root "$VIDEO_ROOT" --total "$TOTAL" --check; then
  echo "[sub9-gap] FATAL: still missing qids after gap fill" >&2
  python3 scripts/sub9_shard_utils.py --base "$BASE" --ann "$ANN" --video-root "$VIDEO_ROOT" --total "$TOTAL" --print-missing
  exit 1
fi

echo "[sub9-gap] done $(date -Iseconds)"
