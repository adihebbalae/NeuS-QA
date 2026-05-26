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
| v3 | [sub5b_failure_audit_v3/](sub5b_failure_audit_v3/) | Auto triage + CoT rerun + FOI/operator/duration analyses — **git-synced** |

**Build v3 (no frame-desc API):**

```bash
python3 scripts/build_failure_audit_packet.py --version v3
```

**v3 companion analyses:**

```bash
python3 scripts/cot_diagnostic_rerun.py              # API ~10 min
python3 scripts/analyze_foi_minus1_prevalence.py
python3 scripts/analyze_per_operator_breakdown.py
python3 scripts/audit_val_video_duration.py          # OpenCV; ffprobe optional
```

See [sub5b_failure_audit_v3/README.md](sub5b_failure_audit_v3/README.md) and [FINDINGS.md](sub5b_failure_audit_v3/FINDINGS.md) for headlines and cross-machine sync (`rsync` / symlink to `/mnt/Data/.../diagnostics/sub5b_failure_audit_v3/`).

**How to read:** rows are **disagreements**, not “Sub #5B wrong.” No local GT — spot-check **star/agqa at 0.25× playback** (time-warped clips). See `RESULTS.md` Q1809 calibration.

## Sub #5B test run analysis (3000 Q)

**Regenerate:**

```bash
cd /home/ah66742/NeuS-QA
source .venv/bin/activate
python3 scripts/analyze_sub5b_test.py
python3 scripts/nsvs_quality_probe.py \
  --output-dir /mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps \
  --label "Sub #5B test full merged" \
  --report /mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_test/nsvs_quality_report.md
# copy summary.json + analysis.md + nsvs_quality_report.md → diagnostics/sub5b_test/
```

| Artifact | Repo path | Description |
| --- | --- | --- |
| Summary JSON | [sub5b_test/summary.json](sub5b_test/summary.json) | Pipeline health, distribution, FOI/VQA breakdowns, val comparison |
| Report | [sub5b_test/analysis.md](sub5b_test/analysis.md) | Human-readable markdown |
| NSVS probe | [sub5b_test/nsvs_quality_report.md](sub5b_test/nsvs_quality_report.md) | FOI coverage, padding mix, multi-prop zero-detection |

Headline (2026-05-23): **3000/3000 rows**, upload-safe (top No 20.9%), FOI **68.5%** (vs val 70.6%), **2 VQA max_tokens errors** (Q1840, Q2504 → fallback `A`).

## Test video OpenCV duration audit

**Regenerate:**

```bash
python3 scripts/audit_val_video_duration.py --phase test \
  --ann /mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json \
  --video-root /mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json \
  --out-dir /mnt/Data/ah66742/timelogic/outputs/diagnostics/test_video_opencv_audit \
  --probe-backend opencv
```

| Artifact | Repo path |
| --- | --- |
| Report | [test_video_opencv_audit/video_duration_audit.md](test_video_opencv_audit/video_duration_audit.md) |
| Per-video CSV | [test_video_opencv_audit/video_duration_audit.csv](test_video_opencv_audit/video_duration_audit.csv) |

Val counterpart: [sub5b_failure_audit_v3/video_duration_audit.md](sub5b_failure_audit_v3/video_duration_audit.md).

## PULS unknown-family analysis (Diagnostic 2)

Driver: `scripts/analyze_puls_unknown_bypassed.py` · **416** NSVS-bypassed `unknown` rows · **173** PULS-attributable.

| Artifact | Repo path |
| --- | --- |
| Report | [puls_unknown_analysis/report.md](puls_unknown_analysis/report.md) |
| Per-row CSV | [puls_unknown_analysis/details.csv](puls_unknown_analysis/details.csv) |
| AM review (94 + 54 rows) | [puls_unknown_analysis/overnight_review.md](puls_unknown_analysis/overnight_review.md) |

## Diagnostic 3 — GPT-5.2 NSVS swap (50-Q subsample)

Output on disk: `/mnt/Data/ah66742/timelogic/outputs/sub5b_subsample/`.

| Artifact | Repo path |
| --- | --- |
| Summary | [diag3_gpt52_swap/SUMMARY.md](diag3_gpt52_swap/SUMMARY.md) |
| Full report | `outputs/sub5b_subsample/report/ablation_summary.md` (not in repo) |

Headline (2026-05-25): **17/48** flips vs Sub #5B; **10/17** toward Sub #1; **78.9%** NSVS vote agreement vs InternVL replay.

## PULS prompt v2 prep (2026-05-26)

| Artifact | Repo path |
| --- | --- |
| Diff / regression | [puls_v2_prep/PROMPT_DIFF.md](puls_v2_prep/PROMPT_DIFF.md) |
| PI audit packet | [puls_v2_prep/PROMPT_AUDIT_PACKET.md](puls_v2_prep/PROMPT_AUDIT_PACKET.md) |

Code: Examples **13–16** in `nsvqa/puls/prompts.py` (append-only). Not yet re-run on val.
