# Overnight PULS review — bucket A (94 empty-PULS rows) + bucket B (54 operator-collapse rows)

Generated: 2026-05-25T04:08:08.637527+00:00

## PULS prompt currently in production

From `nsvqa/puls/prompts.py` → `find_prompt()` (single user message; `{prompt}` filled per question):

```

You are an intelligent agent designed to extract structured representations from video question prompts. You will operate in two stages: (1) proposition extraction and (2) TL specification generation.

Stage 1: Proposition Extraction

Given an input question about a video, extract the atomic propositions that describe the underlying events or facts explicity referenced in the question. These propositions should describe object-action or object-object relationships stated in the question — avoid making assumptions or inferring any additional events. Avoid TL keywords such as 'and', 'or', 'not', 'until'.
Do not include ambiguous propositions that lack specificity. For instance, phrases like "guy does something" are ambiguous and should be omitted. Instead, focus on concrete actions or relationships. For example, given the prompt "In a bustling park, a child kicks a ball. What happens when the ball hits the bench?", the correct propositions are ["child kicks ball", "ball hits bench"].
If a proposition mentions subtitles/captions, the format of the proposition is the word "subtile_" followed by the subtitle in single quotes. Do NOT add words like "appears"/"says"/"mentions" after the subtitle; follow this format to create the individual proposition. For example, given the prompt "After the man gets up, what happens after the subtitle 'Hello Mr. Anderson' appeared?", the correct propositions are ["man gets up", "subtitle_'Hello Mr. Anderson'"].

Stage 2: TL Specification Generation

Using only the list of the propositions extracted in Stage 1, generate a single Temporal Logic (TL) specification that catpures the sequence of logical structure implied by the question. 

Rules:
- The formula must use each proposition **exactly once**
- Use only the TL operators: `AND`, `OR`, `NOT`, `UNTIL`
- Do **not** infer new events or rephrase propositions.
- The formula should reflect the temporal or logical relationships between the propositions under which the question would be understandable.

**Examples**

Example 1: "In a sunny meadow, a child plays with a kite and runs around. What does the child do after falling?"
Output:
{{
  "proposition": ["child plays with kite", "child runs around", "child falls"],
  "specification": "(child plays with kite AND child runs around) UNTIL child falls"
}}

Example 2: "In a dimly lit room, two robots stand silently. What happens when the red robot starts blinking or the green robot does not turn off?"
Output:
{{
  "proposition": ["robots stand silently", "red robot starts blinking", "green robot turns off"],
  "specification": "robots stand silently UNTIL (red robot starts blinking OR NOT green robot turns off)"
}}

Example 3: "Inside a cave, a man holds a lantern. What happens when the man sees the dragon?"
Output:
{{
  "proposition": ["man holds lantern", "man sees dragon"],
  "specification": "man holds lantern UNTIL man sees dragon"
}}

Example 4: "What happened on the screen before a man in black armor with glasses spoke into the microphone in front of a golden sky and the subtitles said 'country uh so we've seen significant'?"
Output:
{{
  "proposition": ["man in black armor with glasses spoke into the microphone", "man is in front of a golden sky", "subtitle_'country uh so we've seen significant'"],
  "specification": "(man in black armor with glasses spoke into the microphone AND man is in front of a golden sky) UNTIL (subtitle_'country uh so we've seen significant')"
}}

Example 5: "A news anchor with curled hair is wearing a pink blazer over a black base and sitting in front of the camera reading the news. What happened before the caption 'standards our climate editor Justin rout' appeared?"
Output:
{{
  "proposition": ["news anchor with curled hair is wearing a pink blazer over a black base", "news anchor sitting in front of the camera reading the news", "subtitle_'standards our climate editor Justin rout'"],
  "specification": "(news anchor with curled hair is wearing a pink blazer over a black base AND news anchor sitting in front of the camera reading the news) UNTIL subtitle_'standards our climate editor Justin rout'"
}}


Example 6: "How did the girl feel before turning on the computer?"
Output:
{{
  "proposition": ["girl turns on computer"],
  "specification": "(girl turns on computer)"
}}

Example 7 (TimeLogic — "what did person do after X" / open-ended forward): "What did the person do after walking through a doorway?"
Output:
{{
  "proposition": ["person walks through a doorway"],
  "specification": "(person walks through a doorway)"
}}

Example 8 (TimeLogic — "what did person do always after X" / open-ended forward, "always" is a qualifier, NOT a negation): "What did the person do always after holding a book?"
Output:
{{
  "proposition": ["person holds a book"],
  "specification": "(person holds a book)"
}}

Example 9 (TimeLogic — "did Y happen always after X" / two-prop ordering, Yes/No): "Did the person hold a phone always after taking a phone from somewhere?"
Output:
{{
  "proposition": ["person takes a phone from somewhere", "person holds a phone"],
  "specification": "person takes a phone from somewhere UNTIL person holds a phone"
}}

Example 10 (TimeLogic — "which action always occurs before X which in turn always occurs before Y" / chained anchor, open-ended backward): "Which action always occurs before person taking something from a box which in turn always occurs before person standing up?"
Output:
{{
  "proposition": ["person takes something from a box", "person stands up"],
  "specification": "person takes something from a box UNTIL person stands up"
}}

Example 11 (TimeLogic — "is it true that X always occurs before Y and Z" / one-to-many ordering, Yes/No): "Is it true that person opening a door always occurs before person talking on a phone and person putting a phone somewhere?"
Output:
{{
  "proposition": ["person opens a door", "person talks on a phone", "person puts a phone somewhere"],
  "specification": "person opens a door UNTIL (person talks on a phone AND person puts a phone somewhere)"
}}

Example 12 (TimeLogic — "A occurs before B and which in turn occurs before C" / 3-event chain expressed within AND/OR/NOT/UNTIL only, Yes/No): "Is it true that person throwing shoes somewhere occurs before person taking a laptop from somewhere and which in turn occurs before person closing a laptop?"
Output:
{{
  "proposition": ["person throws shoes somewhere", "person takes a laptop from somewhere", "person closes a laptop"],
  "specification": "(person throws shoes somewhere AND person takes a laptop from somewhere) UNTIL person closes a laptop"
}}

**Now process the following prompt:**
Input:
{{
  "prompt": "<QUESTION_TEXT>"
}}

Expected Output (only output the following JSON structure — nothing else):
{{
  "proposition": [...],
  "specification": "..."
}}

```

## Bucket A — empty PULS output (94 rows)

### Light tally (Cursor-computed, for Adi's morning skim)

- Mode breakdown: **88 MC**, **6 bool**
- Question-stem frequencies (top 10):
  - `The following is a multiple choice …`: **88**
  - `Does the person eventually …`: **3**
  - `Is the person always …`: **3**
- Source dataset breakdown:
  - **agqa**: 35
  - **ct**: 21
  - **star**: 38
- Average question length: **54.1** words

**Pattern notes (auto, no fix proposals):**
- Unique stem buckets: **3**; top stem covers **93.6%** of bucket.
- Failures are **MC-heavy** — likely MC template / candidate-parameterization gap.
- Largest source slice: **star** (38/94). Concentrated in short-clip sources.

### Rows (sorted by question-stem alphabetically)

#### QID 1975 (agqa, bool, <10s)

**Question:** Does the person eventually fix their hair ?
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** Yes
**Sub #1 answer:** No

#### QID 509 (ct, bool, 60-180s)

**Question:** Does the person eventually jack down ?
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** Yes
**Sub #1 answer:** Yes

#### QID 1779 (ct, bool, >180s)

