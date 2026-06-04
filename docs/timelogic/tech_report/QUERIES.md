# Tech report — queries (v1 clips)

14 benchmark questions tied to the clip gallery (`v1_clips/gallery.html`).
Regenerate: `python3 scripts/build_clip_gallery_meta.py`.

**Note:** EvalAI val **ground truth** is not stored locally. Val rows show Sub #1 vs Sub #5B;
test rows show Sub #7b (and Sub #9 where noted). Step 3 (worked/failed vs GT) needs label export.

## #01 — val qid 1809 (star, immediately_after)

**Question:** Did the person put a phone/camera somewhere immediately after drinking from a cup/glass/bottle ?

**Choices:** Yes / No

**PULS spec:** `"person_drinks_from_cupglassbottle" U "person_puts_phonecamera_somewhere"`

| Run | Answer |
| --- | --- |
| Sub #1 | No |
| Sub #5B (val pipeline) | Yes |
| Sub1 vs 5B | **disagree** |

FOI: `-1` · `star_1SLTT.mp4`

---

## #02 — val qid 1014 (star, since)

**Question:** Has the person been reaching for and grabbing a picture since they lay on the floor ?

**Choices:** Yes / No

**PULS spec:** `"person_lays_on_the_floor" U ("person_reaches_for_a_picture" & "person_grabs_a_picture")`

| Run | Answer |
| --- | --- |
| Sub #1 | No |
| Sub #5B (val pipeline) | Yes |
| Sub1 vs 5B | **disagree** |

FOI: `-1` · `star_LG7WK.mp4`

---

## #03 — val qid 1215 (agqa, always_before)

**Cleaned:** Which action always occurs before person opening a laptop and person opening a bag ?

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person opening a laptop and person opening a bag ? Is it Option A: open a bag, Option B: put a bag somewhere, Option C: hold a bag, Option D: open a laptop. Reply with the chosen option in one character.

**Choices:**
- **A:** open a bag
- **B:** put a bag somewhere
- **C:** hold a bag
- **D:** open a laptop

**PULS spec:** `"person_opens_a_laptop" U "person_opens_a_bag"`

| Run | Answer |
| --- | --- |
| Sub #1 | C |
| Sub #5B (val pipeline) | B |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `agqa_DBT6E.mp4`

---

## #04 — val qid 1252 (agqa, before)

**Question:** Did the person sit at a table before holding a broom ?

**Choices:** Yes / No

**PULS spec:** `"person_sits_at_a_table" U "person_holds_a_broom"`

| Run | Answer |
| --- | --- |
| Sub #1 | Yes |
| Sub #5B (val pipeline) | No |
| Sub1 vs 5B | **disagree** |

FOI: `-1` · `agqa_SXFG6.mp4`

---

## #05 — val qid 107 (bf, always_before)

**Cleaned:** Which action always occurs before person pushing drawer which in turn always occurs before person reaching for Choco lid ?

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person pushing drawer which in turn always occurs before person reaching for Choco lid ? Is it Option A: reach for chocolate powder, Option B: scoop chocolate powder, Option C: reach for spoon, Option D: carry Choco lid. Reply with the chosen option in one character.

**Choices:**
- **A:** reach for chocolate powder
- **B:** scoop chocolate powder
- **C:** reach for spoon
- **D:** carry Choco lid

**PULS spec:** `"person_pushes_drawer" U "person_reaches_for_choco_lid"`

| Run | Answer |
| --- | --- |
| Sub #1 | C |
| Sub #5B (val pipeline) | A |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `bf_P35_webcam02_P35_milk.mp4`

---

## #06 — val qid 808 (bf, unknown)

**Question:** Does the person eventually carry milk ?

**Choices:** Yes / No

**PULS spec:** `("person_carries_milk")`

| Run | Answer |
| --- | --- |
| Sub #1 | No |
| Sub #5B (val pipeline) | Yes |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `bf_P47_cam01_P47_cereals.mp4`

---

## #07 — val qid 1911 (ct, before)

