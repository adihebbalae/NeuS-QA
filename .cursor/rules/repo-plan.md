# NeuS-QA Repo — Edit Plan for TimeLogic Adaptation

Derived from reading `evaluate.py` + README on `UTAustin-SwarmLab/NeuS-QA@main`. Use this as the file-by-file map when starting the implementation. Unknowns that need on-disk verification are flagged at the bottom.

**Where this lives**: `.cursor/rules/repo-plan.md` in `adihebbalae/NeuS-QA` fork. Both laptop and server edit this — be careful with concurrent edits, `git pull --rebase` before pushing.

Last updated: 2026-05-19.

## Pipeline shape (from evaluate.py)

```
data = LongVideoBench().load_data()    # list of entry dicts
for entry in data:
    exec_puls(entry)                   # Step 1: LQ2TL  →  proposition, specification
    exec_target_identification(entry)  # Step 2: temporal-extension predictor (α, β)
    exec_nsvs(entry, sample_rate=1,    # Step 3: video automaton + STORM model check
              device, model)
    exec_merge(entry)                  # Step 4: combine NSVS output + (α, β) → frames_of_interest
postprocess(nsvqa_dir, postprocess_dir, current_split)   # writes per-entry artifacts
# vqa(postprocess_dir, vqa_dir, current_split, vlm_config, eval=True)   # downstream VLM (commented out)
```

The `entry` dict accumulates state across steps. Final keys after pipeline: `puls`, `target_identification`, `metadata` (fps, frame_count, optional error), `nsvs` (output, indices), `frames_of_interest`.

## Module map (from `evaluate.py` imports)

| Path | Role |
| --- | --- |
| `nsvqa/datamanager/longvideobench.py` | `LongVideoBench` loader: `.load_data()` → entry list |
| `nsvqa/datamanager/custom.py` | `Custom` loader: takes `raw_data=[...]` directly; also has `.postprocess_data(nsvqa_dir)` |
| `nsvqa/datamanager/timelogic.py` | **NEW** — `TimeLogic` loader; see implementation in fork |
| `nsvqa/puls/puls.py` | LQ2TL implementation. `PULS(question)` → `{proposition, specification, saved_path}` |
| `nsvqa/target_identification/target_identification.py` | `identify_target(question, candidates, specification, conversation_history)` → `{frame_window, explanation, saved_path}` |
| `nsvqa/nsvs/nsvs.py` | `run_nsvs(video_data, video_path, proposition, specification, device, model)` |
| `nsvqa/nsvs/video/read_video.py` | `Mp4Reader(path, sample_rate)` → `.read_video()` (returns `video_data` dict with `video_info.fps`, `video_info.frame_count`) |
| `nsvqa/nsvs/model_checker/frame_validator.py` | STORM/Stormpy wrapper |
| `nsvqa/nsvs/vlm/obj.py` | VLM wrapper |
| `nsvqa/vqa/vqa.py` | Downstream VLM answering (commented out in evaluate.py; MC-only as-is) |
| `scripts/run_timelogic.py` | **NEW** — TimeLogic-specific pipeline driver (see fork) |

## Defaults baked in (need overriding)