**Question:** Does the person eventually top toast ?
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** Yes
**Sub #1 answer:** Yes

#### QID 655 (agqa, bool, <10s)

**Question:** Is the person always holding some clothes ?
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** No
**Sub #1 answer:** No

#### QID 1833 (agqa, bool, <10s)

**Question:** Is the person always sitting on the floor ?
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** Yes
**Sub #1 answer:** Yes

#### QID 1843 (agqa, bool, <10s)

**Question:** Is the person always talking on a phone ?
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** No
**Sub #1 answer:** No

#### QID 11 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put a dish somewhere, Option B: put a cup somewhere, Option C: make some food, Option D: hold some food. Reply with the chosen option in one character.
**Options:** A: put a dish somewhere, B: put a cup somewhere, C: make some food, D: hold some food
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 50 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: take paper/notebook from somewhere, Option B: hold a dish, Option C: put a dish/es somewhere, Option D: drink from a cup/glass/bottle. Reply with the chosen option in one character.
**Options:** A: take paper/notebook from somewhere, B: hold a dish, C: put a dish/es somewhere, D: drink from a cup/glass/bottle
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 74 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: tidy up a blanket/s, Option B: open a door, Option C: take some clothes from somewhere, Option D: throw a blanket somewhere. Reply with the chosen option in one character.
**Options:** A: tidy up a blanket/s, B: open a door, C: take some clothes from somewhere, D: throw a blanket somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 155 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: hold a blanket, Option B: open a door, Option C: close a door, Option D: put a blanket somewhere. Reply with the chosen option in one character.
**Options:** A: hold a blanket, B: open a door, C: close a door, D: put a blanket somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 156 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: sit in a bed, Option B: laugh at something, Option C: put something on a table, Option D: hold a cup of something. Reply with the chosen option in one character.
**Options:** A: sit in a bed, B: laugh at something, C: put something on a table, D: hold a cup of something
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** C

#### QID 178 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put a dish somewhere, Option B: hold a dish, Option C: make some food, Option D: hold some food. Reply with the chosen option in one character.
**Options:** A: put a dish somewhere, B: hold a dish, C: make some food, D: hold some food
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** B

#### QID 196 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: hold a vacuum, Option B: take a bag from somewhere, Option C: lie on a sofa/couch, Option D: open a door. Reply with the chosen option in one character.
**Options:** A: hold a vacuum, B: take a bag from somewhere, C: lie on a sofa/couch, D: open a door
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 565 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: smile at something, Option B: laugh at something, Option C: take a picture of something, Option D: take a pillow from somewhere. Reply with the chosen option in one character.
**Options:** A: smile at something, B: laugh at something, C: take a picture of something, D: take a pillow from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 588 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: take a dish from somewhere, Option B: wash a dish, Option C: put a dish somewhere, Option D: sneeze somewhere. Reply with the chosen option in one character.
**Options:** A: take a dish from somewhere, B: wash a dish, C: put a dish somewhere, D: sneeze somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 630 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: sit on sofa/couch, Option B: put a towel/s somewhere, Option C: sit at a table, Option D: put shoes somewhere. Reply with the chosen option in one character.
**Options:** A: sit on sofa/couch, B: put a towel/s somewhere, C: sit at a table, D: put shoes somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** A

#### QID 668 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: throw something on the floor, Option B: watch a laptop or something on a laptop, Option C: sit in a chair, Option D: put shoes somewhere. Reply with the chosen option in one character.
**Options:** A: throw something on the floor, B: watch a laptop or something on a laptop, C: sit in a chair, D: put shoes somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** B

#### QID 671 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: watch a book, Option B: close a book, Option C: open a book, Option D: wash a table. Reply with the chosen option in one character.
**Options:** A: watch a book, B: close a book, C: open a book, D: wash a table
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 678 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: take some clothes from somewhere, Option B: stand up, Option C: wash a dish, Option D: put clothes somewhere. Reply with the chosen option in one character.
**Options:** A: take some clothes from somewhere, B: stand up, C: wash a dish, D: put clothes somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 780 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put a picture somewhere, Option B: take paper/notebook from somewhere, Option C: open a door, Option D: lie on a sofa/couch. Reply with the chosen option in one character.
**Options:** A: put a picture somewhere, B: take paper/notebook from somewhere, C: open a door, D: lie on a sofa/couch
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 781 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: take food from somewhere, Option B: sit on the floor, Option C: put something on a table, Option D: take a blanket from somewhere. Reply with the chosen option in one character.
**Options:** A: take food from somewhere, B: sit on the floor, C: put something on a table, D: take a blanket from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 795 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put some food somewhere, Option B: watch/read/look at a book, Option C: take a dish/es from somewhere, Option D: eat a sandwich. Reply with the chosen option in one character.
**Options:** A: put some food somewhere, B: watch/read/look at a book, C: take a dish/es from somewhere, D: eat a sandwich
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 823 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: sit at a table, Option B: drink from a cup/glass/bottle, Option C: sit in a chair, Option D: hold a laptop. Reply with the chosen option in one character.
**Options:** A: sit at a table, B: drink from a cup/glass/bottle, C: sit in a chair, D: hold a laptop
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 889 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: open a bag, Option B: close a door, Option C: hold a mirror, Option D: throw a bag somewhere. Reply with the chosen option in one character.
**Options:** A: open a bag, B: close a door, C: hold a mirror, D: throw a bag somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** B

#### QID 1103 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: walk through a doorway, Option B: grasp onto a doorknob, Option C: hold a phone, Option D: dress themselves. Reply with the chosen option in one character.
**Options:** A: walk through a doorway, B: grasp onto a doorknob, C: hold a phone, D: dress themselves
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1291 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put a dish/es somewhere, Option B: hold some food, Option C: open a closet/cabinet, Option D: throw clothes somewhere. Reply with the chosen option in one character.
**Options:** A: put a dish/es somewhere, B: hold some food, C: open a closet/cabinet, D: throw clothes somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1320 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put some food somewhere, Option B: open a closet/cabinet, Option C: put a dish/es somewhere, Option D: put a picture somewhere. Reply with the chosen option in one character.
**Options:** A: put some food somewhere, B: open a closet/cabinet, C: put a dish/es somewhere, D: put a picture somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1331 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: watch/look at a picture, Option B: put a dish/es somewhere, Option C: hold a dish, Option D: take a bag from somewhere. Reply with the chosen option in one character.
**Options:** A: watch/look at a picture, B: put a dish/es somewhere, C: hold a dish, D: take a bag from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1376 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: watch/look outside of a window, Option B: tidy up with a broom, Option C: open a door, Option D: lie on a bed. Reply with the chosen option in one character.
**Options:** A: watch/look outside of a window, B: tidy up with a broom, C: open a door, D: lie on a bed
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1387 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: sit in a chair, Option B: play with a phone, Option C: take a phone from somewhere, Option D: open a closet. Reply with the chosen option in one character.
**Options:** A: sit in a chair, B: play with a phone, C: take a phone from somewhere, D: open a closet
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** B

