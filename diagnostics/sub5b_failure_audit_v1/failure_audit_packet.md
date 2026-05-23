# Sub #1/Sub #5B Disagreement Audit Packet (duration-stratified v1)

Purpose: a 25-row audit slice of Sub #1 vs Sub #5B (fix2) disagreements, stratified 5 rows per video-duration bucket (<10s, 10-30s, 30-60s, 60-180s, >180s).

> Important label caveat: EvalAI does not expose row-level ground truth locally. Disagreement rows are not conditioned on who was correct.

## Slice Balance

- Rows: 25
- Audit duration buckets: {'<10s': 5, '10-30s': 5, '30-60s': 5, '60-180s': 5, '>180s': 5}
- Legacy length buckets: {'short': 10, 'medium': 8, 'long': 7}
- Source dataset: {'star': 6, 'agqa': 4, 'bf': 5, 'ct': 10}
- Operator family: {'after': 3, 'since': 2, 'always_before': 5, 'before': 3, 'in_turn_occurs': 2, 'unknown': 4, 'until': 3, 'always_after': 3}
- Nearest-midpoint proxy fills: 5
- Frame-description cache: `/home/ah66742/timelogic-data/outputs/diagnostics/sub5b_failure_audit_v1/failure_audit_frame_descriptions.json`
- Selected rows CSV: `/home/ah66742/timelogic-data/outputs/diagnostics/sub5b_failure_audit_v1/selected_rows.csv`

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
<b>Video:</b> star_1SLTT.mp4<br>
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
<li><b>frame 1</b> (frame 1, 0.04s): A person is holding a cup close to their mouth, appearing to drink from it. The background shows a living room with a table and various objects.</li>
<li><b>frame 3</b> (frame 3, 0.12s): The person is still holding the cup, looking down at it after drinking. The table is visible with some items scattered on it.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person is standing with the cup in hand, looking around the room. The table remains cluttered with various objects.</li>
<li><b>frame 10</b> (frame 10, 0.4s): The person is now facing away from the camera, with the cup still in hand. The table and surrounding furniture are clearly visible.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person is moving away from the table, still holding the cup. The background shows the same living room setting.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person is standing with the cup in hand, looking around the room. The table remains cluttered with various objects.</li>
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
<b>Video:</b> star_LG7WK.mp4<br>
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
<li><b>10% of video</b> (frame 2, 0.08s): The person is on the floor, rolling onto their back. They appear to be in a relaxed position.</li>
<li><b>25% of video</b> (frame 4, 0.16s): The person is now sitting up on the floor, with their legs bent. They are looking towards a box nearby.</li>
<li><b>50% of video</b> (frame 8, 0.32s): The person is facing a box, sitting with their legs crossed. They seem to be reaching towards the box.</li>
<li><b>75% of video</b> (frame 13, 0.52s): The person has grabbed a picture from the box. They are holding it in their hands while still seated.</li>
<li><b>90% of video</b> (frame 15, 0.6s): The person continues to hold the picture, examining it closely. They remain seated on the floor.</li>
<li><b>FOI midpoint</b> (frame 8, 0.32s): The person is facing a box, sitting with their legs crossed. They seem to be reaching towards the box.</li>
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
<b>Video:</b> agqa_DBT6E.mp4<br>
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
<li><b>10% of video</b> (frame 2, 0.08s): A person is bending down near a bag on the floor. The person is wearing a blue shirt and pink pants.</li>
<li><b>25% of video</b> (frame 6, 0.24s): The person is sitting on the floor next to the bag. The bag is open and the person is looking inside.</li>
<li><b>50% of video</b> (frame 12, 0.48s): The person is reaching into the bag with one hand. The bag is still open and the person appears focused.</li>
<li><b>75% of video</b> (frame 18, 0.72s): The person is now pulling out a laptop from the bag. The laptop is partially out and the person is seated.</li>
<li><b>90% of video</b> (frame 22, 0.88s): The person is opening the laptop while sitting on the floor. The laptop is positioned on the person&#x27;s lap.</li>
<li><b>FOI midpoint</b> (frame 12, 0.48s): The person is reaching into the bag with one hand. The bag is still open and the person appears focused.</li>
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
<b>Video:</b> agqa_SXFG6.mp4<br>
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
<li><b>frame 2</b> (frame 2, 0.08s): A person is sitting on a chair, holding a brown object close to their chest. The setting includes a table and a laptop in the background.</li>
<li><b>frame 6</b> (frame 6, 0.24s): The person continues to embrace the brown object while seated. The table and kitchen appliances are visible in the background.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person is still seated, maintaining their hold on the brown object. The table remains in the frame, with a laptop visible.</li>
<li><b>frame 19</b> (frame 19, 0.76s): The frame shows the table and a red object on the floor, with no visible person. The kitchen area is also visible in the background.</li>
<li><b>frame 22</b> (frame 22, 0.88s): The scene focuses on the table and the red object on the floor, with no person present. The kitchen appliances are still visible.</li>
<li><b>frame 12</b> (frame 12, 0.48s): The person is still seated, maintaining their hold on the brown object. The table remains in the frame, with a laptop visible.</li>
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
<b>Video:</b> star_X11CU.mp4<br>
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
<li><b>person_sits_at_a_table</b> (frame 3, 0.12s): A person is seated at a round table, engaged with items on the table. Another person stands nearby, facing away from the camera.</li>
<li><b>person_holds_a_dish</b> (frame 7, 0.28s): The seated person continues to interact with the table, while the standing person appears to be preparing to move. The table is cluttered with various items.</li>
<li><b>person_holds_some_food</b> (frame 14, 0.56s): A close-up shows a hand holding a bowl with food, indicating food preparation or consumption. The table is still visible with additional food items around.</li>
<li><b>person_sits_at_a_table</b> (frame 20, 0.8s): The seated person remains at the table, while the standing person is still in the same position. The environment shows a well-lit room with a window.</li>
<li><b>person_holds_a_dish</b> (frame 24, 0.96s): The seated person is now more focused on the items in front of them, with the standing person still nearby. The table continues to display various food items.</li>
<li><b>person_holds_some_food</b> (frame 13, 0.52s): A hand is seen holding a bowl of food, suggesting active consumption. The table is cluttered with food and drink items.</li>
</ul>
</details>

