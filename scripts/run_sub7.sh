#!/usr/bin/env bash
# Sub #7 — first honest end-to-end NeuS-QA test submission.
#
# Pipeline:
#   gpt-4o PULS/target_id -> InternVL2-8B NSVS @ 3fps -> ffmpeg crop -> gpt-5.2 VQA.
#
# Preflight (10-row slice):
#   HEAD=10 bash scripts/run_sub7.sh
#
# Full test run (tmux recommended):
#   tmux new-session -d -s sub7_test 'cd ~/NeuS-QA && bash scripts/run_sub7.sh 2>&1 | tee .../sub7_neusqa_paper_faithful/run.log'
#
# After Sub7a-style NSVS failures, repair with: bash scripts/run_sub7b.sh
# Optional: AUTO_SUB7B=1 on first run_sub7.sh exit chains into run_sub7b.sh (default 0).
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
cd "$REPO"
source .venv/bin/activate

FFMPEG=$(python3 -c "from nsvqa.utils.ffmpeg_path import get_ffmpeg_exe; print(get_ffmpeg_exe())" 2>/dev/null) || {
    echo "FATAL: ffmpeg not found. Install imageio-ffmpeg in .venv: uv pip install imageio-ffmpeg" >&2
    exit 1
}
echo "[preflight] ffmpeg found at $FFMPEG"
export FFMPEG
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful}
TOTAL=${TOTAL:-8}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
PROP_MODEL=${PROP_MODEL:-InternVL2-8B}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}
VQA_MODEL=${VQA_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-16}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
ANSWER_DIR=${ANSWER_DIR:-${BASE}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}}
FINAL=${FINAL:-${BASE}/submission_sub7.json}

LIMIT_ARGS=()
if [[ -n "${HEAD:-}" ]]; then
  LIMIT_ARGS=(--limit "$HEAD")
  TOTAL=1
  echo "[sub7] HEAD=${HEAD} preflight mode: single shard, limit ${HEAD}"
fi

export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

mkdir -p "$BASE"
cat > "${BASE}/config.json" <<EOF
{
  "pipeline": "Sub #7 honest NeuS-QA test",
  "phase": "test",
  "puls_model": "${PULS_MODEL}",
  "target_identification_model": "${PULS_MODEL}",
  "proposition_model": "OpenGVLab/${PROP_MODEL}",
  "sample_rate": ${SAMPLE_RATE},
  "postprocess": "ffmpeg crop via Manager.crop_video",
  "downstream_vqa": "${VQA_MODEL}",
  "downstream_vqa_frames": ${NUM_FRAMES},
  "downstream_vqa_image_detail": "${IMAGE_DETAIL}",
  "video_root": "${VIDEO_ROOT}",
  "ann_path": "${ANN}",
  "output_dir": "${BASE}"
}
EOF

echo "[sub7] BASE=$BASE"
echo "[sub7] ANN=$ANN rows=$(python3 -c "import json; print(len(json.load(open('$ANN'))))")"
echo "[sub7] starting NSVS shards at $(date -Iseconds)"

pids=()
for i in $(seq 1 "$TOTAL"); do
  gpu=$((i - 1))
  out="${BASE}/shard_${i}"
  if [[ -f "${out}/entries.json" ]] && grep -q "completed nsvs" "${out}/run.log" 2>/dev/null; then
    echo "[sub7] shard ${i}/${TOTAL} already complete; skipping"
    continue
  fi
  mkdir -p "$out"
  echo "[sub7] shard ${i}/${TOTAL} on GPU ${gpu} -> ${out}"
  CUDA_VISIBLE_DEVICES=$gpu python3 -u scripts/run_timelogic.py \
    --video-root "$VIDEO_ROOT" \
    --ann-path "$ANN" \
    --output-dir "$out" \
    --full-val \
    --total-splits "$TOTAL" \
    --current-split "$i" \
    --device 0 \
    --proposition-model "$PROP_MODEL" \
    --puls-model "$PULS_MODEL" \
    --sample-rate "$SAMPLE_RATE" \
    --env-file "$HOME/.env" \
    "${LIMIT_ARGS[@]}" \
    > "${out}/run.log" 2>&1 &
  pids+=("$!")
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

echo "[sub7] all NSVS shards exited at $(date -Iseconds)"
for i in $(seq 1 "$TOTAL"); do
  if [[ ! -f "${BASE}/shard_${i}/entries.json" ]]; then
    echo "[sub7] ERROR: missing entries.json for shard ${i}" >&2
    exit 1
  fi
done

MERGED="${BASE}/merged"
POST="${BASE}/postprocess"

shard_dirs=$(python3 - <<PY
import os
base = "${BASE}"
total = int("${TOTAL}")
dirs = [f"{base}/shard_{i}" for i in range(1, total + 1)]
print(",".join(d for d in dirs if os.path.isdir(d)))
PY
)

python3 scripts/merge_nsvs_shards.py \
  --shard-dirs "$shard_dirs" \
  --out-dir "$MERGED"

echo "[sub7] cropping videos at $(date -Iseconds)"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "${MERGED}/entries.json" \
  --output-dir "$POST" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

CROP_FAILS=$(jq '.crop_failures' "${BASE}/postprocess/crop_summary.json")
if [ "$CROP_FAILS" -gt 0 ]; then
    echo "FATAL: ${CROP_FAILS} crop failures. Halting before VQA. Inspect ${BASE}/postprocess/crop_summary.json." >&2
    exit 2
fi
echo "[preflight] crop step produced 0 failures, proceeding to VQA"

echo "[sub7] GPT VQA on cropped clips at $(date -Iseconds)"
python3 -u scripts/answer_cropped_entries.py \
  --entries "${POST}/postprocess_entries.json" \
  --output-dir "$ANSWER_DIR" \
  --model "$VQA_MODEL" \
  --num-frames "$NUM_FRAMES" \
  --image-detail "$IMAGE_DETAIL" \
  --env-file "$HOME/.env" \
  2>&1 | tee "${BASE}/answer_${VQA_MODEL//[^a-zA-Z0-9]/_}.log"

python3 scripts/build_submission.py \
  --val-annotations "$ANN" \
  --partial "${ANSWER_DIR}/submission_partial.json" \
  --output "$FINAL"

python3 postprocess/per_category_breakdown.py \
  --base "$BASE" \
  --ann-path "$ANN" \
  --submission "$FINAL" \
  --entries "${POST}/postprocess_entries.json" \
  --partial "${ANSWER_DIR}/submission_partial.json"

n=$(python3 -c "import json; print(len(json.load(open('$FINAL'))))")
echo "[sub7] wrote $FINAL ($n rows)"
echo "done $(date -Iseconds)" > "${BASE}/DONE"
echo "[sub7] UPLOAD: EvalAI test phase -> $FINAL"

if [[ "${AUTO_SUB7B:-0}" == "1" ]]; then
  echo "[sub7] AUTO_SUB7B=1 -> chaining run_sub7b.sh"
  bash "${REPO}/scripts/run_sub7b.sh"
fi