#### QID 1406 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: take a broom from somewhere, Option B: tidy up a towel/s, Option C: open a laptop, Option D: hold a laptop. Reply with the chosen option in one character.
**Options:** A: take a broom from somewhere, B: tidy up a towel/s, C: open a laptop, D: hold a laptop
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1411 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: put some food somewhere, Option B: take a dish/es from somewhere, Option C: hold a laptop, Option D: open a closet/cabinet. Reply with the chosen option in one character.
**Options:** A: put some food somewhere, B: take a dish/es from somewhere, C: hold a laptop, D: open a closet/cabinet
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1558 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: hold a bag, Option B: make some food, Option C: put a bag somewhere, Option D: hold a cup of something. Reply with the chosen option in one character.
**Options:** A: hold a bag, B: make some food, C: put a bag somewhere, D: hold a cup of something
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1597 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: hold a cup of something, Option B: drink from a cup, Option C: hold some clothes, Option D: work at a table. Reply with the chosen option in one character.
**Options:** A: hold a cup of something, B: drink from a cup, C: hold some clothes, D: work at a table
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1639 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: close a door, Option B: close a laptop, Option C: open a bag, Option D: sit on a table. Reply with the chosen option in one character.
**Options:** A: close a door, B: close a laptop, C: open a bag, D: sit on a table
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1678 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: sit on sofa/couch, Option B: sit at a table, Option C: throw a towel/s somewhere, Option D: take a blanket from somewhere. Reply with the chosen option in one character.
**Options:** A: sit on sofa/couch, B: sit at a table, C: throw a towel/s somewhere, D: take a blanket from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** C

#### QID 1741 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: walk through a doorway, Option B: put some food somewhere, Option C: hold a dish, Option D: take food from somewhere. Reply with the chosen option in one character.
**Options:** A: walk through a doorway, B: put some food somewhere, C: hold a dish, D: take food from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1931 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What action does the person do throughout the video ? Is it Option A: hold a bag, Option B: open a bag, Option C: watch television, Option D: hold a picture. Reply with the chosen option in one character.
**Options:** A: hold a bag, B: open a bag, C: watch television, D: hold a picture
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** B

#### QID 151 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: open a refrigerator, Option B: stand up, Option C: take a picture of something, Option D: smile in a mirror. Reply with the chosen option in one character.
**Options:** A: open a refrigerator, B: stand up, C: take a picture of something, D: smile in a mirror
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 157 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add mustard seeds, Option B: flip bread, Option C: spread creme upon cake, Option D: get things out. Reply with the chosen option in one character.
**Options:** A: add mustard seeds, B: flip bread, C: spread creme upon cake, D: get things out
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** A

#### QID 171 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: open a door, Option B: go from standing to sitting, Option C: throw clothes somewhere, Option D: wash a table. Reply with the chosen option in one character.
**Options:** A: open a door, B: go from standing to sitting, C: throw clothes somewhere, D: wash a table
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 271 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: put a phone somewhere, Option B: wash a cup, Option C: take a pillow from somewhere, Option D: put something on a table. Reply with the chosen option in one character.
**Options:** A: put a phone somewhere, B: wash a cup, C: take a pillow from somewhere, D: put something on a table
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 282 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: put steak on grill, Option B: cut onion, Option C: pour water, Option D: add meat. Reply with the chosen option in one character.
**Options:** A: put steak on grill, B: cut onion, C: pour water, D: add meat
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 350 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: cut shelve, Option B: take pancake from pan, Option C: close cap, Option D: add onion. Reply with the chosen option in one character.
**Options:** A: cut shelve, B: take pancake from pan, C: close cap, D: add onion
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 363 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: get things out, Option B: put bread in pan, Option C: put mixture into bag, Option D: season steak. Reply with the chosen option in one character.
**Options:** A: get things out, B: put bread in pan, C: put mixture into bag, D: season steak
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 386 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: throw a bag somewhere, Option B: put a blanket somewhere, Option C: wash a table, Option D: open a laptop. Reply with the chosen option in one character.
**Options:** A: throw a bag somewhere, B: put a blanket somewhere, C: wash a table, D: open a laptop
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** B

#### QID 411 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add sugar, Option B: pour jello powder, Option C: add vanilla extract, Option D: pour mixture into cup. Reply with the chosen option in one character.
**Options:** A: add sugar, B: pour jello powder, C: add vanilla extract, D: pour mixture into cup
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 424 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a dish, Option B: sit on sofa/couch, Option C: open a laptop, Option D: put a dish/es somewhere. Reply with the chosen option in one character.
**Options:** A: hold a dish, B: sit on sofa/couch, C: open a laptop, D: put a dish/es somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 486 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a pillow, Option B: tidy up a towel/s, Option C: put a box somewhere, Option D: watch/look at a picture. Reply with the chosen option in one character.
**Options:** A: hold a pillow, B: tidy up a towel/s, C: put a box somewhere, D: watch/look at a picture
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 613 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: flip bread, Option B: take steak from grill, Option C: add flour, Option D: add butter. Reply with the chosen option in one character.
**Options:** A: flip bread, B: take steak from grill, C: add flour, D: add butter
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 633 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: put clothes somewhere, Option B: put a bag somewhere, Option C: walk through a doorway, Option D: lie on a sofa/couch. Reply with the chosen option in one character.
**Options:** A: put clothes somewhere, B: put a bag somewhere, C: walk through a doorway, D: lie on a sofa/couch
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 660 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: open a door, Option B: watch television, Option C: put a pillow somewhere, Option D: put a picture somewhere. Reply with the chosen option in one character.
**Options:** A: open a door, B: watch television, C: put a pillow somewhere, D: put a picture somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 662 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: grasp onto a doorknob, Option B: wash some clothes, Option C: sit in a bed, Option D: hold a sandwich. Reply with the chosen option in one character.
**Options:** A: grasp onto a doorknob, B: wash some clothes, C: sit in a bed, D: hold a sandwich
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 684 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a cup of something, Option B: put their paper somewhere, Option C: laugh at a television, Option D: watch outside of a window. Reply with the chosen option in one character.
**Options:** A: hold a cup of something, B: put their paper somewhere, C: laugh at a television, D: watch outside of a window
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 685 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a blanket, Option B: open a book, Option C: take a towel/s from somewhere, Option D: hold a laptop. Reply with the chosen option in one character.
**Options:** A: hold a blanket, B: open a book, C: take a towel/s from somewhere, D: hold a laptop
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** B

