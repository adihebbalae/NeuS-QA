# FOI / Target-Identification Diagnostic Notes

Date: 2026-05-21

This document records the diagnostic findings from the Sub #5B stop/fix/rerun session so the interval-retrieval issue can be analyzed separately from the rest of the TimeLogic adaptation work.

## Summary

The main issue found in the NSVS-based TimeLogic pipeline was that `target_identification` ran before NSVS. It was asked to choose a target window using placeholder `start_time` / `end_time` values even though no retrieved interval existed yet. The merge step then interpreted the LLM output as second offsets and applied those offsets to NSVS frame indices after the fact.

This likely affected all NSVS-dependent submissions:

- Sub #2 directly, because its VQA answerer sampled from `frames_of_interest`.
- Sub #3A / Sub #3B indirectly, because they routed based on Sub #2 metadata and FOI quality.
- Sub #4 indirectly, because the tiebreaker judge used NSVS interval frames as evidence.
- Sub #1 should not be affected, because it used full-video frames and skipped NSVS / target-ID.

The observed scores match this failure mode:

- Sub #1 full-video baseline: 50.50
- Sub #2 NSVS: 48.75
- Sub #3 routed variants: 48.95 / 49.00
- Sub #4 tiebreaker: 50.20

Interpretation: the retrieval interval was noisy enough to hurt more often than it helped, even when the downstream answerer or judge was strong.

## Original Problem

Original ordering in `scripts/run_timelogic.py`:

1. PULS
2. `target_identification`
3. video read
4. NSVS
5. merge target offsets with NSVS output

The target-identification prompt in `nsvqa/target_identification/target_identification.py` said the specification occurs between `start_time` and `end_time`, but those were literal placeholders. At that point in the pipeline, NSVS had not run and real interval times were unavailable.

The target-ID LLM therefore produced offsets or windows without seeing the actual retrieved interval. Later, `run_timelogic.py` parsed signed numbers from that output and applied them to `entry["nsvs"]["output"]`.

## Fixes Applied

### 1. Pipeline ordering

Changed `scripts/run_timelogic.py` ordering to:

1. PULS
2. video read
3. NSVS
4. target identification with real NSVS start/end times
5. merge into `frames_of_interest`

Target identification now receives:

- `nsvs_start_sec`
- `nsvs_end_sec`

These values are computed from NSVS frame indices and FPS.

### 2. Target-identification prompt

Rewrote `nsvqa/target_identification/target_identification.py` so it asks for non-negative second paddings relative to the real NSVS interval.

Expected format:

```json
{
  "target_frame_window": "[+0, +5]",
  "explanation": "..."
}
```

These paddings mean:

- first value extends before the NSVS start
- second value extends after the NSVS end

If target-ID fails, the pipeline falls back to raw NSVS bounds via `[+0, +0]`.

Follow-up live-run finding: the first fix originally parsed `[+2, +8]` as arithmetic offsets, which moved the start forward by 2 seconds instead of extending 2 seconds before the NSVS start. In the 5B rerun this produced invalid intervals such as `[50, 13]` and `[695, 599]` after clamping. `merge_frames_of_interest` now subtracts the first padding from the start, adds the second padding to the end, clamps both to video bounds, and returns `[-1]` if a merged interval is still invalid.

### 3. FOI frame-step guard

Changed `nsvqa/nsvs/nsvs.py`:

```python
fps = float(video_data["video_info"]["fps"] or 1.0)
frame_step = max(1, int(round(fps / video_data["sample_rate"])))
```

This prevents `frame_step` from becoming zero at higher sample rates or unusual FPS values.

### 4. InternVL binary detection determinism

Changed `nsvqa/nsvs/vlm/internvl.py`:

- `do_sample=False`
- `max_new_tokens=8`

The proposition detector only needs a Yes/No answer. This should reduce variance and wasted decoding.

### 5. `evaluate.py` footgun

