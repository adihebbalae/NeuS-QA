#!/usr/bin/env bash
# Sub #9 — PULS v2 full TEST pass (Examples 13–16). EvalAI test phase submission.
#
#   bash scripts/launch_sub9_test_tmux.sh
#
# Preflight: HEAD=10 bash scripts/run_sub9_pulsv2_test.sh
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
export REPO
export SUB9_PHASE=test
export SUB9_LAUNCH_SCRIPT=launch_sub9_test_tmux.sh
export SUB9_GPU_MAP=test8
export SUB9_REPORT_FILE=sub9_test_report.md
export VIDEO_ROOT=${VIDEO_ROOT:-/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json}
export ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json}
export BASE=${BASE:-/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_test}
export TOTAL=${TOTAL:-8}
export SPEND_CAP_USD=${SPEND_CAP_USD:-120}
export FINAL=${FINAL:-${BASE}/submission_sub9_pulsv2_test.json}

# shellcheck source=scripts/lib/require_test_phase.sh
source "${REPO}/scripts/lib/require_test_phase.sh"
REQUIRE_TEST_LABEL=run_sub9_pulsv2_test
require_test_phase "$ANN" "$VIDEO_ROOT" "$BASE"

exec bash "${REPO}/scripts/run_sub9_pulsv2_driver.sh"
