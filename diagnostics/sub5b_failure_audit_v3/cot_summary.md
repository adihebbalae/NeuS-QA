# CoT Diagnostic Rerun (Sub #5B audit slice)

Generated: 2026-05-23T22:40:38.643749+00:00

## Setup

- Model: `gpt-5.2`
- Frame budget: 16 (same as Sub #5B cropped VQA)
- Image detail: `low`
- Video source: `paths.cropped_path` from Sub #5B postprocess (full cropped clip; FOI ignored)
- Runs per row: 2
- Requested temperature: 0.0
- Temperature note: gpt-5.2 is a reasoning model and ignores temperature; using reasoning_effort='low' to mirror Sub #5B VQA settings.
- Selected rows: `diagnostics/sub5b_failure_audit_v3/selected_rows.csv`
- Postprocess entries: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/postprocess/postprocess_entries.json`

## Headline

- Rows processed: **25** (0 with API/frame errors)
- Self-agreement across 2 CoT runs: **17/25** (68.0%)
- Agreement with Sub #5B (both runs): **11/25** (44.0%)
- Agreement with Sub #5B (run 1): **14/25**
- Agreement with Sub #5B (run 2): **14/25**
- Agreement with Sub #5B (either run): **17/25**

## Distributions

- Sub #5B answers: `{'Yes': 10, 'B': 2, 'No': 1, 'C': 4, 'A': 7, 'D': 1}`
- CoT run-1 answers: `{'Yes': 8, 'B': 3, 'No': 3, 'D': 2, 'C': 7, 'A': 2}`
- Sub #5B → CoT run-1 pairs: `{'Yes→Yes': 8, 'B→B': 1, 'No→No': 1, 'B→D': 1, 'C→B': 1, 'A→C': 5, 'Yes→No': 2, 'C→A': 1, 'C→C': 2, 'A→A': 1, 'D→D': 1, 'A→B': 1}`

## Per-row results

| QID | Mode | Sub #5B | CoT r1 | CoT r2 | Self agree | Agree Sub #5B (both) |
| --- | --- | --- | --- | --- | --- | --- |
| 1809 | bool | Yes | Yes | Yes | True | True |
| 1014 | bool | Yes | Yes | Yes | True | True |
| 1215 | mc | B | B | B | True | True |
| 1252 | bool | No | No | No | True | True |
| 1105 | bool | Yes | Yes | No | False | False |
| 489 | mc | B | D | B | False | False |
| 601 | mc | C | B | A | False | False |
| 682 | mc | A | C | C | True | False |
| 34 | bool | Yes | No | No | True | False |
| 262 | mc | A | C | B | False | False |
| 107 | mc | A | C | C | True | False |
| 808 | bool | Yes | Yes | Yes | True | True |
| 224 | bool | Yes | No | No | True | False |
| 1399 | mc | C | A | A | True | False |
| 1135 | mc | C | C | C | True | True |
| 1911 | mc | A | A | A | True | True |
| 738 | bool | Yes | Yes | Yes | True | True |
| 1675 | bool | Yes | Yes | Yes | True | True |
| 1525 | bool | Yes | Yes | No | False | False |
| 635 | mc | A | C | A | False | False |
| 1590 | mc | D | D | D | True | True |
| 1865 | bool | Yes | Yes | No | False | False |
| 1632 | mc | A | B | B | True | False |
| 1942 | mc | C | C | C | True | True |
| 796 | mc | A | C | A | False | False |

## Notes

- Sub #5B baseline answers come from the stored no-CoT gpt-5.2 cropped VQA run.
- CoT prompts ask the model to cite supporting frame numbers before emitting `ANSWER: ...`.
- Self-agreement measures whether two identical-config reruns land on the same letter/Yes/No.
