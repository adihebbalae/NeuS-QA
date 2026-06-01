#!/usr/bin/env bash
# ⛔ VAL — FROZEN 2026-05-29. Refuses unless ALLOW_VAL=1. See .cursor/rules/eval-phase-policy.md
# Start Sub9 val pipeline in a detached tmux session (required for long runs).
#
#   bash scripts/launch_sub9_tmux.sh
#
# Do NOT use nohup — laptop sleep kills the process tree; tmux keeps the server job alive.
set -euo pipefail

if [[ -z "${ALLOW_VAL:-}" ]]; then
  echo "FATAL: launch_sub9_tmux.sh starts a VAL job (FROZEN). Use TEST pipelines only." >&2
  echo "  See .cursor/rules/eval-phase-policy.md" >&2
  exit 99
fi

REPO=${REPO:-/home/ah66742/NeuS-QA}
SESSION=${SESSION:-sub9_val}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_val}
LOG="${BASE}/run.log"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[launch-sub9] tmux session '$SESSION' already exists."
  echo "  attach:  tmux attach -t $SESSION"
  echo "  tail:    tail -f $LOG"
  exit 0
fi

mkdir -p "$BASE"
extra_env=""
if [[ -f "${BASE}/merged/entries.json" ]] && ! python3 -c "import json; json.load(open('${BASE}/merged/entries.json'))" 2>/dev/null; then
  echo "[launch-sub9] removing corrupt ${BASE}/merged/entries.json" >&2
  rm -f "${BASE}/merged/entries.json" "${BASE}/merged/merge_summary.json"
fi
if [[ ! -f "${BASE}/merged/entries.json" ]]; then
  extra_env="FORCE_MERGE=1"
fi
cmd="cd ${REPO} && ${extra_env} SUB9_IN_TMUX=1 bash scripts/run_sub9_pulsv2_val.sh 2>&1 | tee -a ${LOG}"
tmux new-session -d -s "$SESSION" "$cmd"

echo "[launch-sub9] started tmux session: $SESSION"
echo "[launch-sub9] log: $LOG"
echo "[launch-sub9] attach: tmux attach -t $SESSION"
echo "[launch-sub9] ping when DONE exists or you see '[sub9] wrote' in the log."
