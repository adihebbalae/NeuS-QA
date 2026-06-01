# Diagnostics (summary artifacts)

Tracked copies of analysis outputs. Full regeneration commands were in the pre-cleanup README; see `scripts/README.md` for drivers.

## Keep in git

| Directory | What to read |
| --- | --- |
| [`sub5b_failure_audit_v3/`](sub5b_failure_audit_v3/) | **[FINDINGS.md](sub5b_failure_audit_v3/FINDINGS.md)** — main human audit conclusions |
| [`sub1_vs_sub5b_fix2/`](sub1_vs_sub5b_fix2/) | Sub #1 vs #5B disagreement buckets (`summary.json`) |
| [`sub5b_bias_quantification/`](sub5b_bias_quantification/) | A/Yes bias hypothesis rejected |
| [`puls_unknown_analysis/`](puls_unknown_analysis/) | PULS failures on `unknown` operator family |
| [`puls_v2_prep/`](puls_v2_prep/) | PULS v2 prompt diff + 148-row validation summary |
| [`sub5b_test/`](sub5b_test/) | Test-run health summary (tainted submission) |
| [`test_video_opencv_audit/`](test_video_opencv_audit/) | Test video duration audit |
| [`atemporal_mc_prototype/`](atemporal_mc_prototype/) | Atemporal MC diagnostic (small) |

## Removed from git (2026-05-31 cleanup)

- Failure audit **v1** / **v2** packets (superseded by v3; v2 `selected_rows.csv` + frame cache merged into v3)
- **diag3_gpt52_swap/** — see [`docs/timelogic/archive/diagnostic-3-dropped.md`](../docs/timelogic/archive/diagnostic-3-dropped.md)
- Large generated packets (`failure_audit_packet.md`, `cot_traces.json`, build logs)

Canonical working copies may still exist under `/mnt/Data/ah66742/timelogic/outputs/diagnostics/`.
