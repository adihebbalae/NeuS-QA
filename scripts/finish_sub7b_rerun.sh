#!/usr/bin/env bash
# Finish Sub7b after NSVS rerun: crop + hardened VQA on rerun qids, union into final submission.
#
# Full run (after run_sub7_rerun_failed_nsvs.sh completes):
#   bash scripts/finish_sub7b_rerun.sh
#
# Smoke while rerun is in flight (uses per_entry JSON, no merge required):
#   SMOKE=1 bash scripts/finish_sub7b_rerun.sh
#   SMOKE=1 SMOKE_N=10 bash scripts/finish_sub7b_rerun.sh
#
# Optional:
#   SKIP_NSVS_MERGE=1  — merged/entries.json already contains rerun rows
#   DRY_RUN=1          — print planned paths and exit
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful}
RERUN_ROOT=${RERUN_ROOT:-${BASE}/nsvs_rerun}
QID_FILE=${QID_FILE:-${BASE}/rerun_qids.json}
MERGED=${MERGED:-${BASE}/merged/entries.json}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
VQA_MODEL=${VQA_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-16}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
SMOKE_N=${SMOKE_N:-10}

MAIN_PARTIAL=${MAIN_PARTIAL:-${BASE}/answers_gpt_5_2/submission_partial.json}
FINAL=${FINAL:-${BASE}/submission_sub7b.json}

if [[ -n "${SMOKE:-}" ]]; then
  WORK=${WORK:-${BASE}/sub7b_smoke${SMOKE_N}}
  RERUN_ENTRIES="${WORK}/rerun_entries.json"
  POST="${WORK}/postprocess"
  ANSWER_DIR="${WORK}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}"
  OUT_SUB="${WORK}/submission_smoke.json"
  ASSEMBLE_SOURCE=per_entry
  ASSEMBLE_LIMIT="--limit ${SMOKE_N}"
  SKIP_NSVS_MERGE=1
  SKIP_UNION=1
else
  WORK=${WORK:-${BASE}/sub7b_rerun_vqa}
  RERUN_ENTRIES="${WORK}/rerun_entries.json"
  POST="${WORK}/postprocess"
  ANSWER_DIR="${WORK}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}"
  OUT_SUB="${FINAL}"
  ASSEMBLE_SOURCE=shard_entries
  ASSEMBLE_LIMIT=""
  SKIP_UNION=${SKIP_UNION:-0}
fi

cd "$REPO"
source .venv/bin/activate

FFMPEG=$(python3 -c "from nsvqa.utils.ffmpeg_path import get_ffmpeg_exe; print(get_ffmpeg_exe())")
echo "[sub7b-finish] ffmpeg: $FFMPEG"
export FFMPEG

echo "[sub7b-finish] BASE=$BASE"
echo "[sub7b-finish] mode=$([[ -n "${SMOKE:-}" ]] && echo smoke${SMOKE_N} || echo full)"
echo "[sub7b-finish] WORK=$WORK"

if [[ -n "${DRY_RUN:-}" ]]; then
  echo "[sub7b-finish] DRY_RUN — would write:"
  echo "  rerun entries: $RERUN_ENTRIES"
  echo "  postprocess:   $POST"
  echo "  vqa answers:   $ANSWER_DIR"
  echo "  submission:    $OUT_SUB"
  exit 0
fi

if [[ -z "${SKIP_NSVS_MERGE:-}" ]] && [[ -z "${SMOKE:-}" ]]; then
  shard_dirs=$(python3 - <<PY
import os
root = "${RERUN_ROOT}"
dirs = []
for i in range(1, 99):
    d = f"{root}/shard_{i}"
    if os.path.isdir(d):
        dirs.append(d)
    elif i > 2:
        break
missing = [d for d in dirs if not os.path.isfile(os.path.join(d, "entries.json"))]
if missing:
    raise SystemExit(f"FATAL: missing entries.json in: {missing}")
print(",".join(dirs))
PY
  )
  if [[ ! -f "$MERGED" ]]; then
    echo "FATAL: missing base merge file $MERGED" >&2
    exit 1
  fi
  echo "[sub7b-finish] merging NSVS rerun shards into $MERGED at $(date -Iseconds)"
  python3 scripts/merge_nsvs_shards.py \
    --shard-dirs "$shard_dirs" \
    --into-entries "$MERGED" \
    --out-dir "${BASE}/merged"
