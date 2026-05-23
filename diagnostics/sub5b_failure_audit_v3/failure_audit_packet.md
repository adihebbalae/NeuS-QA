# Sub #1/Sub #5B Disagreement Audit Packet (v3)

Purpose: a human-flippable disagreement slice where Sub #1 and Sub #5B gave different answers. v3 pre-fills triage signals (PULS_preliminary, Watch_for, Caption_coverage, Caption_question_mismatch, NSVS_bypassed) to speed tagging.

> Important label caveat: EvalAI does not expose row-level ground truth locally. Disagreement rows are not conditioned on who was correct.

## Slice Balance

- Rows: 25
- Audit duration buckets: {'<10s': 10, '30-60s': 5, '60-180s': 5, '>180s': 5}
- Legacy length buckets: {'short': 10, 'medium': 8, 'long': 7}
- Source dataset: {'star': 6, 'agqa': 4, 'bf': 5, 'ct': 10}
- Operator family: {'after': 3, 'since': 2, 'always_before': 5, 'before': 3, 'in_turn_occurs': 2, 'unknown': 4, 'until': 3, 'always_after': 3}
- Nearest-midpoint proxy fills: 0
- Frame-description cache: `/home/ah66742/NeuS-QA/diagnostics/sub5b_failure_audit_v2/failure_audit_frame_descriptions.json`
- Selected rows CSV: `/home/ah66742/NeuS-QA/diagnostics/sub5b_failure_audit_v2/selected_rows.csv`

## Reader Tally

### Tier 1 — Pre-filled auto triage

Builder-computed counts across the slice. Use these to prioritize human review.

| Signal | Flagged rows | / 25 |
| --- | ---: | ---: |
| PULS_preliminary ≠ pass | 5 | / 25 |
| NSVS_bypassed starts with yes/partial | 19 | / 25 |
| Caption_coverage partial or unknown | 22 | / 25 |
| Caption_question_mismatch ≠ pass | 0 | / 25 |
| Benchmark_confound = yes (star/agqa <10s) | 10 | / 25 |

### Tier 2 — Human review (fill after tagging)

After reviewing each row, tally unchecked boxes here:

- PULS_ok unchecked: ____ / 25
- NSVS_detect_ok unchecked: ____ / 25
- Storm_interval_ok unchecked: ____ / 25
- VQA_ok unchecked: ____ / 25
- Caption_ok unchecked: ____ / 25

Use Tier 2 as the decision signal: dominant `NSVS_detect_ok` failures point at visual grounding / InternVL; dominant `Storm_interval_ok` failures point at interval semantics / DAG-style logic.

Tagging criteria:

- PULS_preliminary / PULS_ok: Does the spec encode the question's actual temporal relationship, and are propositions concrete enough to detect in frames?
- Watch_for: Use the per-row hint to know which temporal edge to inspect in captions/video.
- Caption_coverage / Caption_ok: Do sampled captions cover NSVS detections and the final FOI window?
- Caption_question_mismatch: Do captions mention proposition keywords at all?
- NSVS_bypassed: Was Storm/FOI effectively unusable ([-1] or all-empty detections)?
- NSVS_detect_ok: For each proposition, do detection indices land where captions say the action happens?
- Storm_interval_ok: Given detection arrays, is the raw Storm interval correct for the spec semantics?
- VQA_ok: Given final FOI and frame descriptions, does the answer follow from visible evidence?
- Benchmark_confound: star/agqa sub-10s clips may be time-warped; do not over-penalize ordering at 1× playback.

## 1. QID 1809 - star / <10s / after

**Tagging block (v3)**

- PULS_preliminary: flag: spec uses U (until); question asks immediately_after (ordering may be under-specified)
- Watch_for: Check whether `person puts phonecamera somewhere` begins within 1–2 frames after `person drinks from cupglassbottle` ends. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: full: 14 caption frames cover all 1 target frames
- Caption_question_mismatch: pass
- NSVS_bypassed: yes: Storm/FOI returned [-1] (downstream VQA likely unconstrained)
- Benchmark_confound: yes: star clip 0.6s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Did the person put a phone/camera somewhere immediately after drinking from a cup/glass/bottle ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> star_1SLTT.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_1SLTT.mp4">star_1SLTT.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_1SLTT.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_1SLTT.mp4'</code><br>
<b>Duration:</b> 0.6s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_puts_phonecamera_somewhere&quot;, &quot;person_drinks_from_cupglassbottle&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_drinks_from_cupglassbottle&quot; U &quot;person_puts_phonecamera_somewhere&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_drinks_from_cupglassbottle&quot; U &quot;person_puts_phonecamera_somewhere&quot;` captures the temporal relation; propositions (person puts phonecamera somewhere, person drinks from cupglassbottle) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[-1]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+0, +5]</code><br>
<b>Target-ID explanation:</b> The question is about what happens immediately after an action (&#x27;drinking&#x27;), so a small padding before &#x27;putting phone/camera somewhere&#x27; to include the end of the first action is appropriate, with a larger padding after to capture any ensuing relevant events.<br>
<b>Final FOI:</b> <code>[-1]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 14
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>frame 0</b> (frame 0, 0.0s): A person stands in a room holding a cup to their mouth. The person appears to be drinking from the cup.</li>
<li><b>frame 1</b> (frame 1, 0.04s): The person continues to drink from the cup. The background shows a table with various items.</li>
<li><b>frame 2</b> (frame 2, 0.08s): The person lowers the cup after drinking. They are looking down at the cup.</li>
<li><b>frame 3</b> (frame 3, 0.12s): The person is holding the cup with both hands. They appear to be examining the cup.</li>
<li><b>frame 4</b> (frame 4, 0.16s): The person is still holding the cup and looking at it. The table is visible with items scattered on it.</li>
<li><b>frame 5</b> (frame 5, 0.2s): The person shifts their gaze away from the cup. They are preparing to place the cup down.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person moves the cup towards the table. Their hand is positioned to set the cup down.</li>
<li><b>frame 7</b> (frame 7, 0.28s): The person places the cup on the table. The table is cluttered with various items.</li>
<li><b>frame 8</b> (frame 8, 0.32s): The person reaches for an object on the table. The cup is now resting on the table.</li>
<li><b>frame 9</b> (frame 9, 0.36s): The person picks up a phone from the table. The cup remains in its place.</li>
<li><b>frame 10</b> (frame 10, 0.4s): The person is holding the phone in their hand. They are looking at the phone.</li>
<li><b>frame 11</b> (frame 11, 0.44s): The person turns slightly away from the table. The phone is still in their hand.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person is moving away from the table. The cup is still visible on the table.</li>
<li><b>frame 13</b> (frame 13, 0.52s): The person walks away from the table. The background shows the room&#x27;s decor.</li>
</ul>
</details>

## 2. QID 1014 - star / <10s / since

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Confirm `person grabs a picture` holds continuously from the anchor/start of `person reaches for a picture` through the clip end. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: full: 18 caption frames cover all 1 target frames
- Caption_question_mismatch: pass
- NSVS_bypassed: yes: Storm/FOI returned [-1] (downstream VQA likely unconstrained)
- Benchmark_confound: yes: star clip 0.7s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Has the person been reaching for and grabbing a picture since they lay on the floor ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> star_LG7WK.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LG7WK.mp4">star_LG7WK.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LG7WK.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_LG7WK.mp4'</code><br>
<b>Duration:</b> 0.7s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_reaches_for_a_picture&quot;, &quot;person_grabs_a_picture&quot;, &quot;person_lays_on_the_floor&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_lays_on_the_floor&quot; U (&quot;person_reaches_for_a_picture&quot; &amp; &quot;person_grabs_a_picture&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_lays_on_the_floor&quot; U (&quot;person_reaches_for_a_picture&quot; &amp; &quot;person_grabs_a_picture&quot;)` captures the temporal relation; propositions (person reaches for a picture, person grabs a picture, person lays on the floor) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[-1]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+3, +1]</code><br>
<b>Target-ID explanation:</b> The question asks if the action of reaching for and grabbing a picture has been happening since laying on the floor, which is a &#x27;during&#x27; situation. Modest padding is applied on both sides to capture the initial condition of the person laying on the floor and the ongoing actions of reaching and grabbing.<br>
<b>Final FOI:</b> <code>[-1]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>frame 0</b> (frame 0, 0.0s): A person is lying on the floor with their back against the ground. They appear to be in a relaxed position.</li>
<li><b>frame 1</b> (frame 1, 0.04s): The person is still lying on the floor, slightly shifting their position. Their arms are moving as if preparing to reach for something.</li>
<li><b>frame 2</b> (frame 2, 0.08s): The person continues to shift, with their arms moving more actively. They seem to be attempting to sit up.</li>
<li><b>frame 3</b> (frame 3, 0.12s): The person is now in a more upright position, still on the floor. Their arms are extended forward, indicating a reach.</li>
<li><b>frame 4</b> (frame 4, 0.16s): The person is sitting up with their legs bent, reaching towards a box in front of them. Their focus appears directed at the box.</li>
<li><b>frame 5</b> (frame 5, 0.2s): The person is now fully sitting, with their back straight. They are looking towards the box, preparing to grab something.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person is still facing the box, with their hands moving towards it. They seem to be getting ready to pick something up.</li>
<li><b>frame 7</b> (frame 7, 0.28s): The person is now reaching into the box with both hands. Their body is leaning slightly forward.</li>
<li><b>frame 8</b> (frame 8, 0.32s): The person is still reaching into the box, with their hands inside. They appear to be grasping an object.</li>
<li><b>frame 9</b> (frame 9, 0.36s): The person has pulled their hands out of the box, holding an object. They are looking at it closely.</li>
<li><b>frame 10</b> (frame 10, 0.4s): The person is examining the object they retrieved from the box. Their posture is upright and engaged.</li>
<li><b>frame 11</b> (frame 11, 0.44s): The person continues to hold the object, appearing to inspect it further. Their focus remains on the item.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person is still holding the object, with a slight smile on their face. They seem pleased with what they found.</li>
<li><b>frame 13</b> (frame 13, 0.52s): The person is now turning slightly to the side while still holding the object. Their expression shows interest.</li>
<li><b>frame 14</b> (frame 14, 0.56s): The person is adjusting their position, still focused on the object. They appear to be contemplating their next action.</li>
<li><b>frame 15</b> (frame 15, 0.6s): The person is sitting comfortably, still holding the object. They seem to be enjoying the moment.</li>
<li><b>frame 16</b> (frame 16, 0.64s): The person is now looking around the room while still holding the object. Their demeanor is relaxed.</li>
<li><b>frame 17</b> (frame 17, 0.68s): The person is still seated, with the object in their hands. They appear to be reflecting on it.</li>
</ul>
</details>

## 3. QID 1215 - agqa / <10s / always_before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person opens a laptop before person opens a bag); earlier actions must precede later ones.
- Caption_coverage: partial: missing caption frames [20, 21, 22, 23, 24] (20 captions vs 25 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: no
- Benchmark_confound: yes: agqa clip 1.0s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person opening a laptop and person opening a bag ? Is it Option A: open a bag, Option B: put a bag somewhere, Option C: hold a bag, Option D: open a laptop. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. open a bag<br>B. put a bag somewhere<br>C. hold a bag<br>D. open a laptop<br><br>
<b>Sub #1 answer:</b> C<br>
<b>Sub #5B answer:</b> B<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> agqa_DBT6E.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_DBT6E.mp4">agqa_DBT6E.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_DBT6E.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_DBT6E.mp4'</code><br>
<b>Duration:</b> 1.0s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_opens_a_laptop&quot;, &quot;person_opens_a_bag&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_opens_a_laptop&quot; U &quot;person_opens_a_bag&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_opens_a_laptop&quot; U &quot;person_opens_a_bag&quot;` captures the temporal relation; propositions (person opens a laptop, person opens a bag) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0
  ],
  [
    0
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[0, 0]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+5, +2]; nsvs_start_sec=0.0; nsvs_end_sec=0.0</code><br>
<b>Target-ID explanation:</b> The question is structured as a &#x27;before&#x27; question, where we&#x27;re interested in capturing more context leading up to the interval where the observed event occurs, allowing the system to analyze what actions may have transpired just before the objects are opened.<br>
<b>Final FOI:</b> <code>[0, 24]</code>
</td>
<td>
<b>Answer text:</b> B<br>
<b>Raw answer:</b> <code>B</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>frame 0</b> (frame 0, 0.0s): A person is standing and holding a backpack. The person is wearing a blue shirt and pink pants.</li>
<li><b>frame 1</b> (frame 1, 0.04s): The person bends down towards the backpack. The backpack is positioned on the floor.</li>
<li><b>frame 2</b> (frame 2, 0.08s): The person continues to lean down, looking into the backpack. The backpack remains on the floor.</li>
<li><b>frame 3</b> (frame 3, 0.12s): The person is now squatting next to the backpack. They appear to be reaching into the backpack.</li>
<li><b>frame 4</b> (frame 4, 0.16s): The person is still squatting and has their hand inside the backpack. The backpack is open.</li>
<li><b>frame 5</b> (frame 5, 0.2s): The person is sitting on the floor next to the open backpack. They are looking at the contents of the backpack.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person is still sitting and appears to be sorting through items in the backpack. The backpack is still open.</li>
<li><b>frame 7</b> (frame 7, 0.28s): The person is sitting cross-legged and holding an item from the backpack. The backpack remains open.</li>
<li><b>frame 8</b> (frame 8, 0.32s): The person is still seated and is examining an item taken from the backpack. The backpack is still on the floor.</li>
<li><b>frame 9</b> (frame 9, 0.36s): The person is placing the item back into the backpack. The backpack is open and on the floor.</li>
<li><b>frame 10</b> (frame 10, 0.4s): The person continues to put items back into the backpack. They are focused on the backpack.</li>
<li><b>frame 11</b> (frame 11, 0.44s): The person is still engaged with the backpack, adjusting its contents. The backpack remains open.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person is still seated and appears to be zipping up the backpack. The backpack is partially closed.</li>
<li><b>frame 13</b> (frame 13, 0.52s): The person is zipping the backpack closed. The backpack is now mostly closed.</li>
<li><b>frame 14</b> (frame 14, 0.56s): The person is finishing zipping up the backpack. The backpack is now fully closed.</li>
<li><b>frame 15</b> (frame 15, 0.6s): The person is now holding the closed backpack. They are preparing to move.</li>
<li><b>frame 16</b> (frame 16, 0.64s): The person stands up with the backpack in hand. They are facing forward.</li>
<li><b>frame 17</b> (frame 17, 0.68s): The person is now standing upright with the backpack. They appear to be ready to leave.</li>
<li><b>frame 18</b> (frame 18, 0.72s): The person is moving towards a table with the backpack. The environment is a room with a green cabinet.</li>
<li><b>frame 19</b> (frame 19, 0.76s): The person is placing the backpack on the table. The table is visible in the frame.</li>
</ul>
</details>

## 4. QID 1252 - agqa / <10s / before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Confirm `person sits at a table` completes before `person holds a broom` begins. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: full: 20 caption frames cover all 1 target frames
- Caption_question_mismatch: pass
- NSVS_bypassed: yes: Storm/FOI returned [-1] (downstream VQA likely unconstrained)
- Benchmark_confound: yes: agqa clip 1.0s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Did the person sit at a table before holding a broom ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> Yes<br>
<b>Sub #5B answer:</b> No<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> agqa_SXFG6.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_SXFG6.mp4">agqa_SXFG6.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_SXFG6.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_SXFG6.mp4'</code><br>
<b>Duration:</b> 1.0s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_sits_at_a_table&quot;, &quot;person_holds_a_broom&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_sits_at_a_table&quot; U &quot;person_holds_a_broom&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_sits_at_a_table&quot; U &quot;person_holds_a_broom&quot;` captures the temporal relation; propositions (person sits at a table, person holds a broom) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[-1]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[-5, +2]</code><br>
<b>Target-ID explanation:</b> The question seeks events occurring before a specific action, so a larger padding is needed before the interval start to capture the relevant context leading up to &#x27;person holds a broom&#x27;, and a smaller padding after.<br>
<b>Final FOI:</b> <code>[-1]</code>
</td>
<td>
<b>Answer text:</b> No<br>
<b>Raw answer:</b> <code>No</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>frame 0</b> (frame 0, 0.0s): A person is sitting on a chair, holding a cushion close to their chest. The background shows a kitchen area with a refrigerator and a table.</li>
<li><b>frame 1</b> (frame 1, 0.04s): The person continues to sit on the chair, still holding the cushion tightly. The lighting remains consistent, illuminating the scene.</li>
<li><b>frame 2</b> (frame 2, 0.08s): The person shifts slightly in their seat while maintaining their grip on the cushion. The table and kitchen area are still visible in the background.</li>
<li><b>frame 3</b> (frame 3, 0.12s): The person appears to smile while holding the cushion, indicating a moment of affection. The chair and table remain in the frame.</li>
<li><b>frame 4</b> (frame 4, 0.16s): The person adjusts their position slightly, still embracing the cushion. The kitchen area continues to be visible behind them.</li>
<li><b>frame 5</b> (frame 5, 0.2s): The person leans back in the chair while holding the cushion. The table and surrounding kitchen items are still present.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person appears to be laughing or smiling while holding the cushion. The background remains unchanged with the kitchen visible.</li>
<li><b>frame 7</b> (frame 7, 0.28s): The person continues to hold the cushion closely, showing a relaxed demeanor. The table and kitchen area are still in view.</li>
<li><b>frame 8</b> (frame 8, 0.32s): The person shifts slightly again, maintaining their hold on the cushion. The kitchen background remains consistent.</li>
<li><b>frame 9</b> (frame 9, 0.36s): The person appears to be looking down at the cushion, still holding it tightly. The table and kitchen area are visible.</li>
<li><b>frame 10</b> (frame 10, 0.4s): The person is still seated, holding the cushion with both arms. The kitchen background continues to be present.</li>
<li><b>frame 11</b> (frame 11, 0.44s): The person smiles while holding the cushion, indicating a moment of joy. The table and kitchen items are still visible.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person shifts their position slightly, still embracing the cushion. The kitchen area remains in the background.</li>
<li><b>frame 13</b> (frame 13, 0.52s): The person appears to be enjoying the moment with the cushion. The table and kitchen items are still visible.</li>
<li><b>frame 14</b> (frame 14, 0.56s): The person stands up from the chair while still holding the cushion. The kitchen area is still visible in the background.</li>
<li><b>frame 15</b> (frame 15, 0.6s): The person is now fully standing, still holding the cushion. The table and kitchen area remain in view.</li>
<li><b>frame 16</b> (frame 16, 0.64s): The person begins to walk away from the table while holding the cushion. The kitchen background is still visible.</li>
<li><b>frame 17</b> (frame 17, 0.68s): The person continues walking away, still holding the cushion. The table and kitchen area are still present.</li>
<li><b>frame 18</b> (frame 18, 0.72s): The person is moving further away from the table, still holding the cushion. The kitchen background remains unchanged.</li>
<li><b>frame 19</b> (frame 19, 0.76s): The person is almost out of the frame, still holding the cushion. The table and kitchen area are still visible.</li>
</ul>
</details>

## 5. QID 1105 - star / <10s / in_turn_occurs

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Inspect whether frame captions support the `in_turn_occurs` relation among [&#x27;person sits at a table&#x27;, &#x27;person holds a dish&#x27;, &#x27;person holds some food&#x27;]. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: partial: missing caption frames [20, 21, 22, 23, 24, 25, 26, 27] (20 captions vs 28 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: no
- Benchmark_confound: yes: star clip 1.1s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Is it true that person sitting at a table occurs before person holding a dish and which in turn occurs before person holding some food ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> star_X11CU.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_X11CU.mp4">star_X11CU.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_X11CU.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_X11CU.mp4'</code><br>
<b>Duration:</b> 1.1s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_sits_at_a_table&quot;, &quot;person_holds_a_dish&quot;, &quot;person_holds_some_food&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_sits_at_a_table&quot; &amp; &quot;person_holds_a_dish&quot;) U &quot;person_holds_some_food&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_sits_at_a_table&quot; &amp; &quot;person_holds_a_dish&quot;) U &quot;person_holds_some_food&quot;` captures the temporal relation; propositions (person sits at a table, person holds a dish, person holds some food) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0,
    1
  ],
  [
    0,
    1
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[0, 24]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+3, +1]; nsvs_start_sec=0.0; nsvs_end_sec=0.96</code><br>
<b>Target-ID explanation:</b> The question is evaluating a &#x27;before&#x27; relationship, so larger padding is added before the start of the interval to capture the context leading up to the specified events, while a smaller padding is added after the end of the interval to capture any immediate aftermath.<br>
<b>Final FOI:</b> <code>[0, 27]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>frame 0</b> (frame 0, 0.0s): A person is sitting at a table, engaged with items on the table. Another person is standing nearby, facing away from the camera.</li>
<li><b>frame 1</b> (frame 1, 0.04s): The person at the table continues to interact with the items. The standing person remains in the same position, slightly turned.</li>
<li><b>frame 2</b> (frame 2, 0.08s): The seated person is still focused on the table, possibly picking up something. The standing person is now looking towards the window.</li>
<li><b>frame 3</b> (frame 3, 0.12s): The seated person appears to be reaching for an item on the table. The standing person is still facing the window.</li>
<li><b>frame 4</b> (frame 4, 0.16s): The seated person is now holding something in their hand. The standing person remains stationary, looking out the window.</li>
<li><b>frame 5</b> (frame 5, 0.2s): The person at the table is examining the item they are holding. The standing person is still looking away.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The seated person is now placing the item back on the table. The standing person continues to look out the window.</li>
<li><b>frame 7</b> (frame 7, 0.28s): The seated person is reaching for another item on the table. The standing person is still in the same position.</li>
<li><b>frame 8</b> (frame 8, 0.32s): The seated person is now holding a small bowl. The standing person remains looking away.</li>
<li><b>frame 9</b> (frame 9, 0.36s): The seated person is examining the contents of the bowl. The standing person is still facing the window.</li>
<li><b>frame 10</b> (frame 10, 0.4s): The seated person appears to be preparing to eat from the bowl. The standing person is still looking away.</li>
<li><b>frame 11</b> (frame 11, 0.44s): The seated person is now bringing the bowl closer to their mouth. The standing person remains in the same position.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The seated person is eating from the bowl. The standing person is still looking out the window.</li>
<li><b>frame 13</b> (frame 13, 0.52s): The seated person continues to eat from the bowl. The standing person is still facing away.</li>
<li><b>frame 14</b> (frame 14, 0.56s): The seated person is now looking at the table again. The standing person remains in the same position.</li>
<li><b>frame 15</b> (frame 15, 0.6s): The seated person is reaching for another item on the table. The standing person is still looking away.</li>
<li><b>frame 16</b> (frame 16, 0.64s): The seated person is now holding a different item. The standing person remains stationary.</li>
<li><b>frame 17</b> (frame 17, 0.68s): The seated person appears to be inspecting the new item. The standing person is still facing the window.</li>
<li><b>frame 18</b> (frame 18, 0.72s): The seated person is now placing the item back on the table. The standing person continues to look away.</li>
<li><b>frame 19</b> (frame 19, 0.76s): The seated person is looking at the table again. The standing person is still in the same position.</li>
</ul>
</details>

## 6. QID 489 - agqa / <10s / after

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Confirm `event B` occurs only after `person walks through a doorway` completes. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: partial: missing caption frames [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68] (9 captions vs 70 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: yes: agqa clip 2.8s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do after walking through a doorway ? Is it Option A: turn on a light, Option B: close a door, Option C: eat some food, Option D: grasp onto a doorknob. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. turn on a light<br>B. close a door<br>C. eat some food<br>D. grasp onto a doorknob<br><br>
<b>Sub #1 answer:</b> D<br>
<b>Sub #5B answer:</b> B<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> agqa_KZS5M.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_KZS5M.mp4">agqa_KZS5M.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_KZS5M.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_KZS5M.mp4'</code><br>
<b>Duration:</b> 2.8s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_walks_through_a_doorway&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_walks_through_a_doorway&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_walks_through_a_doorway&quot;)` captures the temporal relation; propositions (person walks through a doorway) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[0, 0]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+0, +5]; nsvs_start_sec=0.0; nsvs_end_sec=0.0</code><br>
<b>Target-ID explanation:</b> The question is an &#x27;after&#x27; question, which suggests smaller padding before the interval end and larger padding after the interval end to capture subsequent actions. Since the interval is at the start of the video [0.00, 0.00], there’s no need for padding before, but a reasonable 5-second padding is added after the interval to capture what the person does immediately after walking through the doorway.<br>
<b>Final FOI:</b> <code>[0, 69]</code>
</td>
<td>
<b>Answer text:</b> B<br>
<b>Raw answer:</b> <code>B</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>~0.00s</b> (frame 0, 0.0s): A person is standing in a doorway, facing slightly to the right. The room behind them is visible with furniture and a rug.</li>
<li><b>~0.40s</b> (frame 10, 0.4s): The person is stepping through the doorway, with their body partially turned. The door is open, revealing more of the room.</li>
<li><b>~0.80s</b> (frame 20, 0.8s): The person is now inside the room, reaching towards a bed with a blue patterned cover. A plate of food is on a small table beside the bed.</li>
<li><b>~1.20s</b> (frame 30, 1.2s): The person is walking away from the bed, moving towards the left side of the frame. The background shows a staircase and more furniture.</li>
<li><b>FOI midpoint</b> (frame 34, 1.36s): The person is in mid-stride, moving towards the left. Their body is slightly blurred, indicating motion.</li>
<li><b>~1.56s</b> (frame 39, 1.56s): The person is reaching towards a television set, with their arm extended. The room is well-lit, showing various objects around.</li>
<li><b>~1.96s</b> (frame 49, 1.96s): The person is standing still, holding something in their hand. They are looking towards the left side of the frame.</li>
<li><b>~2.36s</b> (frame 59, 2.36s): The person is walking back towards the bed, with a focused expression. The plate of food is still visible on the table.</li>
<li><b>~2.76s</b> (frame 69, 2.76s): The person is sitting on the edge of the bed, appearing to be preparing to eat. The room is calm and organized.</li>
</ul>
</details>