#### QID 709 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: wash their hands, Option B: put a picture somewhere, Option C: take a cup from somewhere, Option D: snuggle with a blanket. Reply with the chosen option in one character.
**Options:** A: wash their hands, B: put a picture somewhere, C: take a cup from somewhere, D: snuggle with a blanket
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 720 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: pour lemon juice, Option B: close cap, Option C: add sugar, Option D: lower jack. Reply with the chosen option in one character.
**Options:** A: pour lemon juice, B: close cap, C: add sugar, D: lower jack
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 804 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: open a bag, Option B: wash some clothes, Option C: close a closet/cabinet, Option D: close a window. Reply with the chosen option in one character.
**Options:** A: open a bag, B: wash some clothes, C: close a closet/cabinet, D: close a window
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 931 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: take a sandwich from somewhere, Option B: take a cup/glass/bottle from somewhere, Option C: hold some clothes, Option D: take paper/notebook from somewhere. Reply with the chosen option in one character.
**Options:** A: take a sandwich from somewhere, B: take a cup/glass/bottle from somewhere, C: hold some clothes, D: take paper/notebook from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 937 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: lie on a bed, Option B: watch a picture, Option C: put a book somewhere, Option D: drink from a cup. Reply with the chosen option in one character.
**Options:** A: lie on a bed, B: watch a picture, C: put a book somewhere, D: drink from a cup
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 957 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: wash something with a blanket, Option B: tidy up a closet, Option C: sit in a chair, Option D: put a cup somewhere. Reply with the chosen option in one character.
**Options:** A: wash something with a blanket, B: tidy up a closet, C: sit in a chair, D: put a cup somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 962 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add butter, Option B: take pancake from pan, Option C: flip steak, Option D: add meat. Reply with the chosen option in one character.
**Options:** A: add butter, B: take pancake from pan, C: flip steak, D: add meat
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 981 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add strawberries to cake, Option B: close cap, Option C: melt butter, Option D: add fish. Reply with the chosen option in one character.
**Options:** A: add strawberries to cake, B: close cap, C: melt butter, D: add fish
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1060 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: lie on a sofa/couch, Option B: take food from somewhere, Option C: close a refrigerator, Option D: close a book. Reply with the chosen option in one character.
**Options:** A: lie on a sofa/couch, B: take food from somewhere, C: close a refrigerator, D: close a book
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1070 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: throw a blanket somewhere, Option B: take a dish/es from somewhere, Option C: sit on a table, Option D: open a box. Reply with the chosen option in one character.
**Options:** A: throw a blanket somewhere, B: take a dish/es from somewhere, C: sit on a table, D: open a box
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1099 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: pour mixture into cup, Option B: remove bread from pan, Option C: add tortilla, Option D: add vanilla extract. Reply with the chosen option in one character.
**Options:** A: pour mixture into cup, B: remove bread from pan, C: add tortilla, D: add vanilla extract
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1100 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add meat, Option B: season steak, Option C: pour juice, Option D: put vegetables in water. Reply with the chosen option in one character.
**Options:** A: add meat, B: season steak, C: pour juice, D: put vegetables in water
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1107 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: put groceries somewhere, Option B: throw a pillow somewhere, Option C: hold a pillow, Option D: take a blanket from somewhere. Reply with the chosen option in one character.
**Options:** A: put groceries somewhere, B: throw a pillow somewhere, C: hold a pillow, D: take a blanket from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1119 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: throw a blanket somewhere, Option B: snuggle with a blanket, Option C: open a door, Option D: open a closet. Reply with the chosen option in one character.
**Options:** A: throw a blanket somewhere, B: snuggle with a blanket, C: open a door, D: open a closet
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1185 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: reach for and grab a picture, Option B: put a towel/s somewhere, Option C: put clothes somewhere, Option D: hold a dish. Reply with the chosen option in one character.
**Options:** A: reach for and grab a picture, B: put a towel/s somewhere, C: put clothes somewhere, D: hold a dish
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1198 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: tidy up a table, Option B: put a cup/glass/bottle somewhere, Option C: hold some medicine, Option D: throw a pillow somewhere. Reply with the chosen option in one character.
**Options:** A: tidy up a table, B: put a cup/glass/bottle somewhere, C: hold some medicine, D: throw a pillow somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1214 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a picture, Option B: watch/look at a picture, Option C: walk through a doorway, Option D: hold a box. Reply with the chosen option in one character.
**Options:** A: hold a picture, B: watch/look at a picture, C: walk through a doorway, D: hold a box
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1272 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: throw a blanket somewhere, Option B: hold a book, Option C: put shoes somewhere, Option D: open a bag. Reply with the chosen option in one character.
**Options:** A: throw a blanket somewhere, B: hold a book, C: put shoes somewhere, D: open a bag
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1301 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: whisk mixture, Option B: flip bread, Option C: tight wheel, Option D: add spices. Reply with the chosen option in one character.
**Options:** A: whisk mixture, B: flip bread, C: tight wheel, D: add spices
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1340 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: open a laptop, Option B: sit on the floor, Option C: sneeze somewhere, Option D: hold some clothes. Reply with the chosen option in one character.
**Options:** A: open a laptop, B: sit on the floor, C: sneeze somewhere, D: hold some clothes
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** A

#### QID 1370 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: pour juice, Option B: put bananas into blender, Option C: cut steak, Option D: melt butter. Reply with the chosen option in one character.
**Options:** A: pour juice, B: put bananas into blender, C: cut steak, D: melt butter
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** D

#### QID 1446 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: put a towel/s somewhere, Option B: take a broom from somewhere, Option C: open a door, Option D: stand on a chair. Reply with the chosen option in one character.
**Options:** A: put a towel/s somewhere, B: take a broom from somewhere, C: open a door, D: stand on a chair
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** C

#### QID 1460 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: grasp onto a doorknob, Option B: put a blanket somewhere, Option C: take paper from somewhere, Option D: open a laptop. Reply with the chosen option in one character.
**Options:** A: grasp onto a doorknob, B: put a blanket somewhere, C: take paper from somewhere, D: open a laptop
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1475 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add cheese, Option B: put steak on grill, Option C: flip pancake, Option D: pour juice. Reply with the chosen option in one character.
**Options:** A: add cheese, B: put steak on grill, C: flip pancake, D: pour juice
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1502 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: pour water, Option B: brake on, Option C: jack down, Option D: put meringue into oven. Reply with the chosen option in one character.
**Options:** A: pour water, B: brake on, C: jack down, D: put meringue into oven
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1514 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: take food from somewhere, Option B: lie on a bed, Option C: reach for and grab a picture, Option D: tidy some clothes. Reply with the chosen option in one character.
**Options:** A: take food from somewhere, B: lie on a bed, C: reach for and grab a picture, D: tidy some clothes
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1526 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: tidy up a closet/cabinet, Option B: put some food somewhere, Option C: watch/look outside of a window, Option D: open a bag. Reply with the chosen option in one character.
**Options:** A: tidy up a closet/cabinet, B: put some food somewhere, C: watch/look outside of a window, D: open a bag
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1554 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: turn on a light, Option B: put a bag somewhere, Option C: close a box, Option D: sit at a table. Reply with the chosen option in one character.
**Options:** A: turn on a light, B: put a bag somewhere, C: close a box, D: sit at a table
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** D

#### QID 1629 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a book, Option B: hold a cup of something, Option C: pour something into a cup, Option D: walk through a doorway. Reply with the chosen option in one character.
**Options:** A: hold a book, B: hold a cup of something, C: pour something into a cup, D: walk through a doorway
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1635 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: flip bread, Option B: flip steak, Option C: remove cap, Option D: add spices. Reply with the chosen option in one character.
**Options:** A: flip bread, B: flip steak, C: remove cap, D: add spices
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** D
**Sub #1 answer:** C

#### QID 1854 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: throw food somewhere, Option B: close a book, Option C: close a closet/cabinet, Option D: take paper/notebook from somewhere. Reply with the chosen option in one character.
**Options:** A: throw food somewhere, B: close a book, C: close a closet/cabinet, D: take paper/notebook from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1867 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a book, Option B: throw a blanket somewhere, Option C: tidy up a towel/s, Option D: take a dish/es from somewhere. Reply with the chosen option in one character.
**Options:** A: hold a book, B: throw a blanket somewhere, C: tidy up a towel/s, D: take a dish/es from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1868 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: cut steak, Option B: add lettuce, Option C: add fish, Option D: add whipped cream. Reply with the chosen option in one character.
**Options:** A: cut steak, B: add lettuce, C: add fish, D: add whipped cream
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1875 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: take a dish from somewhere, Option B: close a closet, Option C: throw a book somewhere, Option D: fix a vacuum. Reply with the chosen option in one character.
**Options:** A: take a dish from somewhere, B: close a closet, C: throw a book somewhere, D: fix a vacuum
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1935 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: sit in a chair, Option B: run somewhere, Option C: hold some food, Option D: take a pillow from somewhere. Reply with the chosen option in one character.
**Options:** A: sit in a chair, B: run somewhere, C: hold some food, D: take a pillow from somewhere
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1947 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: sit in a chair, Option B: wash a dish, Option C: tidy up a table, Option D: throw something on the floor. Reply with the chosen option in one character.
**Options:** A: sit in a chair, B: wash a dish, C: tidy up a table, D: throw something on the floor
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1949 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: add kimchi, Option B: taste steak, Option C: pour mixture into pan, Option D: add lettuce. Reply with the chosen option in one character.
**Options:** A: add kimchi, B: taste steak, C: pour mixture into pan, D: add lettuce
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1957 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: peel banana, Option B: put meringue into oven, Option C: add onion, Option D: melt butter. Reply with the chosen option in one character.
**Options:** A: peel banana, B: put meringue into oven, C: add onion, D: melt butter
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1963 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: turn off a light, Option B: take some clothes from somewhere, Option C: take food from somewhere, Option D: dress themselves. Reply with the chosen option in one character.
**Options:** A: turn off a light, B: take some clothes from somewhere, C: take food from somewhere, D: dress themselves
**PULS output:** EMPTY (no spec, no propositions)
**Sub #5B answer:** C
**Sub #1 answer:** C


