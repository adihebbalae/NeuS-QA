# NeuS-QA Storyboard — What Really Happens

*Working doc, not a deck. The deck is built only after the clip/question analysis below.*

---

## The thesis: human understanding is the moat

- We're ~30 points below #1 (48 vs 81) and still can't say *why*. We have symptoms — NSVS silent on 73% of rows, PULS unfaithful on a third, Storm stopping at first satisfaction — all measured in aggregate. A symptom is not a cause.
- Code is now free; Claude writes it. **Human understanding of the data is the scarce thing**, and it's our edge over labs that just scale models. Don't trust the score — inspect the data by hand. Well-understood data beats raw commercial scale.
- So the next artifact is not more corpus statistics. It is a small set of questions we understand *completely*.

## The experiment: one video, five questions, easy → hard

- Hold the **video fixed**, vary only **question difficulty**. That makes the question the single variable — any failure is attributable, not confounded by which clip.
- Author 5 questions up the complexity ladder: a one-glance "what is the person doing?" through a 3-event "always before / until" chain.
- **The easy questions carry the weight.** A miss on a question a human answers instantly is the cleanest possible evidence something is broken — no complexity to hide behind. (All correct is also a finding: the failures are genuinely the hard cases.)
- Run each through the pipeline and **trace every stage against the answer we already know**: what PULS emitted → whether NSVS cropped, and to where → what the VLM saw and said → what vanilla VLM said.
- *This questions × stage-outcome grid is the "taxonomy"* — organized cases, each labeled with what happened and where it broke.

## Choosing the video + questions without ground truth

- The design **dissolves the GT problem**: by authoring questions on a video we annotate frame-by-frame, *we are the ground truth.* Selection becomes authoring — no mining 3,000 unlabeled rows.
- Pick the video for **action density + length in the retrieval band**: a 1–3 min cooking clip has many discrete, ordered actions, so one video can instantiate most of the 16 operators. `ct_x-7J315MKY0` (flip-bread, 182s, a known win) is a candidate; a richer-action cooking clip may beat it.
- Grade difficulty GT-free, reusing the trick that found ill-posed questions:
  - **Cross-model agreement** — several VLMs agree → easy/unambiguous; they split → genuinely hard. (Doubles as the mini-MoE baseline.)
  - **CoT self-consistency** — flaky across reruns → ill-posed → drop. (The same detector, repurposed from "filter junk" to "rank difficulty.")
  - **Benchmark complexity-level tag** as the a-priori difficulty axis.

## Evidence at the PULS stage: all 16 operators

- One reference asset: the **16 TimeLogic operators, 2–3 examples each, with the real PULS text → spec output beside them.** Shows exactly where the operator survives translation and where it collapses (e.g. "always co-occur" → sometimes `&`, sometimes `U`, sometimes dropped).
- This replaces the abstract "operator collapse" claim with the raw translation anyone can read.

## Micro-experiments (each pre-registered with a hypothesis plot)

For each: specify **input → output → deliverable**, and mock the expected result up front (Minkyu-style), so we commit to what we expect before we see it.

1. **Plain-English re-query** — strip the formal phrasing. *Hyp:* spec stabilizes, short-clip answers improve → the phrasing, not perception, was hurting.
2. **YOLO + VLM grounding** — detections (labels + boxes) into the prompt. *Hyp:* short-clip accuracy rises, hallucinations fall → grounding was the bottleneck.
3. **Mini-MoE vote** — 2–3 VLMs, like #1. *Hyp:* approaches #1's behavior at a fraction of the compute → the gap is perception/ensembling, not logic.

## The strategic question this gates

- #1 scored 81% by brute-force MoE — heavy compute, no temporal logic. The question that matters: **can we match it without that compute** — e.g. swap Storm/PRISM for an LLM code generator (English → checkable code over labeled frames)?
- **We do not commit to that rewrite until the experiments say whether the failure is the spec, the grounding, or the perception.** If grounding (exp 2) closes the gap, Storm was never the problem.

## Dropped / deferred

- **Benchmark-quality / ill-posed narrative** — bounds the absolute score, not the 30-pt gap; reads as an excuse. Parked.
- **Formal LTL notation** in the main deck — plain English; the 16-operator table is the only place specs appear.
- **Accuracy-vs-length plot** — needs organizer GT (`accuracy_by_length.csv` accuracy columns are null). Hypothesis-plot version now; real one when GT lands.

## Deliverables

1. One-video / five-question **taxonomy deck** (the per-question panels).
2. **16-operator PULS reference** (text → spec, 2–3 examples each).
3. **Hypothesis plots** for the three experiments (input/output/deliverable specified).
