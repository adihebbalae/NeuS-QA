#!/usr/bin/env bash
# Atemporal-MC prototype: 10 manifest rows × PULS + 4× NSVS per row (~30 min, 1× A5000).
#
# tmux:
#   tmux new-session -d -s atemporal_mc_proto \
#     "bash /home/ah66742/NeuS-QA/scripts/run_atemporal_mc_prototype.sh 2>&1 | tee /home/ah66742/NeuS-QA/diagnostics/atemporal_mc_prototype/runs/run.log"
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
OUT=${OUT:-/home/ah66742/NeuS-QA/diagnostics/atemporal_mc_prototype/runs}
MANIFEST=${MANIFEST:-/home/ah66742/NeuS-QA/diagnostics/atemporal_mc_prototype/manifest.json}
DEVICE=${DEVICE:-0}

cd "$REPO"
source .venv/bin/activate
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

mkdir -p "$OUT"
python3 -u scripts/run_atemporal_mc_prototype.py \
  --manifest "$MANIFEST" \
  --out-dir "$OUT" \
  --device "$DEVICE" \
  --puls-model gpt-4o \
  --sample-rate 3.0 \
  --resume \
  2>&1 | tee -a "$OUT/run.log"
echo "done $(date -Iseconds)" | tee "$OUT/DONE"