## Bucket B — operator-collapse open-ended (54 rows)

### Light tally (Cursor-computed, for Adi's morning skim)

- Mode breakdown: **54 MC**, **0 bool**
- Question-stem frequencies (top 10):
  - `The following is a multiple choice …`: **54**
- Source dataset breakdown:
  - **agqa**: 30
  - **ct**: 23
  - **star**: 1
- Average question length: **58.4** words

**Pattern notes (auto, no fix proposals):**
- Unique stem buckets: **1**; top stem covers **100.0%** of bucket.
- Failures are **MC-heavy** — likely MC template / candidate-parameterization gap.
- Largest source slice: **agqa** (30/54). Concentrated in short-clip sources.

- Operator-cue frequencies in questions:
  - `always`: **15**
  - `overlap`: **39**
  - `co-occur`: **15**
- Dominant cue: **overlap** (39/54 rows). Single-cue concentration → targeted template fix.

### Rows (sorted by question-stem alphabetically)

#### QID 886 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with going from standing to sitting ? Is it Option A: tidy up a closet, Option B: hold a broom, Option C: go from standing to sitting, Option D: sit in a chair. Reply with the chosen option in one character.
**Options:** A: tidy up a closet, B: hold a broom, C: go from standing to sitting, D: sit in a chair
**PULS output:**
  - propositions: ['going_from_standing_to_sitting']
  - spec: `("going_from_standing_to_sitting")`
**Target-ID padding:** The question asks about co-occurring actions, implying that the action of going from standing to sitting should be examined with modest padding on both sides to capture simultaneous or closely related actions. Therefore, a modest padding of about 2 seconds on each side is suitable.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 932 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding a bag ? Is it Option A: hold some food, Option B: put some food somewhere, Option C: hold a phone, Option D: smile at something. Reply with the chosen option in one character.
**Options:** A: hold some food, B: put some food somewhere, C: hold a phone, D: smile at something
**PULS output:**
  - propositions: ['holding_a_bag']
  - spec: `("holding_a_bag")`
**Target-ID padding:** The question implies a 'during' relationship where actions co-occur with holding a bag. Therefore, modest padding of about 2-3 seconds on both sides is appropriate to capture the co-occurrence context within the video.
**Sub #5B answer:** A
**Sub #1 answer:** C

