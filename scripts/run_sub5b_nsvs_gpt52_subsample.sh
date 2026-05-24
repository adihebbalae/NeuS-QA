#!/usr/bin/env bash
# Sub #5B NSVS backend ablation: swap InternVL2-8B for gpt-5.2-medium on a 50-Q subsample.
#
# Pipeline (everything except NSVS detector matches Sub #5B @ 3fps):
#   gpt-4o PULS/target_id (reused from baseline) -> gpt-5.2 NSVS detect -> ffmpeg crop -> gpt-5.2 VQA
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
BASELINE_ENTRIES=${BASELINE_ENTRIES:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_subsample}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}
NSVS_DEVICE=${NSVS_DEVICE:-0}
INTERNVL_DEVICE=${INTERNVL_DEVICE:-0}

cd "$REPO"
source .venv/bin/activate

mkdir -p "$BASE"

echo "[ablation] building 50-Q stratified subsample at $(date -Iseconds)"
python3 scripts/build_nsvs_backend_subsample.py --out "$BASE"

echo "[ablation] running gpt-5.2 NSVS pipeline at $(date -Iseconds)"
python3 -u scripts/run_timelogic.py \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN" \
  --output-dir "$BASE/nsvs" \
  --qid-file "$BASE/subsample_qids.json" \
  --nsvs-backend gpt5.2 \
  --sample-rate "$SAMPLE_RATE" \
  --puls-model "$PULS_MODEL" \
  --reuse-from "$BASELINE_ENTRIES" \
  --env-file "$HOME/.env" \
  2>&1 | tee "$BASE/nsvs/run.log"

echo "[ablation] cropping videos at $(date -Iseconds)"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "$BASE/nsvs/entries.json" \
  --output-dir "$BASE/postprocess" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

echo "[ablation] gpt-5.2 VQA on cropped clips at $(date -Iseconds)"
python3 -u scripts/answer_cropped_entries.py \
  --entries "$BASE/postprocess/postprocess_entries.json" \
  --output-dir "$BASE/answers" \
  --model gpt-5.2 \
  --num-frames 16 \
  --image-detail low \
  --env-file "$HOME/.env" \
  2>&1 | tee "$BASE/answers/run.log"

python3 scripts/build_submission.py \
  --val-annotations "$ANN" \
  --partial "$BASE/answers/submission_partial.json" \
  --output "$BASE/submission_partial_50q.json"

echo "[ablation] replaying InternVL detections for head-to-head at $(date -Iseconds)"
CUDA_VISIBLE_DEVICES="$INTERNVL_DEVICE" python3 -u scripts/replay_internvl_nsvs_detections.py \
  --entries "$BASE/nsvs/entries.json" \
  --output-dir "$BASE/internvl_replay" \
  --sample-rate "$SAMPLE_RATE" \
  --device 0 \
  --cache-dir "$BASE/nsvs_detection_cache" \
  2>&1 | tee "$BASE/internvl_replay/run.log"

echo "[ablation] writing report at $(date -Iseconds)"
python3 scripts/report_nsvs_backend_ablation.py --base "$BASE"

echo "[ablation] done $(date -Iseconds)" | tee "$BASE/DONE"
echo "[ablation] report: $BASE/report/ablation_summary.md"
