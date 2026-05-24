# PULS spec analysis — unknown operator family (NSVS-bypassed)

Generated: 2026-05-24T22:42:02.443917+00:00

## Sources

- Entries: `/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json`
- Filter: `operator_guess == unknown` AND NSVS bypassed (FOI `[-1]`, Storm `[-1]`, or any empty detection split)
- Unknown-family rows in entries: **443**
- NSVS-bypassed unknown slice: **416** (93.9% of unknown family)

## Category counts

| Category | n | % | Action lever |
| --- | ---: | ---: | --- |
| spec_un_groundable | 173 | 41.6% | PULS prompt fix |
| spec_ok_no_detect | 110 | 26.4% | NSVS detector quality |
| spec_partial | 133 | 32.0% | Temporal aggregation / Storm merge |
| unclassifiable | 0 | 0.0% | Human inspection |

### Reason codes (within category)

| Reason | n |
| --- | ---: |
| `zero_detections` | 110 |
| `split_mixed_detections` | 94 |
| `empty_puls_output` | 94 |
| `operator_collapse_open_ended` | 54 |
| `mixed_prop_detections` | 39 |
| `relation_not_in_spec` | 13 |
| `no_groundable_propositions` | 11 |
| `abstract_propositions` | 1 |

## Decision recommendation

**PULS prompt tuning is a high-leverage submission lever.** `spec_un_groundable` is **41.6%** of the slice (>40% threshold). Many unknown-family questions get empty PULS output or operator-collapsed single-proposition specs that cannot encode the question's temporal semantics.

### Classification rules (auto)

- **spec_un_groundable:** empty PULS output; no frame-scorable propositions; open-ended temporal question collapsed to a single non-`UNTIL` proposition; co-occur/overlap questions without multi-prop `AND`/`UNTIL` structure.
- **spec_ok_no_detect:** groundable spec but zero detection windows on every proposition split.
- **spec_partial:** some proposition splits have detections and others do not, or detections exist but FOI still `[-1]`.
- **unclassifiable:** propositions absent from spec or missing NSVS index mapping.

Detection counts map each proposition to its `UNTIL` split bucket (same convention as `PropertyChecker.check_split`) — propositions sharing a split share a count.

## Sampled rows (3 per category)

### spec_un_groundable — PULS prompt fix

#### QID 1833 (`empty_puls_output`)

- **Question:** Is the person always sitting on the floor ?
- **Mode:** bool | **Source:** agqa
- **PULS spec:** ``
- **Propositions:** []
- **Detection counts:** {}
- **NSVS indices (split buckets):** []
- **FOI:** [-1] | **NSVS output:** [-1]

#### QID 359 (`operator_collapse_open_ended`)

- **Question:** The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action by the person does not overlap with putting clothes somewhere ? Is it Option A: put a phone somewhere, Option B: take a picture of something, Option C: put clothes somewhere, Option D: wash a mirror. Reply with the chosen option in one character.
- **Mode:** mc | **Source:** agqa
- **PULS spec:** `("person_puts_clothes_somewhere")`
- **Propositions:** ['person_puts_clothes_somewhere']
- **Detection counts:** {'person_puts_clothes_somewhere': 0}
- **NSVS indices (split buckets):** []
- **FOI:** [-1] | **NSVS output:** [-1]

#### QID 59 (`relation_not_in_spec`)

- **Question:** Do person going from standing to sitting and taking off some shoes overlap ?
- **Mode:** bool | **Source:** agqa
- **PULS spec:** `"person_goes_from_standing_to_sitting" | "person_takes_off_shoes"`
- **Propositions:** ['person_goes_from_standing_to_sitting', 'person_takes_off_shoes']
- **Detection counts:** {'person_goes_from_standing_to_sitting': 0, 'person_takes_off_shoes': 0}
- **NSVS indices (split buckets):** []
- **FOI:** [-1] | **NSVS output:** [-1]

### spec_ok_no_detect — NSVS detector quality

#### QID 1743 (`zero_detections`)

