# NSVS Quality Probe — Sub #5B test full merged

- Generated: 2026-05-23 21:51:34 UTC
- Output dir(s): /mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps
- Mode: one-shot
- Entries analyzed: 3000

## FOI coverage

- Non-empty FOI: 2055/3000 (68.50%)
- FOI `[-1]`: 945/3000 (31.50%)

## FOI length (seconds, valid intervals only)

| stat | value |
|---|---:|
| count | 2055 |
| p25 | 1.40 |
| median | 18.00 |
| p75 | 41.96 |
| p95 | 217.98 |

## Multi-proposition zero-detection rate

Rows with more than one PULS proposition where at least one `nsvs.indices` array is empty.

- Rows: 2035
- Any zero-detection proposition: 447/2035 (21.97%)

## Target-ID padding direction

Direction buckets classify parsed `target_identification.frame_window` padding relative to the NSVS interval.

| direction | count | share |
|---|---:|---:|
| both | 2007 | 66.90% |
| missing | 721 | 24.03% |
| after_only | 139 | 4.63% |
| none | 126 | 4.20% |
| before_only | 7 | 0.23% |

### Parsed before/after second counts

- Before-start seconds: {0: 265, 1: 123, 2: 435, 3: 530, 4: 40, 5: 750, 6: 4, 7: 1, 8: 8, 9: 1, 10: 113, 15: 3, 20: 3, 30: 2, 50: 1}
- After-end seconds: {0: 133, 1: 614, 2: 1002, 3: 220, 4: 15, 5: 218, 6: 2, 7: 4, 8: 45, 10: 25, 15: 1}

### Top raw target-ID templates

- ``: 721
- `[+5, +2]`: 499
- `[+3, +1]`: 377
- `[+2, +2]`: 257
- `[+5, +1]`: 175
- `[+0, +0]`: 125
- `[+2, +3]`: 102
- `[+0, +5]`: 95
- `[+10, +2]`: 95
- `[+1, +5]`: 90
