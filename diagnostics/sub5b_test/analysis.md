# Sub #5B Test Analysis

- Generated: 2026-05-23 21:51:33 UTC
- Test run: `/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps`
- Val reference: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2`

## Pipeline health

- ✅ DONE marker
- ✅ merged/entries.json
- ✅ postprocess/postprocess_entries.json
- ✅ answers_gpt_5_2/submission_partial.json
- ✅ submission_sub5b_test_gpt52.json
- ✅ answers_diag.json

- Submission rows: **3000** (expected 3000)
- Upload safety: **OK** (top label `No` 20.9%)

## Submission distribution

### Overall

| label | count | pct |
|---|---:|---:|
| No | 627 | 20.9% |
| Yes | 495 | 16.5% |
| C | 489 | 16.3% |
| B | 484 | 16.13% |
| D | 467 | 15.57% |
| A | 438 | 14.6% |

### By mode

**bool** (n=1122)

| label | count | pct |
|---|---:|---:|
| No | 627 | 55.88% |
| Yes | 495 | 44.12% |

**mc** (n=1878)

| label | count | pct |
|---|---:|---:|
| C | 489 | 26.04% |
| B | 484 | 25.77% |
| D | 467 | 24.87% |
| A | 438 | 23.32% |

## NSVS / FOI quality (test)

- Non-empty FOI: **2055/3000** (68.50%)
- FOI `[-1]`: **945/3000** (31.50%)
- Val non-empty FOI (reference): **70.55%** on processed entries

## VQA diagnostics

- Errors: **2**
- Error QIDs: 1840, 2504 (fallback answers: {'1840': 'A', '2504': 'A'})
- Zero-frame answers: **2**
- Mean VQA latency: **3.67s**

## Breakdown by source dataset

| source | total | valid FOI | valid FOI % |
|---|---:|---:|---:|
| agqa | 760 | 402 | 52.89% |
| bf | 734 | 622 | 84.74% |
| ct | 729 | 633 | 86.83% |
| star | 777 | 398 | 51.22% |

## Breakdown by duration bucket

| bucket | total | valid FOI | valid FOI % |
|---|---:|---:|---:|
| 10-60s | 195 | 161 | 82.56% |
| 2-10s | 206 | 129 | 62.62% |
| <2s | 1331 | 671 | 50.41% |
| >60s | 1268 | 1094 | 86.28% |

## Val vs test answer distribution

| label | test % | val % | delta |
|---|---:|---:|---:|
| A | 14.6 | 13.9 | +0.7 |
| B | 16.13 | 15.7 | +0.43 |
| C | 16.3 | 15.9 | +0.4 |
| D | 15.57 | 14.5 | +1.07 |
| No | 20.9 | 20.4 | +0.5 |
| Yes | 16.5 | 19.6 | -3.1 |

## Notes

- No hidden test labels locally — this is a pipeline/submission sanity report, not accuracy.
- Upload to EvalAI test phase when ready; record score in `RESULTS.md`.
