#!/usr/bin/env bash
# Resume Sub #5B NSVS gpt-5.2 subsample after intersection_with_gaps fix.
# Re-runs failed NSVS rows (if needed), merges, then crop -> VQA -> InternVL replay -> report.
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
BASELINE_ENTRIES=${BASELINE_ENTRIES:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_subsample}
PULS_MODEL=${PULS_MODEL:-gpt-4o}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}
INTERNVL_DEVICE=${INTERNVL_DEVICE:-0}

cd "$REPO"
source .venv/bin/activate

log() { echo "[resume $(date -Iseconds)] $*"; }

# Tee to LOG but propagate the command's exit code, not tee's (pipefail pitfall).
run_logged() {
  local log_path="$1"
  shift
  mkdir -p "$(dirname "$log_path")"
  "$@" 2>&1 | tee "$log_path"
  local cmd_status=${PIPESTATUS[0]}
  if [[ "$cmd_status" -ne 0 ]]; then
    echo "[resume] command failed (exit $cmd_status); see $log_path" >&2
    exit "$cmd_status"
  fi
}

log "extracting failed NSVS qids from diag.json"
python3 - <<'PY' "$BASE"
import json
import sys
from pathlib import Path

base = Path(sys.argv[1])
diag = json.loads((base / "nsvs/diag.json").read_text())
failed = [
    d["question_id"]
    for d in diag
    if "error" in str(d.get("step_status", {}).get("nsvs", "")).lower()
]
out = base / "nsvs_retry_qids.json"
out.write_text(json.dumps(failed, indent=2) + "\n", encoding="utf-8")
print(f"failed_qids={len(failed)} -> {out}")
PY

FAILED_N=$(python3 -c "import json; print(len(json.load(open('$BASE/nsvs_retry_qids.json'))))")
RETRY_DONE=$(python3 - <<PY
import json
from pathlib import Path
p = Path("$BASE/nsvs_retry/entries.json")
print(len(json.loads(p.read_text())) if p.exists() else 0)
PY
)

if [[ "$FAILED_N" -gt 0 && "$RETRY_DONE" -lt "$FAILED_N" ]]; then
  log "re-running NSVS for $FAILED_N failed qids (cache reused)"
  run_logged "$BASE/nsvs_retry/run.log" \
    python3 -u scripts/run_timelogic.py \
      --video-root "$VIDEO_ROOT" \
      --ann-path "$ANN" \
      --output-dir "$BASE/nsvs_retry" \
      --qid-file "$BASE/nsvs_retry_qids.json" \
      --nsvs-backend gpt5.2 \
      --nsvs-cache-dir "$BASE/nsvs/nsvs_detection_cache" \
      --sample-rate "$SAMPLE_RATE" \
      --puls-model "$PULS_MODEL" \
      --reuse-from "$BASELINE_ENTRIES" \
      --env-file "$HOME/.env"
elif [[ "$FAILED_N" -gt 0 ]]; then
  log "nsvs_retry already complete ($RETRY_DONE/$FAILED_N); skipping re-run"
else
  log "no failed NSVS qids; skipping retry"
fi

exec bash "$REPO/scripts/finish_sub5b_nsvs_gpt52_subsample.sh"
