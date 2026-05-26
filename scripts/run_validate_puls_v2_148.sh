#!/usr/bin/env bash
# Validate PULS v2 on 94+54 Diagnostic-2 target rows (148 Q).
set -euo pipefail
REPO=${REPO:-/home/ah66742/NeuS-QA}
OUT=${OUT:-/mnt/Data/ah66742/timelogic/outputs/puls_v2_validation_148}
cd "$REPO"
source .venv/bin/activate
python3 -u scripts/validate_puls_v2_target_slice.py \
  --out-dir "$OUT" \
  --puls-model gpt-4o \
  --resume \
  2>&1 | tee "$OUT/run.log"
echo "done $(date -Iseconds)" > "$OUT/DONE"
