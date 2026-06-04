# AFRL test reports (committed snapshots)

Tracked copies of Sub7b **test** (3000-row) pipeline / PULS propagation artifacts.

| File | Description |
| --- | --- |
| `test_puls_shard_join.csv` | Per-qid join: `puls_spec`, `foi_raw`, `nsvs_indices`, operator labels, `spec_faithful`, Sub7b vs baseline answers |
| `puls_propagation_crosstab.json` | Machine-readable 2×2 tables (`spec_faithful` × FOI=[-1], × ours≠vanilla) |
| `puls_propagation_crosstab.md` | Slide-ready summary |

Regenerate (writes to `/mnt/Data/ah66742/timelogic/reports/afrl/` by default):

```bash
python3 scripts/afrl/build_puls_propagation_table.py
```

Full test taxonomy pipeline:

```bash
bash scripts/afrl/run_test_taxonomy.sh
```
