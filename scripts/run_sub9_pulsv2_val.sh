#!/usr/bin/env bash
# ⛔ VAL — FROZEN. Use scripts/run_sub9_pulsv2_test.sh for deadline work.
set -euo pipefail

if [[ -z "${ALLOW_VAL:-}" ]]; then
  echo "FATAL: run_sub9_pulsv2_val.sh is VAL-only and FROZEN (2026-05-29)." >&2
  echo "  Run: bash scripts/launch_sub9_test_tmux.sh" >&2
  echo "  Policy: .cursor/rules/eval-phase-policy.md" >&2
  exit 99
fi

REPO=${REPO:-/home/ah66742/NeuS-QA}
export REPO
export SUB9_PHASE=val
export SUB9_LAUNCH_SCRIPT=launch_sub9_tmux.sh
export SUB9_GPU_MAP=val6
export SUB9_REPORT_FILE=sub9_val_report.md
export VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos}
export ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
export BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_val}
export TOTAL=${TOTAL:-6}
export SPEND_CAP_USD=${SPEND_CAP_USD:-60}
export FINAL=${FINAL:-${BASE}/submission_sub9_pulsv2_val.json}

exec bash "${REPO}/scripts/run_sub9_pulsv2_driver.sh"
