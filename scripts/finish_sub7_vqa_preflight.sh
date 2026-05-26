#!/usr/bin/env bash
# Finish Sub7 HEAD=10 preflight from existing NSVS merged entries (no NSVS rerun).
# Steps: ffmpeg crop -> gpt-5.2 VQA -> 10-row smoke submission -> per_category_breakdown.
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub7_preflight_vqa10}
MERGED_ENTRIES=${MERGED_ENTRIES:-${BASE}/merged/entries.json}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
VQA_MODEL=${VQA_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-16}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
POST="${BASE}/postprocess"
ANSWER_DIR="${BASE}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}"
FINAL="${BASE}/submission_smoke10.json"
ANN10="${BASE}/annotations_smoke10.json"

cd "$REPO"
source .venv/bin/activate

FFMPEG=$(python3 -c "from nsvqa.utils.ffmpeg_path import get_ffmpeg_exe; print(get_ffmpeg_exe())")
echo "[vqa-preflight] ffmpeg: $FFMPEG"
export FFMPEG

if [[ ! -f "$MERGED_ENTRIES" ]]; then
  echo "FATAL: missing merged entries: $MERGED_ENTRIES" >&2
  exit 1
fi

n=$(python3 -c "import json; print(len(json.load(open('$MERGED_ENTRIES'))))")
echo "[vqa-preflight] BASE=$BASE merged_entries=$n (NSVS reused, no rerun)"

echo "[vqa-preflight] cropping at $(date -Iseconds)"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "$MERGED_ENTRIES" \
  --output-dir "$POST" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

CROP_FAILS=$(jq '.crop_failures' "${POST}/crop_summary.json")
if [[ "$CROP_FAILS" -gt 0 ]]; then
  echo "FATAL: ${CROP_FAILS} crop failures. See ${POST}/crop_summary.json" >&2
  exit 2
fi
echo "[vqa-preflight] crop failures: 0"

echo "[vqa-preflight] VQA at $(date -Iseconds)"
python3 -u scripts/answer_cropped_entries.py \
  --entries "${POST}/postprocess_entries.json" \
  --output-dir "$ANSWER_DIR" \
  --model "$VQA_MODEL" \
  --num-frames "$NUM_FRAMES" \
  --image-detail "$IMAGE_DETAIL" \
  --env-file "$HOME/.env" \
  2>&1 | tee "${BASE}/answer_${VQA_MODEL//[^a-zA-Z0-9]/_}.log"

python3 - <<PY
import json
merged = json.load(open("${MERGED_ENTRIES}"))
qids = {str(e["metadata"]["question_id"]) for e in merged}
ann = json.load(open("${ANN}"))
slice10 = [a for a in ann if str(a["question_id"]) in qids]
json.dump(slice10, open("${ANN10}", "w"), indent=2)
print(f"[vqa-preflight] wrote {len(slice10)}-row ann slice -> ${ANN10}")
PY

python3 scripts/build_submission.py \
  --val-annotations "$ANN10" \
  --partial "${ANSWER_DIR}/submission_partial.json" \
  --output "$FINAL"

python3 postprocess/per_category_breakdown.py \
  --base "$BASE" \
  --ann-path "$ANN10" \
  --submission "$FINAL" \
  --entries "${POST}/postprocess_entries.json" \
  --partial "${ANSWER_DIR}/submission_partial.json"

echo "[vqa-preflight] done $(date -Iseconds)"
echo "[vqa-preflight] outputs:"
echo "  crop_summary: ${POST}/crop_summary.json"
echo "  submission:   $FINAL"
echo "  breakdown:    ${BASE}/per_category_breakdown.json"