- Proposition VLM (passed as `model` to `run_nsvs`): `"OpenGVLab/InternVL2_5-8B"` (note: 2.5, paper said 2.0) — short-name workaround in our driver
- Output dir: `/nas/mars/experiment_result/nsvqa/9_post_submission/` (UT cluster, must change) — bypassed via `--output-dir` in our driver
- `sample_rate=1` in `exec_nsvs` call (different from paper's 3 fps — verify)
- LongVideoBench is hard-loaded as `loader = LongVideoBench()` with `Custom(...)` commented out
- `puls/llm.py` model default is `gpt-4o` — should be `gpt-5.4-mini` for dev iteration, `gpt-5.4` for val/test runs (per PI's recc)

## Where TimeLogic plugs in — file-by-file

### A. NEW — `nsvqa/datamanager/timelogic.py` ✓ DONE

Loader matches the revised API below. Inherits from `Manager` (for `crop_video` / `speed_adjust`). Parses MC choices via regex (100% match rate). Synthesizes `["Yes","No"]` for bool. Infers operator family for diagnostic bucketing. Marks missing-video entries for default-answer fallback.

### B. EDIT — `evaluate.py`

Three small changes (DEFERRED — we use `scripts/run_timelogic.py` instead, which is cleaner):

1. Add `--dataset {longvideobench, timelogic}` and `--split {val, test}` CLI args.
2. Replace `loader = LongVideoBench()` with a small factory based on `--dataset`.
3. Replace the hardcoded `output_dir = "/nas/mars/..."` with a `--output_dir` arg or env var.

Optional: uncomment the `vqa(...)` call at the bottom — for our submission we need downstream answers, not just `frames_of_interest`.

**Status**: superseded by `scripts/run_timelogic.py`. Only revisit if we need a unified driver across LongVideoBench + TimeLogic.

### C. POSSIBLY EDIT — `nsvqa/vqa/vqa.py`

The paper benchmarks are MC-only. TimeLogic mixes MC and Yes/No. Need to verify (on-disk) whether `vqa(...)`:

- Accepts a `candidates` field that can be `["Yes", "No"]` and prompts correctly, OR
- Needs an explicit `question_type` branch with a different prompt template for booleans.

If the latter, add a branch keyed on `entry["metadata"]["mode"]`. (Lever C in the project plan.)

### D. POSSIBLY EDIT — `nsvqa/puls/puls.py` / `puls/prompts.py`

LQ2TL's few-shot prompt is tuned on LongVideoBench's T3E/E3E/T3O/O3O. TimeLogic has 16 operators (Before, After, Until, Since, …). Two paths:

1. Cheap: trust LQ2TL's generalization, ship as-is, measure per-operator accuracy in val phase, then tune the worst categories.
2. Aggressive (since we're playing to win): add operator-specific few-shot examples upfront, especially for Until/Since which differ from before/after.

**Smoke v4 found path 1 produces bad specs on "X always after Y" agqa questions** (PULS emits `! X` — just the negation). Path 2 is now lever D and is in progress.

### E. POSSIBLY TUNE — temporal extension and threshold

The win-the-prize plan calls for tuning:

- Satisfaction threshold τ (in NSVS / model checker)
- Smoothing γ in `F_b(c) = (1 + e^{-γ(c-τ)})^{-1}`
- α, β temporal extension (currently learned by `identify_target` — could also override)

These are likely config knobs inside `nsvqa/nsvs/nsvs.py` or a config file. Need on-disk inspection.

## Run procedure (current)

```bash
cd /home/ah66742/NeuS-QA
source .venv/bin/activate
python3 scripts/run_timelogic.py \
  --video-root /mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos \
  --ann-path /home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json \
  --output-dir /mnt/Data/ah66742/timelogic/outputs/smoke_vN \
  --device 0 \
  --limit 20 \
  --seed 0 \
  --proposition-model InternVL2-2B
```

For long runs, wrap in tmux per `.cursor/rules/workflow.md`.

## On-disk unknowns — verify these on first clone-and-explore

1. Exact entry schema from `LongVideoBench.load_data()` — what fields does it include? Specifically: does it provide `question_id`, `correct_answer`/`answer_idx`, subtitle paths, anything else?
2. `Custom.postprocess_data()` implementation — is `postprocess_data` the right hook for emitting submission JSON, or is there a separate writer?
3. `vqa(...)` signature in `nsvqa/vqa/vqa.py` — what does it return, what does it expect on each entry, does it write its own JSON?
4. Whether `PULS()` accepts an injectable few-shot prompt / system prompt or it's hardcoded.
5. `pyproject.toml` deps — will `uv sync` succeed cleanly on our compute env? Storm has system-level C++ deps.
6. `sample_rate=1` vs paper's "3 fps" — what unit is `sample_rate` actually using? (Maybe seconds-per-frame, maybe FPS.)
7. Does the lmms-eval path (`scripts/prepare_lmms.py` → `bash vendors/lmms-eval/run_lmms.sh`) supersede the direct `evaluate.py` path, or are they alternatives?

## TimeLogic data schema — verified on-disk

See **Major correction** below.

---

## Verified on-disk (2026-05-19) — addendum

After cloning `Swetha5/TimeLogic@challenge` and reading the actual NeuS-QA fork, several assumptions above need adjusting. The body of this doc is left intact; corrections are gathered here.

### Confirmed about the NeuS-QA repo

- Pipeline shape (`exec_puls` → `exec_target_identification` → `exec_nsvs` → `exec_merge` → `postprocess`) matches what was inferred from the README. Entry-dict accretion behaviour matches.
- Proposition VLM is `OpenGVLab/InternVL2_5-8B` (literal in `evaluate.py:138`).
- Hardcoded output dir `/nas/mars/experiment_result/nsvqa/9_post_submission/` confirmed at `evaluate.py:140`. Hardcoded LongVideoBench paths at `nsvqa/datamanager/longvideobench.py:17-18` and `:70-81`.
- `LongVideoBench.load_data()` filters to a 4-category subset `["T3E","E3E","T3O","O3O"]` (line 21). For TimeLogic we must NOT filter — all 16 operators matter.
- `Manager.crop_video` (ffmpeg-based) and `Manager.speed_adjust` are reusable utilities — our TimeLogic loader inherits from `Manager` to keep them.
- Verified `stormpy==1.11.3` from PyPI works without a custom Storm install on this host. `build_dependency.sh` is not required for the smoke path.

### Correction: `Custom` is partially commented out, not unused

`evaluate.py:89` comments out the `Custom` *loader*. But `evaluate.py:125` (inside `postprocess()`) still instantiates `Custom(postprocess_dir=..., current_split=...)` and calls `.postprocess_data(nsvqa_dir)`. So the active `Custom` path is the post-processor (ffmpeg-crops the satisfying interval out of the video and writes a JSON of cropped paths). For TimeLogic we want our loader to handle both halves itself (load `load_data` + emit submission JSON in `postprocess_data`) rather than relying on `Custom` for the second half.

### Correction: lmms-eval is vendored, not a submodule

The only declared submodule (in `.gitmodules`) is `baselines/videotree` (currently uninitialized — ignore). `lmms-eval` lives as a regular directory at repo root; `build_dependency.sh` moves it to `vendors/lmms-eval/`. For our submission we don't need lmms-eval — we'll call `nsvqa.vqa.vqa.vqa(...)` directly from our driver (or write a small custom answerer that supports bool).

### Major correction: TimeLogic val schema is leaner than the proposed loader API

`upstream/data/val/timelogic_val_data.json` is a list of 2000 dicts with exactly four fields:

```json
{
  "question_id": "1",
  "video_id": "agqa_9A58F.mp4",
  "mode": "bool",
  "question": "Is it true that ... ?"
}
```

Specifically, **missing** from each entry:

- `candidates` — for MC, the four options are baked into the question string in the form `"Is it Option A: <a>, Option B: <b>, Option C: <c>, Option D: <d>. Reply with the chosen option in one character."`. For bool, candidates would be `["Yes", "No"]`.
- `correct_answer` / `correct_choice` — no ground truth in the public val. **We cannot score locally; we must consume EvalAI val submissions (50/day budget) to measure accuracy.**
- Operator label — there is no per-question field naming which of the 16 temporal operators is being tested. Per-operator accuracy breakdowns will have to be inferred from question text (keyword search for `"before"`, `"after"`, `"until"`, `"since"`, `"while"`, `"immediately after"`, etc.).

Distribution: 1200 mc + 800 bool. Source datasets evenly split: `agqa` 500, `bf` (Breakfast) 500, `ct` 500, `star` 500. 940 unique video files (so ~2.1 questions per video on average).

### TimeLogic loader API (as implemented)

```python
class TimeLogic(Manager):
    def __init__(self, split: str = "val", video_root: str = ..., ann_path: str = ...):
        ...

    def load_data(self) -> list[dict]:
        # Each entry produces:
        #   "question": str                 # cleaned question, MC choice block can stay or be stripped
        #   "candidates": list[str]         # for mc: parse 4 options from question text;
        #                                   # for bool: ["Yes", "No"]
        #   "paths": {"video_path": str}    # video_root + entry["video_id"]
        #   "metadata": {
        #       "question_id": str,         # propagate verbatim for the submission JSON
        #       "mode": "mc" | "bool",
        #       "source_dataset": str,      # agqa | bf | ct | star — for per-bucket diag
        #       "operator_guess": str,      # inferred from question keywords; best-effort
        #       "video_present": bool,      # False for the 17/2000 missing videos
        #       "cleaned_question": str,    # MC scaffolding stripped, for PULS
        #   }
        ...

    def postprocess_data(self, nsvqa_dir: str) -> None:
        # Reads nsvqa_output_*.json, calls self.crop_video for each entry,
        # writes postprocess_output_*.json. Submission JSON is written by
        # write_submission once VQA produces the answers.
        ...

    @staticmethod
    def write_submission(answers: list[dict], submission_path: str) -> None:
        # EvalAI-format JSON: [{"question_id": "...", "answer_choice": "A" | "Yes" | ...}, ...]
        ...
```

### Revised `vqa.py` requirement

The paper benchmarks were MC-only, so `nsvqa/vqa/vqa.py` likely lacks a Yes/No branch. For TimeLogic:

- For `mode == "mc"`: pass the (possibly cropped) video + question text + candidates, expect an `"A" | "B" | "C" | "D"` letter back.
- For `mode == "bool"`: pass video + question, candidates `["Yes", "No"]`, expect `"Yes" | "No"`.

The downstream VLM prompt should accept both modes. Cleanest path is a small custom answerer rather than monkey-patching upstream `vqa.py`. (Lever C.)

### Storage and run paths

Replace all `/nas/mars/...` paths with envs from `.cursor/rules/setup.md`:

| Hard-coded | Replace with |
| --- | --- |
| `/nas/mars/dataset/longvideobench/...` | not used for TimeLogic; gated behind `--dataset longvideobench` |
| `/nas/mars/experiment_result/nsvqa/9_post_submission/` | `$TIMELOGIC_OUT/<run-tag>/` via `--output_dir` |
| `/nas/mars/experiment_result/nsvqa/6_formatted_output/...` (in `longvideobench.py::postprocess_data`) | not used for TimeLogic |
| `puls/llm.py` `save_dir=/nas/mars/...` | env var `NSVQA_LLM_HISTORY_DIR` ✓ FIXED |

### Updated submodule / dependency notes

- `pyproject.toml` was edited locally to `requires-python = ">=3.12"` (from `>=3.13`) — see `.cursor/rules/setup.md` for why. Pushed as `b2a848b` on `main`.
- `.venv/` at repo root is the active environment (managed by uv). Don't commit (added to `.gitignore`).
- If/when we re-introduce `build_dependency.sh`, the lmms-eval move at the bottom is the only piece that affects the directory layout.

### Order-of-operations for first smoke test (revised)

1. ✓ Wait for val_videos.zip download to finish on `/mnt/Data/ah66742/timelogic/raw/`.
2. ✓ `unzip val_videos.zip` into `/mnt/Data/ah66742/timelogic/videos/val/`. Verify file count matches the 940 unique `video_id`s in the annotations.
3. ✓ Write `nsvqa/datamanager/timelogic.py` per the revised API above.
4. ✓ Write `scripts/run_timelogic.py` (replaces `evaluate.py` edits for now).
5. ✓ Trim down to ~5 questions (mix of mc + bool, mix of source datasets) for the smoke test.
6. ✓ Run end-to-end without VQA, dump diag JSON, eyeball it.
7. **NEXT**: lever D (TimeLogic-style few-shots in `puls/prompts.py`) → lever A (re-smoke on 20 entries) → lever B (8B device-map fix) → lever C (VQA step) → lever E (parallel sharding).
8. Upload to EvalAI val phase as a private submission to verify scoring works (after lever C produces actual answers).
9. Only then start the full 2000-question val run.

---

## First smoke run — results (2026-05-19)

Drove the pipeline with `scripts/run_timelogic.py`. Five questions, mixed (mc + bool, all four source datasets, varied operators), `InternVL2-2B` as proposition detector on a single A5000.

| qid | mode | src | op | NSVS | foi | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 790 | bool | ct | immediately_after | ok | [11970, 13439] / 13872 | `closes_cap U inserts_dipstick` — sensible spec, found interval |
| 1228 | bool | bf | after | ok | [2025, 2912] / 2913 | `reaches_for_salt U fries_egg` — sensible |
| 1180 | mc | agqa | always_after | ok | [-1] | spec was `! laughs_at_television` — PULS produced negation for "what did they do after"; bad spec quality |
| 756 | bool | agqa | (unknown) | ok | [-1] | `! (stands_up & lies_on_bed)` — sensible negation; very short 38-frame video |
| 1951 | mc | bf | always_before | KeyError | — | propagated up; root-caused below |

**What works:**

- LQ2TL via gpt-4o on TimeLogic phrasings ("immediately after", "U" until, "&" negation/conjunction). PULS calls take ~0.5–1.5s.
- target_identification produces the `[start_time, end_time + 10]` strings the merge step expects.
- NSVS + Storm correctly identify satisfying frame intervals on real videos.
- The TimeLogic loader: 100% MC choice parse success on all 1200 MC questions, sensible operator-family inference.

**What does NOT work, with fixes (now committed on `timelogic-adapt`):**

- **`nsvqa/puls/llm.py` save_dir hardcoded to `/nas/mars/...`** → fixed via `NSVQA_LLM_HISTORY_DIR` env var (commit `cd28708`).
- **`evaluate.py` passes `"OpenGVLab/InternVL2_5-8B"` to `InternVL`** which `KeyError`s. Our driver passes the short name `"InternVL2-8B"` (or `"InternVL2-2B"`). Upstream `evaluate.py` cannot have been recently run.
- **`nsvqa/nsvs/vlm/internvl.py::assign_device_map` and `split_model`** use device-map keys (`language_model.model.embed_tokens`, `language_model.lm_head`) that don't match the actual InternVL2 module names. HF emits "device_map keys do not match any submodules" warning; the un-mapped layers stay on CPU, then `InternVL.move_tensors_to_gpu` shoves them all to GPU 0. The result is that single-GPU mode loads ~16 GB of weights on GPU 0, and multi-GPU mode does the same thing. With InternVL2-8B (the paper-reported model) this OOMs on a 24 GB A5000. **Lever B — pending.** We downgraded the smoke to InternVL2-2B (~4 GB) to unblock; this will hurt accuracy.
- **`nsvqa/puls/puls.py::process_specification`** only substituted a proposition into the TL spec if it appeared exactly once → fixed in commit `82c9611`. Recovers ~125 val entries (~6%) that use the "in turn occurs" phrasing.
- **PULS spec quality on agqa "X always after Y" questions** — see lever D.

**Speed budget**

- PULS + target_identification: ~2–3s per entry combined (gpt-4o calls).
- read_video: 0.04–30s depending on length.
- NSVS: ~1 s/frame-window × len(propositions). Entry 790 (ct, 13.8k frames, 2 propositions) took 143s. Entry 1228 (bf, 2.9k frames) took 51s.
- For full val (2000 entries) on a single GPU: optimistic 30 s/entry → ~17 hours; pessimistic 120 s/entry → ~67 hours. We need `--total_splits 4..8` across GPUs (lever E), or batched per-frame VLM calls.

**Run artifacts** at `/mnt/Data/ah66742/timelogic/outputs/smoke_v4/`:

- `per_entry/{qid}.json` — full entry dict + step status
- `entries.json`, `diag.json`
- `run.log`

## Local edits to the fork — status (2026-05-19 evening)

| File | Change | Commit |
| --- | --- | --- |
| `pyproject.toml`, `uv.lock`, `.python-version` | `requires-python` 3.13 → 3.12; lock regenerated | `b2a848b` on `main`, pushed |
| `nsvqa/puls/llm.py` | `save_dir` reads `NSVQA_LLM_HISTORY_DIR` env var | `cd28708` on `timelogic-adapt`, pushed |
| `nsvqa/puls/puls.py` | spec substitution: `count == 1` → `count >= 1` | `82c9611` on `timelogic-adapt`, pushed |
| `nsvqa/datamanager/timelogic.py` | NEW: TimeLogic loader | `ce2d02e` on `timelogic-adapt`, pushed |
| `scripts/run_timelogic.py` | NEW: pipeline driver | `d1c28f4` on `timelogic-adapt`, pushed |
| `.cursor/rules/*.md`, `CLAUDE.md`, `sessions/*`, `.gitignore` | Architecture migration: rules + logs in the fork | pending in this session |
