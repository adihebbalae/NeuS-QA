# FOI == [-1] prevalence (Sub #5B val)

Generated: 2026-05-23T22:44:21.829346+00:00

## Source

- Entries: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json`
- Audit slice: `/home/ah66742/NeuS-QA/diagnostics/sub5b_failure_audit_v2/selected_rows.csv` (25 QIDs)
- Processed rows in dump: **1983** (EvalAI val is 2000; 17 source videos missing on disk)

## Headline

- Full val rows (processed): **1983**
- `frames_of_interest == [-1]`: **584/1983 (29.5%)**
- Audit slice `FOI == [-1]`: **3/25 (12.0%)**

For context, the v3 audit packet's broader `NSVS_bypassed` signal (FOI [-1], Storm [-1], or any empty proposition detections):

- Full val: **1199/1983 (60.5%)**
- Audit slice: **19/25 (76.0%)**

## Interpretation

- The audit slice's **NSVS_bypassed** rate is much higher than the full val baseline (+15.5 pp). That points to **selection bias**: the disagreement audit over-samples rows where retrieval failed or was weak.
- Strict `FOI == [-1]` alone is **not** the main driver of the audit's ~80% bypass signal (audit 12.0% vs full val 29.5%). Most audit bypass rows still have a numeric FOI but empty/partial NSVS detections.

## Full val — by operator family

| Operator family | n | FOI == [-1] | % | NSVS bypassed | % |
| --- | ---: | ---: | ---: | ---: | ---: |
| always_before | 734 | 104 | 14.2% | 208 | 28.3% |
| unknown | 443 | 258 | 58.2% | 416 | 93.9% |
| after | 202 | 51 | 25.2% | 146 | 72.3% |
| until | 123 | 40 | 32.5% | 96 | 78.0% |
| in_turn_occurs | 120 | 28 | 23.3% | 39 | 32.5% |
| before | 118 | 30 | 25.4% | 90 | 76.3% |
| always_after | 112 | 29 | 25.9% | 87 | 77.7% |
| since | 67 | 21 | 31.3% | 53 | 79.1% |
| during | 32 | 10 | 31.2% | 32 | 100.0% |
| when | 32 | 13 | 40.6% | 32 | 100.0% |

## Full val — by audit duration bucket

| Duration bucket | n | FOI == [-1] | % | NSVS bypassed | % |
| --- | ---: | ---: | ---: | ---: | ---: |
| <10s | 1000 | 458 | 45.8% | 836 | 83.6% |
| 10-30s | 3 | 1 | 33.3% | 1 | 33.3% |
| 30-60s | 65 | 6 | 9.2% | 17 | 26.2% |
| 60-180s | 281 | 47 | 16.7% | 125 | 44.5% |
| >180s | 634 | 72 | 11.4% | 220 | 34.7% |

## Audit slice — by operator family

| Operator family | n | FOI == [-1] | % | NSVS bypassed | % |
| --- | ---: | ---: | ---: | ---: | ---: |
| always_before | 5 | 0 | 0.0% | 2 | 40.0% |
| unknown | 4 | 0 | 0.0% | 4 | 100.0% |
| after | 3 | 1 | 33.3% | 3 | 100.0% |
| always_after | 3 | 0 | 0.0% | 1 | 33.3% |
| before | 3 | 1 | 33.3% | 3 | 100.0% |
| until | 3 | 0 | 0.0% | 3 | 100.0% |
| in_turn_occurs | 2 | 0 | 0.0% | 1 | 50.0% |
| since | 2 | 1 | 50.0% | 2 | 100.0% |

## Audit slice — by audit duration bucket

| Duration bucket | n | FOI == [-1] | % | NSVS bypassed | % |
| --- | ---: | ---: | ---: | ---: | ---: |
| <10s | 10 | 3 | 30.0% | 7 | 70.0% |
| 30-60s | 5 | 0 | 0.0% | 4 | 80.0% |
| 60-180s | 5 | 0 | 0.0% | 3 | 60.0% |
| >180s | 5 | 0 | 0.0% | 5 | 100.0% |

## Notes

- `FOI == [-1]` means Storm/target-ID merge produced no usable interval.
- `NSVS bypassed` matches the v3 audit auto-triage field (yes or partial).
- Duration buckets match the failure-audit packet stratification (<10s, 10-30s, …).