## 7. QID 601 - star / <10s / always_before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person takes a sandwich from somewhere before event B); earlier actions must precede later ones.
- Caption_coverage: partial: missing caption frames [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48] (10 captions vs 50 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: yes: star clip 2.8s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do always before taking a sandwich from somewhere ? Is it Option A: eat a sandwich, Option B: hold a phone/camera, Option C: take food from somewhere, Option D: take a sandwich from somewhere. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. eat a sandwich<br>B. hold a phone/camera<br>C. take food from somewhere<br>D. take a sandwich from somewhere<br><br>
<b>Sub #1 answer:</b> B<br>
<b>Sub #5B answer:</b> C<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> star_FUT86.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_FUT86.mp4">star_FUT86.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_FUT86.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_FUT86.mp4'</code><br>
<b>Duration:</b> 2.8s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_takes_a_sandwich_from_somewhere&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_takes_a_sandwich_from_somewhere&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_takes_a_sandwich_from_somewhere&quot;)` captures the temporal relation; propositions (person takes a sandwich from somewhere) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    1
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[24, 24]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+3, +1]; nsvs_start_sec=0.96; nsvs_end_sec=0.96</code><br>
<b>Target-ID explanation:</b> Since the question is about actions occurring before &#x27;taking a sandwich from somewhere&#x27;, we need larger padding before the interval start to capture the preceding context and a smaller padding after the interval starts.<br>
<b>Final FOI:</b> <code>[0, 49]</code>
</td>
<td>
<b>Answer text:</b> C<br>
<b>Raw answer:</b> <code>C</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>~0.00s</b> (frame 0, 0.0s): The scene shows a room with a table covered in a pink cloth. Various objects are scattered on the table, including a pink teddy bear.</li>
<li><b>NSVS detect: person takes a sandwich from somewhe [0]</b> (frame 1, 0.04s): A person is seated at a table, holding a phone or camera. The focus is on their hands and the surrounding objects.</li>
<li><b>~0.40s</b> (frame 10, 0.4s): The person continues to hold the phone or camera, with their attention directed towards it. The table remains cluttered with items.</li>
<li><b>~0.80s</b> (frame 20, 0.8s): The person is still seated, now appearing to interact with the phone or camera. The pink teddy bear is prominently visible.</li>
<li><b>FOI midpoint</b> (frame 24, 0.96s): The camera angle shifts slightly, showing more of the table and the person&#x27;s hands. The person seems to be preparing for an action.</li>
<li><b>~1.20s</b> (frame 30, 1.2s): The person is now looking down at the table, possibly at the sandwich. The surrounding items remain unchanged.</li>
<li><b>~1.56s</b> (frame 39, 1.56s): The person is still focused on the table, with their hands visible. The sandwich is now more clearly in view.</li>
<li><b>~1.96s</b> (frame 49, 1.96s): The person appears to be reaching for the sandwich. The table is cluttered with various food items.</li>
<li><b>~2.36s</b> (frame 59, 2.36s): The person is now holding the sandwich, bringing it closer. The background shows a well-lit room.</li>
<li><b>~2.76s</b> (frame 69, 2.76s): The person is about to take a bite of the sandwich. The table remains filled with food and other objects.</li>
</ul>
</details>

## 8. QID 682 - star / <10s / always_before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person puts a cup somewhere before person holds a dish); earlier actions must precede later ones.
- Caption_coverage: partial: missing caption frames [3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68] (11 captions vs 70 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: no
- Benchmark_confound: yes: star clip 2.8s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person putting a cup/glass/bottle somewhere and person holding a dish ? Is it Option A: put a dish/es somewhere, Option B: hold some clothes, Option C: walk through a doorway, Option D: put a cup/glass/bottle somewhere. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. put a dish/es somewhere<br>B. hold some clothes<br>C. walk through a doorway<br>D. put a cup/glass/bottle somewhere<br><br>
<b>Sub #1 answer:</b> C<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> star_YIG5G.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_YIG5G.mp4">star_YIG5G.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_YIG5G.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_YIG5G.mp4'</code><br>
<b>Duration:</b> 2.8s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_puts_a_cup_somewhere&quot;, &quot;person_holds_a_dish&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_puts_a_cup_somewhere&quot; U &quot;person_holds_a_dish&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_puts_a_cup_somewhere&quot; U &quot;person_holds_a_dish&quot;` captures the temporal relation; propositions (person puts a cup somewhere, person holds a dish) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    2
  ],
  [
    1,
    2
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[24, 48]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+5, +1]; nsvs_start_sec=0.96; nsvs_end_sec=1.92</code><br>
<b>Target-ID explanation:</b> Since the question asks for actions occurring before a specified event, more padding is added before the interval to capture context and less padding after.<br>
<b>Final FOI:</b> <code>[0, 69]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code></code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>~0.00s</b> (frame 0, 0.0s): The scene shows a living room with two chairs and a table. A person is sitting on one chair, holding a cup.</li>
<li><b>NSVS detect: person holds a dish [0]</b> (frame 1, 0.04s): A person is holding a dish while seated. The other person remains in the same position.</li>
<li><b>NSVS detect: person puts a cup somewhere [0]</b> (frame 2, 0.08s): The person is now putting a cup down on the table. The other person continues to hold the dish.</li>
<li><b>~0.40s</b> (frame 10, 0.4s): The scene remains unchanged with both individuals in their respective positions. The person with the dish is still seated.</li>
<li><b>~0.80s</b> (frame 20, 0.8s): The person holding the dish is still in the same position. The other person is also seated, holding a cup.</li>
<li><b>~1.20s</b> (frame 30, 1.2s): The living room scene continues with both individuals remaining seated. The person with the dish is still holding it.</li>
<li><b>FOI midpoint</b> (frame 34, 1.36s): A person enters the room from the left side. The seated person observes the newcomer.</li>
<li><b>~1.56s</b> (frame 39, 1.56s): The newcomer is now visible, holding something in their hands. The seated person continues to watch.</li>
<li><b>~1.96s</b> (frame 49, 1.96s): The newcomer approaches the seated person. The seated person remains focused on the newcomer.</li>
<li><b>~2.36s</b> (frame 59, 2.36s): The newcomer is closer to the seated person, still holding the item. The seated person is still observing.</li>
<li><b>~2.76s</b> (frame 69, 2.76s): The newcomer is now standing directly in front of the seated person. The seated person continues to hold the cup.</li>
</ul>
</details>

## 9. QID 34 - star / <10s / unknown

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Inspect whether frame captions support the `unknown` relation among [&#x27;person throws clothes somewhere&#x27;]. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: partial: missing caption frames [3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 38, 39, 40, 41, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73] (11 captions vs 75 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: yes: star clip 3.0s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Does the person eventually throw clothes somewhere ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> star_WPU76.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_WPU76.mp4">star_WPU76.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_WPU76.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/star_WPU76.mp4'</code><br>
<b>Duration:</b> 3.0s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_throws_clothes_somewhere&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_throws_clothes_somewhere&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_throws_clothes_somewhere&quot;)` captures the temporal relation; propositions (person throws clothes somewhere) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0,
    1,
    2
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[0, 48]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+2, +2]; nsvs_start_sec=0.0; nsvs_end_sec=1.92</code><br>
<b>Target-ID explanation:</b> The question is about verifying whether an event eventually occurs, which suggests a &#x27;during&#x27; context. Therefore, modest padding is applied on both sides to allow the VLM to better understand the scenario around this event.<br>
<b>Final FOI:</b> <code>[0, 74]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>~0.00s</b> (frame 0, 0.0s): A person stands near a table with a pile of clothes on the floor. The person is wearing a blue shirt and black pants.</li>
<li><b>NSVS detect: person throws clothes somewhere [1]</b> (frame 1, 0.04s): The person appears to be moving their hands towards the table. The pile of clothes remains on the floor.</li>
<li><b>NSVS detect: person throws clothes somewhere [2]</b> (frame 2, 0.08s): The person continues to gesture towards the table, maintaining focus on the task. The clothes on the floor are still visible.</li>
<li><b>~0.44s</b> (frame 11, 0.44s): The person is now walking away from the table towards the kitchen area. The pile of clothes is still on the floor.</li>
<li><b>~0.84s</b> (frame 21, 0.84s): The person is standing at the kitchen sink, looking out the window. The clothes pile is still present in the foreground.</li>
<li><b>~1.28s</b> (frame 32, 1.28s): The person is back near the pile of clothes, appearing to bend down. The clothes are still scattered on the floor.</li>
<li><b>FOI midpoint</b> (frame 37, 1.48s): The person is reaching down towards the pile of clothes. The surrounding area remains unchanged.</li>
<li><b>~1.68s</b> (frame 42, 1.68s): The person is picking up clothes from the floor. The pile is still visible as they interact with it.</li>
<li><b>~2.12s</b> (frame 53, 2.12s): The person is holding a piece of clothing, looking at it. The pile of clothes is still on the floor.</li>
<li><b>~2.52s</b> (frame 63, 2.52s): The person is standing with clothes in hand, appearing to consider their next action. The pile remains unchanged.</li>
<li><b>~2.96s</b> (frame 74, 2.96s): The person is walking away from the pile of clothes. The clothes are still scattered on the floor.</li>
</ul>
</details>

## 10. QID 262 - agqa / <10s / since

**Tagging block (v3)**

- PULS_preliminary: flag: since question but spec has neither U nor G operator
- Watch_for: Confirm `event B` holds continuously from the anchor/start of `person holds some clothes` through the clip end. Use 0.25× playback for star/agqa sub-10s clips.
- Caption_coverage: partial: missing caption frames [3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76] (11 captions vs 78 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: yes: agqa clip 3.1s (likely time-warped; use 0.25× playback)

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What has been the person doing since they held some clothes ? Is it Option A: put clothes somewhere, Option B: put something on a table, Option C: throw a blanket somewhere, Option D: watch a book. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. put clothes somewhere<br>B. put something on a table<br>C. throw a blanket somewhere<br>D. watch a book<br><br>
<b>Sub #1 answer:</b> B<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> agqa_ME4YL.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_ME4YL.mp4">agqa_ME4YL.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_ME4YL.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/agqa_ME4YL.mp4'</code><br>
<b>Duration:</b> 3.1s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_holds_some_clothes&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_holds_some_clothes&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_holds_some_clothes&quot;` captures the temporal relation; propositions (person holds some clothes) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    1,
    2
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[24, 48]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+2, +2]; nsvs_start_sec=0.96; nsvs_end_sec=1.92</code><br>
<b>Target-ID explanation:</b> The question is about &#x27;since they held some clothes&#x27;, implying a &#x27;during&#x27; inquiry of what happened from the point of holding onwards. Thus, modest padding is needed on both sides to capture a reasonable temporal context.<br>
<b>Final FOI:</b> <code>[0, 77]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code>A</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>~0.00s</b> (frame 0, 0.0s): The scene shows a kitchen with wooden cabinets and a table. A person is not yet visible.</li>
<li><b>NSVS detect: person holds some clothes [0]</b> (frame 1, 0.04s): A person is visible holding some clothes. They are standing in the kitchen.</li>
<li><b>NSVS detect: person holds some clothes [1]</b> (frame 2, 0.08s): The person continues to hold the clothes while standing in the same position. The kitchen environment remains unchanged.</li>
<li><b>~0.44s</b> (frame 11, 0.44s): The person is now moving towards the kitchen counter. They are still holding the clothes.</li>
<li><b>~0.88s</b> (frame 22, 0.88s): The person is gesturing with the clothes in their hands. They appear to be preparing to place them down.</li>
<li><b>~1.32s</b> (frame 33, 1.32s): The person is now holding the clothes up, possibly to throw or place them. The kitchen remains the same.</li>
<li><b>FOI midpoint</b> (frame 38, 1.52s): The person is in a mid-action pose, still holding the clothes. They are facing the kitchen counter.</li>
<li><b>~1.76s</b> (frame 44, 1.76s): The person is walking away from the counter, still holding the clothes. The kitchen layout is consistent.</li>
<li><b>~2.20s</b> (frame 55, 2.2s): The person is now at the kitchen counter, appearing to set down the clothes. The environment remains unchanged.</li>
<li><b>~2.64s</b> (frame 66, 2.64s): The person is still at the counter, engaged with the clothes. They are in a stationary position.</li>
<li><b>~3.08s</b> (frame 77, 3.08s): The person is now focused on the counter, possibly interacting with the clothes. The kitchen setting is consistent.</li>
</ul>
</details>

