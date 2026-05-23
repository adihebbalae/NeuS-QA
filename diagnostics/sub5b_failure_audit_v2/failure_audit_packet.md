# Sub #1/Sub #5B Disagreement Audit Packet (v2)

Purpose: a 25-row, human-flippable slice of the disagreement set where Sub #1 and Sub #5B gave different answers.

> Important label caveat: EvalAI does not expose row-level ground truth locally. Disagreement rows are not conditioned on who was correct.

## Slice Balance

- Rows: 25
- Audit duration buckets: {'<10s': 10, '30-60s': 5, '60-180s': 5, '>180s': 5}
- Legacy length buckets: {'short': 10, 'medium': 8, 'long': 7}
- Source dataset: {'star': 6, 'agqa': 4, 'bf': 5, 'ct': 10}
- Operator family: {'after': 3, 'since': 2, 'always_before': 5, 'before': 3, 'in_turn_occurs': 2, 'unknown': 4, 'until': 3, 'always_after': 3}
- Nearest-midpoint proxy fills: 0
- Frame-description cache: `/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v2/failure_audit_frame_descriptions.json`
- Selected rows CSV: `/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_failure_audit_v2/selected_rows.csv`

## Reader Tally

After reviewing, tally unchecked boxes here:

- PULS_ok unchecked: ____ / 25
- NSVS_detect_ok unchecked: ____ / 25
- Storm_interval_ok unchecked: ____ / 25
- VQA_ok unchecked: ____ / 25

Use the tally as the decision signal: dominant `NSVS_detect_ok` failures point at visual grounding / InternVL; dominant `Storm_interval_ok` failures point at interval semantics / DAG-style logic.

Tagging criteria:

- PULS_ok: Does the spec encode the question's actual temporal relationship, and are propositions concrete enough to detect in frames?
- NSVS_detect_ok: For each proposition, do the detection indices land where the frame descriptions say that action is happening? If a visible proposition has zero detections, mark broken.
- Storm_interval_ok: Given the detection arrays, is the returned raw interval the right interval for the spec semantics?
- VQA_ok: Given the final FOI and frame descriptions, does the answer follow from visible evidence?

## 1. QID 1809 - star / <10s / after

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

**Tagging block**

- PULS_ok: [ ]
- NSVS_detect_ok: [ ]
- Storm_interval_ok: [ ]
- VQA_ok: [ ]
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

