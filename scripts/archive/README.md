# Archived scripts

Moved here during repo cleanup (2026-05-31). Not used for active work; kept for reproducibility.

| Script | Why archived |
| --- | --- |
| `finish_sub2.sh`, `wait_shards_and_finish.sh` | Sub #2 era |
| `wait_and_post_sub5b.sh`, `post_sub5b_checklist.sh` | Sub #5B one-shot automation |
| `resume_sub5b_*.sh` | Resume helpers after 5B completed |
| `run_sub1_test.sh` | Early test smoke |
| `run_atemporal_mc_prototype.*` | Diagnostic prototype |
| `run_validate_puls_v2_148.sh`, `validate_puls_v2_target_slice.py` | PULS v2 148-row validation (done) |
| `build_puls_v2_semantic_eyeball_packet.py` | PI review packet builder |
| `run_sub5b_nsvs_gpt52_subsample.sh`, `finish_sub5b_nsvs_gpt52_subsample.sh` | Diagnostic 3 subsample |
| `build_nsvs_backend_subsample.py`, `report_nsvs_backend_ablation.py` | Diag 3 analysis |
| `launch_sub9_tmux.sh`, `run_sub9_pulsv2_val.sh` | Sub9 val (killed / frozen) |
| `neurosymbolic_ablation.py`, `audit_puls_grounding.py` | Early ablations |
| `stratify_sub7_vs_sub1.py`, `assemble_rerun_entries.py` | Sub7 one-offs (see production `run_sub7b.sh`) |
| `compare_sub5b_*_vs_sub1.sh` | Wrapped by `compare_submissions.py` |
| `finish_sub7_vqa_preflight.sh` | Sub7 preflight |
| `build_overnight_puls_review.py`, `analyze_foi_smoke.py` | Overnight diagnostics |

To run an archived script, use `bash scripts/archive/<name>` from repo root (paths inside scripts assume repo root).
