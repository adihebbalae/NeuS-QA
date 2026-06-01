#!/usr/bin/env bash
# Start Sub9 PULS v2 TEST pipeline in detached tmux (required for long runs).
#
#   bash scripts/launch_sub9_test_tmux.sh
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
SESSION=${SESSION:-sub9_test}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_test}
LOG="${BASE}/run.log"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[launch-sub9-test] tmux session '$SESSION' already exists."
  echo "  attach:  tmux attach -t $SESSION"
  echo "  tail:    tail -f $LOG"
  exit 0
fi

mkdir -p "$BASE"
extra_env=""
if [[ -f "${BASE}/merged/entries.json" ]] && ! python3 -c "import json; json.load(open('${BASE}/merged/entries.json'))" 2>/dev/null; then
  echo "[launch-sub9-test] removing corrupt ${BASE}/merged/entries.json" >&2
  rm -f "${BASE}/merged/entries.json" "${BASE}/merged/merge_summary.json"
fi
if [[ ! -f "${BASE}/merged/entries.json" ]]; then
  extra_env="FORCE_MERGE=1"
fi

cmd="cd ${REPO} && ${extra_env} SUB9_IN_TMUX=1 bash scripts/run_sub9_pulsv2_test.sh 2>&1 | tee -a ${LOG}"
tmux new-session -d -s "$SESSION" "$cmd"

echo "[launch-sub9-test] started tmux session: $SESSION"
echo "[launch-sub9-test] phase=TEST ann=timelogic_test_data.json (3000 Q)"
echo "[launch-sub9-test] log: $LOG"
echo "[launch-sub9-test] attach: tmux attach -t $SESSION"
echo "[launch-sub9-test] output: ${BASE}/submission_sub9_pulsv2_test.json"
