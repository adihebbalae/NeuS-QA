#!/usr/bin/env bash
# Sub #9 — first honest full val pass with PULS v2 (Examples 13–16 in prompts.py).
# Straight end-to-end NeuS-QA only — NO hybrid/routing (Sub #8 is reserved for routing levers).
#
# Pipeline (val, paper-faithful hardened):
#   gpt-4o PULS/target_id -> InternVL2-8B NSVS @ 3fps -> ffmpeg crop -> gpt-5.2 VQA.
#
# GPUs 2–7 only (6 shards). Do NOT use default run_sub7.sh GPU mapping (0–5).
#
# Launch in tmux (>5 min; see .cursor/rules/workflow.md):
#   tmux new-session -d -s sub9_val \
#     'cd ~/NeuS-QA && bash scripts/run_sub9_pulsv2_val.sh 2>&1 | tee /mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_val/run.log'
#
# End-to-end (auto): NSVS -> merge -> crop -> VQA -> submission -> analyze.
# Re-run safely after interrupt: skips completed phases (shard NSVS, merge, crop, VQA).
# FORCE=1 ignores DONE and re-runs from the top.
#
# Preflight:
#   HEAD=10 bash scripts/run_sub9_pulsv2_val.sh
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

# Val paths — same as last paper-faithful val (run_sub5b_paper_faithful.sh), NOT run_sub7 test paths.
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_val}
TOTAL=${TOTAL:-6}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
PROP_MODEL=${PROP_MODEL:-InternVL2-8B}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}
VQA_MODEL=${VQA_MODEL:-gpt-5.2}
NUM_FRAMES=${NUM_FRAMES:-16}
IMAGE_DETAIL=${IMAGE_DETAIL:-low}
SPEND_CAP_USD=${SPEND_CAP_USD:-60}
ANSWER_DIR=${ANSWER_DIR:-${BASE}/answers_${VQA_MODEL//[^a-zA-Z0-9]/_}}
FINAL=${FINAL:-${BASE}/submission_sub9_pulsv2_val.json}

LIMIT_ARGS=()
if [[ -n "${HEAD:-}" ]]; then
  LIMIT_ARGS=(--limit "$HEAD")
  TOTAL=1
  echo "[sub9] HEAD=${HEAD} preflight mode: single shard on GPU 2, limit ${HEAD}"
fi

export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

mkdir -p "$BASE"
cat > "${BASE}/config.json" <<EOF
{
  "pipeline": "Sub #9 PULS v2 honest NeuS-QA val (no routing)",
  "phase": "val",
  "routing": false,
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
  "output_dir": "${BASE}",
  "gpu_map": "shard i -> GPU i+1 (i=1..${TOTAL}), GPUs 2-7 only"
}
EOF

echo "[sub9] BASE=$BASE (straight pipeline; Sub #8 reserved for routing experiments)"
echo "[sub9] branch=$(git -C "$REPO" rev-parse --short HEAD) (need fd63192+ for FOI-on-crop fix in VQA)"
echo "[sub9] ANN=$ANN rows=$(python3 -c "import json; print(len(json.load(open('$ANN'))))")"

if [[ -f "${BASE}/DONE" ]] && [[ "${FORCE:-}" != "1" ]]; then
  echo "[sub9] ${BASE}/DONE exists; pipeline complete (FORCE=1 to redo)"
  exit 0
fi

MERGED="${BASE}/merged"
POST="${BASE}/postprocess"
N_ANN=$(python3 -c "import json; print(len(json.load(open('$ANN'))))")

echo "[sub9] starting NSVS shards at $(date -Iseconds)"

pids=()
for i in $(seq 1 "$TOTAL"); do
  gpu=$((i + 1))
  out="${BASE}/shard_${i}"
  if [[ -f "${out}/entries.json" ]] && grep -q "completed nsvs" "${out}/run.log" 2>/dev/null; then
    echo "[sub9] shard ${i}/${TOTAL} already complete; skipping"
    continue
  fi
  mkdir -p "$out"
  echo "[sub9] shard ${i}/${TOTAL} on GPU ${gpu} -> ${out}"
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

if [[ ${#pids[@]} -gt 0 ]]; then
  for pid in "${pids[@]}"; do
    wait "$pid"
  done
  echo "[sub9] all NSVS shards exited at $(date -Iseconds)"
else
  echo "[sub9] all NSVS shards already complete; skipping GPU phase"
fi

for i in $(seq 1 "$TOTAL"); do
  if [[ ! -f "${BASE}/shard_${i}/entries.json" ]]; then
    echo "[sub9] ERROR: missing entries.json for shard ${i}" >&2
    exit 1
  fi
done

python3 - <<'PY' || { echo "[sub9] FATAL: spend projection exceeds cap; halting before merge/VQA." >&2; exit 3; }
import glob
import json
import os
import sys

from nsvqa.utils.api_cost import estimate_vision_call

base = os.environ["BASE"]
cap = float(os.environ.get("SPEND_CAP_USD", "60"))
vqa_model = os.environ.get("VQA_MODEL", "gpt-5.2")
num_frames = int(os.environ.get("NUM_FRAMES", "16"))
ann = os.environ["ANN"]

nsvs = 0.0
for path in glob.glob(os.path.join(base, "shard_*", "api_cost.json")):
    nsvs += float(json.load(open(path)).get("total_usd", 0.0))

n_rows = len(json.load(open(ann)))
vqa_est = n_rows * estimate_vision_call(vqa_model, num_frames=num_frames, image_detail="low")
projected = nsvs + vqa_est
print(f"[sub9] spend check: NSVS metered ${nsvs:.2f} + VQA est ${vqa_est:.2f} = ${projected:.2f} (cap ${cap:.2f})")
if projected > cap:
    print(f"[sub9] HALT: projected ${projected:.2f} > cap ${cap:.2f}", file=sys.stderr)
    sys.exit(1)
PY

shard_dirs=$(python3 - <<PY
import os
base = "${BASE}"
total = int("${TOTAL}")
dirs = [f"{base}/shard_{i}" for i in range(1, total + 1)]
print(",".join(d for d in dirs if os.path.isdir(d)))
PY
)

if [[ -f "${MERGED}/entries.json" ]] && [[ "${FORCE_MERGE:-}" != "1" ]]; then
  echo "[sub9] ${MERGED}/entries.json exists; skipping merge"
else
  echo "[sub9] merging NSVS shards at $(date -Iseconds)"
  python3 scripts/merge_nsvs_shards.py \
    --shard-dirs "$shard_dirs" \
    --out-dir "$MERGED"
fi

if [[ -f "${POST}/crop_summary.json" ]] \
  && [[ "$(jq -r '.crop_failures' "${POST}/crop_summary.json")" == "0" ]] \
  && [[ -f "${POST}/postprocess_entries.json" ]] \
  && [[ "${FORCE_CROP:-}" != "1" ]]; then
  echo "[sub9] crop complete (0 failures); skipping crop"
else
  echo "[sub9] cropping videos at $(date -Iseconds)"
  python3 -u scripts/crop_timelogic_entries.py \
    --entries "${MERGED}/entries.json" \
    --output-dir "$POST" \
    --video-root "$VIDEO_ROOT" \
    --ann-path "$ANN"

  CROP_FAILS=$(jq '.crop_failures' "${POST}/crop_summary.json")
  if [ "$CROP_FAILS" -gt 0 ]; then
      echo "FATAL: ${CROP_FAILS} crop failures. Halting before VQA. Inspect ${POST}/crop_summary.json." >&2
      exit 2
  fi
  echo "[sub9] crop step: 0 failures"
fi

VQA_PARTIAL="${ANSWER_DIR}/submission_partial.json"
VQA_DONE=0
if [[ -f "$VQA_PARTIAL" ]] && [[ "${FORCE_VQA:-}" != "1" ]]; then
  VQA_N=$(python3 -c "import json; print(len(json.load(open('$VQA_PARTIAL'))))")
  if [[ "$VQA_N" -eq "$N_ANN" ]]; then
    echo "[sub9] VQA partial has ${VQA_N}/${N_ANN} rows; skipping VQA"
    VQA_DONE=1
  fi
fi

if [[ "$VQA_DONE" -eq 0 ]]; then
  echo "[sub9] GPT VQA on cropped clips at $(date -Iseconds)"
  python3 -u scripts/answer_cropped_entries.py \
    --entries "${POST}/postprocess_entries.json" \
    --output-dir "$ANSWER_DIR" \
    --model "$VQA_MODEL" \
    --num-frames "$NUM_FRAMES" \
    --image-detail "$IMAGE_DETAIL" \
    --env-file "$HOME/.env" \
    2>&1 | tee -a "${BASE}/answer_${VQA_MODEL//[^a-zA-Z0-9]/_}.log"
fi

if [[ ! -f "$FINAL" ]] || [[ "${FORCE_SUBMISSION:-}" == "1" ]]; then
  python3 scripts/build_submission.py \
    --val-annotations "$ANN" \
    --partial "${ANSWER_DIR}/submission_partial.json" \
    --output "$FINAL"
else
  echo "[sub9] $FINAL exists; skipping build_submission"
fi

if [[ ! -f "${BASE}/per_category_breakdown.json" ]] || [[ "${FORCE_BREAKDOWN:-}" == "1" ]]; then
  python3 postprocess/per_category_breakdown.py \
    --base "$BASE" \
    --ann-path "$ANN" \
    --submission "$FINAL" \
    --entries "${POST}/postprocess_entries.json" \
    --partial "${ANSWER_DIR}/submission_partial.json"
fi

if [[ ! -f "${BASE}/sub9_val_report.md" ]] || [[ "${FORCE_ANALYZE:-}" == "1" ]]; then
  python3 scripts/analyze_sub9_pulsv2_val.py --base "$BASE"
else
  echo "[sub9] sub9_val_report.md exists; skipping analyze"
fi

n=$(python3 -c "import json; print(len(json.load(open('$FINAL'))))")
echo "[sub9] wrote $FINAL ($n rows)"
echo "done $(date -Iseconds)" > "${BASE}/DONE"
echo "[sub9] Val analysis at ${BASE}/sub9_val_report.md (no EvalAI upload — Adi decides test promotion)"