**Cleaned:** What did the person do before steaming milk ?

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do before steaming milk ? Is it Option A: add coffee, Option B: pour milk, Option C: steam milk, Option D: put meringue into oven. Reply with the chosen option in one character.

**Choices:**
- **A:** add coffee
- **B:** pour milk
- **C:** steam milk
- **D:** put meringue into oven

**PULS spec:** `("person_steams_milk")`

| Run | Answer |
| --- | --- |
| Sub #1 | B |
| Sub #5B (val pipeline) | A |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `ct_rUo6VC9HxJ8.mp4`

---

## #08 — val qid 738 (ct, always_after)

**Question:** Did the person put meringue into oven always after spreading mixture ?

**Choices:** Yes / No

**PULS spec:** `"person_spreads_mixture" U "person_puts_meringue_into_oven"`

| Run | Answer |
| --- | --- |
| Sub #1 | No |
| Sub #5B (val pipeline) | Yes |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `ct_Jp1U6Gb1DxM.mp4`

---

## #09 — val qid 1525 (bf, in_turn_occurs)

**Question:** Is it true that person opening butter lid occurs before person opening butter lid and which in turn occurs before person reaching for plate ?

**Choices:** Yes / No

**PULS spec:** `"person_opens_butter_lid" U "person_reaches_for_plate"`

| Run | Answer |
| --- | --- |
| Sub #1 | No |
| Sub #5B (val pipeline) | Yes |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `bf_P43_cam01_P43_scrambledegg.mp4`

---

## #10 — val qid 1590 (ct, always_after)

**Cleaned:** What did the person do always after pouring jello powder ?

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do always after pouring jello powder ? Is it Option A: pour water, Option B: pour juice, Option C: pour jello powder, Option D: pour alcohol. Reply with the chosen option in one character.

**Choices:**
- **A:** pour water
- **B:** pour juice
- **C:** pour jello powder
- **D:** pour alcohol

**PULS spec:** `("person_pours_jello_powder")`

| Run | Answer |
| --- | --- |
| Sub #1 | A |
| Sub #5B (val pipeline) | D |
| Sub1 vs 5B | **disagree** |

FOI: `non_minus1` · `ct_mN3Tus1ellQ.mp4`

---

## #11 — test qid 1 (star, unknown)

**Question:** Does the person taking/consuming some medicine imply holding a laptop ?

**Choices:** Yes / No

**PULS spec:** `"person_takesconsumes_some_medicine" U "person_holds_a_laptop"`

| Run | Answer |
| --- | --- |
| Sub #7b (test) | No |
| Sub #9 PULS v2 (test) | Yes |

FOI: `[-1]` · `star_H8S4L.mp4`

---

## #12 — test qid 2 (agqa, before)

**Question:** Did the person smile in a mirror before watching a book ?

**Choices:** Yes / No

**PULS spec:** `"person_smiles_in_a_mirror" U "person_watches_a_book"`

| Run | Answer |
| --- | --- |
| Sub #7b (test) | No |
| Sub #9 PULS v2 (test) | No |

FOI: `[0, 34]` · `agqa_QZP8N.mp4`

---

## #13 — test qid 500 (bf, immediately_after)

**Question:** Did the person carry kettle immediately after reaching for kettle ?

**Choices:** Yes / No

**PULS spec:** `"person_reaches_for_kettle" U "person_carries_kettle"`

| Run | Answer |
| --- | --- |
| Sub #7b (test) | Yes |
| Sub #9 PULS v2 (test) | Yes |

FOI: `[15, 255]` · `bf_P38_webcam01_P38_tea.mp4`

---

## #14 — test qid 1500 (ct, always_after)

**Question:** Did the person seal jar always after putting vegetables in water ?

**Choices:** Yes / No

**PULS spec:** `"person_puts_vegetables_in_water" U "person_seals_jar"`

| Run | Answer |
| --- | --- |
| Sub #7b (test) | Yes |
| Sub #9 PULS v2 (test) | Yes |

FOI: `[-1]` · `ct_r4bFhhEhLpI.mp4`

---
