#!/usr/bin/env bash
# Compare fixed Sub #5B against Sub #1 with retrieval-quality buckets.
#
# Buckets (see scripts/compare_submissions.py):
#   agree_with_sub_a           — same answer as Sub #1
#   disagree_foi_clean         — different answer, NSVS FOI looks usable
#   disagree_foi_suspicious    — different answer, FOI/indices look broken
#
# Run after Sub #5B finishes (BASE/DONE below).
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2}
SUB1=${SUB1:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json}
SUB5B=${SUB5B:-${BASE}/submission_sub5b_paper_faithful_gpt52.json}
ENTRIES5B=${ENTRIES5B:-${BASE}/merged/entries.json}
OUT=${OUT:-/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2}

cd "$REPO"
source .venv/bin/activate

if [[ ! -f "$SUB5B" ]]; then
  echo "Missing Sub #5B submission: $SUB5B" >&2
  exit 1
fi

python3 scripts/compare_submissions.py \
  --sub-a "$SUB1" \
  --sub-b "$SUB5B" \
  --entries-a "/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/entries.json" \
  --entries-b "$ENTRIES5B" \
  --name-a sub1_baseline \
  --name-b sub5b_paper_faithful_fix2 \
  --score-a 50.5 \
  --score-b "${SCORE_B:-}" \
  --eval-n 2000 \
  --out-dir "$OUT"
