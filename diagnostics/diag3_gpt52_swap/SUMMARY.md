# Diagnostic 3 — GPT-5.2 NSVS detection swap (50-Q val subsample)

Complete (exit 0), finished 2026-05-25 19:54 CDT; artifacts at `/mnt/Data/ah66742/timelogic/outputs/sub5b_subsample/` (not under `outputs/diagnostics/`).
50 val Q: 35 Sub#1≠Sub#5B disagreements + 15 agreement controls; stratified by operator family (`subsample_manifest.json`).
48/50 ran full GPT-5.2 NSVS → crop → GPT-5.2 VQA; qids **57** and **399** have no NSVS/VQA outputs.
**17/48** comparable answers changed vs Sub #5B baseline; **31/48** unchanged (`report/ablation_summary.json`).
Flips: **15/17** on disagree stratum, **2/17** on agree-control stratum (qids 24, 26).
Of all flips, **10/17** adopted Sub #1’s answer; **7/17** chose a third answer (neither Sub #1 nor Sub #5B).
On disagree rows with GPT output (33/35): final answer matches Sub #5B **20**, Sub #1 **10**, third **5** (219, 4, 238, 408, 443).
No local GT; disagree rows tagged `sub1_baseline_preferred_proxy` (Sub1≠Sub5B only). Val EvalAI: Sub #5B 53.35% vs Sub #1 50.5%.
Direction: flips lean toward Sub #1, but most disagree rows still match Sub #5B — weak/ambiguous positive trend without labels.
NSVS vote head-to-head (GPT-5.2 vs InternVL replay): **78.9%** agreement (5231/6630 pairs); NSVS API ~$45.35 (~$0.91/Q).