fi

if [[ -n "${SMOKE:-}" ]]; then
  echo "[sub7b-finish] assembling ${SMOKE_N} rows from per_entry at $(date -Iseconds)"
  python3 scripts/assemble_rerun_entries.py \
    --rerun-root "$RERUN_ROOT" \
    --output "$RERUN_ENTRIES" \
    --source per_entry \
    --require-nsvs-ok \
    $ASSEMBLE_LIMIT
else
  echo "[sub7b-finish] extracting rerun qids -> $RERUN_ENTRIES at $(date -Iseconds)"
  python3 scripts/assemble_rerun_entries.py \
    --rerun-root "$RERUN_ROOT" \
    --output "$RERUN_ENTRIES" \
    --source shard_entries \
    --qid-file "$QID_FILE"
fi

n=$(python3 -c "import json; print(len(json.load(open('$RERUN_ENTRIES'))))")
echo "[sub7b-finish] rerun entries: $n"

echo "[sub7b-finish] cropping at $(date -Iseconds)"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "$RERUN_ENTRIES" \
  --output-dir "$POST" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

CROP_FAILS=$(python3 -c "import json; print(json.load(open('${POST}/crop_summary.json'))['crop_failures'])")
if [[ "$CROP_FAILS" -gt 0 ]]; then
  echo "FATAL: ${CROP_FAILS} crop failures. See ${POST}/crop_summary.json" >&2
  exit 2
fi
echo "[sub7b-finish] crop failures: 0"

echo "[sub7b-finish] VQA (${VQA_MODEL}) at $(date -Iseconds)"
python3 -u scripts/answer_cropped_entries.py \
  --entries "${POST}/postprocess_entries.json" \
  --output-dir "$ANSWER_DIR" \
  --model "$VQA_MODEL" \
  --num-frames "$NUM_FRAMES" \
  --image-detail "$IMAGE_DETAIL" \
  --env-file "$HOME/.env" \
  2>&1 | tee "${WORK}/answer_${VQA_MODEL//[^a-zA-Z0-9]/_}.log"

if [[ -z "${SKIP_UNION:-}" ]]; then
  if [[ ! -f "$MAIN_PARTIAL" ]]; then
    echo "FATAL: missing main VQA partial $MAIN_PARTIAL" >&2
    exit 1
  fi
  echo "[sub7b-finish] union main + rerun partials -> $OUT_SUB at $(date -Iseconds)"
  python3 scripts/build_submission.py \
    --val-annotations "$ANN" \
    --partial "$MAIN_PARTIAL" \
    --partial "${ANSWER_DIR}/submission_partial.json" \
    --output "$OUT_SUB"
else
  python3 - <<PY
import json
ann = json.load(open("${ANN}"))
qids = {str(e["metadata"]["question_id"]) for e in json.load(open("${RERUN_ENTRIES}"))}
slice_ann = [a for a in ann if str(a["question_id"]) in qids]
json.dump(slice_ann, open("${WORK}/annotations_slice.json", "w"), indent=2)
print(f"[sub7b-finish] ann slice rows={len(slice_ann)}")
PY
  python3 scripts/build_submission.py \
    --val-annotations "${WORK}/annotations_slice.json" \
    --partial "${ANSWER_DIR}/submission_partial.json" \
    --output "$OUT_SUB" \
    --force
fi

python3 postprocess/per_category_breakdown.py \
  --base "$WORK" \
  --ann-path "$ANN" \
  --submission "$OUT_SUB" \
  --entries "${POST}/postprocess_entries.json" \
  --partial "${ANSWER_DIR}/submission_partial.json"

echo "[sub7b-finish] done $(date -Iseconds)"
echo "[sub7b-finish] outputs:"
echo "  submission:  $OUT_SUB"
echo "  breakdown:   ${WORK}/per_category_breakdown.json"
echo "  api_cost:    ${ANSWER_DIR}/api_cost.json"
