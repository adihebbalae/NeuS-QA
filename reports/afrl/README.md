# AFRL test reports

Sub7b **test** (3000-row) pipeline taxonomy and PULS propagation artifacts.

| File | Description |
| --- | --- |
| `test_pipeline_taxonomy.csv` | Full per-row log (stage, spec, FOI, answers) |
| `test_pipeline_summary.json` | Stage counts + disagreement stats |
| `accuracy_by_category.csv` | Sliced agree-rate tables (source, operator, mode, stage) |
| `pipeline_examples.json` | Slide case studies (disagreements per pipeline stage) |
| `test_puls_shard_join.csv` | Per-qid PULS/NSVS join + `spec_faithful` |
| `puls_propagation_crosstab.{json,md}` | 2×2 propagation tables |

**Regenerate:**

```bash
bash scripts/afrl/run_test_taxonomy.sh
python3 scripts/afrl/build_puls_propagation_table.py
```

Outputs write to this directory (`reports/afrl/`). Large regenerable assets (`frames/`, val+test `enriched_manifest.json`) are gitignored.