## 11. QID 107 - bf / 30-60s / always_before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person pushes drawer before person reaches for choco lid); earlier actions must precede later ones.
- Caption_coverage: partial: missing caption frames [1, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388] (14 captions vs 390 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: no
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person pushing drawer which in turn always occurs before person reaching for Choco lid ? Is it Option A: reach for chocolate powder, Option B: scoop chocolate powder, Option C: reach for spoon, Option D: carry Choco lid. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. reach for chocolate powder<br>B. scoop chocolate powder<br>C. reach for spoon<br>D. carry Choco lid<br><br>
<b>Sub #1 answer:</b> C<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> bf_P35_webcam02_P35_milk.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P35_webcam02_P35_milk.mp4">bf_P35_webcam02_P35_milk.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P35_webcam02_P35_milk.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P35_webcam02_P35_milk.mp4'</code><br>
<b>Duration:</b> 38.5s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_pushes_drawer&quot;, &quot;person_reaches_for_choco_lid&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_pushes_drawer&quot; U &quot;person_reaches_for_choco_lid&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_pushes_drawer&quot; U &quot;person_reaches_for_choco_lid&quot;` captures the temporal relation; propositions (person pushes drawer, person reaches for choco lid) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    10,
    11
  ],
  [
    2,
    9,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    24,
    28,
    33,
    36,
    37
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[30, 374]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+3, +1]; nsvs_start_sec=2.0; nsvs_end_sec=24.933333333333334</code><br>
<b>Target-ID explanation:</b> Since the question asks about actions occurring before the specified events, we want to allow more time prior to the identified interval to capture relevant preceding actions while adding a smaller buffer after the start to ensure context while being focused on actions leading to the interval.<br>
<b>Final FOI:</b> <code>[0, 389]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code></code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>FOI start</b> (frame 0, 0.0s): The scene shows a kitchen with a table and various items on it. A black mug with the letters &#x27;EBL&#x27; is placed on the table.</li>
<li><b>NSVS detect: person reaches for choco lid [0]</b> (frame 2, 0.133s): A person is seen reaching towards a lid on the table. The background remains unchanged with kitchen items visible.</li>
<li><b>NSVS detect: person reaches for choco lid [1]</b> (frame 9, 0.6s): The person continues to reach for the choco lid, with their hand extended. The kitchen setting remains consistent.</li>
<li><b>NSVS detect: person pushes drawer [0]</b> (frame 10, 0.667s): The person is now pushing a drawer in the kitchen. The drawer is partially open, indicating interaction.</li>
<li><b>NSVS detect: person pushes drawer [1]</b> (frame 11, 0.733s): The drawer is being pushed further by the person. The kitchen environment remains visible in the background.</li>
<li><b>NSVS detect: person reaches for choco lid [3]</b> (frame 12, 0.8s): The person is again reaching for the choco lid, with their hand closer to it. The kitchen items are still in view.</li>
<li><b>NSVS detect: person reaches for choco lid [4]</b> (frame 13, 0.867s): The person&#x27;s hand is now almost touching the choco lid. The surrounding kitchen items remain unchanged.</li>
<li><b>10% of video</b> (frame 58, 3.867s): The scene shows a wider view of the kitchen with various items on the table. The black mug is still prominently placed.</li>
<li><b>25% of video</b> (frame 144, 9.6s): The kitchen scene continues to show the table and items, with no significant changes. The black mug remains in focus.</li>
<li><b>FOI midpoint</b> (frame 194, 12.933s): The kitchen remains unchanged, with the black mug still on the table. Various kitchen items are visible in the background.</li>
<li><b>50% of video</b> (frame 288, 19.2s): The kitchen scene is still visible, showing the table and items. The black mug continues to be a focal point.</li>
<li><b>FOI end</b> (frame 389, 25.933s): The kitchen scene is still present, with the black mug on the table. The surrounding items remain unchanged.</li>
<li><b>75% of video</b> (frame 432, 28.8s): The kitchen view continues, showing the table and various items. The black mug is still prominently displayed.</li>
<li><b>90% of video</b> (frame 518, 34.533s): The kitchen scene remains consistent, with the black mug on the table. Various kitchen items are still visible.</li>
</ul>
</details>

## 12. QID 808 - bf / 30-60s / unknown

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Inspect whether frame captions support the `unknown` relation among [&#x27;person carries milk&#x27;].
- Caption_coverage: partial: missing caption frames [15, 20, 21, 38, 40, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599] (13 captions vs 506 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Does the person eventually carry milk ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> bf_P47_cam01_P47_cereals.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P47_cam01_P47_cereals.mp4">bf_P47_cam01_P47_cereals.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P47_cam01_P47_cereals.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P47_cam01_P47_cereals.mp4'</code><br>
<b>Duration:</b> 45.0s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_carries_milk&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_carries_milk&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_carries_milk&quot;)` captures the temporal relation; propositions (person carries milk) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    7,
    9,
    12,
    13,
    14,
    15,
    20,
    21,
    38,
    40
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[105, 600]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+0, +0]; nsvs_start_sec=7.0; nsvs_end_sec=40.0</code><br>
<b>Target-ID explanation:</b> The question does not specify a temporal relation of before, after, or during, it merely asks if the event eventually occurs. Therefore, no additional padding is needed around the identified interval; the interval itself is sufficient to assess the presence of the event.<br>
<b>Final FOI:</b> <code>[105, 600]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person carries milk [0]</b> (frame 7, 0.467s): A person is seen with their hands on a countertop. There is a bowl and a carton of juice visible on the surface.</li>
<li><b>NSVS detect: person carries milk [1]</b> (frame 9, 0.6s): The person remains in the same position with their hands on the countertop. The bowl and juice carton are still present.</li>
<li><b>NSVS detect: person carries milk [2]</b> (frame 12, 0.8s): The person continues to keep their hands on the countertop. The surrounding objects, including the bowl and juice carton, are unchanged.</li>
<li><b>NSVS detect: person carries milk [3]</b> (frame 13, 0.867s): The person is still positioned at the countertop with their hands resting. The bowl and juice carton remain visible.</li>
<li><b>NSVS detect: person carries milk [4]</b> (frame 14, 0.933s): The person maintains their position with hands on the countertop. The bowl and juice carton are still in view.</li>
<li><b>10% of video</b> (frame 67, 4.467s): The scene shows the countertop with the bowl and juice carton. The person is not visible in this frame.</li>
<li><b>FOI start</b> (frame 105, 7.0s): The person is now visible, standing at the countertop. They are preparing to pour something into a bowl.</li>
<li><b>25% of video</b> (frame 168, 11.2s): The person is holding a carton and appears to be pouring its contents. The bowl is positioned on the countertop.</li>
<li><b>50% of video</b> (frame 337, 22.467s): The person is still at the countertop, now holding a bowl. The surrounding area remains unchanged.</li>
<li><b>FOI midpoint</b> (frame 352, 23.467s): The person is seen with a bowl in hand, looking at the countertop. The environment remains consistent.</li>
<li><b>75% of video</b> (frame 506, 33.733s): The person is still at the countertop, with the bowl visible. The surrounding objects are unchanged.</li>
<li><b>FOI end</b> (frame 600, 40.0s): The person is still present at the countertop, with the bowl in view. The environment remains the same.</li>
<li><b>90% of video</b> (frame 607, 40.467s): The person continues to interact with the bowl at the countertop. The surrounding objects are consistent.</li>
</ul>
</details>

## 13. QID 224 - bf / 30-60s / unknown

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Inspect whether frame captions support the `unknown` relation among [&#x27;person pours water&#x27;, &#x27;person carries kettle&#x27;].
- Caption_coverage: partial: missing caption frames [271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569] (10 captions vs 303 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Is it true that person pouring water does not overlap with carrying kettle ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> bf_P23_webcam01_P23_tea.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P23_webcam01_P23_tea.mp4">bf_P23_webcam01_P23_tea.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P23_webcam01_P23_tea.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P23_webcam01_P23_tea.mp4'</code><br>
<b>Duration:</b> 47.7s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_pours_water&quot;, &quot;person_carries_kettle&quot;]</code><br><br>
<b>TL spec:</b><br><code>(! &quot;person_pours_water&quot;) U &quot;person_carries_kettle&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(! &quot;person_pours_water&quot;) U &quot;person_carries_kettle&quot;` captures the temporal relation; propositions (person pours water, person carries kettle) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [],
  [
    20,
    36
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[300, 540]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+2, +2]; nsvs_start_sec=20.0; nsvs_end_sec=36.0</code><br>
<b>Target-ID explanation:</b> The question asks about the lack of overlap (&#x27;does not overlap with&#x27;), implying a &#x27;during&#x27; relationship where the truth of the specification should be verified throughout the interval. As it&#x27;s important to capture any border effects, modest padding is applied on both sides of the interval.<br>
<b>Final FOI:</b> <code>[270, 570]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person carries kettle [0]</b> (frame 20, 1.333s): A person is seen carrying a kettle in their right hand. The background shows a kitchen setting with a stove and some items on the counter.</li>
<li><b>NSVS detect: person carries kettle [1]</b> (frame 36, 2.4s): The same person continues to carry the kettle while walking away from the camera. The kitchen remains visible with various items on the counter.</li>
<li><b>10% of video</b> (frame 71, 4.733s): The frame shows a view of the kitchen with no visible actions. The kettle is not present in this frame.</li>
<li><b>25% of video</b> (frame 178, 11.867s): A person is seen walking in the background, but no kettle or pouring action is visible. The kitchen environment is still present.</li>
<li><b>FOI start</b> (frame 270, 18.0s): The frame shows a close-up of a person preparing something on the counter. The kettle is not visible in this frame.</li>
<li><b>50% of video</b> (frame 357, 23.8s): A person is seen holding a mug and a packet, preparing to add something to the mug. The kettle is not present.</li>
<li><b>FOI midpoint</b> (frame 420, 28.0s): The person is now placing a lid on the mug, indicating preparation. The kettle is still not visible.</li>
<li><b>75% of video</b> (frame 536, 35.733s): The person is pouring water from a kettle into the mug. The kettle is clearly visible in their hand.</li>
<li><b>FOI end</b> (frame 570, 38.0s): The person continues to pour water into the mug, with the kettle still in view. The action of pouring is evident.</li>
<li><b>90% of video</b> (frame 643, 42.867s): The person is now setting the kettle down after pouring. The mug is in focus, showing the completed action.</li>
</ul>
</details>

## 14. QID 1399 - ct / 30-60s / until

**Tagging block (v3)**

- PULS_preliminary: flag: until question but spec has neither U nor G operator
- Watch_for: Confirm `event B` holds until `person stirs mixture` occurs (then may stop).
- Caption_coverage: partial: missing caption frames [265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031] (13 captions vs 774 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until stirred mixture ? Is it Option A: pour jello powder, Option B: pour mixture into cup, Option C: stir mixture, Option D: pour oil. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. pour jello powder<br>B. pour mixture into cup<br>C. stir mixture<br>D. pour oil<br><br>
<b>Sub #1 answer:</b> A<br>
<b>Sub #5B answer:</b> C<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_qs2eKOubSYY.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_qs2eKOubSYY.mp4">ct_qs2eKOubSYY.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_qs2eKOubSYY.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_qs2eKOubSYY.mp4'</code><br>
<b>Duration:</b> 48.5s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_stirs_mixture&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_stirs_mixture&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_stirs_mixture&quot;)` captures the temporal relation; propositions (person stirs mixture) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    13,
    26,
    28,
    29,
    40
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[312, 960]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+2, +3]; nsvs_start_sec=12.98920754716981; nsvs_end_sec=39.96679245283019</code><br>
<b>Target-ID explanation:</b> The question suggests a &#x27;during&#x27; scenario focusing on events happening until &#x27;stirred mixture&#x27;. It implies observing actions slightly before and slightly after the interval where the mixture is stirred to capture associated activities.<br>
<b>Final FOI:</b> <code>[264, 1032]</code>
</td>
<td>
<b>Answer text:</b> C<br>
<b>Raw answer:</b> <code>C</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person stirs mixture [0]</b> (frame 13, 0.541s): A person is stirring a mixture in a bowl. The motion indicates active mixing.</li>
<li><b>NSVS detect: person stirs mixture [1]</b> (frame 26, 1.082s): The person continues to stir the mixture with a spoon. The mixture appears to be thickening.</li>
<li><b>NSVS detect: person stirs mixture [2]</b> (frame 28, 1.166s): The stirring motion is more vigorous now. The bowl is still in focus as the person mixes.</li>
<li><b>NSVS detect: person stirs mixture [3]</b> (frame 29, 1.207s): The person is still actively stirring the mixture. The spoon is fully submerged in the bowl.</li>
<li><b>NSVS detect: person stirs mixture [4]</b> (frame 40, 1.665s): The stirring continues with a consistent motion. The mixture&#x27;s texture is visibly changing.</li>
<li><b>10% of video</b> (frame 116, 4.829s): The video shows a wider view of the kitchen setup. Various ingredients and utensils are visible.</li>
<li><b>FOI start</b> (frame 264, 10.991s): The focus shifts to a specific area where the mixture is being prepared. The person is not currently visible.</li>
<li><b>25% of video</b> (frame 291, 12.115s): The video captures a close-up of the mixture in a bowl. The texture appears smooth and glossy.</li>
<li><b>50% of video</b> (frame 582, 24.23s): The video shows a different angle of the preparation area. The person is still not in view.</li>
<li><b>FOI midpoint</b> (frame 648, 26.978s): The focus remains on the mixture, which is now in a different container. The stirring action is not visible.</li>
<li><b>75% of video</b> (frame 874, 36.386s): The video shows the final presentation of the prepared mixture. The colors are vibrant and appealing.</li>
<li><b>FOI end</b> (frame 1032, 42.964s): The final product is displayed prominently. The mixture has set into a solid form.</li>
<li><b>90% of video</b> (frame 1048, 43.63s): The video concludes with a view of the finished jello cups. They are arranged neatly on a tray.</li>
</ul>
</details>

## 15. QID 1135 - bf / 30-60s / always_before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person pulls drawer before person carries spoon); earlier actions must precede later ones.
- Caption_coverage: partial: missing caption frames [37, 38, 39, 40, 48, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748] (13 captions vs 549 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. Which action always occurs before person pulling drawer which in turn always occurs before person carrying spoon ? Is it Option A: pull drawer, Option B: move, Option C: garbage, Option D: carry spoon. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. pull drawer<br>B. move<br>C. garbage<br>D. carry spoon<br><br>
<b>Sub #1 answer:</b> B<br>
<b>Sub #5B answer:</b> C<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> bf_P53_cam02_P53_cereals.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P53_cam02_P53_cereals.mp4">bf_P53_cam02_P53_cereals.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P53_cam02_P53_cereals.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P53_cam02_P53_cereals.mp4'</code><br>
<b>Duration:</b> 56.6s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_pulls_drawer&quot;, &quot;person_carries_spoon&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_pulls_drawer&quot; U &quot;person_carries_spoon&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_pulls_drawer&quot; U &quot;person_carries_spoon&quot;` captures the temporal relation; propositions (person pulls drawer, person carries spoon) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [],
  [
    19,
    26,
    27,
    28,
    29,
    37,
    38,
    39,
    40,
    48
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[285, 720]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+5, +2]; nsvs_start_sec=19.02240566037736; nsvs_end_sec=48.056603773584904</code><br>
<b>Target-ID explanation:</b> The question asks about actions occurring before others, indicating a larger padding should be applied before the interval start to capture preceding actions, with a smaller padding after the interval to ensure full context of the action sequence.<br>
<b>Final FOI:</b> <code>[211, 749]</code>
</td>
<td>
<b>Answer text:</b> C<br>
<b>Raw answer:</b> <code>C</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person carries spoon [0]</b> (frame 19, 1.268s): A person is holding a spoon in their right hand. The background shows a kitchen counter with various items.</li>
<li><b>NSVS detect: person carries spoon [1]</b> (frame 26, 1.735s): The person continues to hold the spoon, now slightly raised. The kitchen items remain visible in the background.</li>
<li><b>NSVS detect: person carries spoon [2]</b> (frame 27, 1.802s): The person is still holding the spoon, with a focused expression. The kitchen setting is consistent with previous frames.</li>
<li><b>NSVS detect: person carries spoon [3]</b> (frame 28, 1.869s): The spoon is held at a similar angle, indicating the person is preparing to use it. The kitchen environment is unchanged.</li>
<li><b>NSVS detect: person carries spoon [4]</b> (frame 29, 1.936s): The person maintains their grip on the spoon, suggesting an ongoing action. The kitchen items are still visible in the background.</li>
<li><b>10% of video</b> (frame 85, 5.673s): The scene shows a wider view of the kitchen counter with various items. The lighting is consistent with previous frames.</li>
<li><b>FOI start</b> (frame 211, 14.083s): The focus shifts to a specific area of the kitchen. Items on the counter are clearly visible.</li>
<li><b>25% of video</b> (frame 212, 14.15s): The camera captures a close-up of the kitchen counter. Various containers and utensils are arranged on the surface.</li>
<li><b>50% of video</b> (frame 424, 28.3s): The scene shows a person interacting with kitchen items. The focus is on the actions taking place.</li>
<li><b>FOI midpoint</b> (frame 480, 32.038s): The camera captures a moment of activity in the kitchen. The person is engaged with the items on the counter.</li>
<li><b>75% of video</b> (frame 635, 42.383s): The kitchen scene continues with various items in view. The person is still involved in the activity.</li>
<li><b>FOI end</b> (frame 749, 49.992s): The final moments of the focus show the kitchen environment. The person is concluding their actions.</li>
<li><b>90% of video</b> (frame 762, 50.86s): The scene captures the kitchen in its entirety. The person is still present, indicating ongoing activity.</li>
</ul>
</details>

## 16. QID 1911 - ct / 60-180s / before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Confirm `person steams milk` completes before `event B` begins.
- Caption_coverage: partial: missing caption frames [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 56, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859] (13 captions vs 1861 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do before steaming milk ? Is it Option A: add coffee, Option B: pour milk, Option C: steam milk, Option D: put meringue into oven. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. add coffee<br>B. pour milk<br>C. steam milk<br>D. put meringue into oven<br><br>
<b>Sub #1 answer:</b> B<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_rUo6VC9HxJ8.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_rUo6VC9HxJ8.mp4">ct_rUo6VC9HxJ8.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_rUo6VC9HxJ8.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_rUo6VC9HxJ8.mp4'</code><br>
<b>Duration:</b> 72.2s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_steams_milk&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_steams_milk&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_steams_milk&quot;)` captures the temporal relation; propositions (person steams milk) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    2,
    3,
    54,
    57,
    60
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[60, 1800]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+10, +2]; nsvs_start_sec=2.0; nsvs_end_sec=60.0</code><br>
<b>Target-ID explanation:</b> The question asks what occurred before steaming milk, so we need to allow more time before the identified interval (2.00, 60.00) to capture preceding actions. Minimal padding is added after the interval to ensure the action of steaming milk is included, based on general timeframes for such activities.<br>
<b>Final FOI:</b> <code>[0, 1860]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code>A</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>FOI start</b> (frame 0, 0.0s): The video begins with no visible actions or objects. The scene is blank.</li>
<li><b>NSVS detect: person steams milk [0]</b> (frame 2, 0.067s): A person is seen preparing to steam milk. The background shows a coffee machine.</li>
<li><b>NSVS detect: person steams milk [1]</b> (frame 3, 0.1s): The person is now holding a milk pitcher. The coffee machine is still visible.</li>
<li><b>NSVS detect: person steams milk [2]</b> (frame 54, 1.8s): The person begins to steam the milk, with steam visibly rising from the pitcher. The coffee machine is in focus.</li>
<li><b>NSVS detect: person steams milk [3]</b> (frame 57, 1.9s): The steaming process continues, with more steam being produced. The person&#x27;s hand is steady on the pitcher.</li>
<li><b>NSVS detect: person steams milk [4]</b> (frame 60, 2.0s): The milk is being heated, and the person is focused on the steaming process. The coffee machine remains in the background.</li>
<li><b>10% of video</b> (frame 216, 7.2s): The scene shows the person still steaming milk. The environment is a coffee shop with various equipment visible.</li>
<li><b>25% of video</b> (frame 541, 18.033s): The person is now pouring steamed milk into a cup. The cup is positioned on the counter.</li>
<li><b>FOI midpoint</b> (frame 930, 31.0s): The person is seen finishing the milk pouring process. The cup has a latte art design on top.</li>
<li><b>50% of video</b> (frame 1082, 36.067s): The person holds the finished cup of coffee with latte art. The background shows the coffee shop ambiance.</li>
<li><b>75% of video</b> (frame 1624, 54.133s): The person is now serving the coffee to a customer. The interaction is friendly and casual.</li>
<li><b>FOI end</b> (frame 1860, 62.0s): The video concludes with the person cleaning up the area. The coffee machine and other equipment are still visible.</li>
<li><b>90% of video</b> (frame 1948, 64.933s): The scene shows the coffee shop bustling with activity. Customers are enjoying their drinks.</li>
</ul>
</details>

