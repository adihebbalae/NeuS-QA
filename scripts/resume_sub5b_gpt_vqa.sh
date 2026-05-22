#!/usr/bin/env bash
# Resume Sub #5B after NSVS + crop: swap local Qwen/vLLM for OpenAI GPT VQA.
#
# Paper-faithful core is unchanged: gpt-4o PULS/target_id, InternVL2-8B NSVS @ 3fps,
# Storm check, ffmpeg crop. Only the downstream answerer changes (model-agnostic).
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2}
ANN=${ANN:-/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json}
VQA_MODEL=${VQA_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-16}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
ANSWER_DIR=${ANSWER_DIR:-${BASE}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}}
FINAL=${FINAL:-${BASE}/submission_sub5b_paper_faithful_gpt52.json}

cd "$REPO"
source .venv/bin/activate

POST="${BASE}/postprocess/postprocess_entries.json"
if [[ ! -f "$POST" ]]; then
  echo "[resume-sub5b] missing postprocess entries: $POST" >&2
  exit 1
fi

echo "[resume-sub5b] BASE=$BASE"
echo "[resume-sub5b] VQA model=$VQA_MODEL frames=$NUM_FRAMES detail=$IMAGE_DETAIL"
echo "[resume-sub5b] answering cropped clips at $(date -Iseconds)"

python3 -u scripts/answer_cropped_entries.py \
  --entries "$POST" \
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

echo "[resume-sub5b] wrote $FINAL"
echo "done $(date -Iseconds)" > "${BASE}/DONE"
