#!/usr/bin/env bash
# Poll for Sub #5B DONE, then run all post-score diagnostics automatically.
#
# Safe alongside sub5b_gpt_vqa: only reads submission after VQA writes DONE.
# Launch before stepping away:
#   tmux new-session -d -s sub5b_autofollow \
#     "bash /home/ah66742/NeuS-QA/scripts/wait_and_post_sub5b.sh 2>&1 | tee /mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/autofollow.log"
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2}
SUB1=${SUB1:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json}
SUB5B=${SUB5B:-${BASE}/submission_sub5b_paper_faithful_gpt52.json}
OUT=${OUT:-/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2}
POLL=${POLL:-30}

echo "[autofollow] waiting for ${BASE}/DONE (poll ${POLL}s) ..."
while [[ ! -f "${BASE}/DONE" ]]; do
  if tmux has-session -t sub5b_gpt_vqa 2>/dev/null; then
    progress=$(grep -c '^\[answer ' "${BASE}/resume_gpt_vqa_tmux.log" 2>/dev/null || echo "?")
    echo "[autofollow] $(date -Iseconds) sub5b_gpt_vqa still running (~${progress}/1983 logged)"
  else
    echo "[autofollow] $(date -Iseconds) sub5b_gpt_vqa tmux gone; still no DONE — check logs"
  fi
  sleep "$POLL"
done

echo "[autofollow] DONE found at $(date -Iseconds)"
cd "$REPO"
source .venv/bin/activate

bash scripts/post_sub5b_checklist.sh

python3 scripts/compare_submissions.py \
  --sub-a "$SUB1" \
  --sub-b "$SUB5B" \
  --entries-a "/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/entries.json" \
  --entries-b "${BASE}/merged/entries.json" \
  --name-a sub1_baseline \
  --name-b sub5b_fix2_gpt52 \
  --score-a 50.5 \
  --score-b "${SCORE_B:-}" \
  --eval-n 2000 \
  --out-dir "$OUT"

echo "[autofollow] complete at $(date -Iseconds)"
echo "NEXT: upload $SUB5B to EvalAI val, then SCORE_B=<pct> bash scripts/post_sub5b_checklist.sh"
echo "      operator buckets: $OUT/summary.json → buckets.by_operator_guess"
