#!/usr/bin/env bash
# Wait for all NSVS shards, then run Sub #2 finishing. Intended for tmux.
set -euo pipefail

BASE=/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2
TOTAL=8
POLL_SEC=120

while true; do
  ready=0
  for i in $(seq 1 "$TOTAL"); do
    f="${BASE}/shard_${i}/entries.json"
    log="${BASE}/shard_${i}/run.log"
    if [[ -f "$f" ]] && grep -q "completed nsvs" "$log" 2>/dev/null; then
      # Require at least one successful NSVS entry; "completed nsvs : 0/N"
      # means the shard failed but still exited.
      if ! grep -q "completed nsvs : 0/" "$log"; then
        ready=$((ready + 1))
      fi
    fi
  done
  echo "[wait] shards ready: $ready/$TOTAL ($(date -Iseconds))"
  if [[ "$ready" -eq "$TOTAL" ]]; then
    break
  fi
  sleep "$POLL_SEC"
done

bash /home/ah66742/NeuS-QA/scripts/finish_sub2.sh
echo "[wait] Sub #2 finish script done"
