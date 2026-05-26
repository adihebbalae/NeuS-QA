# PULS v2 — semantic eyeball packet (20 min)

Generated: 2026-05-26 18:03 UTC · Source: `/mnt/Data/ah66742/timelogic/outputs/puls_v2_validation_148/results.jsonl`

## Risk (read once)

A **well-formed-but-wrong** spec can be worse than empty PULS: empty → NSVS bypass → VQA prior (~42–60% Yes on unknown-family). Wrong-but-valid → NSVS runs → confident bad crop → answer flips empty-fallback would not cause. Structural 148/148 pass does not prove semantic correctness.

## How to skim

1. **Bucket A** (10 rows) — generic `person performs action in video`
2. **Bucket B** (10 rows) — `AND` co-occur / `NOT (anchor AND candidate)` non-overlap
3. **Ctrl+click** the **Video** link on each row to open the raw mp4 in Cursor (relative path from this file).
4. Mark **OK / Wrong intent / Ambiguous** per row. Flag over-fire (Example 13 on non-generic stems).

**Pass bar:** no more than ~2 clear Wrong intent per bucket before full val PULS re-run.

---

## Bucket A — was `empty_puls_output` (94 rows total)

Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

### 1. QID 1291 · `star` · atemporal-MC · throughout

**Video:** [star_OJGGZ.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_OJGGZ.mp4) — **~1.16 s** (OpenCV, 29 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_OJGGZ.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 2. QID 660 · `agqa` · atemporal-MC · in-video

**Video:** [agqa_Z0KN7.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_Z0KN7.mp4) — **~0.64 s** (OpenCV, 16 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_Z0KN7.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 3. QID 1502 · `ct` · atemporal-MC · in-video

**Video:** [ct_15nl0YLF8FU.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_15nl0YLF8FU.mp4) — **~494.027 s** (OpenCV, 14806 frames @ 29.97003 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_15nl0YLF8FU.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 4. QID 1070 · `star` · atemporal-MC · in-video

**Video:** [star_H32FR.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_H32FR.mp4) — **~1.12 s** (OpenCV, 28 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_H32FR.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 5. QID 678 · `agqa` · atemporal-MC · throughout

**Video:** [agqa_2U0GH.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_2U0GH.mp4) — **~1.2 s** (OpenCV, 30 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_2U0GH.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 6. QID 157 · `ct` · atemporal-MC · in-video

**Video:** [ct_9CMaZEq1byU.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_9CMaZEq1byU.mp4) — **~227.727 s** (OpenCV, 6825 frames @ 29.97003 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_9CMaZEq1byU.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 7. QID 1514 · `star` · atemporal-MC · in-video

**Video:** [star_LVTRJ.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LVTRJ.mp4) — **~1.6 s** (OpenCV, 40 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LVTRJ.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 8. QID 271 · `agqa` · atemporal-MC · in-video

**Video:** [agqa_EIT66.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_EIT66.mp4) — **~1.32 s** (OpenCV, 33 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_EIT66.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 9. QID 1370 · `ct` · atemporal-MC · in-video

**Video:** [ct_L8E0hD85g3A.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_L8E0hD85g3A.mp4) — **~337.103 s** (OpenCV, 10103 frames @ 29.97003 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_L8E0hD85g3A.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 10. QID 1214 · `star` · atemporal-MC · in-video

**Video:** [star_LKH9A.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LKH9A.mp4) — **~2.88 s** (OpenCV, 72 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LKH9A.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ?

**Baseline (v1):** *(empty — no props, no spec)*

**PULS v2:**
- `person_performs_action_in_video`
- spec: `("person_performs_action_in_video")`

**Check:** Does the generic hook match an **atemporal “which action”** MC (not a specific option, not a temporal before/after)? **Over-fire** = question has a real anchor but spec ignores it.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

## Bucket B — was `operator_collapse_open_ended` (54 rows total)

Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

### 1. QID 1727 · `agqa` · non-overlap MC

**Video:** [agqa_XBXKO.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_XBXKO.mp4) — **~0.76 s** (OpenCV, 19 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_XBXKO.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with playing with a phone ?

**Baseline (v1):** **1 prop** · `! ("person_plays_with_a_phone")`

**PULS v2:**
- `person_plays_with_a_phone`
- `person_performs_candidate_action`
- spec: `! ("person_plays_with_a_phone" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 2. QID 506 · `ct` · non-overlap MC

**Video:** [ct_hQGil8MPacU.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_hQGil8MPacU.mp4) — **~392.933 s** (OpenCV, 11788 frames @ 30.0 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_hQGil8MPacU.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with whisking mixture ?

**Baseline (v1):** **1 prop** · `! "person_whisks_mixture"`

**PULS v2:**
- `person_whisks_mixture`
- `person_performs_candidate_action`
- spec: `! ("person_whisks_mixture" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 3. QID 1774 · `star` · co-occurrence MC

**Video:** [star_NUSKJ.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_NUSKJ.mp4) — **~0.48 s** (OpenCV, 12 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_NUSKJ.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding a dish ?

**Baseline (v1):** **1 prop** · `("person_holds_a_dish")`

**PULS v2:**
- `person_holds_a_dish`
- `person_performs_candidate_action`
- spec: `"person_holds_a_dish" & "person_performs_candidate_action"`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 4. QID 1365 · `agqa` · co-occurrence MC

**Video:** [agqa_VU7P7.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_VU7P7.mp4) — **~1.12 s** (OpenCV, 28 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_VU7P7.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with smiling at a book ?

**Baseline (v1):** **1 prop** · `("smiling_at_a_book")`

**PULS v2:**
- `person_smiles_at_a_book`
- `person_performs_candidate_action`
- spec: `"person_smiles_at_a_book" & "person_performs_candidate_action"`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 5. QID 1582 · `ct` · non-overlap MC

**Video:** [ct_hywbrms5B1k.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_hywbrms5B1k.mp4) — **~333.867 s** (OpenCV, 10006 frames @ 29.97003 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_hywbrms5B1k.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with adding coffee ?

**Baseline (v1):** **1 prop** · `("person_adds_coffee")`

**PULS v2:**
- `person_adds_coffee`
- `person_performs_candidate_action`
- spec: `! ("person_adds_coffee" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 6. QID 803 · `agqa` · co-occurrence MC

**Video:** [agqa_LA266.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_LA266.mp4) — **~1.16 s** (OpenCV, 29 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_LA266.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding some food ?

**Baseline (v1):** **1 prop** · `("person_holds_some_food")`

**PULS v2:**
- `person_holds_some_food`
- `person_performs_candidate_action`
- spec: `"person_holds_some_food" & "person_performs_candidate_action"`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 7. QID 55 · `ct` · non-overlap MC

**Video:** [ct_yOZJFtxl7sA.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_yOZJFtxl7sA.mp4) — **~249.549 s** (OpenCV, 7479 frames @ 29.97003 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_yOZJFtxl7sA.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring jello powder ?

**Baseline (v1):** **1 prop** · `! "person_pours_jello_powder"`

**PULS v2:**
- `person_pours_jello_powder`
- `person_performs_candidate_action`
- spec: `! ("person_pours_jello_powder" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 8. QID 485 · `agqa` · non-overlap MC

**Video:** [agqa_DPLMM.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_DPLMM.mp4) — **~2 s** (OpenCV, 50 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_DPLMM.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with lying on the floor ?

**Baseline (v1):** **1 prop** · `("person_lies_on_the_floor")`

**PULS v2:**
- `person_lies_on_the_floor`
- `person_performs_candidate_action`
- spec: `! ("person_lies_on_the_floor" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 9. QID 161 · `ct` · non-overlap MC

**Video:** [ct_t7gBwQgUgvU.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_t7gBwQgUgvU.mp4) — **~315.849 s** (OpenCV, 9466 frames @ 29.97003 fps) · `>180s`  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_t7gBwQgUgvU.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with flipping pancake ?

**Baseline (v1):** **1 prop** · `("person_flips_pancake")`

**PULS v2:**
- `person_flips_pancake`
- `person_performs_candidate_action`
- spec: `! ("person_flips_pancake" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

### 10. QID 1602 · `agqa` · non-overlap MC

**Video:** [agqa_XBXKO.mp4](../../../../../mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_XBXKO.mp4) — **~0.76 s** (OpenCV, 19 frames @ 25.0 fps) · `<10s` · ⚠ star/agqa short-clip  
<sub>Ctrl+click link in Cursor preview · `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_XBXKO.mp4`</sub>

> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with taking some clothes from somewhere ?

**Baseline (v1):** **1 prop** · `("person_takes_some_clothes_from_somewhere")`

**PULS v2:**
- `person_takes_some_clothes_from_somewhere`
- `person_performs_candidate_action`
- spec: `! ("person_takes_some_clothes_from_somewhere" & "person_performs_candidate_action")`

**Check:** Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; non-overlap = negated joint presence)? **Over-fire** = only anchor restated; **under-fire** = `NOT anchor` alone without candidate slot.

**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________

---

## Sign-off

| Bucket | OK | Wrong | Ambiguous | Block val re-run? |
| --- | ---: | ---: | ---: | --- |
| A (empty → generic) | | | | ☐ |
| B (collapse → AND/NOT) | | | | ☐ |

**Reviewer:** _____________ **Date:** _____________
