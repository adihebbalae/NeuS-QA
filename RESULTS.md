# TimeLogic Results Ledger

Central source of truth for important validation runs, diagnostics, and current interpretation.

Last updated: 2026-05-20.

## Current best

| Rank | Submission | EvalAI val AvgAcc | Delta vs best | Status |
|---|---|---:|---:|---|
| 1 | Sub #1: `baseline_cpu_v01` | **50.50** | 0.00 | Current best |
| 2 | Sub #2: `nsvs_sub2_v2` | **48.75** | -1.75 | NSVS interval retrieval underperformed baseline |

## Submission Runs

| # | Run | Pipeline | Main artifacts | Notes |
|---|---|---|---|---|
| 1 | `baseline_cpu_v01` | PULS with `gpt-5.2`, no GPU/NSVS, 8 full-video frames to `gpt-5.2` vision answerer | `/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json` | 2000/2000 EvalAI rows. 1983 videos answered normally; 17 missing-video defaults. Wall time ~154.8 min. |
| 2 | `nsvs_sub2_v2` | PULS + target identification with `gpt-5.2`; InternVL2-8B NSVS; answerer samples `frames_of_interest` with `gpt-5.2` vision | `/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2/submission_sub2.json` | 8 GPU shards. 1983 processed videos merged; 17 missing-video defaults. |
| 3A candidate | `routed_sub3/submission_sub3a_foi_proxy.json` | Post-processing only: route between Sub #1 and Sub #2 using available FOI quality as a confidence proxy | `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3a_foi_proxy.json` | Not a true Storm-probability gate; raw Storm probabilities were not saved in Sub #2 artifacts. |
| 3B candidate | `routed_sub3/submission_sub3b_bf_mc_gt60.json` | Post-processing only: route `bf` + `mc` + `>60s` to Sub #1; all other rows to Sub #2 | `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3b_bf_mc_gt60.json` | Hard-bucket carve-out from the Sub #1 vs Sub #2 diagnostic. |

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

## Current Interpretation

- The current best is still the full-video CPU/API baseline (`baseline_cpu_v01`).
- Sub #2 did run the substantive NeuS-QA retrieval path: PULS, target identification, InternVL2-8B proposition detection, NSVS model checking, and FOI-guided answer sampling.
- Sub #2 did **not** perform literal `ffmpeg` paper-style cropping. It sampled frames from the computed FOI inside the original video.
- The biggest degradation signal is not simply "NSVS failed to find FOI." Rows with non-`-1` FOI actually disagree more with the baseline than `-1` FOI rows.
- The strongest suspect bucket is long Breakfast multiple-choice videos (`bf`, `>60s`, `mc`), where NSVS changes answers frequently.
- A hybrid policy is likely the next high-signal experiment: use full-video baseline for risky buckets and use NSVS only where it appears beneficial.

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

Recommendation before upload: submit **Sub #3B first** if spending one val submission, because it directly tests the strongest observed degradation bucket while preserving most of Sub #2. Submit Sub #3A if we want a more conservative retrieval-confidence proxy, but do not describe it as Storm-probability gating in the report.

## Recommended Next Diagnostics

1. Build a no-submission hybrid JSON by taking Sub #1 answers for high-risk buckets (`bf`, `mc`, `>60s`, or non-`-1` FOI on `bf`/`ct`) and Sub #2 answers elsewhere. This cannot be scored locally without ground truth, but it defines candidate policies for the next EvalAI run.
2. Run a small paper-crop audit on 100-200 rows: full-video frames vs FOI frame sampling vs literal `ffmpeg` cropped clip. This tests whether physical cropping matters independently of the retrieval quality.
3. Inspect a sample of high-risk disagreements from `diagnostics/sub1_vs_sub2/disagreements.csv`, especially `bf >60s mc` with non-`-1` FOI.
4. In parallel, continue the safer baseline-improvement track: more frames, self-consistency, and reasoning-effort sweeps on the full-video answerer.
