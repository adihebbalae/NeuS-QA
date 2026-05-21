#!/usr/bin/env bash
# Full paper-faithful TimeLogic Sub #5B run.
#
# Pipeline:
#   PULS/target_id gpt-4o -> InternVL2-8B NSVS -> ffmpeg crop -> local Qwen2.5-VL-7B VQA.
#
# Intended to be launched inside a detached tmux session.
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful}
TOTAL=${TOTAL:-8}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
PROP_MODEL=${PROP_MODEL:-InternVL2-8B}
SAMPLE_RATE=${SAMPLE_RATE:-1.0}
QWEN_MODEL=${QWEN_MODEL:-Qwen/Qwen2.5-VL-7B-Instruct}
QWEN_PORT=${QWEN_PORT:-8000}
QWEN_GPU=${QWEN_GPU:-0}
VLLM_VENV=${VLLM_VENV:-${BASE}/vllm_venv}

cd "$REPO"
source .venv/bin/activate
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

mkdir -p "$BASE"
cat > "${BASE}/config.json" <<EOF
{
  "pipeline": "Sub #5B paper-faithful NeuS-QA",
  "puls_model": "${PULS_MODEL}",
  "target_identification_model": "${PULS_MODEL}",
  "proposition_model": "OpenGVLab/${PROP_MODEL}",
  "sample_rate": ${SAMPLE_RATE},
  "postprocess": "ffmpeg crop via Manager.crop_video",
  "downstream_vqa": "${QWEN_MODEL}",
  "downstream_vqa_frames": 16,
  "output_dir": "${BASE}"
}
EOF

echo "[sub5b] BASE=$BASE"
echo "[sub5b] starting NSVS shards at $(date -Iseconds)"

pids=()
for i in $(seq 1 "$TOTAL"); do
  gpu=$((i - 1))
  out="${BASE}/shard_${i}"
  if [[ -f "${out}/entries.json" ]] && grep -q "completed nsvs" "${out}/run.log" 2>/dev/null; then
    echo "[sub5b] shard ${i}/${TOTAL} already complete; skipping"
    continue
  fi
  mkdir -p "$out"
  echo "[sub5b] shard ${i}/${TOTAL} on GPU ${gpu} -> ${out}"
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

echo "[sub5b] all launched shards exited at $(date -Iseconds)"
for i in $(seq 1 "$TOTAL"); do
  log="${BASE}/shard_${i}/run.log"
  if [[ ! -f "${BASE}/shard_${i}/entries.json" ]]; then
    echo "[sub5b] ERROR: missing entries.json for shard ${i}" >&2
    exit 1
  fi
  if grep -q "completed nsvs : 0/" "$log" 2>/dev/null; then
    echo "[sub5b] ERROR: shard ${i} completed zero NSVS entries" >&2
    exit 1
  fi
done

MERGED="${BASE}/merged"
POST="${BASE}/postprocess"
ANSWER="${BASE}/answers_qwen25vl7b"
FINAL="${BASE}/submission_sub5b_paper_faithful.json"

python3 scripts/merge_nsvs_shards.py \
  --shard-dirs "${BASE}/shard_1,${BASE}/shard_2,${BASE}/shard_3,${BASE}/shard_4,${BASE}/shard_5,${BASE}/shard_6,${BASE}/shard_7,${BASE}/shard_8" \
  --out-dir "$MERGED"

echo "[sub5b] cropping videos at $(date -Iseconds)"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "${MERGED}/entries.json" \
  --output-dir "$POST" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

if [[ ! -x "${VLLM_VENV}/bin/vllm" ]]; then
  echo "[sub5b] vllm not found at ${VLLM_VENV}; creating isolated vLLM env"
  uv venv --python 3.12 "$VLLM_VENV"
  uv pip install --python "${VLLM_VENV}/bin/python" vllm
fi

echo "[sub5b] starting local Qwen VQA server on GPU ${QWEN_GPU}, port ${QWEN_PORT}"
CUDA_VISIBLE_DEVICES="$QWEN_GPU" "${VLLM_VENV}/bin/vllm" serve "$QWEN_MODEL" \
  --tensor-parallel-size 1 \
  --port "$QWEN_PORT" \
  --trust-remote-code \
  > "${BASE}/vllm_qwen.log" 2>&1 &
server_pid=$!

cleanup() {
  if kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

python3 - <<PY
import time
from openai import OpenAI

client = OpenAI(api_key="EMPTY", base_url="http://localhost:${QWEN_PORT}/v1")
deadline = time.time() + 1800
while time.time() < deadline:
    try:
        client.models.list()
        print("[sub5b] local Qwen server ready")
        raise SystemExit(0)
    except Exception as exc:
        print(f"[sub5b] waiting for Qwen server: {exc!r}")
        time.sleep(20)
raise SystemExit("[sub5b] Qwen server did not become ready")
PY

echo "[sub5b] answering cropped videos at $(date -Iseconds)"
python3 -u scripts/answer_cropped_timelogic_local.py \
  --entries "${POST}/postprocess_entries.json" \
  --output-dir "$ANSWER" \
  --model "$QWEN_MODEL" \
  --api-base "http://localhost:${QWEN_PORT}/v1" \
  --num-frames 16

python3 scripts/build_submission.py \
  --val-annotations "$ANN" \
  --partial "${ANSWER}/submission_partial.json" \
  --output "$FINAL"

echo "[sub5b] wrote $FINAL"
echo "done $(date -Iseconds)" > "${BASE}/DONE"
