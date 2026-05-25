# TimeLogic Results Ledger

Central source of truth for important validation runs, diagnostics, and current interpretation.

Last updated: 2026-05-24 (PM — manual audit headlines + parallel diagnostics queued).

## Current best

| Rank | Submission | EvalAI val AvgAcc | Delta vs best | Status |
|---|---|---:|---:|---|
| 1 | Sub #5B: `sub5b_paper_faithful_3fps_fix2` | **53.35** | 0.00 | **New best** — paper-faithful NSVS + ffmpeg crop + gpt-5.2 VQA |
| 2 | Sub #1: `baseline_cpu_v01` | **50.50** | -2.85 | Full-video baseline |
| 3 | Sub #4: `sub4_tiebreak_gpt52` | **50.20** | -3.15 | Tiebreaker on 452 disagreements |
| 4 | Sub #3A: FOI proxy routing | **49.00** | -4.35 | Post-process only |
| 5 | Sub #3B: `bf+mc+>60s` routing | **48.95** | -4.40 | Post-process only |
| 6 | Sub #2: `nsvs_sub2_v2` | **48.75** | -4.60 | Contaminated FOI merge |
| 7 | Sub #6A: hybrid 5B+Sub #1 (FOI proxy) | **52.85** | -0.50 | Post-process; below pure 5B |
| 8 | Sub #6B: hybrid 5B+Sub #1 (FOI clean) | **52.60** | -0.75 | Post-process; below pure 5B |

## Submission Runs

