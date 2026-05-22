#!/usr/bin/env bash
# Run after Sub #5B GPT VQA finishes (BASE/DONE exists).
#
# Usage:
#   bash scripts/post_sub5b_checklist.sh
#   SCORE_B=51.2 bash scripts/post_sub5b_checklist.sh   # after EvalAI upload
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2}
SUB1=${SUB1:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json}
SUB5B=${SUB5B:-${BASE}/submission_sub5b_paper_faithful_gpt52.json}
ANN=${ANN:-/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json}
OUT=${OUT:-/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2}
EVALAI_URL="https://eval.ai/web/challenges/challenge-page/2690/overview"

cd "$REPO"
source .venv/bin/activate

fail=0
check() {
  if [[ "$1" == ok ]]; then
    echo "  [ok] $2"
  else
    echo "  [!!] $2"
    fail=1
  fi
}

echo "=== Post Sub #5B checklist ==="
echo "BASE=$BASE"
echo

# --- 1. Completion gates ---
echo "## 1. Artifacts"
if [[ -f "${BASE}/DONE" ]]; then
  check ok "DONE marker present"
else
  check fail "DONE marker missing — VQA may still be running (tmux: sub5b_gpt_vqa)"
fi

for path in \
  "${BASE}/merged/entries.json" \
  "${BASE}/postprocess/postprocess_entries.json" \
  "${BASE}/answers_gpt_5_2/submission_partial.json" \
  "$SUB5B"; do
  if [[ -f "$path" ]]; then
    check ok "$path"
  else
    check fail "missing $path"
  fi
done

if [[ -f "$SUB5B" ]]; then
  n=$(python3 -c "import json; print(len(json.load(open('$SUB5B'))))")
  if [[ "$n" == "2000" ]]; then
    check ok "submission row count = 2000"
  else
    check fail "submission row count = $n (expected 2000)"
  fi
fi

# --- 2. Offline diagnostics ---
echo
echo "## 2. Offline diagnostics"

python3 scripts/nsvs_quality_probe.py \
  --output-dir "$BASE" \
  --label "Sub #5B fix2 full merged" \
  --report "${BASE}/nsvs_quality_report_full.md"

check ok "NSVS quality report → ${BASE}/nsvs_quality_report_full.md"

if [[ -f "$SUB5B" ]]; then
  python3 scripts/compare_5b_vs_sub1.py \
    --sub5b "$SUB5B" \
    --entries-sub5b "${BASE}/merged/entries.json" \
    --score-sub5b "${SCORE_B:-}" \
    --out-dir "$OUT"

  check ok "compare_5b_vs_sub1 → $OUT/"
fi

# --- 3. EvalAI upload (manual) ---
echo
echo "## 3. EvalAI val upload (manual)"
echo "  1. Open: $EVALAI_URL"
echo "  2. Validation phase → Submit"
echo "  3. Upload: $SUB5B"
echo "  4. Note AvgAcc, then rerun:"
echo "       SCORE_B=<pct> bash scripts/post_sub5b_checklist.sh"
echo

# --- 4. Interpret score ---
echo "## 4. Score interpretation"
echo "  Sub #1 baseline: 50.5%"
echo "  Sub #2 NSVS (contaminated FOI): 48.75%"
echo "  Sub #5B config: gpt-4o PULS/target_id + InternVL2-8B NSVS @ 3fps + ffmpeg crop + gpt-5.2 VQA"
echo
echo "  ≥ 50.5%  → fixed retrieval helps; tune hybrid routing Sub #5B + Sub #1"
echo "  48–50.5% → better than Sub #2; GPT answerer may mask retrieval harm"
echo "  ≈ 49%    → NSVS net-negative on TimeLogic even with clean FOI"
echo

# --- 5. Follow-ups ---
echo "## 5. Follow-ups after score lands"
echo "  [ ] Update RESULTS.md with Sub #5B score + config note (GPT VQA, not Qwen)"
echo "  [ ] Update sessions/2026-05-22.md + sessions/INDEX.md"
echo "  [ ] Spot-check disagreements: $OUT/disagreements.csv"
echo "  [ ] If ≥ 50.5%: plan test-phase run with same stack (test data: \$TIMELOGIC_ROOT/annotations/timelogic_test_data.json)"
echo "  [ ] If < 50.5%: pivot to full-video baseline sweeps (frames, self-consistency)"
echo

if [[ "$fail" -ne 0 ]]; then
  echo "Checklist incomplete — fix blockers above and rerun."
  exit 1
fi

echo "Checklist complete (pending EvalAI score if SCORE_B unset)."