## 6. QID 489 - agqa / 10-30s / after

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
<b>Video:</b> agqa_KZS5M.mp4<br>
<b>Duration:</b> 2.8s<br><b>Selection note:</b> <i>proxy fill for empty 10-30s bucket (actual duration 2.8s)</i>
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
<li><b>frame 7</b> (frame 7, 0.28s): A person is stepping through a doorway with one foot. They are positioned sideways, leaning slightly against the door frame.</li>
<li><b>frame 17</b> (frame 17, 0.68s): The person is walking away from the doorway, moving towards a staircase. Their body is turned slightly to the left as they continue forward.</li>
<li><b>frame 34</b> (frame 34, 1.36s): The person is in mid-stride, moving across the room. They appear to be reaching out with one arm.</li>
<li><b>frame 52</b> (frame 52, 2.08s): The person is standing still, facing a table with some items on it. They are holding something in their hand.</li>
<li><b>frame 62</b> (frame 62, 2.48s): The person is bending down towards the table, appearing to pick something up. Their body is angled forward as they reach.</li>
<li><b>frame 34</b> (frame 34, 1.36s): The person is in mid-stride, moving across the room. They appear to be reaching out with one arm.</li>
</ul>
</details>

## 7. QID 601 - star / 10-30s / always_before

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
<b>Video:</b> star_FUT86.mp4<br>
<b>Duration:</b> 2.8s<br><b>Selection note:</b> <i>proxy fill for empty 10-30s bucket (actual duration 2.8s)</i>
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
<li><b>10% of video</b> (frame 7, 0.28s): A person is sitting in a chair, holding a black object in their hands. The table in front has various items, including a pink toy and a book.</li>
<li><b>25% of video</b> (frame 17, 0.68s): The person is still seated, now holding the black object closer to their face. The background shows a cluttered table with more items.</li>
<li><b>50% of video</b> (frame 34, 1.36s): Another person is sitting in a different chair, holding a phone in one hand. A plate with food is visible on the table in front of them.</li>
<li><b>75% of video</b> (frame 52, 2.08s): The same person is now eating something, with a piece of food in their hand. The table remains cluttered with various items.</li>
<li><b>90% of video</b> (frame 62, 2.48s): The person is still seated, looking at the table with food items. The background shows a similar setting with a different arrangement.</li>
<li><b>FOI midpoint</b> (frame 24, 0.96s): The first person is still holding the black object, appearing to focus on it. The table is filled with various items, including a pink toy.</li>
</ul>
</details>

