# Sub #5B failure audit v3 — diagnostics bundle

Git-tracked copy for cross-machine sync. Canonical heavy artifacts (frame-desc cache, merged entries) stay on disk under `/mnt/Data/ah66742/timelogic/outputs/`.

## Findings summary (2026-05-23)

| # | Task | Headline | Artifact |
|---|------|----------|----------|
| 1 | **Audit packet v3** | 25 disagreement rows with auto triage (PULS_preliminary, Watch_for, Caption_*, NSVS_bypassed); Tier-1 tally pre-filled | [`failure_audit_packet.md`](failure_audit_packet.md) |
| 2 | **CoT VQA rerun** | gpt-5.2 CoT on same 25 rows ×2: 68% self-agreement, 44% match Sub #5B on both runs | [`cot_summary.md`](cot_summary.md), [`cot_traces.json`](cot_traces.json) |
| 3 | **FOI=-1 prevalence** | Full val 29.5% FOI `[-1]`; audit slice only 12% — **76% NSVS_bypassed in audit vs 60.5% val** → selection bias | [`foi_minus1_prevalence.md`](foi_minus1_prevalence.md) |
| 4 | **Per-operator breakdown** | No local GT → agreement + FOI rates; `unknown` 82% agree but **57% FOI=-1** | [`per_operator_breakdown.md`](per_operator_breakdown.md) |
| 5 | **Video duration sweep** | **51%** of val videos **<2s** (OpenCV probe); star 82%, agqa 86%; bf/ct ~0% | [`video_duration_audit.md`](video_duration_audit.md), [`video_duration_audit.csv`](video_duration_audit.csv) |

See [`FINDINGS.md`](FINDINGS.md) for claim → source → verify paths.

## Regenerate

```bash
cd /home/ah66742/NeuS-QA
source .venv/bin/activate

# 1. v3 packet (reuses v2 selected_rows + frame-desc cache; no API)
python3 scripts/build_failure_audit_packet.py --version v3

# 2. CoT diagnostic (API; ~10 min for 25×2)
python3 scripts/cot_diagnostic_rerun.py

# 3–5. Offline analyses
python3 scripts/analyze_foi_minus1_prevalence.py
python3 scripts/analyze_per_operator_breakdown.py
python3 scripts/audit_val_video_duration.py
```

## Cross-machine sync

**Recommended:** treat this repo folder as source of truth for markdown/CSV/JSON summaries (~550 KB). Pull/push via git.

**Mirror to on-disk diagnostics** (optional, when `/mnt/Data` is mounted):

```bash
REPO=/home/ah66742/NeuS-QA
CANON=/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v3
mkdir -p "$CANON"
rsync -av --delete "$REPO/diagnostics/sub5b_failure_audit_v3/" "$CANON/"
```

**Symlink** (repo → canonical, if you prefer one write path on a GPU node):

```bash
mkdir -p /mnt/Data/ah66742/timelogic/outputs/diagnostics
ln -sfn /home/ah66742/NeuS-QA/diagnostics/sub5b_failure_audit_v3 \
  /mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v3
```

**Not in git** (copy separately or regenerate): v2 [`failure_audit_frame_descriptions.json`](../sub5b_failure_audit_v2/failure_audit_frame_descriptions.json) (~120 KB), full [`details.csv`](../sub1_vs_sub5b_fix2/) on disk only, Sub #5B `merged/entries.json`.

**ffprobe:** not installed on current host; duration audit uses OpenCV. Re-run with `--probe-backend ffprobe` after `sudo apt install ffmpeg`.
