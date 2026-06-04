# Reports (in-repo)

Analysis and slide artifacts live here instead of `/mnt/Data/ah66742/timelogic/reports/`.
Scripts default to these paths; the old timelogic `reports/` tree is symlinked here for compatibility.

| Directory | Contents |
| --- | --- |
| [`afrl/`](afrl/) | Test taxonomy CSV/JSON, PULS propagation tables, pipeline examples |
| [`tech_report/`](tech_report/) | v1 clip gallery (`v1_clips/`), export bundles |

**Regenerate AFRL test reports:**

```bash
bash scripts/afrl/run_test_taxonomy.sh
python3 scripts/afrl/build_puls_propagation_table.py
```

**Clip gallery:** see [`docs/timelogic/tech_report/CLIPS.md`](../docs/timelogic/tech_report/CLIPS.md).