## 17. QID 738 - ct / 60-180s / always_after

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person spreads mixture before person puts meringue into oven); later actions must follow earlier ones.
- Caption_coverage: partial: missing caption frames [44, 45, 49, 54, 55, 56, 57, 60, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677] (15 captions vs 523 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: no
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Did the person put meringue into oven always after spreading mixture ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_Jp1U6Gb1DxM.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Jp1U6Gb1DxM.mp4">ct_Jp1U6Gb1DxM.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Jp1U6Gb1DxM.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Jp1U6Gb1DxM.mp4'</code><br>
<b>Duration:</b> 77.2s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_spreads_mixture&quot;, &quot;person_puts_meringue_into_oven&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_spreads_mixture&quot; U &quot;person_puts_meringue_into_oven&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_spreads_mixture&quot; U &quot;person_puts_meringue_into_oven&quot;` captures the temporal relation; propositions (person spreads mixture, person puts meringue into oven) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0,
    1,
    2,
    41,
    42,
    44,
    45,
    49,
    54,
    55,
    56,
    57,
    60
  ],
  [
    46,
    47
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[1230, 1439]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+2, +8]; nsvs_start_sec=41.041000000000004; nsvs_end_sec=48.014633333333336</code><br>
<b>Target-ID explanation:</b> Since the question asks about an &#x27;after&#x27; sequence, we use small padding before the interval end and larger padding after the interval end. This allows the VLM to confirm the correctness of actions following the spreading of the mixture.<br>
<b>Final FOI:</b> <code>[1171, 1678]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person spreads mixture [0]</b> (frame 0, 0.0s): A person is spreading a mixture on a flat surface. The mixture appears to be light in color and is being evenly distributed.</li>
<li><b>NSVS detect: person spreads mixture [1]</b> (frame 1, 0.033s): The person continues to spread the mixture with their hands. The surface remains mostly clear as they work.</li>
<li><b>NSVS detect: person spreads mixture [2]</b> (frame 2, 0.067s): The person is still engaged in spreading the mixture. Their hands are moving in a circular motion to ensure even coverage.</li>
<li><b>NSVS detect: person spreads mixture [3]</b> (frame 41, 1.368s): The person is applying more pressure while spreading the mixture. The texture of the mixture is becoming more defined.</li>
<li><b>NSVS detect: person spreads mixture [4]</b> (frame 42, 1.401s): The person finishes spreading the mixture and lifts their hands away. The surface is now fully covered with the mixture.</li>
<li><b>NSVS detect: person puts meringue into oven [0]</b> (frame 46, 1.535s): The person is placing a tray with meringue into an oven. The meringue is white and fluffy, indicating it has been whipped.</li>
<li><b>NSVS detect: person puts meringue into oven [1]</b> (frame 47, 1.568s): The tray is being pushed further into the oven. The oven door is partially open, revealing the interior.</li>
<li><b>10% of video</b> (frame 231, 7.708s): No description returned for this frame.</li>
<li><b>25% of video</b> (frame 578, 19.286s): No description returned for this frame.</li>
<li><b>50% of video</b> (frame 1156, 38.572s): No description returned for this frame.</li>
<li><b>FOI start</b> (frame 1171, 39.072s): No description returned for this frame.</li>
<li><b>FOI midpoint</b> (frame 1424, 47.514s): No description returned for this frame.</li>
<li><b>FOI end</b> (frame 1678, 55.989s): No description returned for this frame.</li>
<li><b>75% of video</b> (frame 1734, 57.858s): No description returned for this frame.</li>
<li><b>90% of video</b> (frame 2081, 69.436s): No description returned for this frame.</li>
</ul>
</details>

## 18. QID 1675 - ct / 60-180s / always_after

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person pours egg before person spreads mixture); later actions must follow earlier ones.
- Caption_coverage: partial: missing caption frames [28, 29, 33, 34, 44, 45, 49, 54, 55, 56, 57, 60, 64, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887] (18 captions vs 711 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: no
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Did the person spread mixture always after pouring egg ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_Jp1U6Gb1DxM.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Jp1U6Gb1DxM.mp4">ct_Jp1U6Gb1DxM.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Jp1U6Gb1DxM.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Jp1U6Gb1DxM.mp4'</code><br>
<b>Duration:</b> 77.2s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_pours_egg&quot;, &quot;person_spreads_mixture&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_pours_egg&quot; U &quot;person_spreads_mixture&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_pours_egg&quot; U &quot;person_spreads_mixture&quot;` captures the temporal relation; propositions (person pours egg, person spreads mixture) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    8,
    15,
    21,
    22,
    26,
    28,
    29,
    33,
    34,
    41,
    64
  ],
  [
    0,
    1,
    2,
    41,
    42,
    44,
    45,
    49,
    54,
    55,
    56,
    57,
    60
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[1230, 1739]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+1, +5]; nsvs_start_sec=41.041000000000004; nsvs_end_sec=58.024633333333334</code><br>
<b>Target-ID explanation:</b> Since the question is an &#x27;always after&#x27; type, indicating interest in actions occurring after a specific point, a small padding before the interval end is sufficient for context, while a larger padding after the interval end allows for capturing subsequent action details.<br>
<b>Final FOI:</b> <code>[1201, 1888]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person spreads mixture [0]</b> (frame 0, 0.0s): A person is seen spreading a mixture on a surface. Their hand is actively moving the mixture around.</li>
<li><b>NSVS detect: person spreads mixture [1]</b> (frame 1, 0.033s): The person continues to spread the mixture with their hand. The mixture appears to be crumbly and is being evenly distributed.</li>
<li><b>NSVS detect: person spreads mixture [2]</b> (frame 2, 0.067s): The person&#x27;s hand is still engaged in spreading the mixture. The surface is partially covered with the mixture.</li>
<li><b>NSVS detect: person pours egg [0]</b> (frame 8, 0.267s): The person is pouring an egg into a bowl. The egg is being released from a container.</li>
<li><b>NSVS detect: person pours egg [1]</b> (frame 15, 0.501s): The pouring action continues as the egg flows into the bowl. The person&#x27;s hand is steady, controlling the pour.</li>
<li><b>NSVS detect: person pours egg [2]</b> (frame 21, 0.701s): The egg is almost fully poured into the bowl. The container is tilted at an angle.</li>
<li><b>NSVS detect: person pours egg [3]</b> (frame 22, 0.734s): The last remnants of the egg are being poured into the bowl. The person&#x27;s focus is on the bowl.</li>
<li><b>NSVS detect: person pours egg [4]</b> (frame 26, 0.868s): The pouring action is complete, and the person is now holding the empty container. The bowl is filled with the egg.</li>
<li><b>NSVS detect: person spreads mixture [3]</b> (frame 41, 1.368s): The person resumes spreading the mixture again. Their hand is moving in a circular motion over the mixture.</li>
<li><b>NSVS detect: person spreads mixture [4]</b> (frame 42, 1.401s): The mixture is being further spread out by the person&#x27;s hand. The surface is becoming more even.</li>
<li><b>10% of video</b> (frame 231, 7.708s): No description returned for this frame.</li>
<li><b>25% of video</b> (frame 578, 19.286s): No description returned for this frame.</li>
<li><b>50% of video</b> (frame 1156, 38.572s): No description returned for this frame.</li>
<li><b>FOI start</b> (frame 1201, 40.073s): No description returned for this frame.</li>
<li><b>FOI midpoint</b> (frame 1544, 51.518s): No description returned for this frame.</li>
<li><b>75% of video</b> (frame 1734, 57.858s): No description returned for this frame.</li>
<li><b>FOI end</b> (frame 1888, 62.996s): No description returned for this frame.</li>
<li><b>90% of video</b> (frame 2081, 69.436s): No description returned for this frame.</li>
</ul>
</details>

## 19. QID 1525 - bf / 60-180s / in_turn_occurs

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Inspect whether frame captions support the `in_turn_occurs` relation among [&#x27;person opens butter lid&#x27;, &#x27;person reaches for plate&#x27;].
- Caption_coverage: partial: missing caption frames [121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] (13 captions vs 1911 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Is it true that person opening butter lid occurs before person opening butter lid and which in turn occurs before person reaching for plate ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> bf_P43_cam01_P43_scrambledegg.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P43_cam01_P43_scrambledegg.mp4">bf_P43_cam01_P43_scrambledegg.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P43_cam01_P43_scrambledegg.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/bf_P43_cam01_P43_scrambledegg.mp4'</code><br>
<b>Duration:</b> 136.9s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_opens_butter_lid&quot;, &quot;person_reaches_for_plate&quot;]</code><br><br>
<b>TL spec:</b><br><code>&quot;person_opens_butter_lid&quot; U &quot;person_reaches_for_plate&quot;</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `&quot;person_opens_butter_lid&quot; U &quot;person_reaches_for_plate&quot;` captures the temporal relation; propositions (person opens butter lid, person reaches for plate) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [],
  [
    13,
    14,
    15,
    19,
    32,
    133
  ]
]</code></pre>
<b>Raw Storm interval:</b> <code>[195, 1995]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+5, +2]; nsvs_start_sec=13.0; nsvs_end_sec=133.0</code><br>
<b>Target-ID explanation:</b> The question &#x27;Is it true that X occurs before Y and which in turn occurs before Z?&#x27; is examining a sequence of events with a focus on their ordering before the last event occurs. Therefore, larger padding is applied before the interval start to capture any contextual setup, with smaller padding after the interval end to ensure the completion of the sequence is captured.<br>
<b>Final FOI:</b> <code>[120, 2025]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person reaches for plate [0]</b> (frame 13, 0.867s): A person is reaching towards a plate on a table. The setting appears to be a kitchen with various items visible.</li>
<li><b>NSVS detect: person reaches for plate [1]</b> (frame 14, 0.933s): The same person continues to reach for the plate, with their hand extended. The kitchen environment remains consistent.</li>
<li><b>NSVS detect: person reaches for plate [2]</b> (frame 15, 1.0s): The person is still in the process of reaching for the plate. The background shows kitchen items and a table.</li>
<li><b>NSVS detect: person reaches for plate [3]</b> (frame 19, 1.267s): The person is now closer to the plate, with their hand hovering above it. The kitchen setting is unchanged.</li>
<li><b>NSVS detect: person reaches for plate [4]</b> (frame 32, 2.133s): The person is reaching for the plate again, with a clear focus on the object. The kitchen remains the same.</li>
<li><b>FOI start</b> (frame 120, 8.0s): The scene shows a wider view of the kitchen, with various items on the counter. The person is not currently visible.</li>
<li><b>10% of video</b> (frame 205, 13.667s): The video shows a broader view of the kitchen, with sunlight streaming in. The person is not in the frame.</li>
<li><b>25% of video</b> (frame 513, 34.2s): The kitchen is still visible, with various items on the counter. The person is not present in this frame.</li>
<li><b>50% of video</b> (frame 1026, 68.4s): The kitchen scene continues, showing the same items and lighting. No person is visible in this frame.</li>
<li><b>FOI midpoint</b> (frame 1072, 71.467s): The kitchen remains in view, with no significant changes. The person is not visible.</li>
<li><b>75% of video</b> (frame 1540, 102.667s): The kitchen is still visible, maintaining the same layout and lighting. The person is absent from this frame.</li>
<li><b>90% of video</b> (frame 1848, 123.2s): The kitchen scene continues, with no changes in the environment. The person is not present.</li>
<li><b>FOI end</b> (frame 2025, 135.0s): The final frame shows the kitchen, with the same items visible. The person is not in this frame.</li>
</ul>
</details>

## 20. QID 635 - ct / 60-180s / until

**Tagging block (v3)**