## 8. QID 682 - star / 10-30s / always_before

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
<b>Video:</b> star_YIG5G.mp4<br>
<b>Duration:</b> 2.8s<br><b>Selection note:</b> <i>proxy fill for empty 10-30s bucket (actual duration 2.8s)</i>
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
<li><b>frame 7</b> (frame 7, 0.28s): A person is sitting on a couch, looking towards another person. The room has a few decorative items and a fish tank in the background.</li>
<li><b>frame 17</b> (frame 17, 0.68s): A person is standing and holding a red object while looking at the seated person. The seated person appears to be engaged in conversation.</li>
<li><b>frame 34</b> (frame 34, 1.36s): The standing person is closer to the seated person, still holding the red object. The seated person is now looking at the object being held.</li>
<li><b>frame 52</b> (frame 52, 2.08s): The standing person is now holding a different object, possibly a dish, while the seated person continues to observe. The room remains unchanged with the same furniture.</li>
<li><b>frame 62</b> (frame 62, 2.48s): The standing person is still holding the object, and the seated person is now holding a different item. Both individuals are engaged in a conversation.</li>
<li><b>frame 34</b> (frame 34, 1.36s): The standing person is closer to the seated person, still holding the red object. The seated person is now looking at the object being held.</li>
</ul>
</details>

## 9. QID 34 - star / 10-30s / unknown

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
<b>Video:</b> star_WPU76.mp4<br>
<b>Duration:</b> 3.0s<br><b>Selection note:</b> <i>proxy fill for empty 10-30s bucket (actual duration 3.0s)</i>
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
<li><b>frame 7</b> (frame 7, 0.28s): A person stands in a room wearing a blue shirt and black pants. They are holding a bottle in one hand while their other hand is resting on their hip.</li>
<li><b>frame 18</b> (frame 18, 0.72s): The person is seen from behind, walking towards a kitchen area. There are bags of clothes on the floor nearby.</li>
<li><b>frame 37</b> (frame 37, 1.48s): The person is bending down to pick up a pile of clothes from the floor. The clothes are colorful and spread out on a mat.</li>
<li><b>frame 56</b> (frame 56, 2.24s): The person is standing upright, holding a piece of clothing in one hand. They appear to be preparing to move or place the clothing somewhere.</li>
<li><b>frame 67</b> (frame 67, 2.68s): The person is lifting a laundry basket off the floor. The basket is filled with clothes and is positioned next to a pile of clothes.</li>
<li><b>FOI midpoint</b> (frame 37, 1.48s): The person is bending down to pick up a pile of clothes from the floor. The clothes are colorful and spread out on a mat.</li>
</ul>
</details>

