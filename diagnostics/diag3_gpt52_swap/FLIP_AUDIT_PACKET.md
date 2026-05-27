# Diag3 flip audit packet (17 questions) — **ARCHIVED / DROPPED**

> **Dropped 2026-05-27.** Diagnostic 3 abandoned — no GT labels collected, no actionable lift found. Kept for historical record only; do not use for submission decisions.

**Purpose (historical):** Manual ground-truth tagging on the 17/48 subsample rows where **Diag3** (GPT-5.2 NSVS swap) changed the final answer vs **Sub5B** (InternVL NSVS).

**Context:** 50-Q val subsample (35 Sub1≠Sub5B disagreements + 15 agree controls). QIDs 57/399 excluded (no Diag3 pipeline output). Of 17 flips: **10 → Sub1 answer**, **7 → third answer** (neither Sub1 nor Sub5B).

**Reasoning:** Diag3 VQA reasoning summaries included for **8/17** rows (qids 9, 65, 84, 238, 387, 408, 443, 558). Sub1/Sub5B baselines have no stored reasoning. Full NSVS-window reasoning for all 17 is in `outputs/sub5b_subsample/report/per_question/{qid}.json`.

**Time-warp note:** `star` / `agqa` clips under **10s** are likely time-warped — use 0.25× playback when judging temporal order.

**How to tag:** Fill `Ground truth:` for each row. Optional verdict in **Notes** (Diag3 / Sub5B / Sub1 / all wrong / unanswerable).

## Quick index


| #   | QID | Source | Type    | Duration | Operator       | Sub1 | Sub5B | Diag3   | Flip toward | VQA reason |
| --- | --- | ------ | ------- | -------- | -------------- | ---- | ----- | ------- | ----------- | ---------- |
| 1   | 4   | bf     | MCQ     | 284.7s   | always_before  | B    | C     | **D**   | third       | —          |
| 2   | 9   | agqa   | Boolean | 2.1s ⚠   | after          | Yes  | No    | **Yes** | Sub1        | yes        |
| 3   | 21  | agqa   | MCQ     | 1.0s ⚠   | after          | C    | B     | **C**   | Sub1        | —          |
| 4   | 24  | ct     | MCQ     | 143.8s   | until          | A    | A     | **D**   | third       | —          |
| 5   | 26  | star   | MCQ     | 0.8s ⚠   | until          | B    | B     | **A**   | third       | —          |
| 6   | 65  | ct     | MCQ     | 240.4s   | always_after   | A    | D     | **A**   | Sub1        | yes        |
| 7   | 84  | agqa   | Boolean | 1.8s ⚠   | since          | No   | Yes   | **No**  | Sub1        | yes        |
| 8   | 206 | ct     | Boolean | 413.8s   | before         | No   | Yes   | **No**  | Sub1        | —          |
| 9   | 219 | agqa   | MCQ     | 1.8s ⚠   | always_after   | B    | C     | **D**   | third       | —          |
| 10  | 238 | ct     | MCQ     | 390.4s   | in_turn_occurs | C    | D     | **A**   | third       | yes        |
| 11  | 332 | star   | MCQ     | 1.6s ⚠   | since          | B    | C     | **B**   | Sub1        | —          |
| 12  | 366 | star   | Boolean | 1.5s ⚠   | since          | No   | Yes   | **No**  | Sub1        | —          |
| 13  | 387 | star   | MCQ     | 1.5s ⚠   | during         | D    | C     | **D**   | Sub1        | yes        |
| 14  | 408 | agqa   | MCQ     | 1.4s ⚠   | since          | C    | D     | **B**   | third       | yes        |
| 15  | 443 | agqa   | MCQ     | 1.9s ⚠   | until          | A    | C     | **D**   | third       | yes        |
| 16  | 484 | star   | MCQ     | 1.7s ⚠   | since          | A    | B     | **A**   | Sub1        | —          |
| 17  | 558 | ct     | MCQ     | 315.2s   | until          | C    | A     | **C**   | Sub1        | yes        |


