# Diagnostics (tracked copies)

Sub #1 vs Sub #5B disagreement analysis and human failure-audit packets. Canonical working copies also live on disk at `/mnt/Data/ah66742/timelogic/outputs/diagnostics/` (mirrored under `/home/ah66742/timelogic-data/outputs/diagnostics/`).

## Sub #1 vs Sub #5B comparison

**Regenerate:**

```bash
cd /home/ah66742/NeuS-QA
SCORE_B=53.35 bash scripts/compare_sub5b_vs_sub1.sh
# writes to timelogic-data by default; copy summary + CSVs here after refresh
```

Wraps `scripts/compare_submissions.py`.

| Artifact | Repo path | Description |
| --- | --- | --- |
| Summary + bucket breakdowns | [sub1_vs_sub5b_fix2/summary.json](sub1_vs_sub5b_fix2/summary.json) | Agreement counts, operator/source/duration/FOI buckets, top answer-pair flips |
| All 464 disagreement rows | [sub1_vs_sub5b_fix2/disagreements.csv](sub1_vs_sub5b_fix2/disagreements.csv) | Per-row answers, FOI status, retrieval-quality bucket |
| Retrieval quality slice | [sub1_vs_sub5b_fix2/retrieval_quality_buckets.csv](sub1_vs_sub5b_fix2/retrieval_quality_buckets.csv) | Same rows keyed for FOI clean vs suspicious splits |

Headline (2026-05-23): **1536/2000 agree (76.8%)**, **464 disagree (23.2%)**, net **+57** correct for Sub #5B (53.35% vs 50.5%).

Full 2000-row `details.csv` stays on disk only (~330 KB) — regenerate via the script above.

## Failure audit packets (25 rows)

**Build / refresh v2:**

```bash
python3 scripts/build_failure_audit_packet.py \
  --diag-dir /home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2 \
  --entries-dir /mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2 \
  --out /mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v2/failure_audit_packet.md \
  --frame-desc-cache /mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v2/failure_audit_frame_descriptions.json \
  --selected-csv diagnostics/sub5b_failure_audit_v2/selected_rows.csv \
  --sub-b-label 'Sub #5B' \
  --sub-b-answer-col sub5b_paper_faithful_fix2_answer \
  --packet-title 'Sub #1/Sub #5B Disagreement Audit Packet (v2)' \
  --force-frame-desc
# then copy failure_audit_packet.md + *.json + selected_rows.csv into diagnostics/sub5b_failure_audit_v2/
```

| Version | Repo path | Notes |
| --- | --- | --- |
| v1 | [sub5b_failure_audit_v1/](sub5b_failure_audit_v1/) | 5 percentile frames + FOI midpoint; includes `failure_audit_frame_descriptions.json` |
| v2 | [sub5b_failure_audit_v2/](sub5b_failure_audit_v2/) | All frames when ≤30; video links; deduped anchors; frame-desc cache |

**How to read:** rows are **disagreements**, not “Sub #5B wrong.” No local GT — spot-check **star/agqa at 0.25× playback** (time-warped clips). See `RESULTS.md` Q1809 calibration.
