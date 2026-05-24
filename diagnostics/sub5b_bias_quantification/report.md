# Sub #5B A/Yes positional bias quantification

Generated: 2026-05-24T22:41:06.071100+00:00

## Sources

- Entries: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json` (1983 processed rows)
- Sub #5B submission: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/submission_sub5b_paper_faithful_gpt52.json`
- Sub #1 submission: `/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json`
- Sub #1 answers cross-check: `/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/details.csv`
- EvalAI val rows: **2000** (17 missing-video defaults without entries)

## Headline

- Sub #5B EvalAI accuracy: **53.35%** (1067 est. correct)
- Sub #1 EvalAI accuracy: **50.5%** (1010 est. correct)
- Net Sub #5B − Sub #1: **+2.85 pp**

### FOI status prevalence

| FOI status | n | % |
| --- | ---: | ---: |
| clean | 784 | 39.2% |
| partial | 615 | 30.8% |
| bypassed | 584 | 29.2% |
| missing_video | 17 | 0.9% |

Classification: **clean** = FOI ≠ `[-1]` and all proposition detections non-empty; **partial** = some empty detection arrays; **bypassed** = FOI `[-1]` or all detection arrays empty; **missing_video** = no pipeline entry (17 default-answer rows).

## Table 1 — Sub #5B answer distribution × FOI status

Does the A/Yes skew concentrate in bypassed rows?

| FOI status | n | Sub #5B answers | bool Yes% | mc A% |
| --- | ---: | --- | ---: | ---: |
| clean | 784 | Yes:148 No:176 A:105 B:125 C:112 D:118 | 45.7% (148/324) | 22.8% (105/460) |
| partial | 615 | Yes:114 No:77 A:91 B:108 C:122 D:103 | 59.7% (114/191) | 21.5% (91/424) |
| bypassed | 584 | Yes:113 No:155 A:82 B:81 C:84 D:69 | 42.2% (113/268) | 25.9% (82/316) |
| missing_video | 17 | Yes:17 | 100.0% (17/17) | 0.0% (0/0) |

## Table 2 — Sub #5B vs Sub #1 on bypassed rows

If Sub #1 is more uniform on the same bypassed slice, that quantifies positional-prior size.

### Sub #5B (bypassed)

| Mode | n | Answers | Yes% or A% |
| --- | ---: | --- | ---: |
| mc | 316 | A:82 B:81 C:84 D:69 | 25.9% A |
| bool | 268 | Yes:113 No:155 | 42.2% Yes |

### Sub #1 (same bypassed rows)

| Mode | n | Answers | Yes% or A% |
| --- | ---: | --- | ---: |
| mc | 316 | A:67 B:88 C:88 D:73 | 21.2% A |
| bool | 268 | Yes:117 No:151 | 43.7% Yes |

## Table 3 — Sub #5B answer distribution by operator family

| Operator family | n | Sub #5B answers | bool Yes% | mc A% |
| --- | ---: | --- | ---: | ---: |
| always_before | 734 | Yes:56 No:102 A:131 B:163 C:147 D:135 | 35.4% | 22.7% |
| unknown | 460 | Yes:209 No:97 A:40 B:28 C:47 D:39 | 68.3% | 26.0% |
| after | 202 | Yes:42 No:59 A:24 B:22 C:22 D:33 | 41.6% | 23.8% |
| until | 123 | Yes:15 No:32 A:16 B:22 C:22 D:16 | 31.9% | 21.1% |
| in_turn_occurs | 120 | Yes:13 No:45 A:15 B:16 C:15 D:16 | 22.4% | 24.2% |
| before | 118 | Yes:25 No:22 A:11 B:17 C:26 D:17 | 53.2% | 15.5% |
| always_after | 112 | Yes:21 No:33 A:15 B:13 C:13 D:17 | 38.9% | 25.9% |
| since | 67 | Yes:11 No:18 A:10 B:7 C:11 D:10 | 37.9% | 26.3% |
| during | 32 | A:7 B:13 C:9 D:3 | 0.0% | 21.9% |
| when | 32 | A:9 B:13 C:6 D:4 | 0.0% | 28.1% |

