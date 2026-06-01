# Tainted Submissions

These submissions ran with known bugs that materially affected their methodology label. Do NOT use them as baselines or attribute their scores to the documented configuration.

## Sub5B (sub5b_paper_faithful_3fps_fix2)

- Val score: 53.35%
- Test score: 51.5% (assumed same bug profile)
- Submission file: submission_sub5b_paper_faithful_gpt52.json
- Output dir: /mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/

**Bugs:**
1. ffmpeg missing from run env → 1983/1983 crop failures, every row fell back to full source video.
2. `answer_cropped_entries.py:prepare_entries` set `frames_of_interest = None` regardless of FOI validity → VQA sampled 16 frames uniformly across the full video.
3. `intersection_with_gaps` IndexError on empty detection lists → 464/1983 NSVS rows crashed and got `foi=[-1]` without target-ID merge.

**Honest label:** gpt-4o PULS/TI + InternVL NSVS (metadata only, never used downstream) + gpt-5.2 full-video VQA (16 frames, low detail, cleaned_question, PULS hints).

**Do not** cite this as evidence of NeuS-QA contribution or as a baseline for cropping ablations.

## Sub7a (`sub7_neusqa_paper_faithful` — first test upload)

- Test score: **49.9%** (EvalAI) — **discarded; do not use for decisions or the report**
- Submission file: `submission_sub7.json`
- Output dir: `/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/`

**Bugs (same run, stacked):**

1. **790/3000 NSVS hard failures** (~26%) — CUDA/KeyError during original 8-shard GPU run (GPU outage May 27); those rows never got a real interval.
2. **Only 817/3000 valid FOI** (27.2%) vs ~70% on fixed val Sub #5B — most rows fell back to full-video-style behavior.
3. **Pre-fix VQA** — `answer_cropped_entries` did not clear `frames_of_interest` on real crops (fixed in `fd63192` after this run); cropped VQA sampled FOI frames inside V′, not uniformly over the crop.
4. NSVS rerun (`run_sub7_rerun_failed_nsvs.sh`) was **not** merged into this submission.

**Honest label:** partial NeuS-QA — broken NSVS on ~26% of qids, weak FOI coverage on the rest, pre-fix crop VQA. Closer to a degraded baseline than paper-faithful NeuS-QA.

**Do not** use Sub7a for stratification vs Sub #1, routing decisions, or leaderboard claims. **Sub7b** = NSVS rerun + re-postprocess + re-VQA with hardened pipeline (`fd63192`).