#### QID 1784 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding a broom ? Is it Option A: tidy up a closet, Option B: go from standing to sitting, Option C: put a broom somewhere, Option D: sit in a chair. Reply with the chosen option in one character.
**Options:** A: tidy up a closet, B: go from standing to sitting, C: put a broom somewhere, D: sit in a chair
**PULS output:**
  - propositions: ['person_holds_a_broom']
  - spec: `("person_holds_a_broom")`
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1774 (star, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding a dish ? Is it Option A: open a closet/cabinet, Option B: hold a dish, Option C: hold a phone/camera, Option D: open a book. Reply with the chosen option in one character.
**Options:** A: open a closet/cabinet, B: hold a dish, C: hold a phone/camera, D: open a book
**PULS output:**
  - propositions: ['person_holds_a_dish']
  - spec: `("person_holds_a_dish")`
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1518 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding a phone ? Is it Option A: sit at a table, Option B: hold a phone, Option C: open a laptop, Option D: smile at something. Reply with the chosen option in one character.
**Options:** A: sit at a table, B: hold a phone, C: open a laptop, D: smile at something
**PULS output:**
  - propositions: ['person_holds_a_phone']
  - spec: `("person_holds_a_phone")`
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 803 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with holding some food ? Is it Option A: sit in a chair, Option B: watch something in a mirror, Option C: hold some food, Option D: sneeze somewhere. Reply with the chosen option in one character.
**Options:** A: sit in a chair, B: watch something in a mirror, C: hold some food, D: sneeze somewhere
**PULS output:**
  - propositions: ['person_holds_some_food']
  - spec: `("person_holds_some_food")`
**Target-ID padding:** The question is about co-occurrence, indicating a 'during' relationship. Thus, a modest padding on both sides is appropriate to capture potential overlapping actions.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1922 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with opening a book ? Is it Option A: sit in a bed, Option B: put something on a table, Option C: tidy up a table, Option D: open a book. Reply with the chosen option in one character.
**Options:** A: sit in a bed, B: put something on a table, C: tidy up a table, D: open a book
**PULS output:**
  - propositions: ['opening_a_book']
  - spec: `("opening_a_book")`
**Target-ID padding:** The question asks about actions that co-occur with opening a book, requiring modest padding on both sides to capture simultaneous events that may not precisely align with the identified interval.
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 134 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with sitting at a table ? Is it Option A: sneeze somewhere, Option B: sit in a chair, Option C: sit at a table, Option D: watch something in a mirror. Reply with the chosen option in one character.
**Options:** A: sneeze somewhere, B: sit in a chair, C: sit at a table, D: watch something in a mirror
**PULS output:**
  - propositions: ['sitting_at_a_table']
  - spec: `("sitting_at_a_table")`
**Target-ID padding:** The question involves co-occurrence, which implies that the event happens during the specified interval. Therefore, modest padding on both sides (about 2 seconds each) ensures the capture of any co-occurring actions adjacent to the interval.
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 892 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with sitting at a table ? Is it Option A: smile at something, Option B: work at a table, Option C: sit at a table, Option D: open a laptop. Reply with the chosen option in one character.
**Options:** A: smile at something, B: work at a table, C: sit at a table, D: open a laptop
**PULS output:**
  - propositions: ['sitting_at_a_table']
  - spec: `"sitting_at_a_table"`
**Target-ID padding:** For co-occurrence questions, there needs to be a modest padding on both sides because co-occurrence implies a simultaneous or closely overlapping timeframe. Thus, extending the interval a bit on both sides helps ensure capturing all potentially relevant actions occurring with 'sitting at a table'.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1113 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with sitting in a bed ? Is it Option A: snuggle with a pillow, Option B: take a blanket from somewhere, Option C: sit in a bed, Option D: sneeze somewhere. Reply with the chosen option in one character.
**Options:** A: snuggle with a pillow, B: take a blanket from somewhere, C: sit in a bed, D: sneeze somewhere
**PULS output:**
  - propositions: ['sitting_in_a_bed']
  - spec: `("sitting_in_a_bed")`
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1295 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with sitting in a bed ? Is it Option A: put a blanket somewhere, Option B: sit in a bed, Option C: put something on a table, Option D: watch a book. Reply with the chosen option in one character.
**Options:** A: put a blanket somewhere, B: sit in a bed, C: put something on a table, D: watch a book
**PULS output:**
  - propositions: ['sitting_in_a_bed']
  - spec: `("sitting_in_a_bed")`
**Target-ID padding:** Since the question asks about actions that co-occur with sitting in a bed, a modest padding on both sides is appropriate to capture the interval where co-occurrence can be observed.
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1140 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with sitting in a chair ? Is it Option A: make some food, Option B: sit at a table, Option C: sit in a chair, Option D: smile at something. Reply with the chosen option in one character.
**Options:** A: make some food, B: sit at a table, C: sit in a chair, D: smile at something
**PULS output:**
  - propositions: ['sitting_in_a_chair']
  - spec: `("sitting_in_a_chair")`
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1365 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with smiling at a book ? Is it Option A: take paper from somewhere, Option B: watch a book, Option C: hold a paper, Option D: sit in a bed. Reply with the chosen option in one character.
**Options:** A: take paper from somewhere, B: watch a book, C: hold a paper, D: sit in a bed
**PULS output:**
  - propositions: ['smiling_at_a_book']
  - spec: `("smiling_at_a_book")`
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 859 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with taking a bag from somewhere ? Is it Option A: watch a picture, Option B: take a bag from somewhere, Option C: hold a picture, Option D: take food from somewhere. Reply with the chosen option in one character.
**Options:** A: watch a picture, B: take a bag from somewhere, C: hold a picture, D: take food from somewhere
**PULS output:**
  - propositions: ['person_takes_a_bag_from_somewhere']
  - spec: `("person_takes_a_bag_from_somewhere")`
**Target-ID padding:** The question asks about actions that co-occur with taking a bag, implying there is no temporal shift needed for 'before' or 'after' padding. This suggests no additional context is needed outside the identified interval.
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 1978 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always co-occurs with tidying up a table ? Is it Option A: tidy up a table, Option B: wash some clothes, Option C: stand on a chair, Option D: tidy up a closet. Reply with the chosen option in one character.
**Options:** A: tidy up a table, B: wash some clothes, C: stand on a chair, D: tidy up a closet
**PULS output:**
  - propositions: ['tidying_up_a_table']
  - spec: `("tidying_up_a_table")`
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1582 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with adding coffee ? Is it Option A: pour milk, Option B: add coffee, Option C: brake on, Option D: add kimchi. Reply with the chosen option in one character.
**Options:** A: pour milk, B: add coffee, C: brake on, D: add kimchi
**PULS output:**
  - propositions: ['person_adds_coffee']
  - spec: `("person_adds_coffee")`
**Target-ID padding:** The question asks about actions that do not overlap with the action of adding coffee, which implies analyzing actions that are occurring during or in proximity to that time frame. A modest padding on both sides ensures coverage of adjacent actions or events, helping to capture potential non-overlapping actions effectively.
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1766 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with adding fish ? Is it Option A: add fish, Option B: close cap, Option C: stir mixture, Option D: brake on. Reply with the chosen option in one character.
**Options:** A: add fish, B: close cap, C: stir mixture, D: brake on
**PULS output:**
  - propositions: ['person_adds_fish']
  - spec: `! "person_adds_fish"`
**Sub #5B answer:** B
**Sub #1 answer:** D

#### QID 1907 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with adding flour ? Is it Option A: add flour, Option B: add butter, Option C: flip pancake, Option D: spread creme upon cake. Reply with the chosen option in one character.
**Options:** A: add flour, B: add butter, C: flip pancake, D: spread creme upon cake
**PULS output:**
  - propositions: ['person_adds_flour']
  - spec: `("person_adds_flour")`
**Target-ID padding:** The question concerns actions not overlapping with adding flour, suggesting a focus on 'during' any such non-overlapping actions. Therefore, modest padding is applied on both sides to capture complete actions around the interval.
**Sub #5B answer:** C
**Sub #1 answer:** D

#### QID 1352 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with adding rice ? Is it Option A: add rice, Option B: take steak from grill, Option C: add kimchi, Option D: add tomato. Reply with the chosen option in one character.
**Options:** A: add rice, B: take steak from grill, C: add kimchi, D: add tomato
**PULS output:**
  - propositions: ['person_adds_rice']
  - spec: `! "person_adds_rice"`
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 138 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with cutting lemon ? Is it Option A: pour lemon juice, Option B: cut lemon, Option C: wipe off dipstick, Option D: cut banana. Reply with the chosen option in one character.
**Options:** A: pour lemon juice, B: cut lemon, C: wipe off dipstick, D: cut banana
**PULS output:**
  - propositions: ['person_cuts_lemon']
  - spec: `("person_cuts_lemon")`
**Target-ID padding:** The question asks about actions that do not overlap, implying a temporal comparison around the specified event 'cutting lemon'. Therefore, modest padding is added before and after the identified window to allow examination of actions just before and after the event.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 557 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with dipping bread in mixture ? Is it Option A: melt butter, Option B: dip bread in mixture, Option C: sand shelve, Option D: take steak from grill. Reply with the chosen option in one character.
**Options:** A: melt butter, B: dip bread in mixture, C: sand shelve, D: take steak from grill
**PULS output:**
  - propositions: ['person_dips_bread_in_mixture']
  - spec: `("person_dips_bread_in_mixture")`
**Target-ID padding:** Since the question is about actions that do not overlap with 'dipping bread in mixture', it implies a 'during' relationship. Thus, a modest padding on both sides is appropriate to ensure the interval where the action occurs is fully captured without overlap.
**Sub #5B answer:** A
**Sub #1 answer:** C

#### QID 161 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with flipping pancake ? Is it Option A: pour milk, Option B: flip pancake, Option C: pour jello powder, Option D: cut banana. Reply with the chosen option in one character.
**Options:** A: pour milk, B: flip pancake, C: pour jello powder, D: cut banana
**PULS output:**
  - propositions: ['person_flips_pancake']
  - spec: `("person_flips_pancake")`
**Target-ID padding:** The question implies examining actions during the interval where flipping pancake occurs to ensure there is no overlap. Therefore, modest padding on both sides is used to ensure no actions overlap at the start or the end of the flipping activity.
**Sub #5B answer:** A
**Sub #1 answer:** D

#### QID 1746 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with flipping steak ? Is it Option A: flip steak, Option B: add spices, Option C: cut banana, Option D: take steak from grill. Reply with the chosen option in one character.
**Options:** A: flip steak, B: add spices, C: cut banana, D: take steak from grill
**PULS output:**
  - propositions: ['person_flips_steak']
  - spec: `("person_flips_steak")`
**Target-ID padding:** The question asks about actions that do not overlap with flipping steak, suggesting a focus on 'during' events. Modest padding on both sides ensures capturing full context without overlapping with the flipping action itself.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1806 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with flipping steak ? Is it Option A: flip steak, Option B: add onion, Option C: add sugar, Option D: cut steak. Reply with the chosen option in one character.
**Options:** A: flip steak, B: add onion, C: add sugar, D: cut steak
**PULS output:**
  - propositions: ['person_flips_steak']
  - spec: `! "person_flips_steak"`
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 309 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with going from standing to sitting ? Is it Option A: walk through a doorway, Option B: put a pillow somewhere, Option C: take a pillow from somewhere, Option D: stand up. Reply with the chosen option in one character.
**Options:** A: walk through a doorway, B: put a pillow somewhere, C: take a pillow from somewhere, D: stand up
**PULS output:**
  - propositions: ['person_goes_from_standing_to_sitting']
  - spec: `("person_goes_from_standing_to_sitting")`
**Target-ID padding:** The question implies checking for actions during the transition of 'going from standing to sitting'. Therefore, modest padding of approximately 2-3 seconds on both sides is appropriate to capture overlapping actions.
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1918 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with holding a pillow ? Is it Option A: awaken in bed, Option B: stand up, Option C: go from standing to sitting, Option D: walk through a doorway. Reply with the chosen option in one character.
**Options:** A: awaken in bed, B: stand up, C: go from standing to sitting, D: walk through a doorway
**PULS output:**
  - propositions: ['person_holds_pillow']
  - spec: `! "person_holds_pillow"`
**Sub #5B answer:** D
**Sub #1 answer:** A

#### QID 1283 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with holding a shoe ? Is it Option A: sit in a bed, Option B: laugh at something, Option C: put shoes somewhere, Option D: laugh at a television. Reply with the chosen option in one character.
**Options:** A: sit in a bed, B: laugh at something, C: put shoes somewhere, D: laugh at a television
**PULS output:**
  - propositions: ['person_holds_a_shoe']
  - spec: `("person_holds_a_shoe")`
**Sub #5B answer:** D
**Sub #1 answer:** B

#### QID 260 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with holding some clothes ? Is it Option A: put clothes somewhere, Option B: hold some clothes, Option C: put a phone somewhere, Option D: take some clothes from somewhere. Reply with the chosen option in one character.
**Options:** A: put clothes somewhere, B: hold some clothes, C: put a phone somewhere, D: take some clothes from somewhere
**PULS output:**
  - propositions: ['person_holds_some_clothes']
  - spec: `("person_holds_some_clothes")`
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1482 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with inserting dipstick ? Is it Option A: insert dipstick, Option B: remove cap, Option C: pour sesame oil, Option D: start loose. Reply with the chosen option in one character.
**Options:** A: insert dipstick, B: remove cap, C: pour sesame oil, D: start loose
**PULS output:**
  - propositions: ['person_inserts_dipstick']
  - spec: `("person_inserts_dipstick")`
**Target-ID padding:** The question asks about actions that do not overlap with inserting the dipstick, suggesting consideration around the interval rather than solely before or after. Therefore, modest padding of around 2 seconds on both sides is appropriate to capture the surrounding context without extending too far.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1634 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with lowering jack ? Is it Option A: lower jack, Option B: remove cap, Option C: raise jack, Option D: pour espresso. Reply with the chosen option in one character.
**Options:** A: lower jack, B: remove cap, C: raise jack, D: pour espresso
**PULS output:**
  - propositions: ['person_lowers_jack']
  - spec: `("person_lowers_jack")`
**Target-ID padding:** The question focuses on an action that does not overlap with the action of lowering the jack, suggesting interest in time just around the interval where the jack is lowered. Therefore, modest padding on both sides is applied.
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 485 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with lying on the floor ? Is it Option A: awaken in bed, Option B: hold a pillow, Option C: turn off a light, Option D: snuggle with a pillow. Reply with the chosen option in one character.
**Options:** A: awaken in bed, B: hold a pillow, C: turn off a light, D: snuggle with a pillow
**PULS output:**
  - propositions: ['person_lies_on_the_floor']
  - spec: `("person_lies_on_the_floor")`
**Target-ID padding:** The question asks about actions that do not overlap with 'lying on the floor', suggesting a need to observe both before and after the identified interval to capture potential non-overlapping actions. Therefore, a modest padding of 2 seconds on both sides allows for observing any actions immediately before and after the person lies on the floor.
**Sub #5B answer:** C
**Sub #1 answer:** A

#### QID 1727 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with playing with a phone ? Is it Option A: take some clothes from somewhere, Option B: hold a phone, Option C: put clothes somewhere, Option D: take a picture of something. Reply with the chosen option in one character.
**Options:** A: take some clothes from somewhere, B: hold a phone, C: put clothes somewhere, D: take a picture of something
**PULS output:**
  - propositions: ['person_plays_with_a_phone']
  - spec: `! ("person_plays_with_a_phone")`
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1375 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring egg ? Is it Option A: flip pancake, Option B: pour egg, Option C: dip bread in mixture, Option D: add ice. Reply with the chosen option in one character.
**Options:** A: flip pancake, B: pour egg, C: dip bread in mixture, D: add ice
**PULS output:**
  - propositions: ['person_pours_egg']
  - spec: `! "person_pours_egg"`
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1407 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring espresso ? Is it Option A: pour espresso, Option B: pour mixture into pan, Option C: add sugar, Option D: dip bread in mixture. Reply with the chosen option in one character.
**Options:** A: pour espresso, B: pour mixture into pan, C: add sugar, D: dip bread in mixture
**PULS output:**
  - propositions: ['person_pours_espresso']
  - spec: `("person_pours_espresso")`
**Target-ID padding:** The question is about actions that do not overlap, indicating a 'during' relationship with modest padding needed on both sides of the interval. This allows for capturing the actions close to the interval defined by 'pouring espresso' without overlap.
**Sub #5B answer:** D
**Sub #1 answer:** B

#### QID 55 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring jello powder ? Is it Option A: pour water, Option B: pour jello powder, Option C: remove bread from pan, Option D: lower jack. Reply with the chosen option in one character.
**Options:** A: pour water, B: pour jello powder, C: remove bread from pan, D: lower jack
**PULS output:**
  - propositions: ['person_pours_jello_powder']
  - spec: `! "person_pours_jello_powder"`
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1008 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring lemon juice ? Is it Option A: pour lemon juice, Option B: close lid, Option C: cut lemon, Option D: add kimchi. Reply with the chosen option in one character.
**Options:** A: pour lemon juice, B: close lid, C: cut lemon, D: add kimchi
**PULS output:**
  - propositions: ['person_pours_lemon_juice']
  - spec: `! "person_pours_lemon_juice"`
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1389 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring vinegar ? Is it Option A: pour vinegar, Option B: add onion, Option C: pour oil, Option D: add sugar. Reply with the chosen option in one character.
**Options:** A: pour vinegar, B: add onion, C: pour oil, D: add sugar
**PULS output:**
  - propositions: ['person_pours_vinegar']
  - spec: `("person_pours_vinegar")`
**Target-ID padding:** The question asks for actions that do not overlap with pouring vinegar, indicating a 'during' type relationship. Therefore, modest padding is applied on both sides of the interval to capture actions happening just before and after the core interval where vinegar is poured.
**Sub #5B answer:** C
**Sub #1 answer:** C

#### QID 1150 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with pouring water ? Is it Option A: pour water, Option B: add rice, Option C: add lettuce, Option D: cut lemon. Reply with the chosen option in one character.
**Options:** A: pour water, B: add rice, C: add lettuce, D: cut lemon
**PULS output:**
  - propositions: ['person_pours_water']
  - spec: `! "person_pours_water"`
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1687 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting a phone somewhere ? Is it Option A: put clothes somewhere, Option B: put a phone somewhere, Option C: take some clothes from somewhere, Option D: hold a phone. Reply with the chosen option in one character.
**Options:** A: put clothes somewhere, B: put a phone somewhere, C: take some clothes from somewhere, D: hold a phone
**PULS output:**
  - propositions: ['person_puts_a_phone_somewhere']
  - spec: `! "person_puts_a_phone_somewhere"`
**Sub #5B answer:** A
**Sub #1 answer:** C

#### QID 1628 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting a pillow somewhere ? Is it Option A: hold a pillow, Option B: stand up, Option C: walk through a doorway, Option D: awaken in bed. Reply with the chosen option in one character.
**Options:** A: hold a pillow, B: stand up, C: walk through a doorway, D: awaken in bed
**PULS output:**
  - propositions: ['person_puts_a_pillow_somewhere']
  - spec: `("person_puts_a_pillow_somewhere")`
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1652 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting bananas into blender ? Is it Option A: put bananas into blender, Option B: mix ingredients, Option C: seal jar, Option D: close lid. Reply with the chosen option in one character.
**Options:** A: put bananas into blender, B: mix ingredients, C: seal jar, D: close lid
**PULS output:**
  - propositions: ['person_puts_bananas_into_blender']
  - spec: `! "person_puts_bananas_into_blender"`
**Sub #5B answer:** D
**Sub #1 answer:** B

#### QID 359 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting clothes somewhere ? Is it Option A: put a phone somewhere, Option B: take a picture of something, Option C: put clothes somewhere, Option D: wash a mirror. Reply with the chosen option in one character.
**Options:** A: put a phone somewhere, B: take a picture of something, C: put clothes somewhere, D: wash a mirror
**PULS output:**
  - propositions: ['person_puts_clothes_somewhere']
  - spec: `("person_puts_clothes_somewhere")`
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 691 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting shoes somewhere ? Is it Option A: sit in a bed, Option B: laugh at a television, Option C: hold a shoe, Option D: put something on a table. Reply with the chosen option in one character.
**Options:** A: sit in a bed, B: laugh at a television, C: hold a shoe, D: put something on a table
**PULS output:**
  - propositions: ['person_puts_shoes_somewhere']
  - spec: `("person_puts_shoes_somewhere")`
**Target-ID padding:** The question is asking about an action that does not overlap with the specified action. Therefore, it is a 'during' type question and requires modest padding on both sides to capture any non-overlapping actions occurring close to the given interval.
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 895 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting something on a table ? Is it Option A: watch television, Option B: put shoes somewhere, Option C: hold a shoe, Option D: laugh at something. Reply with the chosen option in one character.
**Options:** A: watch television, B: put shoes somewhere, C: hold a shoe, D: laugh at something
**PULS output:**
  - propositions: ['person_puts_something_on_a_table']
  - spec: `! "person_puts_something_on_a_table"`
**Sub #5B answer:** B
**Sub #1 answer:** D

#### QID 428 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with sealing jar ? Is it Option A: seal jar, Option B: add spices, Option C: put wheel, Option D: pour water. Reply with the chosen option in one character.
**Options:** A: seal jar, B: add spices, C: put wheel, D: pour water
**PULS output:**
  - propositions: ['person_seals_jar']
  - spec: `("person_seals_jar")`
**Target-ID padding:** The question involves actions that do not overlap with the sealing of the jar, implying a 'during' context might be relevant. Therefore, modest padding is applied on both sides to capture any adjacent actions that could be contrasted with the sealing jar event.
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1286 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with sealing jar ? Is it Option A: seal jar, Option B: cut cucumber, Option C: close lid, Option D: add ice. Reply with the chosen option in one character.
**Options:** A: seal jar, B: cut cucumber, C: close lid, D: add ice
**PULS output:**
  - propositions: ['person_seals_jar']
  - spec: `"person_seals_jar"`
**Target-ID padding:** The question asks about actions occurring 'during' the sealing of the jar, so a modest padding is applied on both sides to capture the relevant context around the interval.
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 791 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with standing up ? Is it Option A: put a pillow somewhere, Option B: awaken in bed, Option C: stand up, Option D: hold a pillow. Reply with the chosen option in one character.
**Options:** A: put a pillow somewhere, B: awaken in bed, C: stand up, D: hold a pillow
**PULS output:**
  - propositions: ['person_stands_up']
  - spec: `("person_stands_up")`
**Target-ID padding:** The question asks about actions that do not overlap with 'standing up', implying we need to consider actions occurring during the potential gap or transition into 'standing up'. Therefore, modest padding on both sides allows examination of actions that might not overlap with the interval of standing up.
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 785 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with stirring mixture ? Is it Option A: stir mixture, Option B: raise jack, Option C: pour mixture into cup, Option D: jack down. Reply with the chosen option in one character.
**Options:** A: stir mixture, B: raise jack, C: pour mixture into cup, D: jack down
**PULS output:**
  - propositions: ['person_stirs_mixture']
  - spec: `("person_stirs_mixture")`
**Target-ID padding:** The question asks about actions that do not overlap with 'stirring mixture', implying an interest in activities occurring during or shortly after the identified event. Therefore, a modest padding is applied to both sides to ensure that the adjacent actions are adequately captured.
**Sub #5B answer:** C
**Sub #1 answer:** B

#### QID 268 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with taking a picture of something ? Is it Option A: hold a phone, Option B: take a picture of something, Option C: play with a phone, Option D: put clothes somewhere. Reply with the chosen option in one character.
**Options:** A: hold a phone, B: take a picture of something, C: play with a phone, D: put clothes somewhere
**PULS output:**
  - propositions: ['person_takes_a_picture_of_something']
  - spec: `("person_takes_a_picture_of_something")`
**Target-ID padding:** The question asks about actions that do not overlap with 'taking a picture of something', suggesting a 'during' relationship. Thus, modest padding on both sides, about 2-3 seconds each, ensures capturing the surrounding context sufficiently.
**Sub #5B answer:** D
**Sub #1 answer:** D

#### QID 1602 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with taking some clothes from somewhere ? Is it Option A: put a phone somewhere, Option B: play with a phone, Option C: hold some clothes, Option D: put clothes somewhere. Reply with the chosen option in one character.
**Options:** A: put a phone somewhere, B: play with a phone, C: hold some clothes, D: put clothes somewhere
**PULS output:**
  - propositions: ['person_takes_some_clothes_from_somewhere']
  - spec: `("person_takes_some_clothes_from_somewhere")`
**Sub #5B answer:** A
**Sub #1 answer:** B

#### QID 1402 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with turning off a light ? Is it Option A: take a pillow from somewhere, Option B: go from standing to sitting, Option C: turn off a light, Option D: snuggle with a pillow. Reply with the chosen option in one character.
**Options:** A: take a pillow from somewhere, B: go from standing to sitting, C: turn off a light, D: snuggle with a pillow
**PULS output:**
  - propositions: ['person_turns_off_a_light']
  - spec: `! "person_turns_off_a_light"`
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 675 (agqa, mc, <10s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with walking through a doorway ? Is it Option A: take a pillow from somewhere, Option B: turn off a light, Option C: snuggle with a pillow, Option D: walk through a doorway. Reply with the chosen option in one character.
**Options:** A: take a pillow from somewhere, B: turn off a light, C: snuggle with a pillow, D: walk through a doorway
**PULS output:**
  - propositions: ['person_walks_through_a_doorway']
  - spec: `! "person_walks_through_a_doorway"`
**Sub #5B answer:** B
**Sub #1 answer:** B

#### QID 506 (ct, mc, >180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with whisking mixture ? Is it Option A: pour egg, Option B: whisk mixture, Option C: pour oil, Option D: add whipped cream. Reply with the chosen option in one character.
**Options:** A: pour egg, B: whisk mixture, C: pour oil, D: add whipped cream
**PULS output:**
  - propositions: ['person_whisks_mixture']
  - spec: `! "person_whisks_mixture"`
**Sub #5B answer:** A
**Sub #1 answer:** A

#### QID 1642 (ct, mc, 60-180s)

**Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with whisking mixture ? Is it Option A: whisk mixture, Option B: open lid, Option C: remove bread from pan, Option D: pour egg. Reply with the chosen option in one character.
**Options:** A: whisk mixture, B: open lid, C: remove bread from pan, D: pour egg
**PULS output:**
  - propositions: ['person_whisks_mixture']
  - spec: `! ("person_whisks_mixture")`
**Sub #5B answer:** C
**Sub #1 answer:** C

