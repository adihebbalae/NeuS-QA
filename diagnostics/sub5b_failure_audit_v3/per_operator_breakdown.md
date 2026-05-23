# Per-operator breakdown: Sub #1 vs Sub #5B (val)

Generated: 2026-05-23T22:44:50.062646+00:00

## Caveat

EvalAI exposes **submission-level** scores only (Sub #1 **50.5%**, Sub #5B **53.35%** on val).
There is no local ground-truth file, so **per-operator accuracy cannot be computed**.
Tables below report:

- **Agreement rate** — fraction of rows where Sub #1 and Sub #5B gave the same answer
- **FOI == [-1] rate** — fraction of rows where Sub #5B merged `frames_of_interest` to `[-1]`

- Source: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/details.csv` (2000 rows)

## Overall

- Agreement: **1536/2000 (76.8%)**
- Disagreement: **464/2000 (23.2%)**
- Sub #5B `FOI == [-1]`: **584/2000 (29.2%)**
- EvalAI accuracy (submission-level): Sub #1 **50.5%**, Sub #5B **53.35%** (net **+2.85** pts for Sub #5B)

## Operator family: `always_before`

Family totals: **n=735**, agreement **77.4%**, FOI=-1 **14.1%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| always_before | 735 | 569 | 166 | 77.4% | 104 | 14.1% |

## Operator family: `unknown`

Family totals: **n=452**, agreement **82.1%**, FOI=-1 **57.1%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| unknown | 452 | 371 | 81 | 82.1% | 258 | 57.1% |

## Operator family: `after`

Family totals: **n=203**, agreement **73.4%**, FOI=-1 **25.1%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **family total** | 203 | 149 | 54 | 73.4% | 51 | 25.1% |
| after | 114 | 84 | 30 | 73.7% | 25 | 21.9% |
| immediately_after | 89 | 65 | 24 | 73.0% | 26 | 29.2% |

## Operator family: `in_turn_occurs`

Family totals: **n=125**, agreement **76.8%**, FOI=-1 **22.4%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| in_turn_occurs | 125 | 96 | 29 | 76.8% | 28 | 22.4% |

## Operator family: `until`

Family totals: **n=124**, agreement **71.0%**, FOI=-1 **32.3%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| until | 124 | 88 | 36 | 71.0% | 40 | 32.3% |

## Operator family: `before`

Family totals: **n=118**, agreement **75.4%**, FOI=-1 **25.4%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| before | 118 | 89 | 29 | 75.4% | 30 | 25.4% |

## Operator family: `always_after`

Family totals: **n=112**, agreement **70.5%**, FOI=-1 **25.9%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| always_after | 112 | 79 | 33 | 70.5% | 29 | 25.9% |

## Operator family: `since`

Family totals: **n=67**, agreement **73.1%**, FOI=-1 **31.3%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| since | 67 | 49 | 18 | 73.1% | 21 | 31.3% |

## Operator family: `during`

Family totals: **n=32**, agreement **68.8%**, FOI=-1 **31.2%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| while | 32 | 22 | 10 | 68.8% | 10 | 31.2% |

## Operator family: `when`

Family totals: **n=32**, agreement **75.0%**, FOI=-1 **40.6%**

| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| when | 32 | 24 | 8 | 75.0% | 13 | 40.6% |

## Notes

- Operator family collapses raw `operator_guess` the same way as the failure-audit packet (`immediately_after` → `after`, etc.).
- High agreement does not imply both submissions are correct — only that they match.
- High FOI=-1 within a family flags weak NSVS/Storm retrieval, not necessarily worse accuracy.