| # | Run | Pipeline | Main artifacts | Notes |
|---|---|---|---|---|
| 1 | `baseline_cpu_v01` | PULS with `gpt-5.2`, no GPU/NSVS, 8 full-video frames to `gpt-5.2` vision answerer | `/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json` | 2000/2000 EvalAI rows. 1983 videos answered normally; 17 missing-video defaults. Wall time ~154.8 min. |
| 2 | `nsvs_sub2_v2` | PULS + target identification with `gpt-5.2`; InternVL2-8B NSVS; answerer samples `frames_of_interest` with `gpt-5.2` vision | `/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2/submission_sub2.json` | 8 GPU shards. 1983 processed videos merged; 17 missing-video defaults. EvalAI val **48.75**. |
| 3A | `routed_sub3/submission_sub3a_foi_proxy.json` | Post-processing: FOI-quality proxy routes 1188→Sub #1, 812→Sub #2 | `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3a_foi_proxy.json` | EvalAI val **49.00**. Not true Storm-P gate (probabilities not logged). |
| 3B | `routed_sub3/submission_sub3b_bf_mc_gt60.json` | Post-processing: `bf+mc+>60s` → Sub #1; else Sub #2 | `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3b_bf_mc_gt60.json` | EvalAI val **48.95**. Did not beat Sub #1. |
| 4 | `sub4_tiebreak_gpt52/submission_sub4_tiebreak_gpt52.json` | Post-processing: copy 1548 agreements; `gpt-5.2` vision judge on 452 disagreements | `/home/ah66742/timelogic-data/outputs/sub4_tiebreak_gpt52/submission_sub4_tiebreak_gpt52.json` | EvalAI val **50.20**. -0.30 vs Sub #1. |
| 5B | `sub5b_paper_faithful_3fps_fix2` | Paper-faithful at **3fps**: `gpt-4o` PULS/target_id, InternVL2-8B NSVS, ffmpeg crop, **gpt-5.2** VQA on crops (16 frames; Qwen blocked by GPU driver) | `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/submission_sub5b_paper_faithful_gpt52.json` | EvalAI val **53.35** (+2.85 vs Sub #1). FOI fix: 70.6% valid intervals. 1983 processed + 17 missing-video defaults. |
| 6A | `sub6_hybrid_routing/submission_sub6a_foi_proxy.json` | Post-process: FOI-confidence proxy routes Sub #1 ↔ **Sub #5B** (877→5B, 1123→Sub #1) | `/mnt/Data/ah66742/timelogic/outputs/sub6_hybrid_routing/submission_sub6a_foi_proxy.json` | EvalAI val **52.85** (−0.50 vs Sub #5B). |
| 6B | `sub6_hybrid_routing/submission_sub6b_foi_clean.json` | Post-process: FOI-confidence + suspicious-FOI flags → Sub #1 | `/mnt/Data/ah66742/timelogic/outputs/sub6_hybrid_routing/submission_sub6b_foi_clean.json` | EvalAI val **52.60** (−0.75 vs Sub #5B). |
| 5B-test | `sub5b_test_3fps` | Same stack as Sub #5B on test split (3000 Q) | `/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps/submission_sub5b_test_gpt52.json` | **Complete** 2026-05-23 13:45 (~21.6h wall). 3000/3000 rows; distribution upload-safe (top No 20.9%). EvalAI score TBD — **not yet uploaded**. |

## Sub #4 Tiebreaker (complete)

Script: `scripts/build_tiebreaker_submission.py`

| Metric | Value |
|---|---:|
| Wall time | ~35 min (2091 s) |
| Agreements copied | 1548 |
| Disagreements judged | 452 |
| Judge picked Sub #2 | 271 |
| Judge picked Sub #1 | 181 |
| Judge errors (fallback Sub #1) | 4 |
| Rows matching Sub #1 | 1729 / 2000 |
| Rows matching Sub #2 | 1819 / 2000 |

## FOI Coverage

Measured from `nsvs_sub2_v2/merged/entries.json`.

| Metric | Count | Percent |
|---|---:|---:|
| Total val annotations | 2000 | 100.00 |
| Processed entries with videos | 1983 | 99.15 |
| Missing or unprocessed videos | 17 | 0.85 |
| Non-`-1` `frames_of_interest` among processed entries | 1161 / 1983 | **58.55** |
| Non-`-1` `frames_of_interest` over all annotations | 1161 / 2000 | **58.05** |
| `-1` or empty `frames_of_interest` among processed entries | 822 / 1983 | **41.45** |

Interpretation: NSVS found a usable interval for only about 58% of processed rows. The answerer fell back to full-video-style behavior or default handling for the rest.

## Video Length Audit

Measured from processed val entries with available video metadata.

| Metric | Value |
|---|---:|
| Durations available | 1983 |
| `<30s` question rows | 1003 / 1983 = **50.58%** |
| `<30s` distinct videos | 565 / 923 = **61.21%** |
| Min duration | 0.16s |
| Median duration | 3.16s |
| Mean duration | 118.10s |
| 75th percentile | 209.80s |
| 90th percentile | 342.20s |
| Max duration | 612.38s |

Source split for `<30s` rows: almost all short rows are `agqa` and `star`; `bf` and `ct` are mostly longer.

Interpretation: interval retrieval has less room to help on the many short clips. It matters most on long `bf`/`ct` videos, but those are also where Sub #2 changed answers most aggressively.

## Case studies

Deep dives on interval grounding failures (NSVS vs target_identification vs visual audit).

| Case | Doc | Summary |
|---|---|---|
| Q2 `bf` scramble egg (`always_before`) | [`FOI_FIX_DIAGNOSTIC.md`](FOI_FIX_DIAGNOSTIC.md) | NSVS interval 270–540 misaligned vs visual melt ~90–150, pour ~350; placeholder target-ID padding made FOI 120–540 partly lucky; both subs answer `A`. |

## Sub #1 vs Sub #2 Diagnostic

Script: `scripts/compare_submissions.py`

Output directory: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2/`

Inputs:

- A: `/home/ah66742/timelogic-data/outputs/baseline_cpu_v01/submission.json`
- B: `/home/ah66742/timelogic-data/outputs/nsvs_sub2_v2/submission_sub2.json`
- A entries: `/home/ah66742/timelogic-data/outputs/baseline_cpu_v01/entries.json`
- B entries: `/home/ah66742/timelogic-data/outputs/nsvs_sub2_v2/merged/entries.json`

### Agreement Matrix

No hidden labels are available locally, so this is an answer-agreement diagnostic, not a true correctness matrix.

| Metric | Count | Percent |
|---|---:|---:|
| Common question IDs | 2000 | 100.00 |
| Same answer | 1548 | **77.40** |
| Different answer | 452 | **22.60** |
| Sub #1 aggregate correct estimate | 1010 / 2000 | 50.50 |
| Sub #2 aggregate correct estimate | 975 / 2000 | 48.75 |
| Net Sub #1 advantage | 35 questions | +1.75 points |

Important interpretation: the submissions disagree on 452 rows, but Sub #1 only has a net advantage of about 35 correct answers. NSVS likely helps a meaningful number of examples, but hurts slightly more than it helps in this configuration.

The often-quoted ~244/~208 split is not row-level ground truth. It comes from aggregate score math: 452 disagreements plus Sub #1's +35 net advantage implies ~243.5 rows where Sub #1 is correct and ~208.5 where Sub #2 is correct only if every disagreement has exactly one correct answer.

### Failure-Audit Packet

Human-readable 25-row packet sampled from the full 452-entry disagreement set:

- Packet: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2/failure_audit_packet.md`
- Frame-description cache: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2/failure_audit_frame_descriptions.json`
- Builder: `scripts/build_failure_audit_packet.py`

Packet contents: question/candidates/answers, PULS propositions and TL spec, full raw `nsvs.indices`, raw Storm interval, target-ID window and explanation, final FOI, Sub #2 VQA answer artifact, and cached `gpt-4o-mini` frame descriptions at video percentiles plus FOI/reference midpoints. Because hidden labels are unavailable locally, the packet does not condition on "Sub #1 won"; it uses the full disagreement set.

### Disagreement by Mode

| Mode | Disagree / Total | Disagree % |
|---|---:|---:|
| `mc` | 313 / 1200 | **26.08** |
| `bool` | 139 / 800 | **17.38** |

### Disagreement by Source Dataset

| Source | Disagree / Total | Disagree % |
|---|---:|---:|
| `bf` | 161 / 500 | **32.20** |
| `ct` | 123 / 500 | **24.60** |
| `star` | 85 / 500 | **17.00** |
| `agqa` | 83 / 500 | **16.60** |

### Disagreement by Duration Bucket

| Duration bucket | Disagree / Total | Disagree % |
|---|---:|---:|
| `>60s` | 266 / 915 | **29.07** |
| `10-60s` | 18 / 68 | **26.47** |
| `2-10s` | 40 / 201 | **19.90** |
| `<2s` | 128 / 799 | **16.02** |
| unknown | 0 / 17 | 0.00 |

### Disagreement by FOI Status

| FOI status | Disagree / Total | Disagree % |
|---|---:|---:|
| non-`-1` FOI | 320 / 1161 | **27.56** |
| `-1` FOI | 124 / 799 | **15.52** |
| missing FOI | 8 / 40 | **20.00** |

### Highest-Risk Intersections

| Bucket | Disagree / Total | Disagree % |
|---|---:|---:|
| `bf` x `>60s` | 146 / 440 | **33.20** |
| `bf` x `mc` | 139 / 410 | **33.90** |
| `bf` x `>60s` x `mc` | 127 / 367 | **34.60** |
| non-`-1` FOI x `bf` | 154 / 452 | **34.10** |
| non-`-1` FOI x `>60s` | 252 / 798 | **31.60** |
| `mc` x `>60s` | 186 / 601 | **30.90** |

## PULS Grounding Audit

Script: `scripts/audit_puls_grounding.py`  
Artifacts: `/mnt/Data/ah66742/timelogic/outputs/puls_grounding_audit/`

Sample: 200 PULS outputs (85 baseline, 115 NSVS), 341 propositions, `gpt-5.2` text-only judge.

| Score | Meaning | Count | % |
|---|---|---:|---:|
| 1 | Clearly single-frame visual | 78 | **22.9** |
| 2 | Ambiguous / needs context | 95 | **27.9** |
| 3 | Needs temporal continuity | 168 | **49.3** |

Interpretation: roughly half of PULS atoms are not reliably scorable as binary predicates on one static frame — consistent with VLTL-Bench's grounding bottleneck and with InternVL frame-wise detection struggling on TimeLogic event verbs (`puts`, `takes`, `opens`, `melts`, etc.).

## Post-Processing Ensemble Results (Sub #3 / #4)

| Submission | Score | Takeaway |
|---|---:|---|
| Sub #3B (`bf+mc+>60s` → Sub #1) | 48.95 | Worst-bucket carve-out insufficient |
| Sub #3A (FOI proxy) | 49.00 | Conservative NSVS gating insufficient |
| Sub #4 (`gpt-5.2` tiebreaker) | 50.20 | Strong judge nearly matches Sub #1 but does not beat it |

Oracle routing ceiling (perfect Sub #1 vs Sub #2 picks) was ~60.9%; realized routing/judging captured little of that gap.

## Sub #1 vs Sub #5B Diagnostic

Script: `scripts/compare_5b_vs_sub1.py`, `scripts/compare_submissions.py`

Output directory: `diagnostics/sub1_vs_sub5b_fix2/` (repo) · `/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub1_vs_sub5b_fix2/` (on disk)

Regenerate: `SCORE_B=53.35 bash scripts/compare_sub5b_vs_sub1.sh`

| Metric | Count | Percent |
|---|---:|---:|
| Common question IDs | 2000 | 100.00 |
| Same answer | 1536 | **76.80** |
| Different answer | 464 | **23.20** |
| Sub #1 aggregate correct estimate | 1010 / 2000 | 50.50 |
| Sub #5B aggregate correct estimate | 1067 / 2000 | 53.35 |
| Net Sub #5B advantage | 57 questions | **+2.85 points** |

Under the "one correct per disagreement" assumption: ~261 rows where Sub #5B is correct vs ~203 where Sub #1 is correct.

### Failure-Audit Packet (Sub #1 vs Sub #5B)

25-row human audit slice from the 464 disagreements (duration-stratified). **Not** a list of Sub #5B errors — both sides may be wrong without local labels.

| Version | Repo copy | On-disk canonical | Notes |
|---|---|---|---|
| v1 | [`diagnostics/sub5b_failure_audit_v1/`](diagnostics/sub5b_failure_audit_v1/) | `/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v1/` | 5 percentile frames + FOI midpoint |
| v2 | [`diagnostics/sub5b_failure_audit_v2/`](diagnostics/sub5b_failure_audit_v2/) | `/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v2/` | All frames when ≤30 frames; video links; deduped anchors |
| v3 | [`diagnostics/sub5b_failure_audit_v3/`](diagnostics/sub5b_failure_audit_v3/) | symlink/`rsync` from repo (see v3 README) | Auto triage packet + CoT/FOI/operator/duration analyses |

Builder: `scripts/build_failure_audit_packet.py` (`--version v3` or `--selected-csv` for v2 QIDs).

**v3 diagnostic headlines (2026-05-23):**

| Analysis | Finding |
|---|---|
| Auto triage (25 rows) | NSVS_bypassed flagged **19/25**; star/agqa &lt;10s confound **10/25** |
| CoT VQA rerun | 68% self-agreement; **44%** match Sub #5B on both CoT runs |
| FOI=-1 prevalence | Val **29.5%** FOI `[-1]`; audit slice **76%** NSVS_bypassed vs **60.5%** val → selection bias |
| Per-operator | `unknown`: 82% agree, **57%** FOI=-1; no per-op accuracy without GT |
| Video duration | **51%** val videos **&lt;2s** (OpenCV); star/agqa **~85%** &lt;2s; bf/ct **0%** |

Full claim → source → verify: [`diagnostics/sub5b_failure_audit_v3/FINDINGS.md`](diagnostics/sub5b_failure_audit_v3/FINDINGS.md).

**Calibration (Q1809, star):** human review at 0.25× playback → person puts phone on table after drinking; **Sub #5B Yes likely correct**, Sub #1 No likely wrong. Audit gpt-4o-mini frame captions mis-described cup vs phone sequence — do not treat captions as GT. STAR/agqa clips appear **time-warped** (~4× motion in sub-second files); review star/agqa at slow playback.

**Failure-mode tags (draft):** `time_warp_star_agqa`, `PULS_spec_mismatch`, `NSVS_prop_miss`, `storm_foi_minus_one`, `vqa_ungrounded`, `baseline_vqa_miss`, `foi_clean_disagree`.

**v3 manual-audit headlines (2026-05-24 PM — 12 of 25 rows reviewed):**

Adi has manually annotated 12 rows: priority-A (CoT stable vs Sub #5B) QIDs 107, 224, 1399, 1632; priority-B (CoT split across reruns) QIDs 1105, 489, 601, 262, 1525, 635, 1865, 796. The 11 "Boring" tier rows (CoT confirms Sub #5B both runs) remain.

| Finding | Detail |
|---|---|
| Failure-mode split (audited slice) | ~50% benchmark-quality (ill-posed/ambiguous/multi-shot/malformed-question); ~25% NSVS perception errors; ~15% QA-layer logic; ~10% clean Sub #5B wins (QID 1865 is the type specimen). |
| **A/Yes positional bias (audit slice)** | Sub #5B answers across 25 audit rows skew strongly A (50% of MC) and Yes (91% of bool). Initially hypothesized to indicate FOI=-1 fallback defaults to a positional prior. **Disproven by Diagnostic 1 on full val — see "Parallel diagnostics — results" below.** Audit pattern was selection-bias artifact. |
| **CoT self-agreement = question-quality proxy** | 17/25 (68%) CoT self-agreed across two identical reruns; 8/25 split. Of the 8 audited splits, every one is ill-posed or ambiguous. Of the 4 audited self-agreeing priority-A cases, all are well-posed (CoT just disagreed with Sub #5B). Useful for slicing val accuracy in the writeup: "53.35% overall, XX% on the self-agreeing CoT slice." |
| Caption ≠ NSVS-vote conflation | Frame captions in packet are gpt-4o-mini post-hoc, not InternVL2-8B votes — when Adi marks "NSVS bad detect" based on caption mismatch, the actual NSVS vote may differ. Surfacing the raw votes is queued as a v4 packet enhancement (see `CURSOR_TASKS.md` task 2). |

**Parallel diagnostics — results (2026-05-24 PM):**

Three diagnostics queued; two complete tonight, one still running. Brief at `diagnostics/sub5b_failure_audit_v3/PARALLEL_DIAGNOSTICS_PM.md`.

**Diagnostic 1 — A/Yes positional bias quantification (COMPLETE 2026-05-24 PM, hypothesis REJECTED).**
Driver: `scripts/quantify_sub5b_positional_bias.py`. Outputs: `diagnostics/sub5b_bias_quantification/report.md` + `details.csv`.

| FOI status | n | bool Yes % | mc A % |
|---|---:|---:|---:|
| clean | 784 | 45.7% | 22.8% |
| partial | 615 | **59.7%** | 21.5% |
| bypassed | 584 | 42.2% | 25.9% |
| missing_video | 17 | 100% Yes | — |

- Bypassed rows are NOT A/Yes-skewed at full-val scale (bool slightly No-heavy, MC A near uniform). The audit slice's pattern was selection-bias artifact.
- On bypass rows, Sub #5B and Sub #1 distributions are nearly identical (no positional-prior delta vs baseline).
- Counterfactual swap of Sub #5B → Sub #1 on bypass rows estimates **−0.67 pp** (and **−1.65 pp** if applied to bypass+partial). Blind fallback rejected.
- Real Yes-skew lives in **partial NSVS rows** (615 rows, +14 pp Yes vs clean) and the **`unknown` operator family** (66.4% Yes on bool, n=460). These are likely a downstream consequence of PULS failures — Diagnostic 2 picks this up directly.

**Diagnostic 2 — PULS spec analysis on `unknown` family (COMPLETE 2026-05-24 PM, PULS LEVER CONFIRMED).**
Driver: `scripts/analyze_puls_unknown_bypassed.py`. Outputs: `diagnostics/puls_unknown_analysis/report.md` + `details.csv` (416 rows).

| Category | n | % | Lever |
|---|---:|---:|---|
| spec_un_groundable | 173 | **41.6%** | **PULS prompt fix** |
| spec_partial | 133 | 32.0% | Storm/temporal aggregation |
| spec_ok_no_detect | 110 | 26.4% | Detector swap (Diagnostic 3 in flight) |

Top reasons within `spec_un_groundable`:
- **94 rows: `empty_puls_output`** — PULS returns no spec/props at all, mostly on MC prompts. Hard PULS failure.
- **54 rows: `operator_collapse_open_ended`** — Wh-questions (What/Which/How) with temporal cues compressed to a single proposition with no UNTIL. Confirms the operator-collapse finding from 2026-05-21 at scale on a specific slice.
- 13 rows: `relation_not_in_spec` — co-occurrence/overlap questions emitted without proper AND/UNTIL.

**Next val-submission lever (validated):** PULS prompt tuning targeted at (a) why PULS emits empty output on MC `unknown` questions (94 rows), and (b) how to preserve operator semantics for Wh+temporal questions (54 rows). `unknown` is 23% of val (n=460); if we rescue half of the 173 un-groundable rows to produce well-formed specs that get baseline-grade answers, ~3-4 pp of val accuracy. Overnight Cursor brief at `diagnostics/puls_unknown_analysis/OVERNIGHT_PULS_PREP.md` extracts the 94+54 rows for AM review.

**Diagnostic 3 — GPT-5.2 NSVS detection backend swap (IN FLIGHT, ETA 2026-05-25 AM).**
50-question stratified val subsample (35 disagreements + 15 both-wrong). Cost ~$200 (SP-approved API directive). Targets the `spec_ok_no_detect` slice (110 rows of bypass `unknown` — smaller than originally framed once Diagnostic 2 segmented the failure modes). See `scripts/answer_cropped_entries.py` + commit e341e85.

**Combined Diagnostic 1+2 narrative for the writeup:** the audit's apparent positional-prior signal was a selection-bias artifact, but the underlying Yes-skew on partial/`unknown` rows is real and is likely a downstream consequence of PULS failures (empty output, operator collapse). Fixing PULS upstream may resolve the downstream skew without touching the answer layer.

### Disagreement by FOI Status (Sub #5B)

| FOI status | Disagree / Total | Disagree % |
|---|---:|---:|
| non-`-1` FOI | 355 / 1399 | **25.38** |
| `-1` FOI | 109 / 584 | **18.66** |

Interpretation: valid FOI rows still change answers more often than `-1` rows, but the **net** score delta is strongly positive — ffmpeg crop + 16-frame VQA on the retrieved segment beats full-video 8-frame sampling on this benchmark when FOI ordering is fixed.

### Disagreement by Source Dataset (Sub #5B)

| Source | Disagree / Total | Disagree % |
|---|---:|---:|
| `bf` | 123 / 500 | **24.60** |
| `ct` | 117 / 500 | **23.40** |
| `star` | 115 / 500 | **23.00** |
| `agqa` | 109 / 500 | **21.80** |

## Current Interpretation

- **Sub #5B is the new best at 53.35%** (+2.85 vs Sub #1). Fixed FOI ordering + 3fps NSVS + ffmpeg crop + gpt-5.2 on crops beats the full-video baseline.
- **Sub #6 hybrid routing (5B + Sub #1 fallback) did not beat pure 5B**: 6A **52.85%**, 6B **52.60%**. Use pure Sub #5B stack for test.
- Sub #2's 48.75% used **contaminated FOI merge** (target-ID before NSVS on placeholder windows). Do not treat it as the final NeuS-QA verdict.
- Downstream VQA used **gpt-5.2 API** (not paper Qwen2.5-VL-7B) due to GPU driver mismatch; NeuS-QA is model-agnostic for the answerer — label accordingly in the report.
- **Test submission ready:** `sub5b_test_3fps/submission_sub5b_test_gpt52.json` — 3000 rows, pure Sub #5B stack; distribution check passed; **first EvalAI test upload pending**.
- **STAR/agqa time-warp:** sub-second clips show impossible motion at 1×; temporal operators (immediately_after, since) may collapse. Stratify analysis by source; spot-check at 0.25×.

## Sub #6 Hybrid Routing (complete)

Script: `scripts/build_sub6_hybrid_routing.sh` · `scripts/build_routed_submission.py` (`foi_clean_proxy`)

Output: `/mnt/Data/ah66742/timelogic/outputs/sub6_hybrid_routing/`

Routes between Sub #1 (`baseline_cpu_v01`) and Sub #5B using Sub #5B merged FOI metadata.

| Variant | EvalAI val | Routed to 5B | Routed to Sub #1 | vs pure 5B |
|---|---:|---:|---:|---:|
| 6A `foi_confidence_proxy` | **52.85** | 877 | 1123 | −0.50 |
| 6B `foi_clean_proxy` | **52.60** | 633 | 1367 | −0.75 |

Interpretation: falling back to full-video Sub #1 on uncertain FOI costs more than it saves vs always trusting cropped Sub #5B answers.

## Sub #3 Routed Candidates

Script: `scripts/build_routed_submission.py`

Output directory: `/home/ah66742/timelogic-data/outputs/routed_sub3/`

Both candidates are pure post-processing; they read Sub #1 answers, Sub #2 answers, and Sub #2 merged metadata/FOI, then emit EvalAI-ready JSON. They do not rerun NSVS, VQA, or any API calls.

### Sub #3A — FOI Confidence Proxy

Requested target idea: Storm-probability gate. Current limitation: Sub #2 artifacts do **not** store raw Storm satisfaction probabilities; the code only persisted thresholded qualitative results and final FOI. Therefore this candidate uses an available no-rerun proxy:

- Trust Sub #2/NSVS when FOI is valid, at least 1 second long, and covers `<95%` of the full video.
- Otherwise trust Sub #1/full-video.

Output: `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3a_foi_proxy.json`

Summary:

| Source | Count |
|---|---:|
| Sub #1/full-video | 1188 |
| Sub #2/NSVS | 812 |

Route reasons:

| Reason | Count |
|---|---:|
| usable cropped FOI proxy -> Sub #2 | 812 |
| invalid or `-1` FOI -> Sub #1 | 822 |
| FOI near full video -> Sub #1 | 214 |
| FOI too short -> Sub #1 | 135 |
| missing NSVS entry -> Sub #1 | 17 |

Validation:

- Rows: 2000
- Unique question IDs: 2000
- Annotation order preserved: yes
- Invalid answers: 0
- Answer distribution: bool `No=462`, `Yes=338`; MC `A=256`, `B=328`, `C=326`, `D=290`

### Sub #3B — Hard Bucket Gate

Rule:

- If `source_dataset == "bf"` and `mode == "mc"` and `duration > 60s`, trust Sub #1/full-video.
- Otherwise trust Sub #2/NSVS.

Output: `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3b_bf_mc_gt60.json`

Summary:

| Source | Count |
|---|---:|
| Sub #1/full-video | 367 |
| Sub #2/NSVS | 1633 |

Validation:

- Rows: 2000
- Unique question IDs: 2000
- Annotation order preserved: yes
- Invalid answers: 0
- Answer distribution: bool `No=467`, `Yes=333`; MC `A=269`, `B=324`, `C=299`, `D=308`

Sub #3A/#3B uploaded; neither beat Sub #1. Sub #4 uploaded at 50.20.

## Probe calibration (staged, not submitted)

**PI constraint:** do not upload constant all-`A` / all-`Yes` — EvalAI may flag it.

| Artifact | Path |
|---|---|
| Submission | `/home/ah66742/timelogic-data/outputs/probe_calibration/submission.json` |
| README + manifest | same dir |
| Builder | `scripts/build_probe_calibration_submission.py` |

Method: deterministic pseudo-random answer per `question_id` (~25% per MC letter, ~50% Yes/No). Intended use: **random-guess baseline** (~32–35% val) if uploaded once with approval — not for per-letter GT priors.

**Blocked on:** nothing — Sub #5B scored 53.35%; primary comparison complete.

## Recommended Next Steps

1. **Upload test submission** — `sub5b_test_3fps/submission_sub5b_test_gpt52.json` to EvalAI test phase.
2. **Human-tag** 25-row audit packet (v2); star/agqa at 0.25× playback.
3. **Sub #5C (planned):** CoT VQA rerun on Sub #5B crops — reuse NSVS, API-only.
4. Operator-aware PULS prompts; STAR/agqa time-warp caveat in report.
5. Log Storm satisfaction probabilities for principled routing (future Sub #7).
6. Fix GPU driver on `ece-859525` only if paper-exact Qwen ablation is needed.
