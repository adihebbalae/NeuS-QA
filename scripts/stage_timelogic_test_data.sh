#!/usr/bin/env bash
# Stage TimeLogic test split: annotations JSON + test_videos.zip + unzip + sanity checks.
#
# Test zip is ~22.7 GiB. Run the full script in tmux for the download portion:
#   tmux new-session -d -s timelogic_test_dl \
#     "bash /home/ah66742/NeuS-QA/scripts/stage_timelogic_test_data.sh 2>&1 | tee /mnt/Data/ah66742/timelogic/logs/stage_test_data.log"
set -euo pipefail

ROOT=${TIMELOGIC_ROOT:-/mnt/Data/ah66742/timelogic}
RAW="${ROOT}/raw"
ANN="${ROOT}/annotations"
VIDEOS="${ROOT}/videos/test"
LOGS="${ROOT}/logs"
TEST_JSON_URL="https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/timelogic_test_data.json"
TEST_ZIP_URL="https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/test_videos.zip"

mkdir -p "$RAW" "$ANN" "$VIDEOS" "$LOGS"

echo "[stage-test] ROOT=$ROOT"
echo "[stage-test] step 1/4: download annotations ($(date -Iseconds))"

curl -L --fail --retry 5 --retry-delay 10 \
  -o "${ANN}/timelogic_test_data.json" \
  "$TEST_JSON_URL"

python3 << 'PY'
import json
from collections import Counter
from pathlib import Path

ann = Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json")
data = json.loads(ann.read_text())
modes = Counter(d.get("mode") for d in data)
vids = {d.get("video_id") for d in data}
print(f"[stage-test] annotations: {len(data)} rows")
print(f"[stage-test] modes: {dict(modes)}")
print(f"[stage-test] unique video_id: {len(vids)}")
if len(data) != 3000:
    print(f"[stage-test] WARNING: expected 3000 test rows, got {len(data)}")
PY

echo "[stage-test] step 2/4: download test_videos.zip ($(date -Iseconds))"

if [[ -f "${RAW}/test_videos.zip" ]]; then
  have=$(stat -c%s "${RAW}/test_videos.zip")
  echo "[stage-test] existing zip size: $have bytes (will resume if incomplete)"
fi

curl -L --fail --retry 5 --retry-delay 10 --continue-at - \
  -o "${RAW}/test_videos.zip" \
  "$TEST_ZIP_URL"

echo "[stage-test] zip size: $(stat -c%s "${RAW}/test_videos.zip") bytes"

echo "[stage-test] step 3/4: unzip to ${VIDEOS} ($(date -Iseconds))"
unzip -q -o "${RAW}/test_videos.zip" -d "${VIDEOS}"

echo "[stage-test] step 4/4: integrity checks ($(date -Iseconds))"

python3 << 'PY'
import json
from pathlib import Path

root = Path("/mnt/Data/ah66742/timelogic")
ann = json.loads((root / "annotations/timelogic_test_data.json").read_text())
video_root = root / "videos/test"

mp4s = list(video_root.rglob("*.mp4"))
mp4_names = {p.name for p in mp4s}
needed = {d["video_id"] for d in ann}
missing = sorted(v for v in needed if v not in mp4_names)

print(f"[stage-test] mp4 files on disk: {len(mp4s)}")
print(f"[stage-test] unique video_id in ann: {len(needed)}")
print(f"[stage-test] missing videos for ann: {len(missing)}")
if missing[:5]:
    print(f"[stage-test] missing sample: {missing[:5]}")
PY

echo "done $(date -Iseconds)" > "${ROOT}/TEST_DATA_STAGED"
echo "[stage-test] wrote marker ${ROOT}/TEST_DATA_STAGED"