- PULS_preliminary: flag: until question but spec has neither U nor G operator
- Watch_for: Confirm `event B` holds until `stirred mixture` occurs (then may stop).
- Caption_coverage: partial: missing caption frames [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 82, 83, 84, 85, 86, 87, 88, 89, 90, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2110, 2111, 2112, 2113, 2114, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2150, 2151, 2152, 2153, 2154, 2155, 2156, 2157, 2158, 2159, 2160, 2161, 2162, 2163, 2164, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2176, 2177, 2178, 2179, 2180, 2181, 2182, 2183, 2184, 2185, 2186, 2187, 2188, 2189, 2190, 2191, 2192, 2193, 2194, 2195, 2196, 2197, 2198, 2199, 2200, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219, 2220, 2221, 2222, 2223, 2224, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2233, 2234, 2235, 2236, 2237, 2238, 2239, 2240, 2241, 2242, 2243, 2244, 2245, 2246, 2247, 2248, 2249, 2250, 2251, 2252, 2253, 2254, 2255, 2256, 2257, 2258, 2259, 2260, 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280, 2281, 2282, 2283, 2284, 2285, 2286, 2287, 2288, 2289, 2290, 2291, 2292, 2293, 2294, 2295, 2296, 2297, 2298, 2299, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361, 2362, 2363, 2364, 2365, 2366, 2367, 2368, 2369, 2370, 2371, 2372, 2373, 2374, 2375, 2376, 2377, 2378, 2379, 2380, 2381, 2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421, 2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2442, 2443, 2444, 2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470, 2471, 2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481, 2482, 2483, 2484, 2485, 2486, 2487, 2488, 2489, 2490, 2491, 2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 2509, 2510, 2511, 2512, 2513, 2514, 2515, 2516, 2517, 2518, 2519, 2520, 2521, 2522, 2523, 2524, 2525, 2526, 2527, 2528, 2529, 2530, 2531, 2532, 2533, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2541, 2542, 2543, 2544, 2545, 2546, 2547, 2548, 2549, 2550, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601, 2602, 2603, 2604, 2605, 2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621, 2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641, 2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651, 2652, 2653, 2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661, 2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701, 2702, 2703, 2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 2714, 2715, 2716, 2717, 2718, 2719, 2720, 2721, 2722, 2723, 2724, 2725, 2726, 2727, 2728, 2729, 2730, 2731, 2732, 2733, 2734, 2735, 2736, 2737, 2738, 2739, 2740, 2741, 2742, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2759, 2760, 2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769, 2770, 2771, 2772, 2773, 2774, 2775, 2776, 2777, 2778, 2779, 2780, 2781, 2782, 2783, 2784, 2785, 2786, 2787, 2788, 2789, 2790, 2792, 2793, 2794, 2795, 2796, 2797, 2798, 2799, 2800, 2801, 2802, 2803, 2804, 2805, 2806, 2807, 2808, 2809, 2810, 2811, 2812, 2813, 2814, 2815, 2816, 2817, 2818, 2819, 2820, 2821, 2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829, 2830, 2831, 2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841, 2842, 2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851, 2852, 2853, 2854, 2855, 2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2905, 2906, 2907, 2908, 2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919, 2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 2972, 2973, 2974, 2975, 2976, 2977, 2978, 2979, 2980, 2981, 2982, 2983, 2984, 2985, 2986, 2987, 2988, 2989, 2990, 2991, 2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151, 3152, 3153, 3154, 3155, 3156, 3157, 3158, 3159, 3160, 3161, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388, 3389, 3390, 3391, 3392, 3393, 3394, 3395, 3396, 3397, 3398, 3399, 3400, 3401, 3402, 3403, 3404, 3405, 3406, 3407, 3408, 3409, 3410, 3411, 3412, 3413, 3414, 3415, 3416, 3417, 3418, 3419, 3420, 3421, 3422, 3423, 3424, 3425, 3426, 3427, 3428, 3429, 3430, 3431, 3432, 3433, 3434, 3435, 3436, 3437, 3438, 3439, 3440, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533, 3534, 3535, 3536, 3537, 3538, 3539, 3540, 3541, 3542, 3543, 3544, 3545, 3546, 3547, 3548, 3549, 3550, 3551, 3552, 3553, 3554, 3555, 3556, 3557, 3558, 3559, 3560, 3561, 3562, 3563, 3564, 3565, 3566, 3567, 3568, 3569, 3570, 3571, 3572, 3573, 3574, 3575, 3576, 3577, 3578, 3579, 3580, 3581, 3582, 3583, 3584, 3585, 3586, 3587, 3588, 3589, 3590, 3591, 3592, 3593, 3594, 3595, 3596, 3597, 3598, 3599, 3600, 3601, 3602, 3603, 3604, 3605, 3606, 3607, 3608, 3609, 3610, 3611, 3612, 3613, 3614, 3615, 3616, 3617, 3618, 3619, 3620, 3621, 3622, 3623, 3624, 3625, 3626, 3627, 3628, 3629, 3630, 3631, 3632, 3633, 3634, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 3643, 3644, 3645, 3646, 3647, 3648, 3649, 3650, 3651, 3652, 3653, 3654, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662, 3663, 3664, 3665, 3666, 3667, 3668, 3669, 3670, 3671, 3672, 3673, 3674, 3675, 3676, 3677, 3678, 3679, 3680, 3681, 3682, 3683, 3684, 3685, 3686, 3687, 3688, 3689, 3690, 3691, 3692, 3693, 3694] (12 captions vs 3696 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until stirred mixture ? Is it Option A: stir mixture, Option B: pour alcohol, Option C: pour mixture into cup, Option D: jack down. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. stir mixture<br>B. pour alcohol<br>C. pour mixture into cup<br>D. jack down<br><br>
<b>Sub #1 answer:</b> B<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_RhuRUsQ6tzw.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_RhuRUsQ6tzw.mp4">ct_RhuRUsQ6tzw.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_RhuRUsQ6tzw.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_RhuRUsQ6tzw.mp4'</code><br>
<b>Duration:</b> 155.2s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;stirred_mixture&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;stirred_mixture&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;stirred_mixture&quot;)` captures the temporal relation; propositions (stirred mixture) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    0,
    81,
    91,
    92,
    108,
    110,
    112,
    113,
    114,
    115,
    116,
    117,
    122,
    124,
    125,
    126,
    127,
    128,
    129,
    131,
    134,
    135,
    137,
    138,
    139,
    140,
    142,
    143,
    150,
    151
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[0, 3624]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+3, +3]; nsvs_start_sec=0.0; nsvs_end_sec=151.15099459072184</code><br>
<b>Target-ID explanation:</b> The question asks about actions that occurred until the event &#x27;stirred mixture&#x27;. This is a &#x27;during&#x27; question, therefore a modest padding (about 2-3 seconds each) is applied on both sides of the interval.<br>
<b>Final FOI:</b> <code>[0, 3695]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code>A</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>FOI start</b> (frame 0, 0.0s): The video begins with a title screen displaying the name of the creation. The background is black with blue text.</li>
<li><b>NSVS detect: stirred mixture [1]</b> (frame 81, 3.378s): Two individuals are seated at a table with various bottles and ingredients in front of them. The person on the left appears to be speaking animatedly.</li>
<li><b>NSVS detect: stirred mixture [2]</b> (frame 91, 3.795s): The same two individuals are still at the table, with the person on the left gesturing while talking. The person on the right is listening attentively.</li>
<li><b>NSVS detect: stirred mixture [3]</b> (frame 92, 3.837s): The individual on the left continues to express excitement, raising their hand. The person on the right maintains a neutral expression.</li>
<li><b>NSVS detect: stirred mixture [4]</b> (frame 108, 4.504s): The left individual is smiling and appears to be explaining something. The right individual is still focused on the conversation.</li>
<li><b>10% of video</b> (frame 372, 15.515s): The scene shows the left individual pouring a mixture from a pot into a pitcher. The right individual watches closely.</li>
<li><b>25% of video</b> (frame 930, 38.789s): The left individual is stirring the contents of the pitcher with a spoon. The right individual is now holding a cup.</li>
<li><b>FOI midpoint</b> (frame 1847, 77.035s): The left individual is animatedly explaining while the right individual is stirring the mixture in the pitcher. The table is cluttered with ingredients.</li>
<li><b>50% of video</b> (frame 1860, 77.577s): The right individual is pouring the mixture from the pitcher into the waiting cups. The left individual is observing.</li>
<li><b>75% of video</b> (frame 2791, 116.408s): The right individual is now placing the filled cups on the table. The left individual is smiling and appears pleased.</li>
<li><b>90% of video</b> (frame 3349, 139.681s): The two individuals are now enjoying the finished cupcakes. The left individual is feeding the right individual a cupcake.</li>
<li><b>FOI end</b> (frame 3695, 154.112s): The video concludes with a final shot of the cupcakes on the table. The right individual is looking at the camera with a smile.</li>
</ul>
</details>

## 21. QID 1590 - ct / >180s / always_after

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Verify global ordering across the chain (person pours jello powder before event B); later actions must follow earlier ones.
- Caption_coverage: partial: missing caption frames [13, 14, 36, 37, 38, 39, 41, 43, 44, 48, 49, 50, 51, 53, 54, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2110, 2111, 2112, 2113, 2114, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2150, 2151, 2152, 2153, 2154, 2155, 2156, 2157, 2158, 2159, 2160, 2161, 2162, 2163, 2164, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2176, 2177, 2178, 2179, 2180, 2181, 2182, 2183, 2184, 2185, 2186, 2187, 2188, 2189, 2190, 2191, 2192, 2193, 2194, 2195, 2196, 2197, 2198, 2199, 2200, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219, 2220, 2221, 2222, 2223, 2224, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2233, 2234, 2235, 2236, 2237, 2238, 2239, 2240, 2241, 2242, 2243, 2244, 2245, 2246, 2247, 2248, 2249, 2250, 2251, 2252, 2253, 2254, 2255, 2256, 2257, 2258, 2259, 2260, 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280, 2281, 2282, 2283, 2284, 2285, 2286, 2287, 2288, 2289, 2290, 2291, 2292, 2293, 2294, 2295, 2296, 2297, 2298, 2299, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361, 2362, 2363, 2364, 2365, 2366, 2367, 2368, 2369, 2370, 2371, 2372, 2373, 2374, 2375, 2376, 2377, 2378, 2379, 2380, 2381, 2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421, 2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2442, 2443, 2444, 2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470, 2471, 2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481, 2482, 2483, 2484, 2485, 2486, 2487, 2488, 2489, 2490, 2491, 2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 2509, 2510, 2511, 2512, 2513, 2514, 2515, 2516, 2517, 2518, 2519, 2520, 2521, 2522, 2523, 2524, 2525, 2526, 2527, 2528, 2529, 2530, 2531, 2532, 2533, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2541, 2542, 2543, 2544, 2545, 2546, 2547, 2548, 2549, 2550, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601, 2602, 2603, 2604, 2605, 2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621, 2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641, 2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651, 2652, 2653, 2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661, 2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701, 2702, 2703, 2704, 2705, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 2715, 2716, 2717, 2718, 2719, 2720, 2721, 2722, 2723, 2724, 2725, 2726, 2727, 2728, 2729, 2730, 2731, 2732, 2733, 2734, 2735, 2736, 2737, 2738, 2739, 2740, 2741, 2742, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2759, 2760, 2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769, 2770, 2771, 2772, 2773, 2774, 2775, 2776, 2777, 2778, 2779, 2780, 2781, 2782, 2783, 2784, 2785, 2786, 2787, 2788, 2789, 2790, 2791, 2792, 2793, 2794, 2795, 2796, 2797, 2798, 2799, 2800, 2801, 2802, 2803, 2804, 2805, 2806, 2807, 2808, 2809, 2810, 2811, 2812, 2813, 2814, 2815, 2816, 2817, 2818, 2819, 2820, 2821, 2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829, 2830, 2831, 2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841, 2842, 2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851, 2852, 2853, 2854, 2855, 2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2905, 2906, 2907, 2908, 2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919, 2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 2972, 2973, 2974, 2975, 2976, 2977, 2978, 2979, 2980, 2981, 2982, 2983, 2984, 2985, 2986, 2987, 2988, 2989, 2990, 2991, 2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151, 3152, 3153, 3154, 3155, 3156, 3157, 3158, 3159, 3160, 3161, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3349, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388, 3389, 3390, 3391, 3392, 3393, 3394, 3395, 3396, 3397, 3398, 3399, 3400, 3401, 3402, 3403, 3404, 3405, 3406, 3407, 3408, 3409, 3410, 3411, 3412, 3413, 3414, 3415, 3416, 3417, 3418, 3419, 3420, 3421, 3422, 3423, 3424, 3425, 3426, 3427, 3428, 3429, 3430, 3431, 3432, 3433, 3434, 3435, 3436, 3437, 3438, 3439, 3440, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533, 3534, 3535, 3536, 3537, 3538, 3539, 3540, 3541, 3542, 3543, 3544, 3545, 3546, 3547, 3548, 3549, 3550, 3551, 3552, 3553, 3554, 3555, 3556, 3557, 3558, 3559, 3560, 3561, 3562, 3563, 3564, 3565, 3566, 3567, 3568, 3569, 3570, 3571, 3572, 3573, 3574, 3575, 3576, 3577, 3578, 3579, 3580, 3581, 3582, 3583, 3584, 3585, 3586, 3587, 3588, 3589, 3590, 3591, 3592, 3593, 3594, 3595, 3596, 3597, 3598, 3599, 3600, 3601, 3602, 3603, 3604, 3605, 3606, 3607, 3608, 3609, 3610, 3611, 3612, 3613, 3614, 3615, 3616, 3617, 3618, 3619, 3620, 3621, 3622, 3623, 3624, 3625, 3626, 3627, 3628, 3629, 3630, 3631, 3632, 3633, 3634, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 3643, 3644, 3645, 3646, 3647, 3648, 3649, 3650, 3651, 3652, 3653, 3654, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662, 3663, 3664, 3665, 3666, 3667, 3668, 3669, 3670, 3671, 3672, 3673, 3674, 3675, 3676, 3677, 3678, 3679, 3680, 3681, 3682, 3683, 3684, 3685, 3686, 3687, 3688, 3689, 3690, 3691, 3692, 3693, 3694, 3695, 3696, 3697, 3698, 3699, 3700, 3701, 3702, 3703, 3704, 3705, 3706, 3707, 3708, 3709, 3710, 3711, 3712, 3713, 3714, 3715, 3716, 3717, 3718, 3719, 3720, 3721, 3722, 3723, 3724, 3725, 3726, 3727, 3728, 3729, 3730, 3731, 3732, 3733, 3734, 3735, 3736, 3737, 3738, 3739, 3740, 3741, 3742, 3743, 3744, 3745, 3746, 3747, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3766, 3767, 3768, 3769, 3770, 3771, 3772, 3773, 3774, 3775, 3776, 3777, 3778, 3779, 3780, 3781, 3782, 3783, 3784, 3785, 3786, 3787, 3788, 3789, 3790, 3791, 3792, 3793, 3794, 3795, 3796, 3797, 3798, 3799, 3800, 3801, 3802, 3803, 3804, 3805, 3806, 3807, 3808, 3809, 3810, 3811, 3812, 3813, 3814, 3815, 3816, 3817, 3818, 3819, 3820, 3821, 3822, 3823, 3824, 3825, 3826, 3827, 3828, 3829, 3830, 3831, 3832, 3833, 3834, 3835, 3836, 3837, 3838, 3839, 3840, 3841, 3842, 3843, 3844, 3845, 3846, 3847, 3848, 3849, 3850, 3851, 3852, 3853, 3854, 3855, 3856, 3857, 3858, 3859, 3860, 3861, 3862, 3863, 3864, 3865, 3866, 3867, 3868, 3869, 3870, 3871, 3872, 3873, 3874, 3875, 3876, 3877, 3878, 3879, 3880, 3881, 3882, 3883, 3884, 3885, 3886, 3887, 3888, 3889, 3890, 3891, 3892, 3893, 3894, 3895, 3896, 3897, 3898, 3899, 3900, 3901, 3902, 3903, 3904, 3905, 3906, 3907, 3908, 3909, 3910, 3911, 3912, 3913, 3914, 3915, 3916, 3917, 3918, 3919, 3920, 3921, 3922, 3923, 3924, 3925, 3926, 3927, 3928, 3929, 3930, 3931, 3932, 3933, 3934, 3935, 3936, 3937, 3938, 3939, 3940, 3941, 3942, 3943, 3944, 3945, 3946, 3947, 3948, 3949, 3950, 3951, 3952, 3953, 3954, 3955, 3956, 3957, 3958, 3959, 3960, 3961, 3962, 3963, 3964, 3965, 3966, 3967, 3968, 3969, 3970, 3971, 3972, 3973, 3974, 3975, 3976, 3977, 3978, 3979, 3980, 3981, 3982, 3983, 3984, 3985, 3986, 3987, 3988, 3989, 3990, 3991, 3992, 3993, 3994, 3995, 3996, 3997, 3998, 3999, 4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009, 4010, 4011, 4012, 4013, 4014, 4015, 4016, 4017, 4018, 4019, 4020, 4021, 4022, 4023, 4024, 4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 4034, 4035, 4036, 4037, 4038, 4039, 4040, 4041, 4042, 4043, 4044, 4045, 4046, 4047, 4048, 4049, 4050, 4051, 4052, 4053, 4054, 4055, 4056, 4057, 4059, 4060, 4061, 4062, 4063, 4064, 4065, 4066, 4067, 4068, 4069, 4070, 4071, 4072, 4073, 4074, 4075, 4076, 4077, 4078, 4079, 4080, 4081, 4082, 4083, 4084, 4085, 4086, 4087, 4088, 4089, 4090, 4091, 4092, 4093, 4094, 4095, 4096, 4097, 4098, 4099, 4100, 4101, 4102, 4103, 4104, 4105, 4106, 4107, 4108, 4109, 4110, 4111, 4112, 4113, 4114, 4115, 4116, 4117, 4118, 4119, 4120, 4121, 4122, 4123, 4124, 4125, 4126, 4127, 4128, 4129, 4130, 4131, 4132, 4133, 4134, 4135, 4136, 4137, 4138, 4139, 4140, 4141, 4142, 4143, 4144, 4145, 4146, 4147, 4148, 4149, 4150, 4151, 4152, 4153, 4154, 4155, 4156, 4157, 4158, 4159, 4160, 4161, 4162, 4163, 4164, 4165, 4166, 4167, 4168, 4169, 4170, 4171, 4172, 4173, 4174, 4175, 4176, 4177, 4178, 4179, 4180, 4181, 4182, 4183, 4184, 4185, 4186, 4187, 4188, 4189, 4190, 4191, 4192, 4193, 4194, 4195, 4196, 4197, 4198, 4199, 4200, 4201, 4202, 4203, 4204, 4205, 4206, 4207, 4208, 4209, 4210, 4211, 4212, 4213, 4214, 4215, 4216, 4217, 4218, 4219, 4220, 4221, 4222, 4223, 4224, 4225, 4226, 4227, 4228, 4229, 4230, 4231, 4232, 4233, 4234, 4235, 4236, 4237, 4238, 4239, 4240, 4241, 4242, 4243, 4244, 4245, 4246, 4247, 4248, 4249, 4250, 4251, 4252, 4253, 4254, 4255, 4256, 4257, 4258, 4259, 4260, 4261, 4262, 4263, 4264, 4265, 4266, 4267, 4268, 4269, 4270, 4271, 4272, 4273, 4274, 4275, 4276, 4277, 4278, 4279, 4280, 4281, 4282, 4283, 4284, 4285, 4286, 4287, 4288, 4289, 4290, 4291, 4292, 4293, 4294, 4295, 4296, 4297, 4298, 4299, 4300, 4301, 4302, 4303, 4304, 4305, 4306, 4307, 4308, 4309, 4310, 4311, 4312, 4313, 4314, 4315, 4316, 4317, 4318, 4319, 4320, 4321, 4322, 4323, 4324, 4325, 4326, 4327, 4328, 4329, 4330, 4331, 4332, 4333, 4334, 4335, 4336, 4337, 4338, 4339, 4340, 4341, 4342, 4343, 4344, 4345, 4346, 4347, 4348, 4349, 4350, 4351, 4352, 4353, 4354, 4355, 4356, 4357, 4358, 4359, 4360, 4361, 4362, 4363, 4364, 4365, 4366, 4367, 4368, 4369, 4370, 4371, 4372, 4373, 4374, 4375, 4376, 4377, 4378, 4379, 4380, 4381, 4382, 4383, 4384, 4385, 4386, 4387, 4388, 4389, 4390, 4391, 4392, 4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400, 4401, 4402, 4403, 4404, 4405, 4406, 4407, 4408, 4409, 4410, 4411, 4412, 4413, 4414, 4415, 4416, 4417, 4418, 4419, 4420, 4421, 4422, 4423, 4424, 4425, 4426, 4427, 4428, 4429, 4430, 4431, 4432, 4433, 4434, 4435, 4436, 4437, 4438, 4439, 4440, 4441, 4442, 4443, 4444, 4445, 4446, 4447, 4448, 4449, 4450, 4451, 4452, 4453, 4454, 4455, 4456, 4457, 4458, 4459, 4460, 4461, 4462, 4463, 4464, 4465, 4466, 4467, 4468, 4469, 4470, 4471, 4472, 4473, 4474, 4475, 4476, 4477, 4478, 4479, 4480, 4481, 4482, 4483, 4484, 4485, 4486, 4487, 4488, 4489, 4490, 4491, 4492, 4493, 4494, 4495, 4496, 4497, 4498, 4499, 4500, 4501, 4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514, 4515, 4516, 4517, 4518, 4519, 4520, 4521, 4522, 4523, 4524, 4525, 4526, 4527, 4528, 4529, 4530, 4531, 4532, 4533, 4534, 4535, 4536, 4537, 4538, 4539, 4540, 4541, 4542, 4543, 4544, 4545, 4546, 4547, 4548, 4549, 4550, 4551, 4552, 4553, 4554, 4555, 4556, 4557, 4558, 4559, 4560, 4561, 4562, 4563, 4564, 4565, 4566, 4567, 4568, 4569, 4570, 4571, 4572, 4573, 4574, 4575, 4576, 4577, 4578, 4579, 4580, 4581, 4582, 4583, 4584, 4585, 4586, 4587, 4588, 4589, 4590, 4591, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599, 4600, 4601, 4602, 4603, 4604, 4605, 4606, 4607, 4608, 4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620, 4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4632, 4633, 4634, 4635, 4636, 4637, 4638, 4639, 4640, 4641, 4642, 4643, 4644, 4645, 4646, 4647, 4648, 4649, 4650, 4651, 4652, 4653, 4654, 4655, 4656, 4657, 4658, 4659, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4667, 4668, 4669, 4670, 4671, 4672, 4673, 4674, 4675, 4676, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4684, 4685, 4686, 4687, 4688, 4689, 4690, 4691, 4692, 4693, 4694, 4695, 4696, 4697, 4698, 4699, 4700, 4701, 4702, 4703, 4704, 4705, 4706, 4707, 4708, 4709, 4710, 4711, 4712, 4713, 4714, 4715, 4716, 4717, 4718, 4719, 4720, 4721, 4722, 4723, 4724, 4725, 4726, 4727, 4728, 4729, 4730, 4731, 4732, 4733, 4734, 4735, 4736, 4737, 4738, 4739, 4740, 4741, 4742, 4743, 4744, 4745, 4746, 4747, 4748, 4749, 4750, 4751, 4752, 4753, 4754, 4755, 4756, 4757, 4758, 4759, 4760, 4761, 4762, 4763, 4764, 4765, 4766, 4767, 4768, 4769, 4770, 4771, 4772, 4773, 4774, 4775, 4776, 4777, 4778, 4779, 4780, 4781, 4782, 4783, 4784, 4785, 4786, 4787, 4788, 4789, 4790, 4791, 4792, 4793, 4794, 4795, 4796, 4797, 4798, 4799, 4800, 4801, 4802, 4803, 4804, 4805, 4806, 4807, 4808, 4809, 4810, 4811, 4812, 4813, 4814, 4815, 4816, 4817, 4818, 4819, 4820, 4821, 4822, 4823, 4824, 4825, 4826, 4827, 4828, 4829, 4830, 4831, 4832, 4833, 4834, 4835, 4836, 4837, 4838, 4839, 4840, 4841, 4842, 4843, 4844, 4845, 4846, 4847, 4848, 4849, 4850, 4851, 4852, 4853, 4854, 4855, 4856, 4857, 4858, 4859, 4860, 4861, 4862, 4863, 4864, 4865, 4866, 4867, 4868, 4869, 4871, 4872, 4873, 4874, 4875, 4876, 4877, 4878, 4879, 4880, 4881, 4882, 4883, 4884, 4885, 4886, 4887, 4888, 4889, 4890, 4891, 4892, 4893, 4894, 4895, 4896, 4897, 4898, 4899, 4900, 4901, 4902, 4903, 4904, 4905, 4906, 4907, 4908, 4909, 4910, 4911, 4912, 4913, 4914, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4922, 4923, 4924, 4925, 4926, 4927, 4928, 4929, 4930, 4931, 4932, 4933, 4934, 4935, 4936, 4937, 4938, 4939, 4940, 4941, 4942, 4943, 4944, 4945, 4946, 4947, 4948, 4949, 4950, 4951, 4952, 4953, 4954, 4955, 4956, 4957, 4958, 4959, 4960, 4961, 4962, 4963, 4964, 4965, 4966, 4967, 4968, 4969, 4970, 4971, 4972, 4973, 4974, 4975, 4976, 4977, 4978, 4979, 4980, 4981, 4982, 4983, 4984, 4985, 4986, 4987, 4988, 4989, 4990, 4991, 4992, 4993, 4994, 4995, 4996, 4997, 4998, 4999, 5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 5011, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020, 5021, 5022, 5023, 5024, 5025, 5026, 5027, 5028, 5029, 5030, 5031, 5032, 5033, 5034, 5035, 5036, 5037, 5038, 5039, 5040, 5041, 5042, 5043, 5044, 5045, 5046, 5047, 5048, 5049, 5050, 5051, 5052, 5053, 5054, 5055, 5056, 5057, 5058, 5059, 5060, 5061, 5062, 5063, 5064, 5065, 5066, 5067, 5068, 5069, 5070, 5071, 5072, 5073, 5074, 5075, 5076, 5077, 5078, 5079, 5080, 5081, 5082, 5083, 5084, 5085, 5086, 5087, 5088, 5089, 5090, 5091, 5092, 5093, 5094, 5095, 5096, 5097, 5098, 5099, 5100, 5101, 5102, 5103, 5104, 5105, 5106, 5107, 5108, 5109, 5110, 5111, 5112, 5113, 5114, 5115, 5116, 5117, 5118, 5119, 5120, 5121, 5122, 5123, 5124, 5125, 5126, 5127, 5128, 5129, 5130, 5131, 5132, 5133, 5134, 5135, 5136, 5137, 5138, 5139, 5140, 5141, 5142, 5143, 5144, 5145, 5146, 5147, 5148, 5149, 5150, 5151, 5152, 5153, 5154, 5155, 5156, 5157, 5158, 5159, 5160, 5161, 5162, 5163, 5164, 5165, 5166, 5167, 5168, 5169, 5170, 5171, 5172, 5173, 5174, 5175, 5176, 5177, 5178, 5179, 5180, 5181, 5182, 5183, 5184, 5185, 5186, 5187, 5188, 5189, 5190, 5191, 5192, 5193, 5194, 5195, 5196, 5197, 5198, 5199, 5200, 5201, 5202, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5211, 5212, 5213, 5214, 5215, 5216, 5217, 5218, 5219, 5220, 5221, 5222, 5223, 5224, 5225, 5226, 5227, 5228, 5229, 5230, 5231, 5232, 5233, 5234, 5235, 5236, 5237, 5238, 5239, 5240, 5241, 5242, 5243, 5244, 5245, 5246, 5247, 5248, 5249, 5250, 5251, 5252, 5253, 5254, 5255, 5256, 5257, 5258, 5259, 5260, 5261, 5262, 5263, 5264, 5265, 5266, 5267, 5268, 5269, 5270, 5271, 5272, 5273, 5274, 5275, 5276, 5277, 5278, 5279, 5280, 5281, 5282, 5283, 5284, 5285, 5286, 5287, 5288, 5289, 5290, 5291, 5292, 5293, 5294, 5295, 5296, 5297, 5298, 5299, 5300, 5301, 5302, 5303, 5304, 5305, 5306, 5307, 5308, 5309, 5310, 5311, 5312, 5313, 5314, 5315, 5316, 5317, 5318, 5319, 5320, 5321, 5322, 5323, 5324, 5325, 5326, 5327, 5328, 5329, 5330, 5331, 5332, 5333, 5334, 5335, 5336, 5337, 5338, 5339, 5340, 5341, 5342, 5343, 5344, 5345, 5346, 5347, 5348, 5349, 5350, 5351, 5352, 5353, 5354, 5355, 5356, 5357, 5358, 5359, 5360, 5361, 5362, 5363, 5364, 5365, 5366, 5367, 5368] (13 captions vs 5331 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do always after pouring jello powder ? Is it Option A: pour water, Option B: pour juice, Option C: pour jello powder, Option D: pour alcohol. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. pour water<br>B. pour juice<br>C. pour jello powder<br>D. pour alcohol<br><br>
<b>Sub #1 answer:</b> A<br>
<b>Sub #5B answer:</b> D<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_mN3Tus1ellQ.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_mN3Tus1ellQ.mp4">ct_mN3Tus1ellQ.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_mN3Tus1ellQ.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_mN3Tus1ellQ.mp4'</code><br>
<b>Duration:</b> 180.6s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_pours_jello_powder&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_pours_jello_powder&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_pours_jello_powder&quot;)` captures the temporal relation; propositions (person pours jello powder) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    2,
    3,
    4,
    5,
    9,
    13,
    14,
    36,
    37,
    38,
    39,
    41,
    43,
    44,
    48,
    49,
    50,
    51,
    53,
    54,
    59,
    60,
    61,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    77,
    87,
    88,
    89,
    97,
    98,
    99,
    100,
    101,
    102,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
    111,
    112,
    113,
    114,
    115,
    116,
    118,
    119,
    120,
    121,
    122,
    123,
    124,
    125,
    166,
    171
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[60, 5130]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+0, +8]; nsvs_start_sec=2.002002002002002; nsvs_end_sec=171.17117117117118</code><br>
<b>Target-ID explanation:</b> Since the question asks what happened &#x27;always after&#x27; pouring jello powder, we focus on padding after the interval end. Therefore, no padding is added to the start of the interval, while a larger padding is added at the end to capture events occurring afterward.<br>
<b>Final FOI:</b> <code>[60, 5369]</code>
</td>
<td>
<b>Answer text:</b> D<br>
<b>Raw answer:</b> <code>D</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person pours jello powder [0]</b> (frame 2, 0.067s): A person is seen pouring jello powder from a container into a bowl. The action is focused and deliberate.</li>
<li><b>NSVS detect: person pours jello powder [1]</b> (frame 3, 0.1s): The person continues to pour jello powder into the bowl. The powder is visibly flowing from the container.</li>
<li><b>NSVS detect: person pours jello powder [2]</b> (frame 4, 0.133s): The pouring action is still in progress, with more jello powder entering the bowl. The person&#x27;s hand is steady.</li>
<li><b>NSVS detect: person pours jello powder [3]</b> (frame 5, 0.167s): The person is nearing the end of pouring the jello powder into the bowl. The container is tilted significantly.</li>
<li><b>NSVS detect: person pours jello powder [4]</b> (frame 9, 0.3s): The person has finished pouring the jello powder and is now holding the empty container. The bowl is filled with jello powder.</li>
<li><b>FOI start</b> (frame 60, 2.002s): No description returned for this frame.</li>
<li><b>10% of video</b> (frame 541, 18.051s): No description returned for this frame.</li>
<li><b>25% of video</b> (frame 1353, 45.145s): No description returned for this frame.</li>
<li><b>50% of video</b> (frame 2706, 90.29s): No description returned for this frame.</li>
<li><b>FOI midpoint</b> (frame 2714, 90.557s): No description returned for this frame.</li>
<li><b>75% of video</b> (frame 4058, 135.402s): No description returned for this frame.</li>
<li><b>90% of video</b> (frame 4870, 162.496s): No description returned for this frame.</li>
<li><b>FOI end</b> (frame 5369, 179.146s): No description returned for this frame.</li>
</ul>
</details>