⚠ = star/agqa clip under 10s (likely time-warped)

---

## 1. QID 4 — bf · MCQ · 284.7s (>180s) · always_before

- **Video:** [bf_P03_webcam01_P03_friedegg.mp4](../../../timelogic-data/videos/val/combined_2k_videos/bf_P03_webcam01_P03_friedegg.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P03_webcam01_P03_friedegg.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P03_webcam01_P03_friedegg.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person reaching for object which in turn always occurs before person reaching for plate ? Is it Option A: carry handle, Option B: carry plate, Option C: close oil cap, Option D: pull drawer.

- **A:** carry handle
- **B:** carry plate
- **C:** close oil cap
- **D:** pull drawer


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | B         |
| **Sub5B** (InternVL NSVS)      | C         |
| **Diag3** (GPT-5.2 NSVS)       | **D**     |
| **Ground truth**               | *Unclear* |


> Diag3 chose a third answer (neither Sub1=B nor Sub5B=C).

**Notes:**

---

## 2. QID 9 — agqa · Boolean · 2.1s (<10s) · ⚠ time-warped · after

- **Video:** [agqa_L0HDB.mp4](../../../timelogic-data/videos/val/combined_2k_videos/agqa_L0HDB.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_L0HDB.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_L0HDB.mp4'`

**Question:** Did the person tidy up a closet after walking through a doorway ?

- **Answers:** Yes / No


|                                | Answer                                                |
| ------------------------------ | ----------------------------------------------------- |
| **Sub1** (full-video baseline) | Yes                                                   |
| **Sub5B** (InternVL NSVS)      | No                                                    |
| **Diag3** (GPT-5.2 NSVS)       | **Yes**                                               |
| **Ground truth**               | *Tidies up cabinet but does not walk through doorway* |


> Diag3 matched Sub1 (not Sub5B).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Determining a yes/no response**

I need a simple yes or no answer. It seems like the situation is that someone walks from the living room to the kitchen through a doorway and then tidies or organizes a cabinet. It feels intuitive that the answer is likely "yes" since they’re moving from one space to another and taking action in the kitchen. So, I’m concluding with a "yes" response based on that context.

**Notes:**

---

## 3. QID 21 — agqa · MCQ · 1.0s (<10s) · ⚠ time-warped · after

- **Video:** [agqa_EDKXT.mp4](../../../timelogic-data/videos/val/combined_2k_videos/agqa_EDKXT.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_EDKXT.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_EDKXT.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do immediately after holding some clothes ? Is it Option A: hold some clothes, Option B: put a bag somewhere, Option C: drink from a cup, Option D: take a pillow from somewhere.

- **A:** hold some clothes
- **B:** put a bag somewhere
- **C:** drink from a cup
- **D:** take a pillow from somewhere


|                                | Answer |
| ------------------------------ | ------ |
| **Sub1** (full-video baseline) | C      |
| **Sub5B** (InternVL NSVS)      | B      |
| **Diag3** (GPT-5.2 NSVS)       | **C**  |
| **Ground truth**               | *C*    |


> Diag3 matched Sub1 (not Sub5B).

**Notes:**

---

## 4. QID 24 — ct · MCQ · 143.8s (60-180s) · until

- **Video:** [ct_fcFC9mEhPZI.mp4](../../../timelogic-data/videos/val/combined_2k_videos/ct_fcFC9mEhPZI.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_fcFC9mEhPZI.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_fcFC9mEhPZI.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until poured juice ? Is it Option A: stir mixture, Option B: pour mixture into cup, Option C: pour juice, Option D: pour water.

- **A:** stir mixture
- **B:** pour mixture into cup
- **C:** pour juice
- **D:** pour water


|                                | Answer |
| ------------------------------ | ------ |
| **Sub1** (full-video baseline) | A      |
| **Sub5B** (InternVL NSVS)      | A      |
| **Diag3** (GPT-5.2 NSVS)       | **D**  |
| **Ground truth**               | *D*    |


> Diag3 chose a third answer (neither Sub1=A nor Sub5B=A). Agree-control stratum (Sub1=Sub5B at baseline).

**Notes:**

---

## 5. QID 26 — star · MCQ · 0.8s (<10s) · ⚠ time-warped · until

- **Video:** [star_E1VFZ.mp4](../../../timelogic-data/videos/val/combined_2k_videos/star_E1VFZ.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_E1VFZ.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_E1VFZ.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until put a picture somewhere ? Is it Option A: put a picture somewhere, Option B: put a box somewhere, Option C: open a refrigerator, Option D: hold a broom.

- **A:** put a picture somewhere
- **B:** put a box somewhere
- **C:** open a refrigerator
- **D:** hold a broom


|                                | Answer |
| ------------------------------ | ------ |
| **Sub1** (full-video baseline) | B      |
| **Sub5B** (InternVL NSVS)      | B      |
| **Diag3** (GPT-5.2 NSVS)       | **A**  |
| **Ground truth**               | *B*    |


> Diag3 chose a third answer (neither Sub1=B nor Sub5B=B). Agree-control stratum (Sub1=Sub5B at baseline).

**Notes:**

---

## 6. QID 65 — ct · MCQ · 240.4s (>180s) · always_after

- **Video:** [ct_J5zJqnLoWCU.mp4](../../../timelogic-data/videos/val/combined_2k_videos/ct_J5zJqnLoWCU.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_J5zJqnLoWCU.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_J5zJqnLoWCU.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do always after pouring water ? Is it Option A: squeeze lemon, Option B: pour water, Option C: pour lemonade into glass, Option D: add sugar.

- **A:** squeeze lemon
- **B:** pour water
- **C:** pour lemonade into glass
- **D:** add sugar


|                                | Answer                                                                                                                                                                |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sub1** (full-video baseline) | A                                                                                                                                                                     |
| **Sub5B** (InternVL NSVS)      | D                                                                                                                                                                     |
| **Diag3** (GPT-5.2 NSVS)       | **A**                                                                                                                                                                 |
| **Ground truth**               | *The person does not pour water in this video. They do pour coconut oil which is clear like water and after that they squeeze a lemon so A would be the most correct* |


> Diag3 matched Sub1 (not Sub5B).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Considering lemonade preparation**

I’m thinking about the steps for making pink lemonade. After pouring water, the next likely action is to squeeze in lemon juice. It seems that adding sugar typically follows this. However, the phrase "always after pouring water" implies a consistent sequence in the recipe. Given that, I think my best option is to emphasize squeezing lemon after pouring the water. That makes sense in the context of making lemonade!

**Notes:**

---

## 7. QID 84 — agqa · Boolean · 1.8s (<10s) · ⚠ time-warped · since

- **Video:** [agqa_APLZS.mp4](../../../timelogic-data/videos/val/combined_2k_videos/agqa_APLZS.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_APLZS.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_APLZS.mp4'`

**Question:** Has the person been sitting at a table since they held a cup of something ?

- **Answers:** Yes / No


|                                | Answer |
| ------------------------------ | ------ |
| **Sub1** (full-video baseline) | No     |
| **Sub5B** (InternVL NSVS)      | Yes    |
| **Diag3** (GPT-5.2 NSVS)       | **No** |
| **Ground truth**               | *Yes*  |


> Diag3 matched Sub1 (not Sub5B).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Evaluating sitting at a table**

I need to consider if the person has been sitting at a table since they held a cup. It’s tricky because it implies they were continuously sitting after holding the cup. However, in the frames, it seems he is already sitting while holding the cup. This raises questions about the wording since it suggests maintaining a seated position. At certain frames, he's bent over the box, but is he still seated?

**Clarifying seating situation**

It seems the person moved away from the table, which leads me to think he might still be seated on a chair beside the box, rather than at the table. So, that means he hasn't been sitting at the table since he held the cup. I can conclude that the answer is "No." It’s interesting how little movements can clarify the situation like this!

**Notes:**

---

## 8. QID 206 — ct · Boolean · 413.8s (>180s) · before

- **Video:** [ct_11n4mQxwuaM.mp4](../../../timelogic-data/videos/val/combined_2k_videos/ct_11n4mQxwuaM.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_11n4mQxwuaM.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_11n4mQxwuaM.mp4'`

**Question:** Did the person brake on before withdrawing wheel ?

- **Answers:** Yes / No


|                                | Answer |
| ------------------------------ | ------ |
| **Sub1** (full-video baseline) | No     |
| **Sub5B** (InternVL NSVS)      | Yes    |
| **Diag3** (GPT-5.2 NSVS)       | **No** |
| **Ground truth**               | *Yes*  |


> Diag3 matched Sub1 (not Sub5B).

**Notes:**

---

## 9. QID 219 — agqa · MCQ · 1.8s (<10s) · ⚠ time-warped · always_after

- **Video:** [agqa_S0Z00.mp4](../../../timelogic-data/videos/val/combined_2k_videos/agqa_S0Z00.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_S0Z00.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_S0Z00.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do always after holding a book ? Is it Option A: watch a book, Option B: take a laptop from somewhere, Option C: take a phone from somewhere, Option D: hold a phone.

- **A:** watch a book
- **B:** take a laptop from somewhere
- **C:** take a phone from somewhere
- **D:** hold a phone


|                                | Answer                                                                                                                                                               |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sub1** (full-video baseline) | B                                                                                                                                                                    |
| **Sub5B** (InternVL NSVS)      | C                                                                                                                                                                    |
| **Diag3** (GPT-5.2 NSVS)       | **D**                                                                                                                                                                |
| **Ground truth**               | *Unclear B; the person holds the book for almost the entire video. After they put the book down they take the laptop from under their arm and place it down as well* |


> Diag3 chose a third answer (neither Sub1=B nor Sub5B=C).

**Notes:**

---

## 10. QID 238 — ct · MCQ · 390.4s (>180s) · in_turn_occurs

- **Video:** [ct_aiYkICcjuTA.mp4](../../../timelogic-data/videos/val/combined_2k_videos/ct_aiYkICcjuTA.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_aiYkICcjuTA.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_aiYkICcjuTA.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action occurs before person flipping steak which in turn occurs before person opening lid ? Is it Option A: taste steak, Option B: cut steak, Option C: take steak from grill, Option D: flip steak.

- **A:** taste steak
- **B:** cut steak
- **C:** take steak from grill
- **D:** flip steak


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | C         |
| **Sub5B** (InternVL NSVS)      | D         |
| **Diag3** (GPT-5.2 NSVS)       | **A**     |
| **Ground truth**               | *fill in* |


> Diag3 chose a third answer (neither Sub1=C nor Sub5B=D).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Analyzing cooking sequence**

I’m working through the sequence of actions for grilling steaks: it appears that flipping the steak should happen before opening the lid. I'm considering possible initial actions, like taking the steak from the grill or slicing it. The frames I see show the grill lid closed before it's open for access, suggesting that I need to open the lid before placing or flipping the steak. This sequence could be confusing if the flipping implies too much. I wonder about alternatives, like using a griddle!

**Exploring grill actions**

I’m considering the actions involved in grilling: could there be a second opening of the lid after flipping? It makes sense to close the lid while cooking, then open it to flip the steak and close it again before removing it later. The frames I see suggest this, especially with the sequence of actions. I need to figure out what actions can happen before the flip, but it seems tricky. The options are limited, and the idea that flipping happens before flipping itself feels confusing!

**Clarifying steak grilling order**

I’m considering whether "take steak from grill" could happen before flipping. Could it be that after taking the first steak off, I flip another? In the sampling I reviewed, I see the steaks with grill marks and a man wrapping them in foil before serving at the table. There’s no explicit flipping shown, which makes me think it likely happened between placing and those final marks. Also, the lid opening in frame 11 suggests it happens before flipping too.

**Notes:**

---

## 11. QID 332 — star · MCQ · 1.6s (<10s) · ⚠ time-warped · since

- **Video:** [star_9EP7R.mp4](../../../timelogic-data/videos/val/combined_2k_videos/star_9EP7R.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_9EP7R.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_9EP7R.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What has been the person doing since they held a pillow ? Is it Option A: walk through a doorway, Option B: hold a pillow, Option C: sit in a bed, Option D: hold a phone/camera.

- **A:** walk through a doorway
- **B:** hold a pillow
- **C:** sit in a bed
- **D:** hold a phone/camera


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | B         |
| **Sub5B** (InternVL NSVS)      | C         |
| **Diag3** (GPT-5.2 NSVS)       | **B**     |
| **Ground truth**               | *fill in* |


> Diag3 matched Sub1 (not Sub5B).

**Notes:**

---

## 12. QID 366 — star · Boolean · 1.5s (<10s) · ⚠ time-warped · since

- **Video:** [star_18FTZ.mp4](../../../timelogic-data/videos/val/combined_2k_videos/star_18FTZ.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_18FTZ.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_18FTZ.mp4'`

**Question:** Has the person been taking food from somewhere since they sat on the floor ?

- **Answers:** Yes / No


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | No        |
| **Sub5B** (InternVL NSVS)      | Yes       |
| **Diag3** (GPT-5.2 NSVS)       | **No**    |
| **Ground truth**               | *fill in* |


> Diag3 matched Sub1 (not Sub5B).

**Notes:**

---

## 13. QID 387 — star · MCQ · 1.5s (<10s) · ⚠ time-warped · during

- **Video:** [star_L0YQM.mp4](../../../timelogic-data/videos/val/combined_2k_videos/star_L0YQM.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_L0YQM.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_L0YQM.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. While the person is taking a book from somewhere , what does this imply about person action ? Is it Option A: hold a book, Option B: throw a bag somewhere, Option C: open a bag, Option D: take a book from somewhere.

- **A:** hold a book
- **B:** throw a bag somewhere
- **C:** open a bag
- **D:** take a book from somewhere


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | D         |
| **Sub5B** (InternVL NSVS)      | C         |
| **Diag3** (GPT-5.2 NSVS)       | **D**     |
| **Ground truth**               | *fill in* |


> Diag3 matched Sub1 (not Sub5B).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Determining book implications**

I’m analyzing the question about what it implies when a person takes a book. I think the options revolve around whether it connects to the action of just taking the book or if it suggests something like having an open bag. It seems like if they’re pulling the book from an open bag, that’s relevant too. However, the strongest implication is still option D, as it most closely matches the event. I'll go with D.

**Notes:**

---

## 14. QID 408 — agqa · MCQ · 1.4s (<10s) · ⚠ time-warped · since

- **Video:** [agqa_VNMNF.mp4](../../../timelogic-data/videos/val/combined_2k_videos/agqa_VNMNF.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_VNMNF.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_VNMNF.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What has been the person doing since they undressed themselves ? Is it Option A: take a book from somewhere, Option B: sit in a chair, Option C: go from standing to sitting, Option D: watch a book.

- **A:** take a book from somewhere
- **B:** sit in a chair
- **C:** go from standing to sitting
- **D:** watch a book


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | C         |
| **Sub5B** (InternVL NSVS)      | D         |
| **Diag3** (GPT-5.2 NSVS)       | **B**     |
| **Ground truth**               | *fill in* |


> Diag3 chose a third answer (neither Sub1=C nor Sub5B=D).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Evaluating clothing removal context**

Hmm, the phrase "since they undressed themselves" suggests they’ve been doing something continuously afterward, likely standing. I wonder what they could be doing—maybe they undressed and then started reading a book? No, that doesn’t feel right. The most plausible scenario seems to be that they sat down in a chair after undressing. So, I'll go with option B.

**Notes:**

---

## 15. QID 443 — agqa · MCQ · 1.9s (<10s) · ⚠ time-warped · until

- **Video:** [agqa_TIWRY.mp4](../../../timelogic-data/videos/val/combined_2k_videos/agqa_TIWRY.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_TIWRY.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_TIWRY.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until put a bag somewhere ? Is it Option A: take food from somewhere, Option B: put a box somewhere, Option C: open a bag, Option D: take a box from somewhere.

- **A:** take food from somewhere
- **B:** put a box somewhere
- **C:** open a bag
- **D:** take a box from somewhere


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | A         |
| **Sub5B** (InternVL NSVS)      | C         |
| **Diag3** (GPT-5.2 NSVS)       | **D**     |
| **Ground truth**               | *fill in* |


> Diag3 chose a third answer (neither Sub1=A nor Sub5B=C).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Deciding on actions**

I need to clarify what the person did with the bag. Initially, they hold a plastic bag, open it, take out boxes, and put them on the counter. At some point, they set the bag down, possibly off-screen. The crucial action seems to be taking a box from the bag, specifically a food box. So, I'd say option D is correct: she removed a box from the bag before putting it somewhere.

**Notes:**

---

## 16. QID 484 — star · MCQ · 1.7s (<10s) · ⚠ time-warped · since

- **Video:** [star_ZF5CP.mp4](../../../timelogic-data/videos/val/combined_2k_videos/star_ZF5CP.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_ZF5CP.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_ZF5CP.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What has been the person doing since they opened a door ? Is it Option A: hold some clothes, Option B: close a closet/cabinet, Option C: open a closet/cabinet, Option D: close a door.

- **A:** hold some clothes
- **B:** close a closet/cabinet
- **C:** open a closet/cabinet
- **D:** close a door


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | A         |
| **Sub5B** (InternVL NSVS)      | B         |
| **Diag3** (GPT-5.2 NSVS)       | **A**     |
| **Ground truth**               | *fill in* |


> Diag3 matched Sub1 (not Sub5B).

**Notes:**

---

## 17. QID 558 — ct · MCQ · 315.2s (>180s) · until

- **Video:** [ct_EaRdzd6KSGE.mp4](../../../timelogic-data/videos/val/combined_2k_videos/ct_EaRdzd6KSGE.mp4)
- **Path:** `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_EaRdzd6KSGE.mp4`
- **Play:** `ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_EaRdzd6KSGE.mp4'`

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until poured lemon juice ? Is it Option A: pour lemon juice, Option B: add lettuce, Option C: add ice, Option D: add tomato.

- **A:** pour lemon juice
- **B:** add lettuce
- **C:** add ice
- **D:** add tomato


|                                | Answer    |
| ------------------------------ | --------- |
| **Sub1** (full-video baseline) | C         |
| **Sub5B** (InternVL NSVS)      | A         |
| **Diag3** (GPT-5.2 NSVS)       | **C**     |
| **Ground truth**               | *fill in* |


> Diag3 matched Sub1 (not Sub5B).

**Diag3 VQA reasoning** *(gpt-5.2 summary)*

**Exploring beverage preparation**

The question, "What did the person do until poured lemon juice?" is asking for the actions that occurred prior to that moment. It seems like the context is about making a beverage, with ingredients like lemons, ice, and mint involved. I think it's likely that ice was added before pouring the lemon juice. So, among the options, I would choose option C for clarity.

**Notes:**

---

## Tally (fill after review)


| Verdict       | Count |
| ------------- | ----- |
| Diag3 correct |       |
| Sub5B correct |       |
| Sub1 correct  |       |
| All wrong     |       |
| Unanswerable  |       |


