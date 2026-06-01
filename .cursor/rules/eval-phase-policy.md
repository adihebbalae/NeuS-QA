# Eval phase policy — READ FIRST (agents)

**PROJECT CLOSED 2026-05-31.** Challenge ended; do not launch val or test pipelines unless Adi explicitly reopens work.

**Historical (2026-05-29):** Hard deadline mode — TEST only until challenge end.

## Rule (non-negotiable)

| Phase | Status |
| --- | --- |
| **Test** (3k, EvalAI test phase) | **ALLOWED** — default for every pipeline run, tmux job, and API spend |
| **Val** (2k, validation leaderboard) | **FROZEN** — do not launch, resume, or “just finish” val jobs unless the user explicitly types `ALLOW_VAL=1` in that session |

### What counts as a VAL run (forbidden)

- `--ann-path` / `ANN=` pointing at `timelogic_val_data.json` or `.../data/val/...`
- `--video-root` / `VIDEO_ROOT=` under `videos/val/` or `combined_2k_videos` (val tree)
- Scripts whose primary purpose is val: `run_sub9_pulsv2_val.sh`, `run_sub5b_paper_faithful.sh`, `launch_sub9_tmux.sh`, `fill_sub9_nsvs_gaps.sh`, etc.
- `HEAD=` smokes on val paths

### What counts as TEST (required for new work)

- `timelogic_test_data.json` (3000 Q)
- `videos/test/benchmark_test_videos_json`
- Outputs under e.g. `outputs/sub7_neusqa_paper_faithful/` (Sub7/7b test repair)

## Before starting ANY long job

1. Print `ANN=` and `VIDEO_ROOT=` (or `BASE=` config) in the session log.
2. If either path contains `/val/` or `val_data`, **stop** and ask — do not assume “resume previous job.”
3. Use **tmux** for runs >5 min (see `workflow.md`). Never nohup.

## Incident log (2026-05-29)

- **Sub7b** — TEST only (`timelogic_test_data.json`, 3000-row `submission_sub7b.json`). Not val.
- **Sub9 val** — FROZEN (`run_sub9_pulsv2_val.sh`). Killed 2026-05-29.
- **Sub9 test** — completed 2026-05-30; JSON at `outputs/sub9_pulsv2_test/` — **not uploaded** (deadline).
- **Sub7b** — final official test submission **47.97** AvgAcc.

## Override

Only if the user explicitly requests a val run in the current message:

```bash
ALLOW_VAL=1 bash scripts/...   # rare; document why in sessions/
```