## 22. QID 1865 - ct / >180s / unknown

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Inspect whether frame captions support the `unknown` relation among [&#x27;person flips bread&#x27;].
- Caption_coverage: partial: missing caption frames [47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2110, 2111, 2112, 2113, 2114, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2150, 2151, 2152, 2153, 2154, 2155, 2156, 2157, 2158, 2159, 2160, 2161, 2162, 2163, 2164, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2176, 2177, 2178, 2179, 2180, 2181, 2182, 2183, 2184, 2185, 2186, 2187, 2188, 2189, 2190, 2191, 2192, 2193, 2194, 2195, 2196, 2197, 2198, 2199, 2200, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219, 2220, 2221, 2222, 2223, 2224, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2233, 2234, 2235, 2236, 2237, 2238, 2239, 2240, 2241, 2242, 2243, 2244, 2245, 2246, 2247, 2248, 2249, 2250, 2251, 2252, 2253, 2254, 2255, 2256, 2257, 2258, 2259, 2260, 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2275, 2276, 2277, 2278, 2279, 2280, 2281, 2282, 2283, 2284, 2285, 2286, 2287, 2288, 2289, 2290, 2291, 2292, 2293, 2294, 2295, 2296, 2297, 2298, 2299, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361, 2362, 2363, 2364, 2365, 2366, 2367, 2368, 2369, 2370, 2371, 2372, 2373, 2374, 2375, 2376, 2377, 2378, 2379, 2380, 2381, 2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421, 2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2442, 2443, 2444, 2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470, 2471, 2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481, 2482, 2483, 2484, 2485, 2486, 2487, 2488, 2489, 2490, 2491, 2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 2509, 2510, 2511, 2512, 2513, 2514, 2515, 2516, 2517, 2518, 2519, 2520, 2521, 2522, 2523, 2524, 2525, 2526, 2527, 2528, 2529, 2530, 2531, 2532, 2533, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2541, 2542, 2543, 2544, 2545, 2546, 2547, 2548, 2549, 2550, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601, 2602, 2603, 2604, 2605, 2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621, 2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641, 2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651, 2652, 2653, 2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661, 2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701, 2702, 2703, 2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 2714, 2715, 2716, 2717, 2718, 2719, 2720, 2721, 2722, 2723, 2724, 2725, 2726, 2727, 2728, 2729, 2730, 2731, 2732, 2733, 2734, 2735, 2736, 2737, 2738, 2739, 2740, 2741, 2742, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2759, 2760, 2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769, 2770, 2771, 2772, 2773, 2774, 2775, 2776, 2777, 2778, 2779, 2780, 2781, 2782, 2783, 2784, 2785, 2786, 2787, 2788, 2789, 2790, 2791, 2792, 2793, 2794, 2795, 2796, 2797, 2798, 2799, 2800, 2801, 2802, 2803, 2804, 2805, 2806, 2807, 2808, 2809, 2810, 2811, 2812, 2813, 2814, 2815, 2816, 2817, 2818, 2819, 2820, 2821, 2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829, 2830, 2831, 2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841, 2842, 2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851, 2852, 2853, 2854, 2855, 2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2905, 2906, 2907, 2908, 2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919, 2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 2972, 2973, 2974, 2975, 2976, 2977, 2978, 2979, 2980, 2981, 2982, 2983, 2984, 2985, 2986, 2987, 2988, 2989, 2990, 2991, 2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151, 3152, 3153, 3154, 3155, 3156, 3157, 3158, 3159, 3160, 3161, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3349, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388, 3389, 3390, 3391, 3392, 3393, 3394, 3395, 3396, 3397, 3398, 3399, 3400, 3401, 3402, 3403, 3404, 3405, 3406, 3407, 3408, 3409, 3411, 3412, 3413, 3414, 3415, 3416, 3417, 3418, 3419, 3420, 3421, 3422, 3423, 3424, 3425, 3426, 3427, 3428, 3429, 3430, 3431, 3432, 3433, 3434, 3435, 3436, 3437, 3438, 3439, 3440, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533, 3534, 3535, 3536, 3537, 3538, 3539, 3540, 3541, 3542, 3543, 3544, 3545, 3546, 3547, 3548, 3549, 3550, 3551, 3552, 3553, 3554, 3555, 3556, 3557, 3558, 3559, 3560, 3561, 3562, 3563, 3564, 3565, 3566, 3567, 3568, 3569, 3570, 3571, 3572, 3573, 3574, 3575, 3576, 3577, 3578, 3579, 3580, 3581, 3582, 3583, 3584, 3585, 3586, 3587, 3588, 3589, 3590, 3591, 3592, 3593, 3594, 3595, 3596, 3597, 3598, 3599, 3600, 3601] (13 captions vs 3560 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> Does the person eventually flip bread ?<br><br>
<b>Candidates:</b><br>Yes<br>No<br><br>
<b>Sub #1 answer:</b> No<br>
<b>Sub #5B answer:</b> Yes<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_x-7J315MKY0.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_x-7J315MKY0.mp4">ct_x-7J315MKY0.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_x-7J315MKY0.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_x-7J315MKY0.mp4'</code><br>
<b>Duration:</b> 181.9s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_flips_bread&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_flips_bread&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_flips_bread&quot;)` captures the temporal relation; propositions (person flips bread) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    4,
    5,
    17,
    60,
    102,
    104,
    125,
    129,
    131,
    140,
    144,
    148
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[96, 3552]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+2, +2]; nsvs_start_sec=3.84; nsvs_end_sec=142.08</code><br>
<b>Target-ID explanation:</b> The question asks about the eventual flipping of bread, which implies observing the action within its context, without specific before or after detail preferences. Therefore, a modest padding of 2 seconds on both sides is appropriate to capture the action and immediate context.<br>
<b>Final FOI:</b> <code>[46, 3602]</code>
</td>
<td>
<b>Answer text:</b> Yes<br>
<b>Raw answer:</b> <code>Yes</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person flips bread [0]</b> (frame 4, 0.16s): A person is seen holding a piece of bread above a tray. The bread is positioned near other items on the tray.</li>
<li><b>NSVS detect: person flips bread [1]</b> (frame 5, 0.2s): The person continues to hold the bread, preparing to flip it. The tray remains in the same position with the bread visible.</li>
<li><b>NSVS detect: person flips bread [2]</b> (frame 17, 0.68s): The person is now in the process of flipping the bread. The tray is still visible with the bread in focus.</li>
<li><b>FOI start</b> (frame 46, 1.84s): The scene transitions, showing the tray with bread. The person is not currently visible in this frame.</li>
<li><b>NSVS detect: person flips bread [3]</b> (frame 60, 2.4s): The person is actively flipping the bread again. The tray is still in view, showcasing the bread&#x27;s position.</li>
<li><b>NSVS detect: person flips bread [4]</b> (frame 102, 4.08s): The person has successfully flipped the bread onto the tray. The bread is now positioned differently on the tray.</li>
<li><b>10% of video</b> (frame 455, 18.2s): The video shows a wider view of the tray with multiple pieces of bread. The person is not visible in this frame.</li>
<li><b>25% of video</b> (frame 1137, 45.48s): The tray is filled with several pieces of bread. The scene captures the bread without any visible actions.</li>
<li><b>FOI midpoint</b> (frame 1824, 72.96s): The video shows a close-up of the bread on the tray. The person is not present in this frame.</li>
<li><b>50% of video</b> (frame 2274, 90.96s): The tray is still filled with bread, showcasing its texture. No actions are occurring in this frame.</li>
<li><b>75% of video</b> (frame 3410, 136.4s): The video captures a plate of finished bread items. The person is not visible in this frame.</li>
<li><b>FOI end</b> (frame 3602, 144.08s): The final frame shows a close-up of the finished bread. The person is absent from this scene.</li>
<li><b>90% of video</b> (frame 4092, 163.68s): The video displays a plate of bread with strawberries in the background. The person is not present in this frame.</li>
</ul>
</details>

## 23. QID 1632 - ct / >180s / after

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Confirm `event B` occurs only after `person withdraws wheel` completes.
- Caption_coverage: partial: missing caption frames [31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 159, 160, 161, 162, 163, 164, 165, 166, 167, 169, 170, 171, 172, 173, 174, 175, 176, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2110, 2111, 2112, 2113, 2114, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2150, 2151, 2152, 2153, 2154, 2155, 2156, 2157, 2158, 2159, 2160, 2161, 2162, 2163, 2164, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2176, 2177, 2178, 2179, 2180, 2181, 2182, 2183, 2184, 2185, 2186, 2187, 2188, 2189, 2190, 2191, 2192, 2193, 2194, 2195, 2196, 2197, 2198, 2199, 2200, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219, 2220, 2221, 2222, 2223, 2224, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2233, 2234, 2235, 2236, 2237, 2238, 2239, 2240, 2241, 2242, 2243, 2244, 2245, 2246, 2247, 2248, 2249, 2250, 2251, 2252, 2253, 2254, 2255, 2256, 2257, 2258, 2259, 2260, 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280, 2281, 2282, 2283, 2284, 2285, 2286, 2287, 2288, 2289, 2290, 2291, 2292, 2293, 2294, 2295, 2296, 2297, 2298, 2299, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361, 2362, 2363, 2364, 2365, 2366, 2367, 2368, 2369, 2370, 2371, 2372, 2373, 2374, 2375, 2376, 2377, 2378, 2379, 2380, 2381, 2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421, 2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2442, 2443, 2444, 2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470, 2471, 2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481, 2482, 2483, 2484, 2485, 2486, 2487, 2488, 2489, 2490, 2491, 2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 2509, 2510, 2511, 2512, 2513, 2514, 2515, 2516, 2517, 2518, 2519, 2520, 2521, 2522, 2523, 2524, 2525, 2526, 2527, 2528, 2529, 2530, 2531, 2532, 2533, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2541, 2542, 2543, 2544, 2545, 2546, 2547, 2548, 2549, 2550, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601, 2602, 2603, 2604, 2605, 2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621, 2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641, 2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651, 2652, 2653, 2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661, 2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701, 2702, 2703, 2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 2714, 2715, 2716, 2717, 2718, 2719, 2720, 2721, 2722, 2723, 2724, 2725, 2726, 2727, 2728, 2729, 2730, 2731, 2732, 2733, 2734, 2735, 2736, 2737, 2738, 2739, 2740, 2741, 2742, 2743, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2759, 2760, 2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769, 2770, 2771, 2772, 2773, 2774, 2775, 2776, 2777, 2778, 2779, 2780, 2781, 2782, 2783, 2784, 2785, 2786, 2787, 2788, 2789, 2790, 2791, 2792, 2793, 2794, 2795, 2796, 2797, 2798, 2799, 2800, 2801, 2802, 2803, 2804, 2805, 2806, 2807, 2808, 2809, 2810, 2811, 2812, 2813, 2814, 2815, 2816, 2817, 2818, 2819, 2820, 2821, 2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829, 2830, 2831, 2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841, 2842, 2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851, 2852, 2853, 2854, 2855, 2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2906, 2907, 2908, 2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919, 2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 2972, 2973, 2974, 2975, 2976, 2977, 2978, 2979, 2980, 2981, 2982, 2983, 2984, 2985, 2986, 2987, 2988, 2989, 2990, 2991, 2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151, 3152, 3153, 3154, 3155, 3156, 3157, 3158, 3159, 3160, 3161, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3349, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388, 3389, 3390, 3391, 3392, 3393, 3394, 3395, 3396, 3397, 3398, 3399, 3400, 3401, 3402, 3403, 3404, 3405, 3406, 3407, 3408, 3409, 3410, 3411, 3412, 3413, 3414, 3415, 3416, 3417, 3418, 3419, 3420, 3421, 3422, 3423, 3424, 3425, 3426, 3427, 3428, 3429, 3430, 3431, 3432, 3433, 3434, 3435, 3436, 3437, 3438, 3439, 3440, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533, 3534, 3535, 3536, 3537, 3538, 3539, 3540, 3541, 3542, 3543, 3544, 3545, 3546, 3547, 3548, 3549, 3550, 3551, 3552, 3553, 3554, 3555, 3556, 3557, 3558, 3559, 3560, 3561, 3562, 3563, 3564, 3565, 3566, 3567, 3568, 3569, 3570, 3571, 3572, 3573, 3574, 3575, 3576, 3577, 3578, 3579, 3580, 3581, 3582, 3583, 3584, 3585, 3586, 3587, 3588, 3589, 3590, 3591, 3592, 3593, 3594, 3595, 3596, 3597, 3598, 3599, 3600, 3601, 3602, 3603, 3604, 3605, 3606, 3607, 3608, 3609, 3610, 3611, 3612, 3613, 3614, 3615, 3616, 3617, 3618, 3619, 3620, 3621, 3622, 3623, 3624, 3625, 3626, 3627, 3628, 3629, 3630, 3631, 3632, 3633, 3634, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 3643, 3644, 3645, 3646, 3647, 3648, 3649, 3650, 3651, 3652, 3653, 3654, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662, 3663, 3664, 3665, 3666, 3667, 3668, 3669, 3670, 3671, 3672, 3673, 3674, 3675, 3676, 3677, 3678, 3679, 3680, 3681, 3682, 3683, 3684, 3685, 3686, 3687, 3688, 3689, 3690, 3691, 3692, 3693, 3694, 3695, 3696, 3697, 3698, 3699, 3700, 3701, 3702, 3703, 3704, 3705, 3706, 3707, 3708, 3709, 3710, 3711, 3712, 3713, 3714, 3715, 3716, 3717, 3718, 3719, 3720, 3721, 3722, 3723, 3724, 3725, 3726, 3727, 3728, 3729, 3730, 3731, 3732, 3733, 3734, 3735, 3736, 3737, 3738, 3739, 3740, 3741, 3742, 3743, 3744, 3745, 3746, 3747, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3766, 3767, 3768, 3769, 3770, 3771, 3772, 3773, 3774, 3775, 3776, 3777, 3778, 3779, 3780, 3781, 3782, 3783, 3784, 3785, 3786, 3787, 3788, 3789, 3790, 3791, 3792, 3793, 3794, 3795, 3796, 3797, 3798, 3799, 3800, 3801, 3802, 3803, 3804, 3805, 3806, 3807, 3808, 3809, 3810, 3811, 3812, 3813, 3814, 3815, 3816, 3817, 3818, 3819, 3820, 3821, 3822, 3823, 3824, 3825, 3826, 3827, 3828, 3829, 3830, 3831, 3832, 3833, 3834, 3835, 3836, 3837, 3838, 3839, 3840, 3841, 3842, 3843, 3844, 3845, 3846, 3847, 3848, 3849, 3850, 3851, 3852, 3853, 3854, 3855, 3856, 3857, 3858, 3859, 3860, 3861, 3862, 3863, 3864, 3865, 3866, 3867, 3868, 3869, 3870, 3871, 3872, 3873, 3874, 3875, 3876, 3877, 3878, 3879, 3880, 3881, 3882, 3883, 3884, 3885, 3886, 3887, 3888, 3889, 3890, 3891, 3892, 3893, 3894, 3895, 3896, 3897, 3898, 3899, 3900, 3901, 3902, 3903, 3904, 3905, 3906, 3907, 3908, 3909, 3910, 3911, 3912, 3913, 3914, 3915, 3916, 3917, 3918, 3919, 3920, 3921, 3922, 3923, 3924, 3925, 3926, 3927, 3928, 3929, 3930, 3931, 3932, 3933, 3934, 3935, 3936, 3937, 3938, 3939, 3940, 3941, 3942, 3943, 3944, 3945, 3946, 3947, 3948, 3949, 3950, 3951, 3952, 3953, 3954, 3955, 3956, 3957, 3958, 3959, 3960, 3961, 3962, 3963, 3964, 3965, 3966, 3967, 3968, 3969, 3970, 3971, 3972, 3973, 3974, 3975, 3976, 3977, 3978, 3979, 3980, 3981, 3982, 3983, 3984, 3985, 3986, 3987, 3988, 3989, 3990, 3991, 3992, 3993, 3994, 3995, 3996, 3997, 3998, 3999, 4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009, 4010, 4011, 4012, 4013, 4014, 4015, 4016, 4017, 4018, 4019, 4020, 4021, 4022, 4023, 4024, 4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 4034, 4035, 4036, 4037, 4038, 4039, 4040, 4041, 4042, 4043, 4044, 4045, 4046, 4047, 4048, 4049, 4050, 4051, 4052, 4053, 4054, 4055, 4056, 4057, 4058, 4059, 4060, 4061, 4062, 4063, 4064, 4065, 4066, 4067, 4068, 4069, 4070, 4071, 4072, 4073, 4074, 4075, 4076, 4077, 4078, 4079, 4080, 4081, 4082, 4083, 4084, 4085, 4086, 4087, 4088, 4089, 4090, 4091, 4092, 4093, 4094, 4095, 4096, 4097, 4098, 4099, 4100, 4101, 4102, 4103, 4104, 4105, 4106, 4107, 4108, 4109, 4110, 4111, 4112, 4113, 4114, 4115, 4116, 4117, 4118, 4119, 4120, 4121, 4122, 4123, 4124, 4125, 4126, 4127, 4128, 4129, 4130, 4131, 4132, 4133, 4134, 4135, 4136, 4137, 4138, 4139, 4140, 4141, 4142, 4143, 4144, 4145, 4146, 4147, 4148, 4149, 4150, 4151, 4152, 4153, 4154, 4155, 4156, 4157, 4158, 4159, 4160, 4161, 4162, 4163, 4164, 4165, 4166, 4167, 4168, 4169, 4170, 4171, 4172, 4173, 4174, 4175, 4176, 4177, 4178, 4179, 4180, 4181, 4182, 4183, 4184, 4185, 4186, 4187, 4188, 4189, 4190, 4191, 4192, 4193, 4194, 4195, 4196, 4197, 4198, 4199, 4200, 4201, 4202, 4203, 4204, 4205, 4206, 4207, 4208, 4209, 4210, 4211, 4212, 4213, 4214, 4215, 4216, 4217, 4218, 4219, 4220, 4221, 4222, 4223, 4224, 4225, 4226, 4227, 4228, 4229, 4230, 4231, 4232, 4233, 4234, 4235, 4236, 4237, 4238, 4239, 4240, 4241, 4242, 4243, 4244, 4245, 4246, 4247, 4248, 4249, 4250, 4251, 4252, 4253, 4254, 4255, 4256, 4257, 4258, 4259, 4260, 4261, 4262, 4263, 4264, 4265, 4266, 4267, 4268, 4269, 4270, 4271, 4272, 4273, 4274, 4275, 4276, 4277, 4278, 4279, 4280, 4281, 4282, 4283, 4284, 4285, 4286, 4287, 4288, 4289, 4290, 4291, 4292, 4293, 4294, 4295, 4296, 4297, 4298, 4299, 4300, 4301, 4302, 4303, 4304, 4305, 4306, 4307, 4308, 4309, 4310, 4311, 4312, 4313, 4314, 4315, 4316, 4317, 4318, 4319, 4320, 4321, 4322, 4323, 4324, 4325, 4326, 4327, 4328, 4329, 4330, 4331, 4332, 4333, 4334, 4335, 4336, 4337, 4338, 4339, 4340, 4341, 4342, 4343, 4344, 4345, 4346, 4347, 4348, 4349, 4350, 4351, 4352, 4353, 4354, 4355, 4356, 4357, 4359, 4360, 4361, 4362, 4363, 4364, 4365, 4366, 4367, 4368, 4369, 4370, 4371, 4372, 4373, 4374, 4375, 4376, 4377, 4378, 4379, 4380, 4381, 4382, 4383, 4384, 4385, 4386, 4387, 4388, 4389, 4390, 4391, 4392, 4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400, 4401, 4402, 4403, 4404, 4405, 4406, 4407, 4408, 4409, 4410, 4411, 4412, 4413, 4414, 4415, 4416, 4417, 4418, 4419, 4420, 4421, 4422, 4423, 4424, 4425, 4426, 4427, 4428, 4429, 4430, 4431, 4432, 4433, 4434, 4435, 4436, 4437, 4438, 4439, 4440, 4441, 4442, 4443, 4444, 4445, 4446, 4447, 4448, 4449, 4450, 4451, 4452, 4453, 4454, 4455, 4456, 4457, 4458, 4459, 4460, 4461, 4462, 4463, 4464, 4465, 4466, 4467, 4468, 4469, 4470, 4471, 4472, 4473, 4474, 4475, 4476, 4477, 4478, 4479, 4480, 4481, 4482, 4483, 4484, 4485, 4486, 4487, 4488, 4489, 4490, 4491, 4492, 4493, 4494, 4495, 4496, 4497, 4498, 4499, 4500, 4501, 4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514, 4515, 4516, 4517, 4518, 4519, 4520, 4521, 4522, 4523, 4524, 4525, 4526, 4527, 4528, 4529, 4530, 4531, 4532, 4533, 4534, 4535, 4536, 4537, 4538, 4539, 4540, 4541, 4542, 4543, 4544, 4545, 4546, 4547, 4548, 4549, 4550, 4551, 4552, 4553, 4554, 4555, 4556, 4557, 4558, 4559, 4560, 4561, 4562, 4563, 4564, 4565, 4566, 4567, 4568, 4569, 4570, 4571, 4572, 4573, 4574, 4575, 4576, 4577, 4578, 4579, 4580, 4581, 4582, 4583, 4584, 4585, 4586, 4587, 4588, 4589, 4590, 4591, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599, 4600, 4601, 4602, 4603, 4604, 4605, 4606, 4607, 4608, 4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620, 4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4632, 4633, 4634, 4635, 4636, 4637, 4638, 4639, 4640, 4641, 4642, 4643, 4644, 4645, 4646, 4647, 4648, 4649, 4650, 4651, 4652, 4653, 4654, 4655, 4656, 4657, 4658, 4659, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4667, 4668, 4669, 4670, 4671, 4672, 4673, 4674, 4675, 4676, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4684, 4685, 4686, 4687, 4688, 4689, 4690, 4691, 4692, 4693, 4694, 4695, 4696, 4697, 4698, 4699, 4700, 4701, 4702, 4703, 4704, 4705, 4706, 4707, 4708, 4709, 4710, 4711, 4712, 4713, 4714, 4715, 4716, 4717, 4718, 4719, 4720, 4721, 4722, 4723, 4724, 4725, 4726, 4727, 4728, 4729, 4730, 4731, 4732, 4733, 4734, 4735, 4736, 4737, 4738, 4739, 4740, 4741, 4742, 4743, 4744, 4745, 4746, 4747, 4748, 4749, 4750, 4751, 4752, 4753, 4754, 4755, 4756, 4757, 4758, 4759, 4760, 4761, 4762, 4763, 4764, 4765, 4766, 4767, 4768, 4769, 4770, 4771, 4772, 4773, 4774, 4775, 4776, 4777, 4778, 4779, 4780, 4781, 4782, 4783, 4784, 4785, 4786, 4787, 4788, 4789, 4790, 4791, 4792, 4793, 4794, 4795, 4796, 4797, 4798, 4799, 4800, 4801, 4802, 4803, 4804, 4805, 4806, 4807, 4808, 4809, 4810, 4811, 4812, 4813, 4814, 4815, 4816, 4817, 4818, 4819, 4820, 4821, 4822, 4823, 4824, 4825, 4826, 4827, 4828, 4829, 4830, 4831, 4832, 4833, 4834, 4835, 4836, 4837, 4838, 4839, 4840, 4841, 4842, 4843, 4844, 4845, 4846, 4847, 4848, 4849, 4850, 4851, 4852, 4853, 4854, 4855, 4856, 4857, 4858, 4859, 4860, 4861, 4862, 4863, 4864, 4865, 4866, 4867, 4868, 4869, 4870, 4871, 4872, 4873, 4874, 4875, 4876, 4877, 4878, 4879, 4880, 4881, 4882, 4883, 4884, 4885, 4886, 4887, 4888, 4889, 4890, 4891, 4892, 4893, 4894, 4895, 4896, 4897, 4898, 4899, 4900, 4901, 4902, 4903, 4904, 4905, 4906, 4907, 4908, 4909, 4910, 4911, 4912, 4913, 4914, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4922, 4923, 4924, 4925, 4926, 4927, 4928, 4929, 4930, 4931, 4932, 4933, 4934, 4935, 4936, 4937, 4938, 4939, 4940, 4941, 4942, 4943, 4944, 4945, 4946, 4947, 4948, 4949, 4950, 4951, 4952, 4953, 4954, 4955, 4956, 4957, 4958, 4959, 4960, 4961, 4962, 4963, 4964, 4965, 4966, 4967, 4968, 4969, 4970, 4971, 4972, 4973, 4974, 4975, 4976, 4977, 4978, 4979, 4980, 4981, 4982, 4983, 4984, 4985, 4986, 4987, 4988, 4989, 4990, 4991, 4992, 4993, 4994, 4995, 4996, 4997, 4998, 4999, 5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 5011, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020, 5021, 5022, 5023, 5024, 5025, 5026, 5027, 5028, 5029, 5030, 5031, 5032, 5033, 5034, 5035, 5036, 5037, 5038, 5039, 5040, 5041, 5042, 5043, 5044, 5045, 5046, 5047, 5048, 5049, 5050, 5051, 5052, 5053, 5054, 5055, 5056, 5057, 5058, 5059, 5060, 5061, 5062, 5063, 5064, 5065, 5066, 5067, 5068, 5069, 5070, 5071, 5072, 5073, 5074, 5075, 5076, 5077, 5078, 5079, 5080, 5081, 5082, 5083, 5084, 5085, 5086, 5087, 5088, 5089, 5090, 5091, 5092, 5093, 5094, 5095, 5096, 5097, 5098, 5099, 5100, 5101, 5102, 5103, 5104, 5105, 5106, 5107, 5108, 5109, 5110, 5111, 5112, 5113, 5114, 5115, 5116, 5117, 5118, 5119, 5120, 5121, 5122, 5123, 5124, 5125, 5126, 5127, 5128, 5129, 5130, 5131, 5132, 5133, 5134, 5135, 5136, 5137, 5138, 5139, 5140, 5141, 5142, 5143, 5144, 5145, 5146, 5147, 5148, 5149, 5150, 5151, 5152, 5153, 5154, 5155, 5156, 5157, 5158, 5159, 5160, 5161, 5162, 5163, 5164, 5165, 5166, 5167, 5168, 5169, 5170, 5171, 5172, 5173, 5174, 5175, 5176, 5177, 5178, 5179, 5180, 5181, 5182, 5183, 5184, 5185, 5186, 5187, 5188, 5189, 5190, 5191, 5192, 5193, 5194, 5195, 5196, 5197, 5198, 5199, 5200, 5201, 5202, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5211, 5212, 5213, 5214, 5215, 5216, 5217, 5218, 5219, 5220, 5221, 5222, 5223, 5224, 5225, 5226, 5227, 5228, 5230, 5231, 5232, 5233, 5234, 5235, 5236, 5237, 5238, 5239, 5240, 5241, 5242, 5243, 5244, 5245, 5246, 5247, 5248, 5249, 5250, 5251, 5252, 5253, 5254, 5255, 5256, 5257, 5258, 5259, 5260, 5261, 5262, 5263, 5264, 5265, 5266, 5267, 5268, 5269, 5270, 5271, 5272, 5273, 5274, 5275, 5276, 5277, 5278, 5279, 5280, 5281, 5282, 5283, 5284, 5285, 5286, 5287, 5288, 5289, 5290, 5291, 5292, 5293, 5294, 5295, 5296, 5297, 5298, 5299, 5300, 5301, 5302, 5303, 5304, 5305, 5306, 5307, 5308, 5309, 5310, 5311, 5312, 5313, 5314, 5315, 5316, 5317, 5318, 5319, 5320, 5321, 5322, 5323, 5324, 5325, 5326, 5327, 5328, 5329, 5330, 5331, 5332, 5333, 5334, 5335, 5336, 5337, 5338, 5339, 5340, 5341, 5342, 5343, 5344, 5345, 5346, 5347, 5348, 5349, 5350, 5351, 5352, 5353, 5354, 5355, 5356, 5357, 5358, 5359, 5360, 5361, 5362, 5363, 5364, 5365, 5366, 5367, 5368, 5369, 5370, 5371, 5372, 5373, 5374, 5375, 5376, 5377, 5378, 5379, 5380, 5381, 5382, 5383, 5384, 5385, 5386, 5387, 5388, 5389, 5390, 5391, 5392, 5393, 5394, 5395, 5396, 5397, 5398, 5399, 5400, 5401, 5402, 5403, 5404, 5405, 5406, 5407, 5408, 5409, 5410, 5411, 5412, 5413, 5414, 5415, 5416, 5417, 5418, 5419, 5420, 5421, 5422, 5423, 5424, 5425, 5426, 5427, 5428, 5429, 5430, 5431, 5432, 5433, 5434, 5435, 5436, 5437, 5438, 5439, 5440, 5441, 5442, 5443, 5444, 5445, 5446, 5447, 5448, 5449, 5450, 5451, 5452, 5453, 5454, 5455, 5456, 5457, 5458] (13 captions vs 5432 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do after withdrawing wheel ? Is it Option A: unscrew wheel, Option B: start loose, Option C: tight wheel, Option D: withdraw wheel. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. unscrew wheel<br>B. start loose<br>C. tight wheel<br>D. withdraw wheel<br><br>
<b>Sub #1 answer:</b> C<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_goqPhR4gW4Y.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_goqPhR4gW4Y.mp4">ct_goqPhR4gW4Y.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_goqPhR4gW4Y.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_goqPhR4gW4Y.mp4'</code><br>
<b>Duration:</b> 193.9s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_withdraws_wheel&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_withdraws_wheel&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_withdraws_wheel&quot;)` captures the temporal relation; propositions (person withdraws wheel) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    1,
    29,
    158,
    168,
    177
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[30, 5310]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+0, +5]; nsvs_start_sec=1.0008311822405782; nsvs_end_sec=177.14711925658236</code><br>
<b>Target-ID explanation:</b> Since the question is about what happens after withdrawing the wheel, we apply a small padding before the interval end and a larger padding of 5 seconds after the interval end to ensure any relevant subsequent actions are captured.<br>
<b>Final FOI:</b> <code>[30, 5459]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code>A</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person withdraws wheel [0]</b> (frame 1, 0.033s): A person is seen near a vehicle&#x27;s wheel. The wheel appears to be in place.</li>
<li><b>NSVS detect: person withdraws wheel [1]</b> (frame 29, 0.967s): The person is still near the wheel, which remains attached to the vehicle. The scene shows no significant changes.</li>
<li><b>FOI start</b> (frame 30, 1.001s): The focus of interest begins as the person interacts with the wheel. The wheel is still visible and attached.</li>
<li><b>NSVS detect: person withdraws wheel [2]</b> (frame 158, 5.271s): The person is now using a tool on the wheel. The wheel is still mounted on the vehicle.</li>
<li><b>NSVS detect: person withdraws wheel [3]</b> (frame 168, 5.605s): The person continues to manipulate the tool on the wheel. The wheel remains in place.</li>
<li><b>NSVS detect: person withdraws wheel [4]</b> (frame 177, 5.905s): The person is still engaged with the wheel using the tool. The wheel has not been removed yet.</li>
<li><b>10% of video</b> (frame 581, 19.383s): The video shows a wider view of the scene. The wheel is still attached to the vehicle.</li>
<li><b>25% of video</b> (frame 1452, 48.44s): The scene captures the person still working on the wheel. The wheel remains in its original position.</li>
<li><b>FOI midpoint</b> (frame 2744, 91.543s): The focus of interest continues with the person near the wheel. The wheel is still not removed.</li>
<li><b>50% of video</b> (frame 2905, 96.914s): The video shows the person still interacting with the wheel. The wheel is still attached.</li>
<li><b>75% of video</b> (frame 4358, 145.387s): The scene shows the person still engaged with the wheel. The wheel has not been withdrawn yet.</li>
<li><b>90% of video</b> (frame 5229, 174.445s): The person is still working on the wheel. The wheel remains in place.</li>
<li><b>FOI end</b> (frame 5459, 182.118s): The focus of interest concludes with the person still near the wheel. The wheel is still attached to the vehicle.</li>
</ul>
</details>

