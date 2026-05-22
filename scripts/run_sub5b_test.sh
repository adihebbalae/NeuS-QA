#!/usr/bin/env bash
# Sub #5B test-phase run — same stack as val fix2:
#   gpt-4o PULS/target_id -> InternVL2-8B NSVS @ 3fps -> ffmpeg crop -> gpt-5.2 VQA.
#
# Launch in tmux:
#   tmux new-session -d -s sub5b_test \
#     "bash /home/ah66742/NeuS-QA/scripts/run_sub5b_test.sh 2>&1 | tee /mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps/run.log"
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps}
TOTAL=${TOTAL:-8}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
PROP_MODEL=${PROP_MODEL:-InternVL2-8B}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}
VQA_MODEL=${VQA_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-16}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
ANSWER_DIR=${ANSWER_DIR:-${BASE}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}}
FINAL=${FINAL:-${BASE}/submission_sub5b_test_gpt52.json}

cd "$REPO"
source .venv/bin/activate
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

mkdir -p "$BASE"
cat > "${BASE}/config.json" <<EOF
{
  "pipeline": "Sub #5B test paper-faithful NeuS-QA",
  "phase": "test",
  "puls_model": "${PULS_MODEL}",
  "target_identification_model": "${PULS_MODEL}",
  "proposition_model": "OpenGVLab/${PROP_MODEL}",
  "sample_rate": ${SAMPLE_RATE},
  "postprocess": "ffmpeg crop via Manager.crop_video",
  "downstream_vqa": "${VQA_MODEL}",
  "downstream_vqa_frames": ${NUM_FRAMES},
  "output_dir": "${BASE}"
}
EOF

echo "[sub5b-test] BASE=$BASE"
echo "[sub5b-test] ANN=$ANN rows=$(python3 -c "import json; print(len(json.load(open('$ANN'))))")"
echo "[sub5b-test] starting NSVS shards at $(date -Iseconds)"

pids=()
for i in $(seq 1 "$TOTAL"); do
  gpu=$((i - 1))
  out="${BASE}/shard_${i}"
  if [[ -f "${out}/entries.json" ]] && grep -q "completed nsvs" "${out}/run.log" 2>/dev/null; then
    echo "[sub5b-test] shard ${i}/${TOTAL} already complete; skipping"
    continue
  fi
  mkdir -p "$out"
  echo "[sub5b-test] shard ${i}/${TOTAL} on GPU ${gpu} -> ${out}"
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
    > "${out}/run.log" 2>&1 &
  pids+=("$!")
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

echo "[sub5b-test] all NSVS shards exited at $(date -Iseconds)"
for i in $(seq 1 "$TOTAL"); do
  if [[ ! -f "${BASE}/shard_${i}/entries.json" ]]; then
    echo "[sub5b-test] ERROR: missing entries.json for shard ${i}" >&2
    exit 1
  fi
done

MERGED="${BASE}/merged"
POST="${BASE}/postprocess"

python3 scripts/merge_nsvs_shards.py \
  --shard-dirs "${BASE}/shard_1,${BASE}/shard_2,${BASE}/shard_3,${BASE}/shard_4,${BASE}/shard_5,${BASE}/shard_6,${BASE}/shard_7,${BASE}/shard_8" \
  --out-dir "$MERGED"

echo "[sub5b-test] cropping videos at $(date -Iseconds)"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "${MERGED}/entries.json" \
  --output-dir "$POST" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

echo "[sub5b-test] GPT VQA on cropped clips at $(date -Iseconds)"
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

n=$(python3 -c "import json; print(len(json.load(open('$FINAL'))))")
echo "[sub5b-test] wrote $FINAL ($n rows)"
echo "done $(date -Iseconds)" > "${BASE}/DONE"
echo "[sub5b-test] UPLOAD: EvalAI test phase -> $FINAL"
