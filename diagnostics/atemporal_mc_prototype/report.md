# Atemporal-MC prototype — analysis report

Generated: 2026-05-26 19:18:12 UTC
Runs: `/home/ah66742/NeuS-QA/diagnostics/atemporal_mc_prototype/runs` · Manifest rows: 10 · Analyzed: 10

## Recommendation

**KILL** — Median differentiation_gap 0.034 < 0.05 — NSVS scores are near-uniform across choices at this clip-length regime; do not scale this NSVS path. Recommend fallback: direct per-choice binary VQA (separate experiment).

## Headline metric

- **Median differentiation_gap:** **0.0340** (10/10 rows with scores)

Decision thresholds (mechanical):
- **≥ 0.20** → **SHIP** — scale to all 88 Bucket-A rows for val submission.
- **0.05–0.20** → **INSPECT** — mixed signal; per-stratum review.
- **< 0.05** → **KILL** — no choice-level NSVS signal; use per-choice VQA fallback instead.

## Per-stratum differentiation_gap

| Stratum | n | median gap | mean gap |
|---------|---|------------|----------|
| `long_ct` | 2 | 0.0070 | 0.0070 |
| `mid_agqa` | 3 | 0.0200 | 0.0150 |
| `short_star_agqa` | 5 | 0.0940 | 0.1812 |

### Long vs short (critical)

- **Long (CT ≥60s):** n=2, median gap=0.007000000000000006
- **Short (STAR/AGQA <10s):** n=8, median gap=0.05999999999999994

> Mixed long/short pattern — see per-row table.

## Argmax vs Sub #1 proxy (weak; n≈10, Sub #1 ≠ GT)

- Rows where **argmax ≠ Sub #5B** answer: **7** / 10
- Of those, argmax **matches Sub #1**: **0** / 7 (0%)

*Do not over-interpret; 10-row prototype only.*

## Spec quality spot-check (PULS propositions per row)

### QID 74 · `star_2MGC1.mp4` · short_star_agqa · ok

- Stem: What action does the person do throughout the video ?
- Duration: 0.52s · Sub #5B: **B** · Sub #1: **B**
- Argmax: **A** (score 0.93, gap 0.18700000000000006)

- **A:** `person_tidies_up_a_blankets` · spec `("person_tidies_up_a_blankets")` · NSVS max_p=0.93 · satisfied=False
- **B:** `person_opens_a_door` · spec `("person_opens_a_door")` · NSVS max_p=0.743 · satisfied=True
- **C:** `person_takes_some_clothes_from_somewhere` · spec `("person_takes_some_clothes_from_somewhere")` · NSVS max_p=0.351 · satisfied=False
- **D:** `person_throws_a_blanket_somewhere` · spec `("person_throws_a_blanket_somewhere")` · NSVS max_p=0.445 · satisfied=False

### QID 196 · `star_FV9AL.mp4` · short_star_agqa · ok

- Stem: What action does the person do throughout the video ?
- Duration: 0.16s · Sub #5B: **D** · Sub #1: **D**
- Argmax: **C** (score 0.966, gap 0.07399999999999995)

- **A:** `person_holds_a_vacuum` · spec `("person_holds_a_vacuum")` · NSVS max_p=0.892 · satisfied=False
- **B:** `person_takes_a_bag_from_somewhere` · spec `("person_takes_a_bag_from_somewhere")` · NSVS max_p=0.752 · satisfied=False
- **C:** `person_lies_on_a_sofacouch` · spec `("person_lies_on_a_sofacouch")` · NSVS max_p=0.966 · satisfied=False
- **D:** `person_opens_a_door` · spec `("person_opens_a_door")` · NSVS max_p=0.354 · satisfied=False

### QID 271 · `agqa_EIT66.mp4` · short_star_agqa · ok

- Stem: What does the person do in the video ?
- Duration: 1.32s · Sub #5B: **A** · Sub #1: **A**
- Argmax: **B** (score 0.975, gap 0.04599999999999993)