Added missing `import re` to `evaluate.py`, since `exec_merge` used `re.search`.

Note: `evaluate.py` is still not canonical for TimeLogic. `scripts/run_timelogic.py` remains the TimeLogic driver.

## Smoke Test

Smoke output:

`/mnt/Data/ah66742/timelogic/outputs/smoke_foi_fix_v0/`

Command used a 3-entry smoke with:

- `--sample-rate 3.0`
- `--puls-model gpt-4o-mini`
- InternVL2-8B

Results:

- NSVS completed: 3/3
- Non-empty FOI: 2/3
- Target identification ran after NSVS and received real interval times.

Example qid 790:

- question: `Did the person insert dipstick immediately after closing cap ?`
- NSVS output: `[9090, 9959]`
- FPS: `29.97002997002997`
- `nsvs_start_sec`: about `303.303`
- target window: `[+0, +5]`
- final FOI: `[9090, 10108]`
- step status: PULS ok, NSVS ok, target_identification ok, merge ok

The smoke command exited with code 1 only because `tee` tried to write `run.log` before the output directory existed. The actual pipeline completed and wrote `entries.json`, `diag.json`, and per-entry artifacts.

## Sub #5B Run Handling

Stopped the old 3fps run:

- tmux session: `sub5b_paper_faithful_3fps`
- output preserved at: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps/`
- marker written: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps/STOPPED`

Started fixed rerun:

- tmux session: `sub5b_paper_faithful_3fps_fix`
- output root: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix/`
- tmux log: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix/tmux.log`
- sample rate: `3.0`
- PULS / target-ID model: `gpt-4o`
- proposition model: `InternVL2-8B`
- downstream planned by script: ffmpeg crop plus local Qwen2.5-VL-7B VQA

Stopped this first fixed rerun after a live check found invalid merged intervals caused by the padding-sign interpretation described above. Its partial output should be treated as contaminated:

