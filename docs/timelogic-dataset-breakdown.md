# TimeLogic Val & Test Video Benchmark — Detailed Breakdown

Reference doc for the **CVPR 2026 VidLLMs Workshop TimeLogic Challenge** dataset (EvalAI [#2690](https://eval.ai/web/challenges/challenge-page/2690/overview)). Subset of the full **TimeLogic / TLQA** benchmark from [*TimeLogic: A Temporal Logic Benchmark for Video QA*](https://arxiv.org/abs/2501.07214) (Jan 2025).

On this server, data lives under **`/mnt/Data/ah66742/timelogic/`** (~98 GB total).

Last updated: 2026-05-22.

---

## 1. High-level summary

| | **Val (dev)** | **Test** |
|---|---|---|
| **Purpose** | Development + private EvalAI scoring | Final leaderboard + prize eligibility |
| **QA pairs** | **2,000** | **3,000** |
| **Unique videos referenced** | **940** | **1,850** |
| **Answer types** | 1,200 MC + 800 bool | 1,878 MC + 1,122 bool |
| **Ground-truth labels** | **Not released** | **Not released** |
| **EvalAI submission budget** | 800 total, 50/day | 1,000 total, 100/day |
| **Video coverage on disk** | **17 missing** (all `ct_*`) | **0 missing** (staged 2026-05-22) |

The challenge tests **16 temporal-logic operators** (Before, After, Until, Since, ordering chains, etc.) expressed as natural-language questions over video. Questions are either **multiple-choice (A–D)** or **Yes/No**.

---

## 2. Where the files live

### Annotations (JSON)

| Split | Path | Size |
|---|---|---|
| Val | `/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json` | 697 KB |
| Test | `/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json` | 1.06 MB |

Upstream mirror (val only): `/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json` — **MD5-identical** to local val.

**Download URLs:**
- Val videos: `https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/val_videos.zip` (23.4 GB)
- Test videos: `.../test/test_videos.zip` (~23 GB)
- Test JSON: `.../test/timelogic_test_data.json`

### Videos (MP4/AVI)

| Split | Directory | Files | Size | Formats |
|---|---|---|---|---|
| Val | `videos/val/combined_2k_videos/` | **2,032** | 22 GB | 1,705 `.mp4` + 327 `.avi` (all `bf_*`) |
| Test | `videos/test/benchmark_test_videos_json/` | **1,850** | 23 GB | all `.mp4` |

Raw zips: `raw/val_videos.zip`, `raw/test_videos.zip`.

**Important:** The val zip ships **1,109 extra video files** not referenced by any of the 2,000 questions. Only **940 unique `video_id`s** appear in the val JSON.

### Env vars (from setup.md)

```
TIMELOGIC_VAL_VIDEOS  → .../videos/val/combined_2k_videos
TIMELOGIC_TEST_VIDEOS → .../videos/test
TIMELOGIC_VAL_ANN     → annotation path
TIMELOGIC_TEST_ANN    → annotation path
```

---

## 3. Annotation schema (the only 4 fields)

Every entry is a flat dict with **exactly 4 keys**. There is no separate options array, no operator label, no duration, no resolution, and **no answer**.

```json
{
  "question_id": "1",
  "video_id": "agqa_9A58F.mp4",
  "mode": "bool",
  "question": "Is it true that person throwing shoes somewhere occurs before ..."
}
```

| Field | Type | Notes |
|---|---|---|
| `question_id` | string | `"1"` … `"2000"` (val) or `"3000"` (test). Must be preserved verbatim in submissions. |
| `video_id` | string | Filename of the video file. Prefix before first `_` = source dataset. |
| `mode` | `"mc"` \| `"bool"` | Answer format for EvalAI. |
| `question` | string | Full natural-language question. MC options are embedded in the string. |

### Bool questions (~40% val, ~37% test)

Typical phrasing patterns (val bool first-word counts):

| Starter | Val count | Test count |
|---|---|---|
| `Is` | 316 | 511 |
| `Did` | 307 | 418 |
| `Does` | 111 | 47 |
| `Do` | 37 | 88 |
| `Has` | 29 | 58 |

Example bool (ordering chain):

```json
{
  "question_id": "1",
  "video_id": "agqa_9A58F.mp4",
  "mode": "bool",
  "question": "Is it true that person throwing shoes somewhere occurs before person taking a laptop from somewhere and which in turn occurs before person closing a laptop ?"
}
```

Example bool (eventual):

```json
{
  "question_id": "3",
  "video_id": "bf_P25_cam01_P25_sandwich.mp4",
  "mode": "bool",
  "question": "Does the person eventually carry knife ?"
}
```

Example bool (implies):

```json
{
  "question_id": "1",
  "video_id": "star_H8S4L.mp4",
  "mode": "bool",
  "question": "Does the person taking/consuming some medicine imply holding a laptop ?"
}
```

**Submission answers:** `"Yes"` or `"No"`.

### Multiple-choice questions (~60% val, ~63% test)

Fixed boilerplate template:

```
The following is a multiple choice question with four possible answer choices: A, B, C, D.
<temporal question>
Is it Option A: ..., Option B: ..., Option C: ..., Option D: ....
Reply with the chosen option in one character.
```

Example MC (`always_before` + ordering chain):

```json
{
  "question_id": "2",
  "video_id": "bf_P13_webcam01_P13_scrambledegg.mp4",
  "mode": "mc",
  "question": "The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person melting butter which in turn always occurs before person pouring salt ? Is it Option A: carry butter, Option B: carry bowl, Option C: carry pepper, Option D: pour salt. Reply with the chosen option in one character."
}
```

Example MC (`until`):

```json
{
  "question_id": "8",
  "video_id": "ct_zlyrv-h97z8.mp4",
  "mode": "mc",
  "question": "... What did the person do until got things out ? Is it Option A: jack down, Option B: get things out, ..."
}
```

**MC parsing:** Loader regex extracts all 4 option texts — **100% success** on both splits (1200/1200 val, 1878/1878 test).

**Submission answers:** `"A"`, `"B"`, `"C"`, or `"D"`.

### Question text length

| Stat | Val | Test |
|---|---|---|
| Min chars | 36 | 39 |
| Median | 305 | 300 |
| Mean | 236 | 241 |
| Max | 417 | 428 |

---

## 4. Val vs test — structural differences

### Scale and balance

| Metric | Val | Test |
|---|---|---|
| Total questions | 2,000 | 3,000 |
| MC / bool | 1200 / 800 (60/40) | 1878 / 1122 (62.6/37.4) |
| Unique videos | 940 | 1,850 |
| Avg questions per video | ~2.1 | ~1.62 |
| Max questions on one video | **47** | 9 |

**Questions-per-video distribution (val):**

| Qs/video | # videos |
|---|---|
| 1 | 526 |
| 2 | 225 |
| 3 | 96 |
| 4 | 39 |
| 5+ | 54 |
| max | 47 |

Test is more **one-question-per-video** (1,062 of 1,850 videos have exactly 1 question).

### Source dataset balance

Val is **perfectly balanced** — exactly 500 questions per source:

| Source | Val total | Val bool | Val MC | Test total | Test bool | Test MC |
|---|---|---|---|---|---|---|
| **agqa** | 500 | 244 | 256 | 760 | 343 | 417 |
| **bf** | 500 | 90 | 410 | 734 | 109 | 625 |
| **ct** | 500 | 262 | 238 | 729 | 374 | 355 |
| **star** | 500 | 204 | 296 | 777 | 296 | 481 |

Test is **slightly uneven** (~730–777 per source). Val was designed as a balanced diagnostic set; test is larger and less strictly controlled.

### Mode × source skew (important for routing)

| Source | Val bool% | Val MC% | Notes |
|---|---|---|---|
| **agqa** | 49% | 51% | Roughly even |
| **bf** | **18%** | **82%** | Heavily MC — long cooking videos |
| **ct** | 52% | 48% | Roughly even |
| **star** | 41% | 59% | Slightly MC-heavy |

**bf** is the standout: 410/500 val questions are MC on long videos. This drives hybrid routing logic (`bf ∨ mc ∨ >60s`).

---

## 5. The four underlying video sources

Each `video_id` is `{source}_{original_id}.mp4`:

| Prefix | Dataset | Content | Typical length |
|---|---|---|---|
| **agqa** | [AGQA](https://arxiv.org/abs/2105.08276) | Indoor scene-graph activities | **~1–2 s** clips |
| **bf** | [Breakfast](https://serre-lab.clps.brown.edu/resource/breakfast-actions-dataset/) | Kitchen cooking actions | **~3–10 min** |
| **ct** | [CrossTask](https://github.com/crossdomain/crosstask) | YouTube instructional tasks | **~4–10 min** |
| **star** | [STAR](https://star.csail.mit.edu/) | Situation hypergraphs | **~1–2 s** clips |

Naming examples:
- `agqa_9A58F.mp4`
- `bf_P13_webcam01_P13_scrambledegg.mp4`
- `ct_zlyrv-h97z8.mp4`
- `star_H8S4L.mp4`

On-disk file counts in val zip (includes unused extras):

| Prefix | Files on disk (val zip) |
|---|---|
| bf | 654 |
| agqa | 483 |
| star | 449 |
| ct | 446 |

---

## 6. Video metadata (not in JSON — measured from files)

Annotations carry **zero** video metadata. Duration, fps, and resolution must be read at runtime (OpenCV/ffprobe).

### Duration statistics (val, 1,983 measured entries)

From `/mnt/Data/ah66742/timelogic/outputs/duration_sweep_val.json`:

| Stat | All val entries | agqa | star | bf | ct* |
|---|---|---|---|---|---|
| **Median** | **3.16 s** | 1.32 s | 1.48 s | 194.2 s | 247.4 s |
| **Mean** | 118.1 s | 1.39 s | 1.51 s | 197.5 s | 277.5 s |
| **Min** | 0.16 s | 0.16 s | 0.16 s | 20.5 s | 42.3 s |
| **Max** | 612.4 s | 4.0 s | 4.4 s | 546.5 s | 612.4 s |
| **p90** | 344.9 s | 2.2 s | 2.4 s | 361.2 s | 510.8 s |

\*ct: 483 measured (17 questions reference missing files)

**Duration buckets (entry-level):**

| Bucket | Val | Test |
|---|---|---|
| **≤30 s** | 1,003 (50.2%) | 1,577 (52.6%) |
| **30–60 s** | 65 (3.3%) | 155 (5.2%) |
| **>60 s** | 915 (45.8%) | 1,268 (42.3%) |
| Missing/unreadable | 17 | 0 |

**Short-clip threshold (≤2 s):** 799 val entries.

**Bimodal distribution:** Half the questions sit on **1–2 second** agqa/star clips; nearly half sit on **multi-minute** bf/ct cooking/instruction videos. This is the central difficulty for interval-based methods (FOI cropping helps long videos but is meaningless on 1-second clips).

### FPS and resolution (sampled, 15 videos per source)

| Source | Typical FPS | Typical resolution |
|---|---|---|
| **agqa** | 25 fps | 320×240, 320×180, 180×320 |
| **star** | 25 fps | 320×180, 320×240, 180×320 |
| **bf** | 15 fps | 320×240, 320×180 |
| **ct** | 24–30 fps | **1280×720**, 640×360 |

Resolution and fps are **not standardized** across the benchmark — they inherit from each source dataset.

---

## 7. Temporal logic taxonomy (paper's 16 operators)

The challenge covers the **16 temporal-logic categories** from the TimeLogic paper, organized into 5 complexity levels:

| Level | Operators |
|---|---|
| 1 | **Eventual** — E(X) |
| 2 | **Always** — G(X) |
| 3 | **Until**, **Since**, **Disjoint**, **Implies**, **Co-Occur**, **Before/After** (Next) |
| 4 | **Immediately Before/After**, **Always Before/After**, **Always Co-Occur** |
| 5 | **Compounding Strict Ordering** (X AB Y AB Z), **Loose Ordering** (X<Y<Z), **X always before (Y,Z)** |

**Critical limitation:** The released JSON has **no per-question operator label**. You only get natural-language phrasing. The loader infers an `operator_guess` via regex heuristics (`nsvqa/datamanager/timelogic.py`) — diagnostic only, not ground truth.

### Heuristic operator breakdown (val)

| Operator guess | Count | % |
|---|---|---|
| `always_before` | 735 | 36.8% |
| `unknown` | 452 | 22.6% |
| `in_turn_occurs` | 125 | 6.2% |
| `until` | 124 | 6.2% |
| `before` | 118 | 5.9% |
| `after` | 114 | 5.7% |
| `always_after` | 112 | 5.6% |
| `immediately_after` | 89 | 4.5% |
| `since` | 67 | 3.4% |
| `while` / `when` | 32 each | 1.6% |

### Heuristic operator breakdown (test)

| Operator guess | Count | % |
|---|---|---|
| `always_before` | 825 | 27.5% |
| `in_turn_occurs` | 549 | 18.3% |
| `unknown` | 373 | 12.4% |
| `when` | 252 | 8.4% |
| `until` | 185 | 6.2% |
| `before` | 161 | 5.4% |
| `immediately_after` | 157 | 5.2% |
| `after` | 155 | 5.2% |
| `always_after` | 136 | 4.5% |
| `since` | 112 | 3.7% |
| `while` | 95 | 3.2% |

Test has **more ordering-chain questions** (`in_turn_occurs` jumps from 6% → 18%) and fewer `unknown` (23% → 12%).

Many paper operators (Eventual, Disjoint, Implies, Co-Occur, compounding chains) either map to `unknown` or overlap with broader heuristics like `always_before`.

---

## 8. What is NOT in the dataset

| Missing field | Impact |
|---|---|
| Ground-truth answers | **Cannot score locally.** All accuracy numbers require EvalAI submission. |
| Operator label | Per-operator accuracy must be inferred from question text. |
| `candidates` array | MC options parsed from question string at load time. |
| Video duration/fps/resolution | Read from MP4 at runtime. |
| Train split | Challenge provides **val + test only** (no public training set with labels). |
| Frame indices / FOI | **Pipeline artifact**, not dataset field. Produced by NSVS/Storm. |

---

## 9. Submission format (EvalAI output)

```json
[
  {"question_id": "1", "answer_choice": "D"},
  {"question_id": "2", "answer_choice": "Yes"}
]
```

- One entry per question (2,000 val / 3,000 test).
- Metric: **Overall Accuracy (AvgAcc)** — simple accuracy across all questions.
- MC answers: single character `"A"`–`"D"`.
- Bool answers: `"Yes"` or `"No"`.

Written by `TimeLogic.write_submission()` / `scripts/build_submission.py`.

---

## 10. Known data issues

### 17 missing val videos (all CrossTask)

These `video_id`s are in the val JSON but **absent from the official val zip**:

```
ct_sBJJ0Cj0GG4.mp4, ct_Sm-Er9tMi8g.mp4, ct_XhZnEq3mJy4.mp4,
ct_7MWzU--xApU.mp4, ct_yyIOce1XvpY.mp4, ct_MEYXUyEXd88.mp4,
ct_Mlscv4JxrfU.mp4, ct_ygv6jXn59t8.mp4, ct_GbgRRMMJHTU.mp4,
ct_Uj0WzaLGg3Y.mp4, ct_78c2HuuwmVA.mp4, ct_VEjQ3lIZIb4.mp4,
ct_BtDvFEFiQ5k.mp4, ct_L0MVdMNihGI.mp4, ct_LKd2oIsM3uE.mp4,
ct_1jqTfi145xQ.mp4, ct_I-9uVsmWoEU.mp4
```

Impact: **17/2000 = 0.85%** of val rows. Pipeline answers these with a **default fallback** (typically `"A"` for MC, `"No"` for bool).

### 1,109 extra val videos on disk

The val zip contains 2,032 files but only 940 unique IDs are referenced. The extras are unused clips shipped with the source datasets.

### bf videos as AVI

327 Breakfast videos are `.avi` (not `.mp4`) in the val zip. The loader checks filename presence by exact `video_id` match — these work if the JSON references the `.avi` name.

### Test is complete

Test staging marker: `TEST_DATA_STAGED` (2026-05-22). **0/3000 missing**, all 1,850 referenced videos present.

---

## 11. Pipeline-relevant buckets (not official labels)

Conventions used in the NeuS-QA fork for analysis and hybrid routing:

### Duration buckets

| Bucket | Val entries | Test entries |
|---|---|---|
| ≤30 s | 1,003 | 1,577 |
| 30–60 s | 65 | 155 |
| >60 s | 915 | 1,268 |

### Hybrid routing bucket (`bf ∨ mc ∨ >60s`)

| Condition | Val | Test |
|---|---|---|
| source = bf | 500 | 734 |
| mode = mc | 1,200 | 1,878 |
| duration >60s | 915 | 1,268 |
| **Any of above (overlap)** | **1,531** | **2,358** |

~**77% of val** and ~**79% of test** fall into this routing bucket.

### FOI (frames of interest)

Not a dataset field. NSVS + Storm temporal model-checking produces `[start_frame, end_frame]` intervals. On val Sub #5B (best run): **70.6% valid FOI** on processed entries. Coverage varies heavily by source:

| Source | FOI valid rate (Sub #5B) | Median FOI span |
|---|---|---|
| bf | 91.2% | 31.1 s |
| ct | 83.0% | 42.8 s |
| star | 55.2% | 1.4 s |
| agqa | 53.2% | 1.4 s |

---

## 12. Full TLQA paper scale vs challenge subset

The paper defines a much larger benchmark:

| Scale | Per source dataset | Total (4 sources) |
|---|---|---|
| Small | 32k QA (16 operators × 2k each) | 128k |
| Large | 160k QA (16 operators × 10k each) | 640k |

Full scale: 50/50 bool/MC balance, all 16 operators explicitly represented.

**Challenge subset:** 2k val + 3k test = **5k total**, a curated slice for the workshop. Operator coverage is implicit in question phrasing, not explicitly balanced per operator.

---

## 13. EvalAI context (leaderboard snapshot)

From project docs (2026-05-19):

**Val leaders:** ~62–65% (top teams). Host baseline (Qwen3VL): 43.15%.

**Test leaders:** anmspro 56.80%, host baseline 39.97%.

**Best val score (this fork):** **53.35%** (Sub #5B, paper-faithful 3fps pipeline).

Clearing the host baseline is straightforward; winning requires ~57%+ on test with a clean technical report.

---

## 14. Loader behavior (what NeuS-QA adds)

The loader at `nsvqa/datamanager/timelogic.py` transforms each raw entry into:

```python
{
  "question": "...",
  "candidates": ["Yes", "No"] or [optA, optB, optC, optD],
  "paths": {"video_path": "/full/path/to/video.mp4"},
  "metadata": {
    "question_id": "1",
    "video_id": "agqa_9A58F.mp4",
    "mode": "bool",
    "source_dataset": "agqa",      # prefix before first _
    "operator_guess": "before",    # regex heuristic
    "video_present": True,
    "cleaned_question": "...",     # MC scaffolding stripped for PULS
  }
}
```

After the full pipeline, entries also carry `puls`, `target_identification`, `nsvs`, `frames_of_interest`, and runtime `metadata.fps` / `metadata.frame_count`.

---

## 15. Key reference files

| File | What it tells you |
|---|---|
| `annotations/timelogic_{val,test}_data.json` | Raw benchmark |
| `outputs/duration_sweep_val.json` | Full duration stats by source/operator |
| `outputs/diagnostics/sub5b_fix2_nsvs_by_bucket/nsvs_by_bucket.json` | FOI coverage by bucket |
| `nsvqa/datamanager/timelogic.py` | Schema, MC parsing, operator inference |
| `RESULTS.md` | Submission scores + diagnostic breakdowns |
| [TimeLogic paper](https://arxiv.org/abs/2501.07214) | 16-operator taxonomy |
| [Challenge repo](https://github.com/Swetha5/TimeLogic) (branch `challenge`) | Official data source |

---

**Bottom line:** The benchmark is a lean **4-field JSON + MP4** pairing with no local labels. Val is a **balanced 2k diagnostic set** (500/source) with 17 known missing ct videos; test is a **larger 3k set** with complete coverage. The hardest structural feature is the **bimodal duration distribution** — half the questions sit on 1–2 second clips (agqa/star) and half on multi-minute cooking/instruction videos (bf/ct) — which makes any single pipeline strategy (full-video vs FOI-crop) a compromise rather than a universal win.
