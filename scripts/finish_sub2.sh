#!/usr/bin/env bash
# After all NSVS shards finish: merge -> answer (gpt-5.2) -> full submission.
set -euo pipefail

REPO=/home/ah66742/NeuS-QA
BASE=/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2
MERGED="${BASE}/merged"
ANSWER_OUT="${BASE}/answers_gpt52"
ANN=/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json
FINAL="${BASE}/submission_sub2.json"

cd "$REPO"
source .venv/bin/activate

python3 scripts/merge_nsvs_shards.py \
  --shard-dirs "${BASE}/shard_1,${BASE}/shard_2,${BASE}/shard_3,${BASE}/shard_4,${BASE}/shard_5,${BASE}/shard_6,${BASE}/shard_7,${BASE}/shard_8" \
  --out-dir "$MERGED"

python3 -u scripts/answer_entries.py \
  --entries "${MERGED}/entries.json" \
  --output-dir "$ANSWER_OUT" \
  --model gpt-5.2 \
  --num-frames 8 \
  --env-file "$HOME/.env"

python3 scripts/build_submission.py \
  --val-annotations "$ANN" \
  --partial "${ANSWER_OUT}/submission.json" \
  --output "$FINAL"

echo "[finish_sub2] wrote $FINAL"
