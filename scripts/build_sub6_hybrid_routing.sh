#!/usr/bin/env bash
# Sub #6: hybrid val routing — Sub #1 baseline + Sub #5B (53.35%).
#
# Builds two post-process candidates (no API/GPU reruns):
#   6A: foi_confidence_proxy (same gate as old Sub #3A, but sub2=Sub #5B)
#   6B: foi_clean_proxy (confidence + no suspicious FOI flags)
set -euo pipefail

REPO=${REPO:-/home/ah66742/NeuS-QA}
ANN=${ANN:-/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json}
SUB1=${SUB1:-/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json}
SUB5B=${SUB5B:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/submission_sub5b_paper_faithful_gpt52.json}
ENTRIES5B=${ENTRIES5B:-/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json}
OUT=${OUT:-/mnt/Data/ah66742/timelogic/outputs/sub6_hybrid_routing}

cd "$REPO"
source .venv/bin/activate

mkdir -p "$OUT"

echo "[sub6] Sub #1=$SUB1"
echo "[sub6] Sub #5B=$SUB5B"
echo "[sub6] entries=$ENTRIES5B"

python3 scripts/build_routed_submission.py \
  --annotations "$ANN" \
  --sub1 "$SUB1" \
  --sub2 "$SUB5B" \
  --entries2 "$ENTRIES5B" \
  --variant foi_confidence_proxy \
  --output "${OUT}/submission_sub6a_foi_proxy.json" \
  --summary "${OUT}/summary_sub6a.json" \
  --details "${OUT}/details_sub6a.csv"

python3 scripts/build_routed_submission.py \
  --annotations "$ANN" \
  --sub1 "$SUB1" \
  --sub2 "$SUB5B" \
  --entries2 "$ENTRIES5B" \
  --variant foi_clean_proxy \
  --output "${OUT}/submission_sub6b_foi_clean.json" \
  --summary "${OUT}/summary_sub6b.json" \
  --details "${OUT}/details_sub6b.csv"

echo
echo "[sub6] wrote:"
echo "  ${OUT}/submission_sub6a_foi_proxy.json"
echo "  ${OUT}/submission_sub6b_foi_clean.json"
echo "[sub6] Upload both to EvalAI val; pick the higher AvgAcc for test if it beats 53.35%."