- **Question:** Is it true that person holding a mirror always co-occur with sitting at a table ?
- **Mode:** bool | **Source:** star
- **PULS spec:** `"person_holds_a_mirror" U "person_sits_at_a_table"`
- **Propositions:** ['person_holds_a_mirror', 'person_sits_at_a_table']
- **Detection counts:** {'person_holds_a_mirror': 0, 'person_sits_at_a_table': 0}
- **NSVS indices (split buckets):** []
- **FOI:** [-1] | **NSVS output:** [-1]

#### QID 639 (`zero_detections`)

- **Question:** Is it true that person holding a cup of something does not overlap with holding some clothes ?
- **Mode:** bool | **Source:** agqa
- **PULS spec:** `("person_holds_a_cup_of_something") U ! ("person_holds_some_clothes")`
- **Propositions:** ['person_holds_a_cup_of_something', 'person_holds_some_clothes']
- **Detection counts:** {'person_holds_a_cup_of_something': 0, 'person_holds_some_clothes': 0}
- **NSVS indices (split buckets):** []
- **FOI:** [-1] | **NSVS output:** [-1]

#### QID 503 (`zero_detections`)

- **Question:** Is it true that person carrying handle does not overlap with reaching for salt ?
- **Mode:** bool | **Source:** bf
- **PULS spec:** `! ("person_carrying_handle" & "person_reaches_for_salt")`
- **Propositions:** ['person_carrying_handle', 'person_reaches_for_salt']
- **Detection counts:** {'person_carrying_handle': 0, 'person_reaches_for_salt': 0}
- **NSVS indices (split buckets):** []
- **FOI:** [-1] | **NSVS output:** [-1]

### spec_partial — temporal aggregation

#### QID 656 (`split_mixed_detections`)

- **Question:** Do person holding some clothes and throwing clothes somewhere overlap ?
- **Mode:** bool | **Source:** agqa
- **PULS spec:** `"person_holds_some_clothes" & "person_throws_clothes_somewhere"`
- **Propositions:** ['person_holds_some_clothes', 'person_throws_clothes_somewhere']
- **Detection counts:** {'person_holds_some_clothes': 3, 'person_throws_clothes_somewhere': 3}
- **NSVS indices (split buckets):** [[0, 1, 2], []]
- **FOI:** [0, 55] | **NSVS output:** [0, 48]

#### QID 483 (`mixed_prop_detections`)

- **Question:** Is it true that person holding a phone/camera always co-occur with closing a closet/cabinet ?
- **Mode:** bool | **Source:** star
- **PULS spec:** `"person_holds_a_phonecamera" U "person_closes_a_closetcabinet"`
- **Propositions:** ['person_holds_a_phonecamera', 'person_closes_a_closetcabinet']
- **Detection counts:** {'person_holds_a_phonecamera': 0, 'person_closes_a_closetcabinet': 1}
- **NSVS indices (split buckets):** [[], [0]]
- **FOI:** [0, 10] | **NSVS output:** [0, 0]

#### QID 431 (`mixed_prop_detections`)

- **Question:** Do person putting some food somewhere and standing up overlap ?
- **Mode:** bool | **Source:** agqa
- **PULS spec:** `! ("person_puts_food_somewhere" U "person_stands_up")`
- **Propositions:** ['person_puts_food_somewhere', 'person_stands_up']
- **Detection counts:** {'person_puts_food_somewhere': 0, 'person_stands_up': 1}
- **NSVS indices (split buckets):** [[], [2]]
- **FOI:** [0, 76] | **NSVS output:** [48, 48]

### unclassifiable — human inspection

_No rows in this category._

## Notes

- `unknown` operator family is **23%** of val; **93.9%** NSVS-bypass rate on this family (416/443 in this dump).
- Empty PULS output (`empty_puls_output`, n=94) often corresponds to MC prompts where PULS returned no propositions — a strong PULS-side failure mode.
- `operator_collapse_open_ended` flags What/Which/How + temporal cue questions reduced to a single proposition without `UNTIL` — PULS cannot represent the queried event.