- tmux session: `sub5b_paper_faithful_3fps_fix`
- output root: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix/`
- completed per-entry artifacts at stop time: 28

Started the second fixed rerun after correcting padding direction:

- tmux session: `sub5b_paper_faithful_3fps_fix2`
- output root: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/`
- tmux log: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/tmux.log`

## Wider Smoke Gate Before Resuming 5B

Sub #5B was not resumed. Instead, a 40-entry mixed val smoke was run on the fixed pipeline:

- output root: `/mnt/Data/ah66742/timelogic/outputs/smoke_foi_fix_wide_40_parallel/`
- QID list: `/mnt/Data/ah66742/timelogic/outputs/smoke_foi_fix_wide_40_parallel/qids.json`
- aggregate probe: `/mnt/Data/ah66742/timelogic/outputs/smoke_foi_fix_wide_40_parallel/foi_nsvs_probe.post_fix_adjusted.json`
- mix: 20 bool / 20 MC, and 10 rows each from `ct`, `agqa`, `bf`, and `star`

FOI / merge results after replacing the one NSVS crash row with the targeted post-fix rerun:

- non-empty FOI: 28/40 = 70.00%
- final FOI `[-1]`: 12/40 = 30.00%
- raw NSVS valid bounds: 28/40 = 70.00%
- raw NSVS `[-1]`: 12/40 = 30.00%
- final FOI `[-1]` despite valid raw NSVS bounds: 0/28 = 0.00%
- merged FOI not a superset of raw NSVS bounds: 0/28 = 0.00%
- FOI length seconds: min 0.04, p25 1.40, median 18.77, p75 74.75, p90 146.24, max 205.88
- short valid FOI windows: `<=1s` 4/28 = 14.29%, `<=2s` 10/28 = 35.71%, `<=5s` 11/28 = 39.29%

Interpretation: the corrected target-ID merge is no longer producing invalid intervals or shrinking below raw NSVS bounds in this smoke. The short-window rate is non-trivial, but many short windows are from short `agqa`/`star` clips and are not, by themselves, evidence of the padding-direction bug.

NSVS-quality probe:

- rows with `nsvs.indices`: 40/40 after the targeted post-fix rerun
- rows where at least one `nsvs.indices` array is empty: 24/40 = 60.00%
- rows where all `nsvs.indices` arrays are empty: 9/40 = 22.50%
- empty `nsvs.indices` arrays: 33/80 = 41.25%

Important caveat: `nsvs.indices` currently stores two temporal split arrays from `PropertyChecker.check_split`, not necessarily one array per proposition. For example, a three-proposition question can still produce two arrays. The Q2-style empty-array signal is still meaningful, but the name should be understood as "empty temporal detection split" rather than literally "empty proposition array" in all cases.

One concrete bug was found during the smoke: qid `1936` originally crashed inside `run_nsvs` with `ValueError('min() iterable argument is empty')` when the automaton produced FOI candidates but the detection intersection was empty. `nsvqa/nsvs/nsvs.py` now checks the detection intersection before calling `min()` / `max()` and returns `[-1]` cleanly. A targeted one-row rerun of qid `1936` completed successfully and produced raw NSVS `[-1]`, final FOI `[-1]`, and populated `nsvs.indices`.

## Remaining Risks

The fixes address the most obvious ordering and frame-step bugs, but several accuracy risks remain:

1. PULS propositions may still be non-frame-local. Prior grounding audit found about 49.3% of sampled propositions required temporal continuity.
2. `frame_validator.py` still uses approximate symbolic filtering semantics, including majority-style AND behavior.
3. Storm probabilities are not persisted, so routing still lacks calibrated confidence.
4. Repeated video sampling is still per-question, not cached per repeated video ID.
5. `answer_cropped_timelogic_local.py` may still include duplicated MC option text if the original question already contains options.

## Case Study: Q2 Scrambled-Egg Window

This row is useful because the final answer was correct even though the interval grounding was not clean.

| Field | Value |
|---|---|
| `question_id` | `2` |
| `video_id` | `bf_P13_webcam01_P13_scrambledegg.mp4` |
| Question type | `mc`, `always_before` |
| Question | Which action always occurs before person melting butter which in turn always occurs before person pouring salt? |
| Choices | A: carry butter, B: carry bowl, C: carry pepper, D: pour salt |
| Sub #1 answer | `A` |
| Sub #2 answer | `A` |

Sub #2 logged:

```json
{
  "puls": {
    "proposition": ["person_melts_butter", "person_pours_salt"],
    "specification": "\"person_melts_butter\" U \"person_pours_salt\""
  },
  "nsvs": {
    "output": [270, 540],
    "indices": [[], [6, 11, 12]]
  },
  "frames_of_interest": [120, 540]
}
```

Visual audit of sampled frames from `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P13_webcam01_P13_scrambledegg.mp4`:

| Frame range | Approx. time | Observation |
|---:|---:|---|
| 0-90 | 0-6s | Prep: eggs/carton/mug, pan empty or heating |
| 90-150 | 6-10s | Butter/fat melting in pan |
| 200 | 13s | Cracking egg; pan already has butter |
| 350 | 23s | Seasoning raw eggs, likely salt |
| 500-600 | 33-40s | Whisking eggs; pan still empty of egg mixture |
| 800+ | 53s+ | Eggs cooking in pan |

Interpretation:

- NSVS scanned the video but did not detect `person_melts_butter` at all (`indices[0] == []`).
- The NSVS interval `[270, 540]` starts late relative to visual melt (~90-150) and ends after likely salt (~350).
- The final FOI `[120, 540]` was partly lucky: target-ID's `-10s` padding pulled the late NSVS start back to the real melt region.
- The FOI still likely misses the cleanest evidence for "carry butter" before melt, which is probably in the first few seconds.
- The model still answered `A`, likely because the window included indirect butter evidence, the anchors were visible enough, and the distractors were weak. This is a false-comfort example: correct answer does not imply correct localization.

This suggests the next fix should not only repair target-ID ordering. We also need to measure NSVS proposition-detection quality directly, especially rows where the first proposition has no detections but Storm still returns a non-empty interval.

## Fixed Sub #5B Full-Val Run (Resumed)

Full val was resumed after the 40-entry smoke gate:

- tmux session: `sub5b_paper_faithful_3fps_fix2`
- output root: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/`
- tmux log: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/tmux.log`
- sample rate: `3.0`
- pipeline: `scripts/run_sub5b_paper_faithful.sh` (8 NSVS shards → merge → ffmpeg crop → local Qwen2.5-VL-7B)
- partial pre-smoke attempt archived at: `sub5b_paper_faithful_3fps_fix2_aborted/` (if present)

Completion marker: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/DONE`

