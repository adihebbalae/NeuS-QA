# PULS v2 validation — 148-row target slice

Generated: 2026-05-26T17:53:57.128190+00:00
PULS model: `gpt-4o` · Prompt: current `nsvqa/puls/prompts.py` (Examples 13–16)

## Target slice

- **94** `empty_puls_output` + **54** `operator_collapse_open_ended`
- Source: `diagnostics/puls_unknown_analysis/details.csv`
- Full per-row log: `/mnt/Data/ah66742/timelogic/outputs/puls_v2_validation_148/results.jsonl`

## Headline

| Metric | Count |
| --- | ---: |
| Total | 148 |
| **Structurally rescued** (v2 passes PULS gates) | **148** (100.0%) |
| Still failing structural gate | 0 |
| Est. API spend | $0.8299 |

### By baseline bucket

| Baseline reason | n | Rescued | Still fail |
| --- | ---: | ---: | ---: |
| `empty_puls_output` | 94 | 94 | 0 |
| `operator_collapse_open_ended` | 54 | 54 | 0 |

### v2 failure reasons (remaining)

```json
{}
```

## Notes

- **Rescued** = baseline had empty/collapse; v2 returns non-empty spec passing `relation_not_in_spec` / `operator_collapse` / `empty` gates (PULS-only).
- Does **not** re-run NSVS or measure val accuracy.
- Re-run: `python3 scripts/validate_puls_v2_target_slice.py --resume`
- **Semantic skim (20 min):** [SEMANTIC_EYEBALL_PACKET.md](../SEMANTIC_EYEBALL_PACKET.md) — 10+10 rescued rows, question vs v2 spec.
