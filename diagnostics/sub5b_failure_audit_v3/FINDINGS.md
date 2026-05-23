# Failure audit v3 — findings, sources, verification

Generated during the 2026-05-23 diagnostic session. Each claim lists where to read the output and how to recompute.

---

## 1. Audit packet v3 (auto triage)

**Claims**

- 25-row slice reuses v2 QIDs; adds pre-filled PULS_preliminary, Watch_for, Caption_coverage, Caption_question_mismatch, NSVS_bypassed, and two-tier reader tally.
- Tier-1 auto flags (of 25): PULS_preliminary ≠ pass **5**; NSVS_bypassed **19**; Caption_coverage gaps **22**; star/agqa &lt;10s confound **10**.

**Sources**

| Item | Path |
|------|------|
| Packet | [`failure_audit_packet.md`](failure_audit_packet.md) |
| Builder | [`../../scripts/build_failure_audit_packet.py`](../../scripts/build_failure_audit_packet.py) (`--version v3`) |
| Reused QIDs | [`../sub5b_failure_audit_v2/selected_rows.csv`](../sub5b_failure_audit_v2/selected_rows.csv) |
| Frame captions (not regenerated) | [`../sub5b_failure_audit_v2/failure_audit_frame_descriptions.json`](../sub5b_failure_audit_v2/failure_audit_frame_descriptions.json) |
| Pipeline entries | `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json` |

**Verify**

```bash
python3 scripts/build_failure_audit_packet.py --version v3
grep -c 'Tagging block (v3)' diagnostics/sub5b_failure_audit_v3/failure_audit_packet.md  # expect 25
```

---

## 2. CoT VQA diagnostic (25 audit rows)

**Claims**

- Same setup as Sub #5B VQA: gpt-5.2, 16 frames, cropped clip, `reasoning_effort=low` (temperature ignored on gpt-5.2).
- **Self-agreement** (2 runs): **17/25 (68%)**.
- **Agreement with stored Sub #5B answer** (both runs): **11/25 (44%)**; either run: 17/25.

**Sources**

| Item | Path |
|------|------|
| Summary | [`cot_summary.md`](cot_summary.md) |
| Full traces | [`cot_traces.json`](cot_traces.json) |
| Build log | [`cot_build.log`](cot_build.log) |
| Script | [`../../scripts/cot_diagnostic_rerun.py`](../../scripts/cot_diagnostic_rerun.py) |
| Sub #5B answers | [`../sub5b_failure_audit_v2/selected_rows.csv`](../sub5b_failure_audit_v2/selected_rows.csv) column `sub5b_paper_faithful_fix2_answer` |
| Cropped clips | `/mnt/Data/.../sub5b_paper_faithful_3fps_fix2/postprocess/postprocess_entries.json` |

**Verify**

```bash
python3 scripts/cot_diagnostic_rerun.py   # requires OPENAI_API_KEY; ~10 min
python3 -c "import json; d=json.load(open('diagnostics/sub5b_failure_audit_v3/cot_traces.json')); print(d['summary'])"
```

---

## 3. FOI == [-1] prevalence (full val vs audit slice)

**Claims**

- Full val (1983 processed): **29.5%** `FOI == [-1]`; **60.5%** NSVS_bypassed (broader v3 signal).
- Audit slice (25 disagreements): **12%** FOI `[-1]`; **76%** NSVS_bypassed (+15.5 pp vs val) → **selection bias** in the audit sample.
- Hot spots: `unknown` operator 58% FOI=-1; `&lt;10s` duration 45.8% FOI=-1 / 83.6% bypassed.

**Sources**

| Item | Path |
|------|------|
| Report | [`foi_minus1_prevalence.md`](foi_minus1_prevalence.md) |
| Script | [`../../scripts/analyze_foi_minus1_prevalence.py`](../../scripts/analyze_foi_minus1_prevalence.py) |
| Entries | `/mnt/Data/.../sub5b_paper_faithful_3fps_fix2/merged/entries.json` |
| Audit QIDs | [`../sub5b_failure_audit_v2/selected_rows.csv`](../sub5b_failure_audit_v2/selected_rows.csv) |

**Verify**

```bash
python3 scripts/analyze_foi_minus1_prevalence.py
```

Cross-check FOI rates on disagreements only: [`../sub1_vs_sub5b_fix2/summary.json`](../sub1_vs_sub5b_fix2/summary.json) buckets → `foi_status`.

---

## 4. Per-operator Sub #1 vs Sub #5B (val)

**Claims**

- **Per-operator accuracy unavailable** without EvalAI row labels.
- Overall agreement: **1536/2000 (76.8%)**; overall Sub #5B FOI=-1: **584/2000 (29.2%)**.
- `unknown` family: **82.1%** agreement but **57.1%** FOI=-1 (high match ≠ healthy retrieval).
- `always_before`: 77.4% agreement, 14.1% FOI=-1 (largest family, n=735).

**Sources**

| Item | Path |
|------|------|
| Report | [`per_operator_breakdown.md`](per_operator_breakdown.md) |
| Script | [`../../scripts/analyze_per_operator_breakdown.py`](../../scripts/analyze_per_operator_breakdown.py) |
| Row-level data | `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/details.csv` (regen via compare script) |
| EvalAI scores | [`../sub1_vs_sub5b_fix2/summary.json`](../sub1_vs_sub5b_fix2/summary.json) → 50.5% vs 53.35% |

**Verify**

```bash
python3 scripts/analyze_per_operator_breakdown.py
SCORE_B=53.35 bash scripts/compare_sub5b_vs_sub1.sh   # refresh details.csv if needed
```

---

## 5. Val video duration / speed distortion

**Claims**

- **ffprobe not installed**; OpenCV metadata used (documented limitation).
- Of **923** probed unique val videos: **51% &lt;2s**, **19% &lt;1s**, **4% &lt;0.5s**.
- By source: **star 82%** and **agqa 86%** under 2s; **bf/ct 0%** under 2s.
- Q1809 clip `star_1SLTT.mp4`: **0.56 s**, 14 frames @ 25 fps (matches prior calibration).

**Sources**

| Item | Path |
|------|------|
| Summary | [`video_duration_audit.md`](video_duration_audit.md) |
| Per-video CSV | [`video_duration_audit.csv`](video_duration_audit.csv) |
| Script | [`../../scripts/audit_val_video_duration.py`](../../scripts/audit_val_video_duration.py) |
| Val annotations | `/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json` |
| Videos | `/mnt/Data/.../videos/val/combined_2k_videos/` |

**Verify**

```bash
python3 scripts/audit_val_video_duration.py
grep star_1SLTT diagnostics/sub5b_failure_audit_v3/video_duration_audit.csv
# Optional after ffmpeg install:
python3 scripts/audit_val_video_duration.py --probe-backend ffprobe
```

Human playback check: Q1809 discussion in [`../../RESULTS.md`](../../RESULTS.md) (Failure-Audit Packet section).
