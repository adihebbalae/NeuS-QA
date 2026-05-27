# Diagnostic 3 — GPT-5.2 NSVS detection swap (50-Q val subsample)

**Status: DROPPED (2026-05-27).** No actionable result — flip audit was not completed (no local GT), signal was weak/ambiguous without labels, and **GPT-5.2 NSVS swap is not a submission lever**. Primary levers remain PULS v2 + honest Sub7 pipeline. Artifacts kept for record only.

---

Historical run (exit 0), finished 2026-05-25 19:54 CDT; artifacts at `/mnt/Data/ah66742/timelogic/outputs/sub5b_subsample/`.
50 val Q: 35 Sub#1≠Sub#5B disagreements + 15 agreement controls; stratified by operator family (`subsample_manifest.json`).
48/50 ran full GPT-5.2 NSVS → crop → GPT-5.2 VQA; qids **57** and **399** have no NSVS/VQA outputs.
**17/48** comparable answers changed vs Sub #5B baseline; **31/48** unchanged (`report/ablation_summary.json`).
Of all flips, **10/17** adopted Sub #1’s answer; **7/17** chose a third answer (neither Sub #1 nor Sub #5B).
NSVS vote head-to-head (GPT-5.2 vs InternVL replay): **78.9%** agreement (5231/6630 pairs); NSVS API ~$45.35 (~$0.91/Q).

**Conclusion:** Cannot claim detector-swap lift without GT; not worth further spend. Do not cite in submission strategy.

**Archived:** [FLIP_AUDIT_PACKET.md](FLIP_AUDIT_PACKET.md) — 17-flip packet prepared but **not annotated**; do not use for decisions.
