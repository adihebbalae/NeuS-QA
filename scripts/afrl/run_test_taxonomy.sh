#!/usr/bin/env bash
# Test pipeline taxonomy: manifest (test) -> CSV -> category tables -> slide examples.
#
# Resource profile: CPU-only, no GPU; ~3–5s wall time. Loads postprocess JSON (~150MB)
# into RAM once per Python process. Safe to run alongside tmux GPU jobs, but avoid
# re-running in a tight loop while sub7b_val / other heavy pipelines are starved for I/O.
#
# Preflight: SKIP_PREFLIGHT=1 to skip. ABORT_ON_HEAVY_LOAD=1 to exit if load > 48.
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
AFRL_ROOT=${AFRL_ROOT:-${REPO}/reports/afrl}

cd "$REPO"
# shellcheck source=/dev/null
source "${REPO}/.venv/bin/activate"

if [[ "${SKIP_PREFLIGHT:-}" != "1" ]]; then
  load_1m=$(awk '{print int($1)}' /proc/loadavg)
  mem_avail_kb=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  mem_avail_gi=$((mem_avail_kb / 1024 / 1024))
  gpu_note=""
  if command -v nvidia-smi >/dev/null 2>&1; then
    gpu_note=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null \
      | awk '{if ($1+0>=80) hot++} END {if (hot) print " GPUs>=80% util on " hot " device(s)"}')
  fi
  if pgrep -f 'outputs/sub7b_val.*run_timelogic' >/dev/null 2>&1; then
    echo "[run_test_taxonomy] NOTE: sub7b_val NeuS-QA shards are running (GPU/API heavy)." >&2
  fi
  echo "[run_test_taxonomy] preflight: load_1m=${load_1m} mem_available~${mem_avail_gi}GiB${gpu_note}" >&2
  if [[ -n "${gpu_note}" ]]; then
    echo "[run_test_taxonomy] This script is lightweight; GPU contention is from other jobs." >&2
  fi
  if [[ "${ABORT_ON_HEAVY_LOAD:-}" == "1" ]] && [[ "${load_1m}" -gt 48 ]]; then
    echo "[run_test_taxonomy] ABORT: load_1m=${load_1m} > 48 (set SKIP_PREFLIGHT=1 to override)." >&2
    exit 2
  fi
  if [[ "${mem_avail_gi}" -lt 8 ]]; then
    echo "[run_test_taxonomy] WARNING: <8GiB MemAvailable; postprocess JSON load may spike RAM." >&2
  fi
fi

echo "[run_test_taxonomy] manifest (test only) at $(date -Iseconds)"
python3 scripts/afrl/build_enriched_manifest.py \
  --split test \
  --out "${AFRL_ROOT}/enriched_manifest_test.json"

echo "[run_test_taxonomy] taxonomy CSV at $(date -Iseconds)"
python3 scripts/afrl/build_test_pipeline_taxonomy.py \
  --manifest "${AFRL_ROOT}/enriched_manifest_test.json" \
  --out-csv "${AFRL_ROOT}/test_pipeline_taxonomy.csv" \
  --out-summary "${AFRL_ROOT}/test_pipeline_summary.json"

echo "[run_test_taxonomy] category tables at $(date -Iseconds)"
python3 scripts/afrl/build_category_tables.py \
  --taxonomy-csv "${AFRL_ROOT}/test_pipeline_taxonomy.csv" \
  --out "${AFRL_ROOT}/accuracy_by_category.csv"

echo "[run_test_taxonomy] pipeline examples at $(date -Iseconds)"
python3 scripts/afrl/select_pipeline_examples.py \
  --taxonomy-csv "${AFRL_ROOT}/test_pipeline_taxonomy.csv" \
  --out "${AFRL_ROOT}/pipeline_examples.json" \
  --per-stage 4

echo "[run_test_taxonomy] PULS propagation crosstab at $(date -Iseconds)"
python3 scripts/afrl/build_puls_propagation_table.py \
  --out-csv "${AFRL_ROOT}/test_puls_shard_join.csv" \
  --out-json "${AFRL_ROOT}/puls_propagation_crosstab.json"

echo "[run_test_taxonomy] done at $(date -Iseconds)"
python3 -c "
import json, csv
from collections import Counter
root = '${AFRL_ROOT}'
summary = json.load(open(root + '/test_pipeline_summary.json'))
rows = list(csv.DictReader(open(root + '/test_pipeline_taxonomy.csv')))
print('rows', len(rows))
print('stages', summary['pipeline_stage_counts'])
print('disagree', summary['disagree_sub7b_baseline'])
examples = json.load(open(root + '/pipeline_examples.json'))
print('examples', len(examples), Counter(e['pipeline_stage'] for e in examples))
"