## Table 4 — Counterfactual: swap Sub #5B → Sub #1 on bypass rows

No hidden labels — accuracy deltas are **estimates** from row-wise answer swaps under stated assumptions about who is correct on disagreements.

### Bypassed only (`foi_status=bypassed`)

- Slice size: **584** rows (bypassed)
- Agree Sub #1 = Sub #5B: **475** (swap is a no-op)
- Disagree: **109** (answers would change)

Proxy for Sub #1 win rate on *all* val disagreements (from aggregate scores): **43.9%** (Sub #5B **56.1%**).

| Scenario | p(Sub #1 right on slice disagreements) | Δ correct rows | Δ accuracy (pp) | Est. new accuracy |
| --- | ---: | ---: | ---: | ---: |
| pessimistic_sub5b_wins_all | 0.0% | -109.0 | -5.45 | 47.90% |
| overall_disagree_rate | 43.9% | -13.4 | -0.67 | 52.68% |
| neutral_50_50 | 50.0% | +0.0 | +0.00 | 53.35% |
| optimistic_sub1_wins_all | 100.0% | +109.0 | +5.45 | 58.80% |

### Bypass + partial (`bypassed` ∪ `partial`)

- Slice size: **1199** rows (bypassed, partial)
- Agree Sub #1 = Sub #5B: **931** (swap is a no-op)
- Disagree: **268** (answers would change)

Proxy for Sub #1 win rate on *all* val disagreements (from aggregate scores): **43.9%** (Sub #5B **56.1%**).

| Scenario | p(Sub #1 right on slice disagreements) | Δ correct rows | Δ accuracy (pp) | Est. new accuracy |
| --- | ---: | ---: | ---: | ---: |
| pessimistic_sub5b_wins_all | 0.0% | -268.0 | -13.40 | 39.95% |
| overall_disagree_rate | 43.9% | -32.9 | -1.65 | 51.70% |
| neutral_50_50 | 50.0% | +0.0 | +0.00 | 53.35% |
| optimistic_sub1_wins_all | 100.0% | +268.0 | +13.40 | 66.75% |

### Missing-video defaults (`missing_video`)

- Slice size: **17** rows (missing_video)
- Agree Sub #1 = Sub #5B: **17** (swap is a no-op)
- Disagree: **0** (answers would change)

Proxy for Sub #1 win rate on *all* val disagreements (from aggregate scores): **43.9%** (Sub #5B **56.1%**).

| Scenario | p(Sub #1 right on slice disagreements) | Δ correct rows | Δ accuracy (pp) | Est. new accuracy |
| --- | ---: | ---: | ---: | ---: |
| pessimistic_sub5b_wins_all | 0.0% | -0.0 | -0.00 | 53.35% |
| overall_disagree_rate | 43.9% | -0.0 | -0.00 | 53.35% |
| neutral_50_50 | 50.0% | +0.0 | +0.00 | 53.35% |
| optimistic_sub1_wins_all | 100.0% | +0.0 | +0.00 | 53.35% |

## Interpretation

- **Bypassed vs clean (Sub #5B):** bool Yes rate 42.2% vs 45.7% (-3.5 pp); mc A rate 25.9% vs 22.8% (+3.1 pp).
- **Partial vs clean:** bool Yes 59.7% vs 45.7% (+14.0 pp); mc A 21.5% vs 22.8% (-1.3 pp). Partial rows show the largest Yes skew — weak/partial NSVS may share the same fallback pathology.
- **Missing-video defaults:** all **17** rows use Sub #5B default `Yes` (17/17 Yes) — strong positional prior independent of NSVS.
- **Bypass-only swap at overall disagree proxy:** estimated **-0.67 pp** → ~52.68% accuracy.

## Decision lever

If bypass/partial rows show concentrated A/Yes skew *and* the counterfactual swap is neutral-or-positive under realistic Sub #1 win rates, the next val submission can route FOI=-1 / bypass fallbacks to Sub #1 answers (one-line config change, no new API).

See `details.csv` for per-row `foi_status`, answers, and operator metadata.

