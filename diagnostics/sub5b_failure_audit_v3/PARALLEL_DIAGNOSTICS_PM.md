# Parallel diagnostics — 2026-05-24 PM

Two zero-spend diagnostics to run in parallel with the GPT-5.2 NSVS swap (already in flight). Both surface from today's audit-pattern analysis on the 12 reviewed rows. Both inform the **next val submission strategy**. Neither requires API calls — pure data analysis on existing artifacts.

Run order: independent, can launch simultaneously. Outputs feed back into a submission-strategy decision after the GPT-5.2 swap completes.

---

## Diagnostic 1 — A/Yes positional bias quantification

### Motivation

In the 25-row audit, Sub #5B's answer distribution skews heavily A/Yes vs. CoT's same-input distribution:

```
Sub #5B answers:  Yes:10  A:7  C:4  B:2  No:1  D:1
CoT run-1:        Yes:8   C:7  B:3  No:3  D:2  A:2
```

Sub #5B picks A on 50% of MC questions; CoT picks A on 14% of MC. Yes:No is 10:1 for Sub #5B vs ~3:1 for CoT. The audit is selection-biased toward NSVS-bypassed rows (76%), so this is most likely the **FOI=-1 / bypass-fallback strategy defaulting to a positional prior** instead of reasoning from frames. Touches 60.5% of val if confirmed — high leverage, low risk to fix.

### Hypothesis

When NSVS bypasses (FOI=-1 or any empty proposition detection), Sub #5B's answer is determined more by a positional prior (A for MC, Yes for boolean) than by video content.

### Task

Pull `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json` (2000 rows). For each row, compute:

- `foi_status`: clean (FOI != [-1] and all propositions have detections) / partial (some empty) / bypassed (FOI == [-1] or all empty)
- `sub5b_answer`: stored final answer
- `sub1_answer`: from `diagnostics/sub1_vs_sub5b_fix2/details.csv`
- `question_mode`: bool (Yes/No) vs mc (A/B/C/D)

Emit four tables:

1. **Sub #5B answer distribution × FOI status** — does the A/Yes skew concentrate in `bypassed`?
2. **Sub #5B vs Sub #1 answer distribution on `bypassed` rows** — if Sub #1's distribution on the same rows is more uniform, that quantifies the bug's size.
3. **Per-operator-family Sub #5B answer distribution** — does the skew vary by operator?
4. **Counterfactual estimate:** for the `bypassed` rows, if we replaced Sub #5B's answer with Sub #1's, how does the EvalAI accuracy estimate change? (Requires no new EvalAI submission — just compute the row-wise swap and report deltas under different baseline assumptions, e.g., "assuming Sub #1 is right on X% of disagreements within this slice...")

### Output

`diagnostics/sub5b_bias_quantification/report.md` + `details.csv` (per-row breakdown).

### Decision this enables

If the bypass-rows distribution is heavily A/Yes-skewed and the counterfactual swap shows meaningful gain, the **next val submission** swaps the FOI=-1 fallback from "Sub #5B's current default" to "Sub #1's answer." This is a one-line config change with potentially several points of accuracy lift. Memory-allowed (improves NeuS-QA component, not Frankenstein).

### Cost / time

Zero API. ~30 min compute. ~2 hr Cursor wall-clock including analysis writeup.

---

## Diagnostic 2 — PULS spec analysis for `unknown` operator family

### Motivation

`unknown` operator is the second-largest family in val (n=452, ~23% of val) and has **93.9% NSVS bypassed**. Per the project's operator-collapse finding, PULS is suspected of compressing operator semantics into UNTIL-style logic. If PULS is producing un-groundable specs for `unknown` questions, that's why NSVS can't find detections — and PULS prompt tuning becomes a high-leverage submission lever.

### Hypothesis

For `unknown`-family questions, PULS is producing specs that either (a) don't encode the question's semantics (operator collapse), or (b) decompose the question into propositions that can't be scored frame-by-frame. Distinguishing (a) from (b) is required before committing time to a PULS prompt fix.

### Task

Filter `entries.json` to `unknown`-family rows where Sub #5B is NSVS-bypassed (n ≈ 416). For each row, extract:

- `question_text`
- `puls_spec` (the emitted spec string)
- `propositions` (the atomic propositions)
- `nsvs.detection_count_per_prop` (how many windows each prop matched)
- `nsvs.indices` (sample-position indices that fired, if any)

Categorize each row into one of:

- **`spec_un_groundable`** — the PULS spec doesn't reference any atomic action that could be scored on a frame (e.g., abstract relations, missing candidate parameterization, operator collapsed to UNTIL when it shouldn't). Action: PULS prompt fix.
- **`spec_ok_no_detect`** — spec references a clear visual action, but NSVS returned zero detections. Action: NSVS detector quality (covered by the GPT-5.2 swap experiment).
- **`spec_partial`** — spec is well-formed but one proposition has zero detections while another has some.
- **`unclassifiable`** — needs human inspection.

For each category, sample 3 representative rows and emit `question / spec / propositions / detection_counts` so we can eyeball whether the auto-classification is faithful.

### Output

`diagnostics/puls_unknown_analysis/report.md` with:

1. Category counts (n per bucket)
2. 3 sampled rows per category
3. **Decision recommendation:** if `spec_un_groundable` is >40% of the slice, PULS prompt tuning is a high-leverage submission lever. If `spec_ok_no_detect` dominates, the win is in detector quality (GPT-5.2 swap). If `spec_partial` dominates, the win is in temporal aggregation logic.

Plus `details.csv` with per-row categorization.

### Cost / time

Zero API. ~1 hr compute (text-pattern matching). ~half day Cursor wall-clock including analysis.

### Connection to Task 7 in `CURSOR_TASKS.md`

Task 7 ("Investigate PULS MC-candidate dropping") looks at MC-specific candidate dropping. This diagnostic is broader — `unknown` is mostly boolean questions, so the failure mode will look different. Run both; they complement.

---

## What this DOESN'T do

- Doesn't compute EvalAI accuracy directly (we don't have row-level GT).
- Doesn't propose a fix — only scopes whether a fix is worth pursuing.
- Doesn't blow audit-packet scope — runs on the full val, not the 25-row audit.

## Handoff

Pull this branch, run both diagnostics in any order, commit outputs to `diagnostics/sub5b_bias_quantification/` and `diagnostics/puls_unknown_analysis/`. Ping when both reports land — Adi will use them to decide the next val-submission lever before the May 31 deadline.
