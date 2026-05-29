#!/usr/bin/env bash
# Sub7b — end-to-end honest test repair after Sub7a discard.
#
#   failed NSVS rerun (790 qids) -> merge -> crop -> VQA on reruns -> union -> submission_sub7b.json
#
# Idempotent: skips phases already complete. Safe to re-run after interrupt.
#
# Launch in tmux (>5 min; see .cursor/rules/workflow.md):
#   tmux new-session -d -s sub7b \
#     'cd ~/NeuS-QA && bash scripts/run_sub7b.sh 2>&1 | tee /mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/sub7b_pipeline.log'
#
# Phases (PHASE=auto|rerun|finish):
#   auto   — rerun if needed, then finish (default)
#   rerun  — NSVS rerun + merge only
#   finish — crop + VQA + union only (SKIP_RERUN=1 implied)
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful}
FINAL=${FINAL:-${BASE}/submission_sub7b.json}
WORK=${WORK:-${BASE}/sub7b_rerun_vqa}
PHASE=${PHASE:-auto}
RERUN_LOG=${BASE}/nsvs_rerun/run.log

cd "$REPO"

if [[ -f "$FINAL" ]] && [[ "${FORCE:-}" != "1" ]]; then
  echo "[sub7b] complete: $FINAL"
  exit 0
fi

mkdir -p "$WORK"
exec 9>"${WORK}/.pipeline.lock"
if ! flock -n 9; then
  echo "[sub7b] another step holds ${WORK}/.pipeline.lock (finish or rerun may be running)"
  exit 0
fi

rerun_done() {
  [[ -f "$RERUN_LOG" ]] && grep -q '^\[sub7-rerun\] done ' "$RERUN_LOG"
}

need_rerun() {
  if [[ "${SKIP_RERUN:-}" == "1" ]] || [[ "$PHASE" == "finish" ]]; then
    return 1
  fi
  if [[ "$PHASE" == "rerun" ]]; then
    return 0
  fi
  # auto: rerun unless already finished
  ! rerun_done
}

run_rerun() {
  echo "[sub7b] phase: NSVS rerun at $(date -Iseconds)"
  AUTO_FINISH_SUB7B=0 bash "${REPO}/scripts/run_sub7_rerun_failed_nsvs.sh"
}

run_finish() {
  echo "[sub7b] phase: finish (crop + VQA + union) at $(date -Iseconds)"
  SKIP_NSVS_MERGE=1 BASE="$BASE" bash "${REPO}/scripts/finish_sub7b_rerun.sh"
}

case "$PHASE" in
  rerun)
    run_rerun
    ;;
  finish)
    run_finish
    ;;
  auto)
    if need_rerun; then
      run_rerun
    else
      echo "[sub7b] NSVS rerun already done; skipping to finish"
    fi
    run_finish
    ;;
  *)
    echo "FATAL: unknown PHASE=$PHASE (use auto|rerun|finish)" >&2
    exit 1
    ;;
esac

if [[ ! -f "$FINAL" ]]; then
  echo "[sub7b] FATAL: expected $FINAL after pipeline" >&2
  exit 1
fi

echo "done $(date -Iseconds)" > "${BASE}/sub7b_DONE"
echo "[sub7b] pipeline complete -> $FINAL"
