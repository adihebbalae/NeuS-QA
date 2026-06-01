#!/usr/bin/env bash
# Finish Sub #5B subsample from merge onward (after NSVS + retry are done).
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub5b_subsample}
SAMPLE_RATE=${SAMPLE_RATE:-3.0}
INTERNVL_DEVICE=${INTERNVL_DEVICE:-0}

cd "$REPO"
source .venv/bin/activate

log() { echo "[finish $(date -Iseconds)] $*"; }

# Run CMD, tee to LOG. With pipefail, check the command's exit code — not tee's.
run_logged() {
  local log_path="$1"
  shift
  mkdir -p "$(dirname "$log_path")"
  "$@" 2>&1 | tee "$log_path"
  local cmd_status=${PIPESTATUS[0]}
  if [[ "$cmd_status" -ne 0 ]]; then
    echo "[finish] command failed (exit $cmd_status); see $log_path" >&2
    exit "$cmd_status"
  fi
}

merge_nsvs_results() {
  python3 - <<'PY' "$BASE"
import json
import shutil
import sys
from pathlib import Path

base = Path(sys.argv[1])
main_dir = base / "nsvs"
retry_dir = base / "nsvs_retry"

if not (main_dir / "entries.json").exists():
    raise SystemExit(f"missing {main_dir / 'entries.json'}")
if not (retry_dir / "entries.json").exists():
    raise SystemExit(f"missing {retry_dir / 'entries.json'} — run NSVS retry first")

main_entries = json.loads((main_dir / "entries.json").read_text())
retry_entries = json.loads((retry_dir / "entries.json").read_text())
by_qid = {str(e["metadata"]["question_id"]): e for e in main_entries}
for entry in retry_entries:
    by_qid[str(entry["metadata"]["question_id"])] = entry

qids = json.loads((base / "subsample_qids.json").read_text())
merged = [by_qid[str(q)] for q in qids if str(q) in by_qid]
(main_dir / "entries.json").write_text(json.dumps(merged, indent=2, default=str) + "\n", encoding="utf-8")

main_diag = json.loads((main_dir / "diag.json").read_text())
retry_diag = json.loads((retry_dir / "diag.json").read_text())
diag_by_qid = {str(d["question_id"]): d for d in main_diag}
for row in retry_diag:
    diag_by_qid[str(row["question_id"])] = row
merged_diag = [diag_by_qid[str(q)] for q in qids if str(q) in diag_by_qid]
(main_dir / "diag.json").write_text(json.dumps(merged_diag, indent=2, default=str) + "\n", encoding="utf-8")

pe = main_dir / "per_entry"
pe.mkdir(parents=True, exist_ok=True)
for path in (retry_dir / "per_entry").glob("*.json"):
    shutil.copy2(path, pe / path.name)

retry_cost = retry_dir / "api_cost.json"
if retry_cost.exists():
    main_cost_path = main_dir / "api_cost.json"
    main_cost = json.loads(main_cost_path.read_text()) if main_cost_path.exists() else {}
    retry_cost_data = json.loads(retry_cost.read_text())
    total = round(float(main_cost.get("estimated_total_usd", 0)) + float(retry_cost_data.get("estimated_total_usd", 0)), 4)
    calls = int(main_cost.get("calls", 0)) + int(retry_cost_data.get("calls", 0))
    main_cost["estimated_total_usd"] = total
    main_cost["calls"] = calls
    main_cost["metered_calls"] = calls
    main_cost["retry_usd"] = retry_cost_data.get("estimated_total_usd")
    main_cost["entries"] = len(merged)
    main_cost_path.write_text(json.dumps(main_cost, indent=2) + "\n", encoding="utf-8")

ok = sum(1 for d in merged_diag if d.get("step_status", {}).get("nsvs") == "ok")
print(f"merged_entries={len(merged)} nsvs_ok={ok}/{len(merged_diag)}")
PY
}

log "merging nsvs_retry into nsvs/"
merge_nsvs_results

log "cropping videos"
mkdir -p "$BASE/postprocess"
python3 -u scripts/crop_timelogic_entries.py \
  --entries "$BASE/nsvs/entries.json" \
  --output-dir "$BASE/postprocess" \
  --video-root "$VIDEO_ROOT" \
  --ann-path "$ANN"

log "gpt-5.2 VQA on cropped clips"
run_logged "$BASE/answers/run.log" \
  python3 -u scripts/answer_cropped_entries.py \
    --entries "$BASE/postprocess/postprocess_entries.json" \
    --output-dir "$BASE/answers" \
    --model gpt-5.2 \
    --num-frames 16 \
    --image-detail low \
    --env-file "$HOME/.env"

python3 scripts/build_submission.py \
  --val-annotations "$ANN" \
  --partial "$BASE/answers/submission_partial.json" \
  --output "$BASE/submission_partial_50q.json"

log "replaying InternVL detections for head-to-head"
run_logged "$BASE/internvl_replay/run.log" \
  env CUDA_VISIBLE_DEVICES="$INTERNVL_DEVICE" \
  python3 -u scripts/replay_internvl_nsvs_detections.py \
    --entries "$BASE/nsvs/entries.json" \
    --output-dir "$BASE/internvl_replay" \
    --sample-rate "$SAMPLE_RATE" \
    --device 0 \
    --cache-dir "$BASE/nsvs/nsvs_detection_cache"

log "writing ablation report"
python3 scripts/report_nsvs_backend_ablation.py --base "$BASE"

log "done" | tee "$BASE/DONE"
log "report: $BASE/report/ablation_summary.md"