## 24. QID 1942 - ct / >180s / before

**Tagging block (v3)**

- PULS_preliminary: pass
- Watch_for: Confirm `person adds meat` completes before `event B` begins.
- Caption_coverage: partial: missing caption frames [119, 120, 122, 123, 125, 131, 132, 135, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2110, 2111, 2112, 2113, 2114, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2150, 2151, 2152, 2153, 2154, 2155, 2156, 2157, 2158, 2159, 2160, 2161, 2162, 2163, 2164, 2165, 2166, 2167, 2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2176, 2177, 2178, 2179, 2180, 2181, 2182, 2183, 2184, 2185, 2186, 2187, 2188, 2189, 2190, 2191, 2192, 2193, 2194, 2195, 2196, 2197, 2198, 2199, 2200, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2210, 2211, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219, 2220, 2221, 2222, 2223, 2224, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2233, 2234, 2235, 2236, 2237, 2238, 2239, 2240, 2241, 2242, 2243, 2244, 2245, 2246, 2247, 2248, 2249, 2250, 2251, 2252, 2253, 2254, 2255, 2256, 2257, 2258, 2259, 2260, 2261, 2262, 2263, 2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272, 2273, 2274, 2275, 2276, 2277, 2278, 2279, 2280, 2281, 2282, 2283, 2284, 2285, 2286, 2287, 2288, 2289, 2290, 2291, 2292, 2293, 2294, 2295, 2296, 2297, 2298, 2299, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351, 2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361, 2362, 2363, 2364, 2365, 2366, 2367, 2368, 2369, 2370, 2371, 2372, 2373, 2374, 2375, 2376, 2377, 2378, 2379, 2380, 2381, 2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421, 2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2442, 2443, 2444, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461, 2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470, 2471, 2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481, 2482, 2483, 2484, 2485, 2486, 2487, 2488, 2489, 2490, 2491, 2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 2509, 2510, 2511, 2512, 2513, 2514, 2515, 2516, 2517, 2518, 2519, 2520, 2521, 2522, 2523, 2524, 2525, 2526, 2527, 2528, 2529, 2530, 2531, 2532, 2533, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2541, 2542, 2543, 2544, 2545, 2546, 2547, 2548, 2549, 2550, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2558, 2559, 2560, 2561, 2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571, 2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601, 2602, 2603, 2604, 2605, 2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621, 2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641, 2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651, 2652, 2653, 2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661, 2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701, 2702, 2703, 2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 2714, 2715, 2716, 2717, 2718, 2719, 2720, 2721, 2722, 2723, 2724, 2725, 2726, 2727, 2728, 2729, 2730, 2731, 2732, 2733, 2734, 2735, 2736, 2737, 2738, 2739, 2740, 2741, 2742, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2759, 2760, 2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769, 2770, 2771, 2772, 2773, 2774, 2775, 2776, 2777, 2778, 2779, 2780, 2781, 2782, 2783, 2784, 2785, 2786, 2787, 2788, 2789, 2790, 2791, 2792, 2793, 2794, 2795, 2796, 2797, 2798, 2799, 2800, 2801, 2802, 2803, 2804, 2805, 2806, 2807, 2808, 2809, 2810, 2811, 2812, 2813, 2814, 2815, 2816, 2817, 2818, 2819, 2820, 2821, 2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829, 2830, 2831, 2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841, 2842, 2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851, 2852, 2853, 2854, 2855, 2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2905, 2906, 2907, 2908, 2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 2972, 2973, 2974, 2975, 2976, 2977, 2978, 2979, 2980, 2981, 2982, 2983, 2984, 2985, 2986, 2987, 2988, 2989, 2990, 2991, 2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151, 3152, 3153, 3154, 3155, 3156, 3157, 3158, 3159, 3160, 3161, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3349, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388, 3389, 3390, 3391, 3392, 3393, 3394, 3395, 3396, 3397, 3398, 3399, 3400, 3401, 3402, 3403, 3404, 3405, 3406, 3407, 3408, 3409, 3410, 3411, 3412, 3413, 3414, 3415, 3416, 3417, 3418, 3419, 3420, 3421, 3422, 3423, 3424, 3425, 3426, 3427, 3428, 3429, 3430, 3431, 3432, 3433, 3434, 3435, 3436, 3437, 3438, 3439, 3440, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533, 3534, 3535, 3536, 3537, 3538, 3539, 3540, 3541, 3542, 3543, 3544, 3545, 3546, 3547, 3548, 3549, 3550, 3551, 3552, 3553, 3554, 3555, 3556, 3557, 3558, 3559, 3560, 3561, 3562, 3563, 3564, 3565, 3566, 3567, 3568, 3569, 3570, 3571, 3572, 3573, 3574, 3575, 3576, 3577, 3578, 3579, 3580, 3581, 3582, 3583, 3584, 3585, 3586, 3587, 3588, 3589, 3590, 3591, 3592, 3593, 3594, 3595, 3596, 3597, 3598, 3599, 3600, 3601, 3602, 3603, 3604, 3605, 3606, 3607, 3608, 3609, 3610, 3611, 3612, 3613, 3614, 3615, 3616, 3617, 3618, 3619, 3620, 3621, 3622, 3623, 3624, 3625, 3626, 3627, 3628, 3629, 3630, 3631, 3632, 3633, 3634, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 3643, 3644, 3645, 3646, 3647, 3648, 3649, 3650, 3651, 3652, 3653, 3654, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662, 3663, 3664, 3665, 3666, 3667, 3668, 3669, 3670, 3671, 3672, 3673, 3674, 3675, 3676, 3677, 3678, 3679, 3680, 3681, 3682, 3683, 3684, 3685, 3686, 3687, 3688, 3689, 3690, 3691, 3692, 3693, 3694, 3695, 3696, 3697, 3698, 3699, 3700, 3701, 3702, 3703, 3704, 3705, 3706, 3707, 3708, 3709, 3710, 3711, 3712, 3713, 3714, 3715, 3716, 3717, 3718, 3719, 3720, 3721, 3722, 3723, 3724, 3725, 3726, 3727, 3728, 3729, 3730, 3731, 3732, 3733, 3734, 3735, 3736, 3737, 3738, 3739, 3740, 3741, 3742, 3743, 3744, 3745, 3746, 3747, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3766, 3767, 3768, 3769, 3770, 3771, 3772, 3773, 3774, 3775, 3776, 3777, 3778, 3779, 3780, 3781, 3782, 3783, 3784, 3785, 3786, 3787, 3788, 3789, 3790, 3791, 3792, 3793, 3794, 3795, 3796, 3797, 3798, 3799, 3800, 3801, 3802, 3803, 3804, 3805, 3806, 3807, 3808, 3809, 3810, 3811, 3812, 3813, 3814, 3815, 3816, 3817, 3818, 3819, 3820, 3821, 3822, 3823, 3824, 3825, 3826, 3827, 3828, 3829, 3830, 3831, 3832, 3833, 3834, 3835, 3836, 3837, 3838, 3839, 3840, 3841, 3842, 3843, 3844, 3845, 3846, 3847, 3848, 3849, 3850, 3851, 3852, 3853, 3854, 3855, 3856, 3857, 3858, 3859, 3860, 3861, 3862, 3863, 3864, 3865, 3866, 3867, 3868, 3869, 3870, 3871, 3872, 3873, 3874, 3875, 3876, 3877, 3878, 3879, 3880, 3881, 3882, 3883, 3884, 3885, 3886, 3887, 3888, 3889, 3890, 3891, 3892, 3893, 3894, 3895, 3896, 3897, 3898, 3899, 3900, 3901, 3902, 3903, 3904, 3905, 3906, 3907, 3908, 3909, 3910, 3911, 3912, 3913, 3914, 3915, 3916, 3917, 3918, 3919, 3920, 3921, 3922, 3923, 3924, 3925, 3926, 3927, 3928, 3929, 3930, 3931, 3932, 3933, 3934, 3935, 3936, 3937, 3938, 3939, 3940, 3941, 3942, 3943, 3944, 3945, 3946, 3947, 3948, 3949, 3950, 3951, 3952, 3953, 3954, 3955, 3956, 3957, 3958, 3959, 3960, 3961, 3962, 3963, 3964, 3965, 3966, 3967, 3968, 3969, 3970, 3971, 3972, 3973, 3974, 3975, 3976, 3977, 3978, 3979, 3980, 3981, 3982, 3983, 3984, 3985, 3986, 3987, 3988, 3989, 3990, 3991, 3992, 3993, 3994, 3995, 3996, 3997, 3998, 3999, 4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009, 4010, 4011, 4012, 4013, 4014, 4015, 4016, 4017, 4018, 4019, 4020, 4021, 4022, 4023, 4024, 4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 4034, 4035, 4036, 4037, 4038, 4039, 4040, 4041, 4042, 4043, 4044, 4045, 4046, 4047, 4048, 4049, 4050, 4051, 4052, 4053, 4054, 4055, 4056, 4057, 4058, 4059, 4060, 4061, 4062, 4063, 4064, 4065, 4066, 4067, 4068, 4069, 4070, 4071, 4072, 4073, 4074, 4075, 4076, 4077, 4078, 4079, 4080, 4081, 4082, 4083, 4084, 4085, 4086, 4087, 4088, 4089, 4090, 4091, 4092, 4093, 4094, 4095, 4096, 4097, 4098, 4099, 4100, 4101, 4102, 4103, 4104, 4105, 4106, 4107, 4108] (13 captions vs 3342 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do before adding meat ? Is it Option A: add cheese, Option B: add lettuce, Option C: stir, Option D: add meat. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. add cheese<br>B. add lettuce<br>C. stir<br>D. add meat<br><br>
<b>Sub #1 answer:</b> B<br>
<b>Sub #5B answer:</b> C<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_Fsosc3B0Agw.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Fsosc3B0Agw.mp4">ct_Fsosc3B0Agw.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Fsosc3B0Agw.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_Fsosc3B0Agw.mp4'</code><br>
<b>Duration:</b> 195.2s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_adds_meat&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_adds_meat&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_adds_meat&quot;)` captures the temporal relation; propositions (person adds meat) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    36,
    51,
    115,
    116,
    118,
    119,
    120,
    122,
    123,
    125,
    131,
    132,
    135
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[1080, 4050]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+10, +2]; nsvs_start_sec=36.09987632449778; nsvs_end_sec=135.37453621686666</code><br>
<b>Target-ID explanation:</b> The question asks what happened before &#x27;adding meat,&#x27; so padding should be larger before the start of the interval capturing this event to ensure we capture sufficient context for actions leading up to it. A small padding after ensures any immediate aftermath is also considered.<br>
<b>Final FOI:</b> <code>[781, 4109]</code>
</td>
<td>
<b>Answer text:</b> C<br>
<b>Raw answer:</b> <code>C</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person adds meat [0]</b> (frame 36, 1.203s): A person is preparing food, holding a piece of meat above a dish. The dish appears to be a taco or similar food item.</li>
<li><b>NSVS detect: person adds meat [1]</b> (frame 51, 1.705s): The person is now placing the meat into the dish. The meat is visibly being added to the existing ingredients.</li>
<li><b>NSVS detect: person adds meat [2]</b> (frame 115, 3.844s): The person continues to add more meat to the dish. The dish is filled with various ingredients, including vegetables.</li>
<li><b>NSVS detect: person adds meat [3]</b> (frame 116, 3.877s): The person is still focused on adding meat to the dish. The action appears deliberate and careful.</li>
<li><b>NSVS detect: person adds meat [4]</b> (frame 118, 3.944s): The meat is now fully integrated into the dish. The person is adjusting the placement of the ingredients.</li>
<li><b>10% of video</b> (frame 584, 19.521s): The video shows a wider view of the preparation area. Various ingredients are visible, but the focus is not on the person.</li>
<li><b>FOI start</b> (frame 781, 26.106s): The video transitions to a new segment, showing a different angle of the preparation. The person is not currently visible.</li>
<li><b>25% of video</b> (frame 1460, 48.802s): The video captures a broader scene of the cooking process. Ingredients are laid out, but no specific actions are occurring.</li>
<li><b>FOI midpoint</b> (frame 2445, 81.726s): The video shows a pause in the action, focusing on the completed dish. The person is not present in this frame.</li>
<li><b>50% of video</b> (frame 2920, 97.603s): The video highlights the final presentation of the dish. The ingredients are arranged attractively, but no actions are visible.</li>
<li><b>FOI end</b> (frame 4109, 137.347s): The video concludes with a close-up of the finished dish. The person is absent, and the focus is solely on the food.</li>
<li><b>75% of video</b> (frame 4380, 146.405s): The video shows a distant view of the preparation area. The person is not visible, and the focus is on the surrounding environment.</li>
<li><b>90% of video</b> (frame 5256, 175.686s): The video captures the end of the cooking process. The dish is displayed prominently, with no actions occurring.</li>
</ul>
</details>

## 25. QID 796 - ct / >180s / until

**Tagging block (v3)**

- PULS_preliminary: flag: until question but spec has neither U nor G operator
- Watch_for: Confirm `event B` holds until `person adds lettuce` occurs (then may stop).
- Caption_coverage: partial: missing caption frames [4381, 4382, 4383, 4384, 4385, 4386, 4387, 4388, 4389, 4390, 4391, 4392, 4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400, 4401, 4402, 4403, 4404, 4405, 4406, 4407, 4408, 4409, 4410, 4411, 4412, 4413, 4414, 4415, 4416, 4417, 4418, 4419, 4420, 4421, 4422, 4423, 4424, 4425, 4426, 4427, 4428, 4429, 4430, 4431, 4432, 4433, 4434, 4435, 4436, 4437, 4438, 4439, 4440, 4441, 4442, 4443, 4444, 4445, 4446, 4447, 4448, 4449, 4450, 4451, 4452, 4453, 4454, 4455, 4456, 4457, 4458, 4459, 4460, 4461, 4462, 4463, 4464, 4465, 4466, 4467, 4468, 4469, 4470, 4471, 4472, 4473, 4474, 4475, 4476, 4477, 4478, 4479, 4480, 4481, 4482, 4483, 4484, 4485, 4486, 4487, 4488, 4489, 4490, 4491, 4492, 4493, 4494, 4495, 4496, 4497, 4498, 4499, 4500, 4501, 4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514, 4515, 4516, 4517, 4518, 4519, 4520, 4521, 4522, 4523, 4524, 4525, 4526, 4527, 4528, 4529, 4531, 4532, 4533, 4534, 4535, 4536, 4537, 4538, 4539, 4540, 4541, 4542, 4543, 4544, 4545, 4546, 4547, 4548, 4549, 4550, 4551, 4552, 4553, 4554, 4555, 4556, 4557, 4558, 4559, 4560, 4561, 4562, 4563, 4564, 4565, 4566, 4567, 4568, 4569, 4570, 4571, 4572, 4573, 4574, 4575, 4576, 4577, 4578, 4579, 4580, 4581, 4582, 4583, 4584, 4585, 4586, 4587, 4588, 4589, 4590, 4591, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599, 4600, 4601, 4602, 4603, 4604, 4605, 4606, 4607, 4608, 4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620, 4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4633, 4634, 4635, 4636, 4637, 4638, 4639, 4640, 4641, 4642, 4643, 4644, 4645, 4646, 4647, 4648, 4649, 4650, 4651, 4652, 4653, 4654, 4655, 4656, 4657, 4658, 4659, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4667, 4668, 4669, 4670, 4671, 4672, 4673, 4674, 4675, 4676, 4677, 4678, 4679] (10 captions vs 303 target frames)
- Caption_question_mismatch: pass
- NSVS_bypassed: partial: 1/2 propositions have zero detections
- Benchmark_confound: no

Human confirmation:

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
- Caption_ok: [ ]
- Notes:

<table>
<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>
<tr>
<td>
<b>Question:</b> The following is a multiple choice question with four possible answer choices: A, B, C, D. What did the person do until added lettuce ? Is it Option A: add cheese, Option B: add tortilla, Option C: add tomato, Option D: add lettuce. Reply with the chosen option in one character.<br><br>
<b>Candidates:</b><br>A. add cheese<br>B. add tortilla<br>C. add tomato<br>D. add lettuce<br><br>
<b>Sub #1 answer:</b> C<br>
<b>Sub #5B answer:</b> A<br>
<b>Ground truth:</b> <i>not available locally</i><br>
<b>Video:</b> ct_S3TWfylBt08.mp4<br><b>Open:</b> <a href="file:///mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_S3TWfylBt08.mp4">ct_S3TWfylBt08.mp4</a><br><b>Path:</b> <code>/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_S3TWfylBt08.mp4</code><br><b>Play:</b> <code>ffplay -autoexit '/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/ct_S3TWfylBt08.mp4'</code><br>
<b>Duration:</b> 205.9s
</td>
<td>
<b>Propositions:</b><br><code>[&quot;person_adds_lettuce&quot;]</code><br><br>
<b>TL spec:</b><br><code>(&quot;person_adds_lettuce&quot;)</code><br><br>
<b>Does this spec encode the question?</b><br>Stub: check whether `(&quot;person_adds_lettuce&quot;)` captures the temporal relation; propositions (person adds lettuce) look concrete enough to audit visually.
</td>
<td>
<b>Raw nsvs.indices (per proposition):</b><pre><code>[
  [
    149,
    154
  ],
  []
]</code></pre>
<b>Raw Storm interval:</b> <code>[4470, 4620]</code><br>
<b>Target-ID padding:</b> <code>frame_window=[+3, +2]; nsvs_start_sec=149.0; nsvs_end_sec=154.0</code><br>
<b>Target-ID explanation:</b> Given that the question refers to events leading up to when the person adds lettuce, it is classified as a &#x27;before&#x27; question. We must focus on capturing actions preceding the reference action &#x27;adds lettuce&#x27;. Thus, larger padding is applied before the identified frame window&#x27;s start to include previous context, with smaller padding following the interval&#x27;s end.<br>
<b>Final FOI:</b> <code>[4380, 4680]</code>
</td>
<td>
<b>Answer text:</b> A<br>
<b>Raw answer:</b> <code>A</code><br>
<b>Reasoning:</b> <i>not persisted: Sub #5B answerer emits final answer only.</i><br>
<b>Frames sampled by answerer:</b> 16
</td>
</tr>
</table>

<details open>
<summary><b>Frame Description Block</b></summary>
<ul>
<li><b>NSVS detect: person adds lettuce [0]</b> (frame 149, 4.967s): The person is holding a bag of lettuce. They are in the process of adding the lettuce to a plate.</li>
<li><b>NSVS detect: person adds lettuce [1]</b> (frame 154, 5.133s): The person continues to add lettuce from the bag onto the plate. The action appears deliberate and focused.</li>
<li><b>10% of video</b> (frame 618, 20.6s): The scene shows a table with various food items, including a plate with some food. The person is not visible in this frame.</li>
<li><b>25% of video</b> (frame 1544, 51.467s): The person is seen preparing food on the counter. Several bowls and plates are visible, indicating a meal is being assembled.</li>
<li><b>50% of video</b> (frame 3088, 102.933s): The person is actively mixing ingredients in a bowl. The kitchen environment is cluttered with various food items.</li>
<li><b>FOI start</b> (frame 4380, 146.0s): The person is reaching for a container on the counter. The focus is on their hand and the container.</li>
<li><b>FOI midpoint</b> (frame 4530, 151.0s): The person is pouring a substance from the container into a bowl. The action suggests they are adding an ingredient.</li>
<li><b>75% of video</b> (frame 4632, 154.4s): The person is seen stirring the contents of a bowl. The kitchen remains busy with various food items around.</li>
<li><b>FOI end</b> (frame 4680, 156.0s): The person is finishing up their preparation. The focus is on the bowl and the ingredients being mixed.</li>
<li><b>90% of video</b> (frame 5558, 185.267s): The scene shows the completed dish on the table. The person is not visible, but the food looks ready to serve.</li>
</ul>
</details>