- **A:** `person_puts_a_phone_somewhere` · spec `("person_puts_a_phone_somewhere")` · NSVS max_p=0.412 · satisfied=False
- **B:** `person_washes_a_cup` · spec `("person_washes_a_cup")` · NSVS max_p=0.975 · satisfied=False
- **C:** `person_takes_a_pillow_from_somewhere` · spec `("person_takes_a_pillow_from_somewhere")` · NSVS max_p=0.929 · satisfied=False
- **D:** `person_puts_something_on_a_table` · spec `("person_puts_something_on_a_table")` · NSVS max_p=0.893 · satisfied=False

### QID 678 · `agqa_2U0GH.mp4` · short_star_agqa · ok

- Stem: What action does the person do throughout the video ?
- Duration: 1.2s · Sub #5B: **C** · Sub #1: **C**
- Argmax: **C** (score 0.948, gap 0.5049999999999999)

- **A:** `person_takes_some_clothes_from_somewhere` · spec `("person_takes_some_clothes_from_somewhere")` · NSVS max_p=0.443 · satisfied=False
- **B:** `person_stands_up` · spec `("person_stands_up")` · NSVS max_p=0.309 · satisfied=False
- **C:** `person_washes_a_dish` · spec `("person_washes_a_dish")` · NSVS max_p=0.948 · satisfied=False
- **D:** `person_puts_clothes_somewhere` · spec `("person_puts_clothes_somewhere")` · NSVS max_p=0.261 · satisfied=False

### QID 720 · `ct_Qf2E1pEiaXM.mp4` · long_ct · ok

- Stem: What does the person do in the video ?
- Duration: 198.06s · Sub #5B: **C** · Sub #1: **C**
- Argmax: **A** (score 0.978, gap 0.013000000000000012)

- **A:** `person_pours_lemon_juice` · spec `("person_pours_lemon_juice")` · NSVS max_p=0.978 · satisfied=False
- **B:** `person_closes_cap` · spec `("person_closes_cap")` · NSVS max_p=0.965 · satisfied=False
- **C:** `person_adds_sugar` · spec `("person_adds_sugar")` · NSVS max_p=0.965 · satisfied=True
- **D:** `person_lowers_jack` · spec `("person_lowers_jack")` · NSVS max_p=0.806 · satisfied=False

### QID 1387 · `agqa_JJ47B.mp4` · mid_agqa · ok

- Stem: What action does the person do throughout the video ?
- Duration: 0.76s · Sub #5B: **A** · Sub #1: **B**
- Argmax: **D** (score 0.963, gap 0.02200000000000002)

- **A:** `person_sits_in_a_chair` · spec `("person_sits_in_a_chair")` · NSVS max_p=0.941 · satisfied=True
- **B:** `person_plays_with_a_phone` · spec `("person_plays_with_a_phone")` · NSVS max_p=0.91 · satisfied=True
- **C:** `person_takes_a_phone_from_somewhere` · spec `("person_takes_a_phone_from_somewhere")` · NSVS max_p=0.622 · satisfied=True
- **D:** `person_opens_a_closet` · spec `("person_opens_a_closet")` · NSVS max_p=0.963 · satisfied=False

### QID 1460 · `agqa_5LJ3J.mp4` · mid_agqa · ok

- Stem: What does the person do in the video ?
- Duration: 0.88s · Sub #5B: **B** · Sub #1: **B**
- Argmax: **A** (score 0.926, gap 0.020000000000000018)

- **A:** `person_grasps_onto_a_doorknob` · spec `("person_grasps_onto_a_doorknob")` · NSVS max_p=0.926 · satisfied=False
- **B:** `person_puts_a_blanket_somewhere` · spec `("person_puts_a_blanket_somewhere")` · NSVS max_p=0.46 · satisfied=False
- **C:** `person_takes_paper_from_somewhere` · spec `("person_takes_paper_from_somewhere")` · NSVS max_p=0.838 · satisfied=True
- **D:** `person_opens_a_laptop` · spec `("person_opens_a_laptop")` · NSVS max_p=0.906 · satisfied=False

