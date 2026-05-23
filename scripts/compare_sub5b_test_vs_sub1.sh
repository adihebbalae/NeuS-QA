#!/usr/bin/env bash
# Compare test Sub #5B vs test Sub #1 (offline disagreement diagnostic).
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
SUB1=${SUB1:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test/submission.json}
SUB5B=${SUB5B:-/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps/submission_sub5b_test_gpt52.json}
ENTRIES5B=${ENTRIES5B:-/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps/merged/entries.json}
ENTRIES1=${ENTRIES1:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test/entries.json}
OUT=${OUT:-/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub1_vs_sub5b_test}

cd "$REPO"
source .venv/bin/activate

if [[ ! -f "$SUB1" ]]; then
  echo "Missing test Sub #1 submission: $SUB1" >&2
  echo "Run: bash scripts/run_sub1_test.sh" >&2
  exit 1
fi
if [[ ! -f "$SUB5B" ]]; then
  echo "Missing test Sub #5B submission: $SUB5B" >&2
  exit 1
fi

python3 scripts/compare_submissions.py \
  --sub-a "$SUB1" \
  --sub-b "$SUB5B" \
  --entries-a "$ENTRIES1" \
  --entries-b "$ENTRIES5B" \
  --name-a sub1_baseline_test \
  --name-b sub5b_test \
  --eval-n 3000 \
  --out-dir "$OUT"

echo "Wrote diagnostics to $OUT"
