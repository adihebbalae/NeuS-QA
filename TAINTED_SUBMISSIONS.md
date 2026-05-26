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