### QID 1597 · `agqa_LPPFL.mp4` · short_star_agqa · ok

- Stem: What action does the person do throughout the video ?
- Duration: 0.36s · Sub #5B: **D** · Sub #1: **D**
- Argmax: **D** (score 0.942, gap 0.09399999999999997)

- **A:** `person_holds_a_cup_of_something` · spec `("person_holds_a_cup_of_something")` · NSVS max_p=0.824 · satisfied=True
- **B:** `person_drinks_from_a_cup` · spec `("person_drinks_from_a_cup")` · NSVS max_p=0.848 · satisfied=True
- **C:** `person_holds_some_clothes` · spec `("person_holds_some_clothes")` · NSVS max_p=0.373 · satisfied=False
- **D:** `person_works_at_a_table` · spec `("person_works_at_a_table")` · NSVS max_p=0.942 · satisfied=True

### QID 1635 · `ct_eEBZ0nY0FFI.mp4` · long_ct · ok

- Stem: What does the person do in the video ?
- Duration: 319.83s · Sub #5B: **D** · Sub #1: **C**
- Argmax: **A** (score 0.989, gap 0.0010000000000000009)

- **A:** `person_flips_bread` · spec `("person_flips_bread")` · NSVS max_p=0.989 · satisfied=False
- **B:** `person_flips_steak` · spec `("person_flips_steak")` · NSVS max_p=0.988 · satisfied=False
- **C:** `person_removes_cap` · spec `("person_removes_cap")` · NSVS max_p=0.987 · satisfied=True
- **D:** `person_adds_spices` · spec `("person_adds_spices")` · NSVS max_p=0.988 · satisfied=True

### QID 1947 · `agqa_9OMY1.mp4` · mid_agqa · ok

- Stem: What does the person do in the video ?
- Duration: 0.92s · Sub #5B: **A** · Sub #1: **A**
- Argmax: **A** (score 0.959, gap 0.0030000000000000027)

- **A:** `person_sits_in_a_chair` · spec `("person_sits_in_a_chair")` · NSVS max_p=0.959 · satisfied=True
- **B:** `person_washes_a_dish` · spec `("person_washes_a_dish")` · NSVS max_p=0.956 · satisfied=False
- **C:** `person_tidies_up_a_table` · spec `("person_tidies_up_a_table")` · NSVS max_p=0.753 · satisfied=True
- **D:** `person_throws_something_on_the_floor` · spec `("person_throws_something_on_the_floor")` · NSVS max_p=0.46 · satisfied=False

## Per-row summary

| qid | stratum | dur(s) | gap | argmax | Sub5B | Sub1 | match Sub1 |
|-----|---------|--------|-----|--------|-------|------|------------|
| 74 | short_star_agqa | 0.52 | 0.18700000000000006 | A | B | B | False |
| 196 | short_star_agqa | 0.16 | 0.07399999999999995 | C | D | D | False |
| 271 | short_star_agqa | 1.32 | 0.04599999999999993 | B | A | A | False |
| 678 | short_star_agqa | 1.2 | 0.5049999999999999 | C | C | C | True |
| 720 | long_ct | 198.06 | 0.013000000000000012 | A | C | C | False |
| 1387 | mid_agqa | 0.76 | 0.02200000000000002 | D | A | B | False |
| 1460 | mid_agqa | 0.88 | 0.020000000000000018 | A | B | B | False |
| 1597 | short_star_agqa | 0.36 | 0.09399999999999997 | D | D | D | True |
| 1635 | long_ct | 319.83 | 0.0010000000000000009 | A | D | C | False |
| 1947 | mid_agqa | 0.92 | 0.0030000000000000027 | A | A | A | True |

Full columns: `report/per_row.csv`
