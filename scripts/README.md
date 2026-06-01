# Scripts

## Production (TimeLogic)

| Script | Purpose |
| --- | --- |
| `run_timelogic.py` | Main pipeline driver (PULS → target_id → NSVS → merge) |
| `run_baseline_cpu.py` | Sub #1 — CPU baseline, no NSVS |
| `run_sub5b_paper_faithful.sh` | Sub #5B val — paper-faithful 3fps stack |
| `run_sub5b_test.sh` | Sub #5B test (tainted — do not upload) |
| `run_sub7.sh` / `run_sub7b.sh` | Sub #7 / #7b honest test stack |
| `finish_sub7b_rerun.sh` | Sub7b union after NSVS rerun |
| `run_sub7_rerun_failed_nsvs.sh` | NSVS gap fill for Sub7 |
| `run_sub9_pulsv2_test.sh` | Sub #9 test (PULS v2) — complete, not uploaded |
| `run_sub9_pulsv2_driver.sh` | Shared Sub9 driver (called by test/val wrappers) |
| `launch_sub9_test_tmux.sh` | Tmux launcher for Sub9 test |
| `fill_sub9_nsvs_gaps.sh` | Sub9 NSVS gap fill |
| `sub9_shard_utils.py` | Sub9 shard coverage helpers |
| `run_nsvs_sharded.sh` | Multi-GPU NSVS sharding |
| `merge_nsvs_shards.py` | Merge shard `entries.json` |
| `crop_timelogic_entries.py` | ffmpeg crop from FOI |
| `answer_cropped_entries.py` | GPT VQA on crops |
| `build_submission.py` | EvalAI JSON builder |
| `build_tiebreaker_submission.py` | Sub #4 post-process |
| `build_routed_submission.py` | Sub #3 routing |
| `compare_submissions.py` | Agreement / bucket diagnostics |
| `estimate_api_spend.py` | API spend guard |
| `lib/require_test_phase.sh` | Test-phase guard (challenge closed) |

## Diagnostics (still useful to regenerate reports)

| Script | Output |
| --- | --- |
| `build_failure_audit_packet.py` | `diagnostics/sub5b_failure_audit_v3/` |
| `quantify_sub5b_positional_bias.py` | `diagnostics/sub5b_bias_quantification/` |
| `analyze_puls_unknown_bypassed.py` | `diagnostics/puls_unknown_analysis/` |
| `analyze_sub5b_test.py` | `diagnostics/sub5b_test/` |
| `analyze_sub9_pulsv2_val.py` | `<base>/sub9_*_report.md` |

## Archive

One-off, superseded, or challenge-complete helpers live in [`archive/`](archive/README.md).