## 10. QID 262 - agqa / 10-30s / since

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
<b>Video:</b> agqa_ME4YL.mp4<br>
<b>Duration:</b> 3.1s<br><b>Selection note:</b> <i>proxy fill for empty 10-30s bucket (actual duration 3.1s)</i>
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
<li><b>frame 8</b> (frame 8, 0.32s): A person stands in a kitchen, holding a blanket and a piece of clothing. The kitchen has wooden cabinets and a stove in the background.</li>
<li><b>frame 19</b> (frame 19, 0.76s): The person is now lifting the blanket higher while still holding the clothing. The kitchen remains visible with the same layout.</li>
<li><b>frame 38</b> (frame 38, 1.52s): The person is holding the blanket and clothing in front of them, appearing to prepare for an action. The kitchen&#x27;s features are consistent with previous frames.</li>
<li><b>frame 58</b> (frame 58, 2.32s): The person walks away from the stove, still holding the blanket and clothing. The kitchen&#x27;s arrangement is unchanged.</li>
<li><b>frame 69</b> (frame 69, 2.76s): The person is now at the counter, placing the blanket and clothing down. The kitchen environment continues to show the same elements.</li>
<li><b>frame 38</b> (frame 38, 1.52s): The person is holding the blanket and clothing in front of them, appearing to prepare for an action. The kitchen&#x27;s features are consistent with previous frames.</li>
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
<b>Video:</b> bf_P35_webcam02_P35_milk.mp4<br>
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
<li><b>10% of video</b> (frame 58, 3.867s): A person is standing in a kitchen near a table. They are facing the camera with a cup on the table.</li>
<li><b>25% of video</b> (frame 144, 9.6s): The person is reaching towards a carton of milk on the table. The cup remains in the same position.</li>
<li><b>50% of video</b> (frame 288, 19.2s): The person is holding a container, possibly for scooping. They are positioned close to the cup on the table.</li>
<li><b>75% of video</b> (frame 432, 28.8s): The person is stirring something in the cup with a spoon. The kitchen environment is visible in the background.</li>
<li><b>90% of video</b> (frame 518, 34.533s): The person is walking away from the table, leaving the cup behind. The kitchen area is cluttered with various items.</li>
<li><b>FOI midpoint</b> (frame 194, 12.933s): The person is pouring something from a container into the cup. The carton of milk is still on the table.</li>
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
<b>Video:</b> bf_P47_cam01_P47_cereals.mp4<br>
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
<li><b>10% of video</b> (frame 67, 4.467s): A person is standing at a kitchen counter with a coffee machine in the background. There is a bowl and a small cup on the counter.</li>
<li><b>25% of video</b> (frame 168, 11.2s): The person is holding a box and appears to be preparing to pour its contents. The bowl is still on the counter, and the coffee machine remains visible.</li>
<li><b>50% of video</b> (frame 337, 22.467s): The person is pouring cereal from the box into the bowl. The kitchen counter is cluttered with a small cup and the box of cereal.</li>
<li><b>75% of video</b> (frame 506, 33.733s): The person is holding a spoon and appears to be mixing the contents of the bowl. The coffee machine and other items are still present on the counter.</li>
<li><b>90% of video</b> (frame 607, 40.467s): The person is still at the counter, holding a spoon and looking at the bowl. The box of cereal is positioned nearby.</li>
<li><b>FOI midpoint</b> (frame 352, 23.467s): The person continues to pour cereal into the bowl from the box. The kitchen setup includes a coffee machine and a small cup on the counter.</li>
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
<b>Video:</b> bf_P23_webcam01_P23_tea.mp4<br>
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
<li><b>10% of video</b> (frame 71, 4.733s): A kitchen countertop is visible with a carton and a mug. A person is seen in the background, moving towards a door.</li>
<li><b>25% of video</b> (frame 178, 11.867s): A person in a blue sweater is holding a small packet while standing at the countertop. The mug is placed on the counter, and the background shows the kitchen.</li>
<li><b>50% of video</b> (frame 357, 23.8s): The person in the blue sweater is still at the counter, with the packet now on the countertop. The background shows the person from earlier still moving.</li>
<li><b>75% of video</b> (frame 536, 35.733s): The person is now holding a kettle above the mug on the counter. The kettle is positioned to pour, indicating an action about to take place.</li>
<li><b>90% of video</b> (frame 643, 42.867s): The kettle is actively pouring water into the mug on the counter. The person is focused on the action of pouring.</li>
<li><b>FOI midpoint</b> (frame 420, 28.0s): The person is still at the counter, with the kettle now in hand. The mug remains in place, indicating preparation for pouring.</li>
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
<b>Video:</b> ct_qs2eKOubSYY.mp4<br>
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
<li><b>10% of video</b> (frame 116, 4.829s): A woman is speaking directly to the camera, likely explaining a recipe. She has a friendly expression and is wearing an apron.</li>
<li><b>25% of video</b> (frame 291, 12.115s): A close-up of a box of gelatin powder is shown, with instructions visible on the packaging. The text indicates how to prepare the gelatin.</li>
<li><b>50% of video</b> (frame 582, 24.23s): A measuring cup filled with a pink liquid is shown on a countertop. A hand is seen pouring something into the cup.</li>
<li><b>75% of video</b> (frame 874, 36.386s): Several small cups filled with different colored gelatin are arranged on a tray. A hand reaches for one of the cups.</li>
<li><b>90% of video</b> (frame 1048, 43.63s): A close-up of a pot on the stove shows a dark mixture being stirred with a wooden spoon. The mixture appears thick and glossy.</li>
<li><b>FOI midpoint</b> (frame 648, 26.978s): The camera focuses on the measuring cup again, showing the liquid inside. The liquid is being stirred with a spoon.</li>
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
<b>Video:</b> bf_P53_cam02_P53_cereals.mp4<br>
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
<li><b>10% of video</b> (frame 85, 5.673s): A person is holding a box and appears to be opening it. The kitchen counter is visible with various items in the background.</li>
<li><b>25% of video</b> (frame 212, 14.15s): The person continues to manipulate the box, possibly extracting its contents. The kitchen setting remains consistent with previous frame.</li>
<li><b>50% of video</b> (frame 424, 28.3s): The person is now holding a bowl and appears to be preparing to add something to it. Various kitchen items are still visible on the counter.</li>
<li><b>75% of video</b> (frame 635, 42.383s): The person is reaching for a can on the counter, indicating a transition in their actions. The bowl remains in the foreground.</li>
<li><b>90% of video</b> (frame 762, 50.86s): The person is using a spoon to scoop something from a can into the bowl. The kitchen environment continues to show various utensils and containers.</li>
<li><b>FOI midpoint</b> (frame 480, 32.038s): The person is preparing to add contents to the bowl, with a focus on their hand movements. The kitchen counter is cluttered with items.</li>
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
<b>Video:</b> ct_rUo6VC9HxJ8.mp4<br>
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
<li><b>10% of video</b> (frame 216, 7.2s): The video shows a coffee shop window with the name &#x27;THIRD RAIL COFFEE&#x27; visible. People can be seen outside the shop, and a car is parked nearby.</li>
<li><b>25% of video</b> (frame 541, 18.033s): A close-up of a latte art design on a coffee cup is displayed. The cup is held by a person, showcasing intricate patterns made with milk.</li>
<li><b>50% of video</b> (frame 1082, 36.067s): A person is holding a cup of espresso in one hand and a milk pitcher in the other. The setting appears to be a coffee preparation area.</li>
<li><b>75% of video</b> (frame 1624, 54.133s): The person is pouring steamed milk from the pitcher into the cup of espresso. The milk is creating a design as it mixes with the coffee.</li>
<li><b>90% of video</b> (frame 1948, 64.933s): The person is holding the cup of coffee with latte art and the milk pitcher in the other hand. The background shows coffee-making equipment.</li>
<li><b>FOI midpoint</b> (frame 930, 31.0s): The person is preparing to pour milk into a cup of espresso. The cup is placed on a counter, and the milk pitcher is raised.</li>
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
<b>Video:</b> ct_Jp1U6Gb1DxM.mp4<br>
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
<li><b>person_spreads_mixture</b> (frame 231, 7.708s): A person is holding a food processor containing meringue powder. The powder is visible and appears to be ready for mixing.</li>
<li><b>person_spreads_mixture</b> (frame 578, 19.286s): The person is using a whisk to mix egg whites in a bowl. The whisk is lifted out of the bowl, indicating mixing activity.</li>
<li><b>person_spreads_mixture</b> (frame 1156, 38.572s): The person is placing a silicone baking mat onto a baking tray. The mat is being adjusted to fit the tray.</li>
<li><b>person_spreads_mixture</b> (frame 1734, 57.858s): The person is breaking apart pieces of meringue on the baking mat. The meringue appears to be in a rough, uneven state.</li>
<li><b>person_puts_meringue_into_oven</b> (frame 2081, 69.436s): The person is placing a tray with meringue into the oven. The oven door is open, and the tray is being positioned on the rack.</li>
<li><b>person_spreads_mixture</b> (frame 1424, 47.514s): A person is holding a jar of meringue powder while other mixing equipment is visible on the counter. The jar is being prepared for use.</li>
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
<b>Video:</b> ct_Jp1U6Gb1DxM.mp4<br>
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
<li><b>person_pours_egg</b> (frame 231, 7.708s): A person is holding a container with meringue powder. The container is positioned above a mixing bowl.</li>
<li><b>person_spreads_mixture</b> (frame 578, 19.286s): The person is using a whisk to mix ingredients in a bowl. The bowl contains a light-colored mixture.</li>
<li><b>person_spreads_mixture</b> (frame 1156, 38.572s): The person is placing a silicone baking mat onto a baking tray. The mat is smooth and flat.</li>
<li><b>person_spreads_mixture</b> (frame 1734, 57.858s): The person is breaking apart pieces of a baked mixture on the baking mat. The pieces are uneven and crumbly.</li>
<li><b>person_pours_egg</b> (frame 2081, 69.436s): A person is holding a jar filled with a powdery substance. The jar is being lifted towards the camera.</li>
<li><b>person_spreads_mixture</b> (frame 1544, 51.518s): The camera is focused on a kitchen appliance with various attachments. The background shows a blurred countertop.</li>
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
<b>Video:</b> bf_P43_cam01_P43_scrambledegg.mp4<br>
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
<li><b>person_opens_butter_lid</b> (frame 205, 13.667s): A person is seen holding a butter container with one hand while using the other hand to open the lid. The kitchen setting is visible with various utensils and a window in the background.</li>
<li><b>person_opens_butter_lid</b> (frame 513, 34.2s): The person continues to manipulate the butter container, now fully opening the lid. The countertop is cluttered with cooking items, and the lighting suggests it is daytime.</li>
<li><b>person_opens_butter_lid</b> (frame 1026, 68.4s): The person is now holding the butter lid in one hand while the other hand is positioned near the butter container. The focus remains on the butter as the background shows a kitchen environment.</li>
<li><b>person_reaches_for_plate</b> (frame 1540, 102.667s): The person is reaching out towards a plate that is placed on the countertop. The kitchen remains visible, with the butter container still in the frame.</li>
<li><b>person_reaches_for_plate</b> (frame 1848, 123.2s): The person is now closer to the plate, extending their hand to grab it. The lighting has changed slightly, indicating a transition in time within the kitchen setting.</li>
<li><b>person_opens_butter_lid</b> (frame 1072, 71.467s): The person is still engaged with the butter container, appearing to scoop out some butter. The kitchen&#x27;s layout is consistent, with various cooking items scattered around.</li>
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
<b>Video:</b> ct_RhuRUsQ6tzw.mp4<br>
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
<li><b>10% of video</b> (frame 372, 15.515s): A man is pouring a liquid from a metal container into a pitcher. A woman is watching him with a surprised expression.</li>
<li><b>25% of video</b> (frame 930, 38.789s): The man is speaking while gesturing with his hands, and the woman is stirring a blue mixture in the pitcher. Various bottles of alcohol are visible on the table.</li>
<li><b>50% of video</b> (frame 1860, 77.577s): The woman is pouring the blue mixture from the pitcher into small cups arranged on the table. The man is observing her actions closely.</li>
<li><b>75% of video</b> (frame 2791, 116.408s): The man is feeding a cupcake to the woman, who is smiling and looking at him. Several decorated cupcakes are placed on the table.</li>
<li><b>90% of video</b> (frame 3349, 139.681s): The man is animatedly talking while holding a cupcake, and the woman is smiling and looking at him. The table is still filled with cupcakes.</li>
<li><b>FOI midpoint</b> (frame 1847, 77.035s): The woman is pouring the blue mixture into the cups, with the man watching her. The pitcher is nearly empty, indicating the mixture is being used.</li>
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
<b>Video:</b> ct_mN3Tus1ellQ.mp4<br>
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
<li><b>10% of video</b> (frame 541, 18.051s): The person is standing at a counter with a bowl and a container of jello powder. They appear to be preparing to pour the jello powder into the bowl.</li>
<li><b>25% of video</b> (frame 1353, 45.145s): The person is holding a bottle, possibly of liquid, and is gesturing towards the bowl. The jello powder container is still visible on the counter.</li>
<li><b>50% of video</b> (frame 2706, 90.29s): The person is stirring the contents of the bowl with a spoon. The jello powder is already mixed in, indicating a previous action.</li>
<li><b>75% of video</b> (frame 4058, 135.402s): The person is in a kitchen, holding a tray that appears to contain jello. They are smiling and looking towards the camera.</li>
<li><b>90% of video</b> (frame 4870, 162.496s): Two individuals are seated at a table, engaged in an activity involving jello. One person is animatedly gesturing, while the other is focused on the table.</li>
<li><b>FOI midpoint</b> (frame 2714, 90.557s): The person is still stirring the bowl, with a focused expression. The surrounding area shows various kitchen items, emphasizing the cooking context.</li>
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
<b>Video:</b> ct_x-7J315MKY0.mp4<br>
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
<li><b>10% of video</b> (frame 455, 18.2s): A stack of bread slices is placed on a plate. The background shows a wooden surface.</li>
<li><b>25% of video</b> (frame 1137, 45.48s): Egg yolks are being poured into a clear container. The container is filled with liquid and sits on a surface.</li>
<li><b>50% of video</b> (frame 2274, 90.96s): A text overlay discusses meal prepping and recipes. The background features a plate of food and strawberries.</li>
<li><b>75% of video</b> (frame 3410, 136.4s): Slices of bread are arranged in a tray, showing a light yellow color. The bread appears to be prepared for cooking.</li>
<li><b>90% of video</b> (frame 4092, 163.68s): A close-up of fried bread sticks is displayed on a plate. Strawberries are visible in the background.</li>
<li><b>FOI midpoint</b> (frame 1824, 72.96s): Sugar is being poured into a clear container from a hand. The container is placed on a wooden surface.</li>
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
<b>Video:</b> ct_goqPhR4gW4Y.mp4<br>
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
<li><b>10% of video</b> (frame 581, 19.383s): A person is using a jack to lift a vehicle. The wheel is partially elevated off the ground.</li>
<li><b>25% of video</b> (frame 1452, 48.44s): The camera focuses on a flat tire resting on the ground. The tire appears to be damaged and is not inflated.</li>
<li><b>50% of video</b> (frame 2905, 96.914s): The camera shows the same flat tire from a different angle. The tire is still resting on the ground, showing no signs of movement.</li>
<li><b>75% of video</b> (frame 4358, 145.387s): A close-up view of the tire&#x27;s rim and tread is visible. There is dirt and debris around the tire.</li>
<li><b>90% of video</b> (frame 5229, 174.445s): The camera captures a person&#x27;s feet next to wooden blocks on the ground. The blocks are positioned near the flat tire.</li>
<li><b>FOI midpoint</b> (frame 2744, 91.543s): The flat tire is still in view, with wooden supports visible underneath. The tire remains stationary and deflated.</li>
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
<b>Video:</b> ct_Fsosc3B0Agw.mp4<br>
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
<li><b>10% of video</b> (frame 584, 19.521s): A wooden spoon is stirring a mixture in a large pot. The contents appear to be ground meat cooking.</li>
<li><b>25% of video</b> (frame 1460, 48.802s): The camera focuses on a pot filled with liquid, possibly broth or oil. Small particles are floating on the surface.</li>
<li><b>50% of video</b> (frame 2920, 97.603s): A close-up of a cooked item, possibly a piece of meat or bread, is shown. The surface appears golden and crispy.</li>
<li><b>75% of video</b> (frame 4380, 146.405s): A hand is adding chopped vegetables, including lettuce and tomatoes, into a taco shell. The shell is placed on a decorative plate.</li>
<li><b>90% of video</b> (frame 5256, 175.686s): A taco shell is filled with various toppings, including cheese and vegetables. The plate has a colorful design and is set on a table.</li>
<li><b>FOI midpoint</b> (frame 2445, 81.726s): A spoon is scooping a portion of a cooked item from a pot. The item appears to be a type of meat or sauce.</li>
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
<b>Video:</b> ct_S3TWfylBt08.mp4<br>
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
<li><b>10% of video</b> (frame 618, 20.6s): A person is holding a plate with a portion of food. The background shows various ingredients and utensils on a countertop.</li>
<li><b>25% of video</b> (frame 1544, 51.467s): The person is pouring a mixture onto the plate of food. The plate is filled with a base layer of food, and the countertop is cluttered with more ingredients.</li>
<li><b>50% of video</b> (frame 3088, 102.933s): The person is using a spoon to add a topping to the food on the plate. There are additional bowls of ingredients visible in the background.</li>
<li><b>75% of video</b> (frame 4632, 154.4s): The person is reaching for a container of a specific ingredient. The kitchen setting is visible with various items on the countertop.</li>
<li><b>90% of video</b> (frame 5558, 185.267s): The person is using a spoon to scoop out an ingredient from a container. The countertop is still cluttered with various food items.</li>
<li><b>FOI midpoint</b> (frame 4530, 151.0s): The person is holding a bag of cheese, indicating preparation for adding it to the dish. The kitchen environment is filled with cooking supplies.</li>
</ul>
</details>

