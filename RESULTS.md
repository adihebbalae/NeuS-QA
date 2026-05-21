# TimeLogic Results Ledger

Central source of truth for important validation runs, diagnostics, and current interpretation.

Last updated: 2026-05-21.

## Current best

| Rank | Submission | EvalAI val AvgAcc | Delta vs best | Status |
|---|---|---:|---:|---|
| 1 | Sub #1: `baseline_cpu_v01` | **50.50** | 0.00 | Current best |
| 2 | Sub #4: `sub4_tiebreak_gpt52` | **50.20** | -0.30 | Tiebreaker on 452 disagreements; did not beat baseline |
| 3 | Sub #3A: FOI proxy routing | **49.00** | -1.50 | Post-process only |
| 4 | Sub #3B: `bf+mc+>60s` routing | **48.95** | -1.55 | Post-process only |
| 5 | Sub #2: `nsvs_sub2_v2` | **48.75** | -1.75 | NSVS + gpt-5.2 on FOI frames (not paper crop/VQA) |

## Submission Runs

| # | Run | Pipeline | Main artifacts | Notes |
|---|---|---|---|---|
| 1 | `baseline_cpu_v01` | PULS with `gpt-5.2`, no GPU/NSVS, 8 full-video frames to `gpt-5.2` vision answerer | `/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json` | 2000/2000 EvalAI rows. 1983 videos answered normally; 17 missing-video defaults. Wall time ~154.8 min. |
| 2 | `nsvs_sub2_v2` | PULS + target identification with `gpt-5.2`; InternVL2-8B NSVS; answerer samples `frames_of_interest` with `gpt-5.2` vision | `/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2/submission_sub2.json` | 8 GPU shards. 1983 processed videos merged; 17 missing-video defaults. EvalAI val **48.75**. |
| 3A | `routed_sub3/submission_sub3a_foi_proxy.json` | Post-processing: FOI-quality proxy routes 1188→Sub #1, 812→Sub #2 | `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3a_foi_proxy.json` | EvalAI val **49.00**. Not true Storm-P gate (probabilities not logged). |
| 3B | `routed_sub3/submission_sub3b_bf_mc_gt60.json` | Post-processing: `bf+mc+>60s` → Sub #1; else Sub #2 | `/home/ah66742/timelogic-data/outputs/routed_sub3/submission_sub3b_bf_mc_gt60.json` | EvalAI val **48.95**. Did not beat Sub #1. |
| 4 | `sub4_tiebreak_gpt52/submission_sub4_tiebreak_gpt52.json` | Post-processing: copy 1548 agreements; `gpt-5.2` vision judge on 452 disagreements | `/home/ah66742/timelogic-data/outputs/sub4_tiebreak_gpt52/submission_sub4_tiebreak_gpt52.json` | EvalAI val **50.20**. -0.30 vs Sub #1. |
| 5B (running) | `sub5b_paper_faithful_3fps` | Paper-faithful at **3fps**: `gpt-4o` PULS/target_id, InternVL2-8B, ffmpeg crop, Qwen2.5-VL-7B (16 frames) | `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps/` | tmux `sub5b_paper_faithful_3fps`. 1fps partial abandoned at `sub5b_paper_faithful/` (~20% NSVS). Score TBD. |

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

## Current Interpretation

- The current best is still the full-video CPU/API baseline (`baseline_cpu_v01`) at **50.50**.
- Sub #2–#4 confirm that NSVS-as-implemented and post-hoc fixes do not beat full-video `gpt-5.2` on TimeLogic val.
- Sub #2 did run PULS, target identification, InternVL2-8B, and Storm; it did **not** use paper ffmpeg crop or local Qwen VQA (Sub #5B tests that).
- Non-`-1` FOI rows disagree **more** with Sub #1 than `-1` FOI rows — active NSVS intervals are often harmful, not merely unhelpful.
- **Sub #5B** (paper-faithful at 3fps, in progress) is the clarity run: paper stack without `gpt-5.2` substitutes; restarted from 1fps because sparse sampling likely under-served short TimeLogic clips.

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

## Recommended Next Steps

1. Complete **Sub #5B** (`sub5b_paper_faithful_3fps` tmux) and upload when `DONE` appears.
2. Continue full-video baseline sweeps: more frames, self-consistency, reasoning effort.
3. Operator-aware PULS prompts / proposition templates given the grounding audit.
4. Log Storm satisfaction probabilities in future NSVS runs for principled confidence routing (Sub #6).
