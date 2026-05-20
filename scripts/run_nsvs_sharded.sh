#!/usr/bin/env bash
# Launch 8 parallel NSVS shards for full val. Run from tmux; do not poll.
set -euo pipefail

REPO=/home/ah66742/NeuS-QA
VIDEO_ROOT=/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos
ANN=/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json
BASE_OUT=/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2
PULS_MODEL=gpt-5.2
PROP_MODEL=InternVL2-8B
TOTAL=8

cd "$REPO"
source .venv/bin/activate
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

for i in $(seq 1 "$TOTAL"); do
  gpu=$((i - 1))
  out="${BASE_OUT}/shard_${i}"
  mkdir -p "$out"
  echo "[launcher] shard $i/$TOTAL on GPU $gpu -> $out"
  CUDA_VISIBLE_DEVICES=$gpu nohup python3 -u scripts/run_timelogic.py \
    --video-root "$VIDEO_ROOT" \
    --ann-path "$ANN" \
    --output-dir "$out" \
    --full-val \
    --total-splits "$TOTAL" \
    --current-split "$i" \
    --device 0 \
    --proposition-model "$PROP_MODEL" \
    --puls-model "$PULS_MODEL" \
    --env-file "$HOME/.env" \
    > "$out/run.log" 2>&1 &
done

echo "[launcher] started $TOTAL shards under $BASE_OUT"
