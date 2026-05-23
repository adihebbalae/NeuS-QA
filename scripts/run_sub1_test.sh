#!/usr/bin/env bash
# Sub #1 test-phase baseline — same stack as val baseline_cpu_v01:
#   gpt-5.2 PULS + 8 full-video frames + gpt-5.2 vision (no NSVS/GPU).
#
# Launch in tmux:
#   tmux new-session -d -s sub1_test \
#     "bash /home/ah66742/NeuS-QA/scripts/run_sub1_test.sh 2>&1 | tee /mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test/submission_run.log"
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test}
PULS_MODEL=${PULS_MODEL:-gpt-5.2}
ANSWER_MODEL=${ANSWER_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-8}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
FINAL=${FINAL:-${BASE}/submission.json}

cd "$REPO"
source .venv/bin/activate

mkdir -p "$BASE"
cat > "${BASE}/config.json" <<EOF
{
  "pipeline": "Sub #1 test CPU baseline",
  "phase": "test",
  "puls_model": "${PULS_MODEL}",
  "answer_model": "${ANSWER_MODEL}",
  "num_frames": ${NUM_FRAMES},
  "image_detail": "${IMAGE_DETAIL}",
  "output_dir": "${BASE}"
}
EOF

echo "[sub1-test] BASE=$BASE"
echo "[sub1-test] ANN=$ANN rows=$(python3 -c "import json; print(len(json.load(open('$ANN'))))")"
echo "[sub1-test] starting at $(date -Iseconds)"

python3 -u scripts/run_baseline_cpu.py \
  --split test \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN" \
  --output-dir "$BASE" \
  --puls-model "$PULS_MODEL" \
  --answer-model "$ANSWER_MODEL" \
  --num-frames "$NUM_FRAMES" \
  --image-detail "$IMAGE_DETAIL" \
  --env-file "$HOME/.env" \
  2>&1 | tee -a "${BASE}/run.log"

n=$(python3 -c "import json; print(len(json.load(open('$FINAL'))))")
echo "[sub1-test] wrote $FINAL ($n rows)"
echo "done $(date -Iseconds)" > "${BASE}/DONE"
echo "[sub1-test] compare vs Sub #5B test:"
echo "  bash scripts/compare_sub5b_test_vs_sub1.sh"
echo "[sub1-test] api cost estimate:"
echo "  cat ${BASE}/api_cost.json"