## Post-Run Comparison vs Sub #1 (Pre-Committed)

Primary tool: `scripts/compare_submissions.py` (now includes `retrieval_quality_bucket`).

Convenience wrapper:

```bash
bash scripts/compare_sub5b_vs_sub1.sh
# or, after EvalAI score is known:
SCORE_B=<pct> bash scripts/compare_sub5b_vs_sub1.sh
```

Output directory: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/`

Three buckets to read whether retrieval is helping:

| Bucket | Meaning |
|---|---|
| `agree_with_sub_a` | Sub #5B matches Sub #1 answer |
| `disagree_foi_clean` | Answers differ, but FOI is valid, non-`[-1]`, no empty `nsvs.indices` arrays, not absurdly short, and merge did not shrink below raw NSVS |
| `disagree_foi_suspicious` | Answers differ and FOI/indices look broken (`[-1]`, invalid bounds, empty detection splits, merge collapse, `<1s` window, etc.) |

Interpretation guide:

- If most disagreements are `disagree_foi_suspicious`, retrieval is still harming answers even after the ordering/padding fixes.
- If disagreements split evenly but `disagree_foi_clean` is large, NSVS may be changing answers on plausible intervals — check EvalAI score delta and spot-check cropped clips in that bucket.
- Compare `disagree_foi_clean` vs `disagree_foi_suspicious` disagree rates by `mode` / `source_dataset` in `summary.json` cross-tabs (`foi_status`, `duration_bucket`).

Also run FOI coverage on merged entries:

```bash
python3 scripts/analyze_foi_smoke.py \
  --output-dir /mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged \
  --write-json /home/ah66742/timelogic-data/outputs/diagnostics/sub5b_fix2_foi_probe.json
```

## Sub #1/Sub #2 Disagreement Failure-Audit Packet

For human review of where NSVS harmed or changed answers in Sub #2, a 25-row packet was built from the full 452-question Sub #1/Sub #2 disagreement set:

- packet: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2/failure_audit_packet.md`
- frame-description cache: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2/failure_audit_frame_descriptions.json`
- builder: `scripts/build_failure_audit_packet.py`

Important framing correction: the ~244/~208 split in planning docs is aggregate-inferred from EvalAI scores, not row-level ground truth. The audit packet therefore does not condition on "Sub #1 won"; it stratifies over the full 452 disagreements and marks ground truth as unavailable locally.

## Recommended Next Analysis

After the fixed Sub #5B run finishes:

1. Compare its EvalAI score against Sub #1 and Sub #2.
2. Measure FOI coverage and FOI length distribution from the fixed run (`analyze_foi_smoke.py` on merged entries).
3. Run `scripts/compare_sub5b_vs_sub1.sh` for the three retrieval-quality buckets above.
4. Inspect a small sample of cropped videos from `disagree_foi_clean` vs `disagree_foi_suspicious` rows.
5. If fixed Sub #5B still underperforms Sub #1, pivot toward full-video baseline improvements plus selective retrieval, not full reliance on NSVS intervals.
