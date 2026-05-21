# Next-days plan — TimeLogic submissions, May 20 → May 31

Strategic ops doc for the back half of the challenge. Read alongside `project-context.md` (target outcome, levers, leaderboards) and `repo-plan.md` (file-by-file edit map).

**Where this lives**: `.cursor/rules/next-days-plan.md` in `adihebbalae/NeuS-QA` fork. Auto-loaded by Cursor + Claude Code. Laptop owns updates (same convention as `project-context.md`).

Last updated: 2026-05-20 evening (after Sub #2 result + diagnostic).

---

## TL;DR — current state (read this first)

- **Sub #1 (Config 0, CPU-only, full-video VLM + PULS hint)**: 50.5% on val ✅
- **Sub #2 (NSVS pipeline, NeuS-QA-flavored, gpt-5.2 vision on FOI frames)**: 48.75% on val ⚠️ (LOWER than Sub #1 by 1.75)
- **Sub #3a (FOI-quality proxy routing, 1188 from Sub #1)**: submitted, awaiting score
- **Sub #3b (bf+mc+>60s bucket routing, 367 from Sub #1)**: submitted, awaiting score
- **Disagreement diagnostic**: Sub #1 vs Sub #2 agree on 77.4%, disagree on 22.6% (452 questions). Sub #1's aggregate +35 net advantage implies ~244 vs ~208 only under the "one correct per disagreement" assumption; individual winners are not known without hidden labels.
- **Oracle routing ceiling**: ~60-61% (best-case if we could perfectly pick which pipeline to trust per question). Realistic ceiling with heuristic routing: 52-55%.
- **Honest read**: NSVS as currently implemented is net-negative on TimeLogic. The path to 57%+ goes through routing + ensemble + possibly enabling target_identification α/β extension. Probability of hitting 57% on test by May 31: ~30-40%. Mid-pack (45-55% test) is the more likely outcome.

## target_identification verification (resolved 2026-05-20 evening)

**target_identification DID run** in Sub #2. All 1983/1983 processed entries have `step_status.target_identification = "ok"` and ~3966 LLM history logs exist for the calls. Padding patterns: α ∈ {−10, −3, 0}s (most common −10 on 884 rows), β ∈ {0, +3, +10}s (most common 0 on 932 rows, +10 on 536). Top templates: `[start_time - 10, end_time]` (810), `[start_time, end_time + 10]` (494), `[start_time - 3, end_time + 3]` (347).

**Implication**: Sub #2 IS paper-faithful (includes α/β extension and Storm model checking). The 1.75-pt underperformance is therefore not explained by "we ablated a critical paper component." This sharpens the tech report claim:

> Paper-faithful NeuS-QA (with α/β extension and Storm checking) scores 48.75% on TimeLogic val; an ablated baseline that uses PULS specs only as a text hint to a global-clip VLM scores 50.5%. NSVS's interval retrieval is therefore net-negative on this benchmark, contradicting the paper's +10% claim on LongVideoBench.

That's a real negative result, not a methodology gap. Likely cause is no longer "missing α/β"; more likely candidates:
- PULS proposition grounding mismatch (per VLTL-Bench — overnight diagnostic will tell)
- Storm interval quality on TimeLogic's specific 16 operators (especially Until/Since/While)
- Frame-level VLM noise on noisy real-world clips (esp. agqa, breakfast)

The "enable α/β as a silver bullet" hypothesis is dead. Remaining real interventions: routing (Sub #3a/3b in flight), tiebreaker ensemble (Sub #4 building overnight), Storm-P gated routing (Sub #6 once logged), spatial hybrid retrieval (Sub #7 if routing plateaus).

---

## Where we are right now (status snapshot)

**Big jump since the 2026-05-19 evening commit**: levers C and D are done, Submission #1 (`baseline_cpu_v01`) scored 50.5 on EvalAI val, and Submission #2 (`nsvs_sub2_v2`) scored 48.75. Current best is still the CPU/API full-video baseline.

- ✅ **Lever D**: 6 TimeLogic-specific few-shot examples added to `nsvqa/puls/prompts.py`. smoke_v5 (20Q) ran with 0 errors — fixed both the "always after" negation bug and the earlier `always_before` KeyError.
- ✅ **Lever C**: custom answerer at `nsvqa/vqa/answer_timelogic.py` handling both MC and bool. Driver scripts: `scripts/answer_entries.py`, `scripts/build_submission.py`, `scripts/run_baseline_cpu.py`.
- ✅ **smoke_v6**: answerer-only 20Q smoke on smoke_v5 entries. Done.
- ✅ **Submission #1 / `baseline_cpu_v01` complete** — EvalAI val **AvgAcc 50.5**. Full 2000-question JSON at `/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json`.
  - PULS 2000/2000 ok; answers 1983/2000 ok (17 missing ct_* videos defaulted to `"Yes"` — they're absent from the official zip)
  - 154.8 min wall time, exit 0
  - MC roughly balanced; bool Yes 44% / No 56% — not collapsed to a single answer
- ✅ **Lever B smoke**: `smoke_v8_8b_reuse` completed 20/20 NSVS with 10/20 non-empty `frames_of_interest`.
- ✅ **Sub #2 / `nsvs_sub2_v2` complete**: 8 InternVL2-8B shards, merged 1983 videos, 1161 non-empty `frames_of_interest`, gpt-5.2 answerer, EvalAI val **48.75** (**-1.75 vs Sub #1**).
- **Submissions used**: 1/50 today val · 0/100 today test · 1/800 total val · 0/1000 total test.
- **Days to deadline**: 11 calendar days (today is May 20; deadline May 31 16:59 PST).

### What `baseline_cpu_v01` actually is (read carefully — it's not the paper pipeline)

```
Question ──► PULS (gpt-5.2) ──► propositions + TL spec
                                       │
                                       ▼ (passed as HINT only — not used for retrieval)
Full video ──► sample 8 frames evenly ──► VQA (gpt-5.2 vision, with PULS hint) ──► answer
```

What's **missing** vs. paper NeuS-QA: no NSVS, no InternVL proposition detection, no Storm model checking, no interval retrieval, no temporal extension. The VLM sees the whole clip, not the cropped-to-φ-satisfying segment.

Why this is a smart first sub anyway:
- bypasses Levers B + E entirely (no GPU device-map or sharding work needed)
- gets a leaderboard number tomorrow morning, not in 4 days
- isolates "does PULS hint help" from "does NSVS interval retrieval help" — if `baseline_cpu_v01` already scores high, NSVS may add less than the paper suggests for these operators
- API-only spend (~$30 estimated), no GPU cluster time

The score from this submission is the **strategic pivot point** for the rest of the plan — see "Decision point" below.

## The compute mix — how PULS / API / GPU / CPU combine

The NeuS-QA pipeline is a fixed five-stage pipeline. The four compute classes are mapped to stages — **you choose the *model* at each stage, not the stage order**. The "combinations" we tune are: which API model for PULS, which VLM on GPU for proposition detection, which backend (API vs local GPU) for VQA, and how many GPUs we shard across.

### Stage → compute mapping

| # | Stage | What it does | Compute | Bottleneck | Notes |
|---|---|---|---|---|---|
| 1 | **PULS (LQ2TL)** | NL question → propositions + temporal-logic spec φ | **API** (OpenAI) | API latency (~0.5–1.5s) | One LLM call per question. Cheap. Cost is in dollars, not seconds. |
| 2 | **target_identification** | Predicts (α, β) — how far to extend the matched interval | **API** (OpenAI) | API latency (~1s) | Second LLM call per question. Same model as PULS by default. |
| 3a | **NSVS — proposition detection** | For each frame in the video, run the VLM on `Yes/No: does <prop> hold?` for each proposition | **GPU** (VLM) | GPU compute; this is THE hot path | InternVL2-8B is paper config; we're stuck on 2B until Lever B. Scales as `frames × propositions × VLM_latency`. |
| 3b | **NSVS — model checking** | Builds the Markov-chain video automaton A_V from frame labels, runs Storm to compute P[A_V ⊨ φ] | **CPU** (Stormpy / C++) | Trivial — ms to single seconds | Stormpy wheel works, no system Storm needed. |
| 4 | **postprocess (crop)** | ffmpeg-trims the video to the satisfying interval | **CPU** (ffmpeg) | Disk I/O + ffmpeg | Cheap. Optional — could skip and pass frame indices to VQA directly. |
| 5 | **VQA (downstream answerer)** | Answer the original question on the cropped video | **GPU** (local VLM) OR **API** (vision LLM) | Either GPU compute OR API latency/$$$ | This is the *other* big lever. Local Qwen2.5-VL is fast + free; gpt-5.2 with vision is stronger but $$$. |

### Inter-stage interaction (what depends on what)

```
Question ──► [1: PULS  API]──┐
                              ├──► spec φ + props
                              │
Question ──► [2: target_id API]──► (α, β)
                              │
Video frames ─► [3a: NSVS-VLM GPU]──┐
                                     ├──► [3b: NSVS-Storm CPU] ──► satisfying interval
                                     │
                                     └──► [4: ffmpeg CPU] ──► cropped V'
                                                                  │
Question + V' ──► [5: VQA GPU or API] ──► "A" | "B" | "C" | "D" | "Yes" | "No"
                                                                  │
                                                                  ▼
                                                       EvalAI submission JSON
```

Three things to notice:

1. **PULS and target_identification can run in parallel with NSVS-VLM warmup** — they don't read each other's output until NSVS starts. Tiny win, not on critical path.
2. **NSVS-VLM is sequential per-question** (each frame must be classified before Storm can score), but **questions are embarrassingly parallel across GPUs** — this is what `--total_splits` exploits (Lever E).
3. **VQA is the largest single quality lever and the cheapest to A/B test.** Same NSVS output, swap the answerer, resubmit. Plan multiple val submissions exploring this axis.

## Submission configurations (the matrix you asked for)

Each row is a self-contained "config" you can run end-to-end. Time/Q estimates assume the device-map fix (Lever B) is in and 8B loads. Wall-clock for full 2k val is rough — depends on video lengths.

| Config | PULS (API) | NSVS-VLM (GPU) | VQA (GPU or API) | GPUs | ~Time / Q | ~$ / Q | Expected score | When to use |
|---|---|---|---|---|---|---|---|---|
| **0 — CPU baseline (DONE)** | gpt-5.2 | **SKIPPED** (no NSVS) | gpt-5.2 vision, 8 frames of full clip, PULS-as-hint | **0 (API only)** | ~4.6s avg | $0.015 | TBD (uploading) | Submission #1 — already built as `baseline_cpu_v01`. Establishes "PULS hint + strong VLM" baseline. |
| **A — Cheap dev** | gpt-4o-mini | InternVL2-2B | gpt-4o-mini (vision) | 1 | ~5–10s | $0.002 | ~40% (host baseline tier) | Iteration: smoke runs, prompt sweeps, debugging |
| **B — Paper baseline** | gpt-4o-mini | InternVL2-8B | Qwen2.5-VL-7B (local) | 1 (8B fits on 1 A5000 once Lever B is in) | ~30–60s | $0.001 | ~50–55% | First *real* NeuS-QA GPU submission |
| **C — API answerer on NSVS clip** | gpt-4o-mini | InternVL2-8B | gpt-5.2 (vision, medium reasoning) | 1 | ~25s + API | $0.015 | ~55–60% | Test "stronger answer on NSVS-cropped clip vs. on full clip" — i.e., does interval retrieval beat Config 0? |
| **D — Strong specs + strong answer** | gpt-5.2 (medium reasoning) | InternVL2-8B | gpt-5.2 (vision, medium) | 1 | ~30s + API | $0.04 | ~58–62% | After we see whether PULS quality is the bottleneck |
| **E — Premium (winning bet)** | gpt-5.2 (high reasoning) | InternVL2.5-8B | gpt-5.2 (high reasoning) + o3 tiebreaker on disagreements | 4–8 sharded | ~15s wallclock | $0.08 | ~62–66% | Final test submission(s); aim for #1 |
| **F — Production-fast** | gpt-4o-mini | InternVL2-8B | Qwen2.5-VL-7B (local) | 8 sharded (Lever E) | ~3–8s wallclock | $0.001 | ~50–55% | Once we have headroom: cheap, fast, run many configs in a day |

**Important read of Config 0**: it answers a different scientific question than the paper. Paper claim: "interval retrieval (NSVS) → stronger downstream answer." Config 0 asks: "if we just hand the VLM the full clip + a PULS hint, how close can we get?" The delta between Config 0 score and Config B/C score *is* the empirical value of NSVS on TimeLogic. That delta will be the headline finding in our tech report regardless of which way it cuts.

### Budget math (full 2k val · full 3k test)

| Config | Val (2000Q) | Test (3000Q) |
|---|---|---|
| 0 — CPU baseline | $30 · 0 GPU · 155 min (actual) | $45 · 0 GPU · ~4hr |
| A — Cheap dev | $4 · 1 GPU 3–5hr | n/a (don't burn test on this) |
| B — Paper baseline | $2 · 1 GPU 16–33hr → use F instead | $3 · 8 GPU 2–7hr |
| C — API answerer on NSVS clip | $30 · 1 GPU 14hr | $45 · 8 GPU 2hr + API |
| D — Strong specs + strong answer | $80 · 1 GPU 16hr | $120 · 8 GPU 3hr |
| **E — Premium** | $160 · 8 GPU 8hr | $240 · 8 GPU 12hr |
| F — Production-fast | $2 · 8 GPU 2–4hr | $3 · 8 GPU 3–6hr |

Total estimated spend if we run ~4 val passes (mix of 0/C/D/F) + 5 test passes (mix of D/E): roughly **$500–$800 of OpenAI** + ~80 GPU-hours. Sandeep already green-lit aggressive spend. Log per session under `## Compute footprint`.

## The 11-day plan (revised after baseline_cpu_v01 complete)

Phase 1 of the original plan is **already done** — submission file is built. Critical path is now: upload Config 0 → read the score → decide where NSVS sits on the priority list → build the GPU pipeline submission accordingly.

### Phase 1 — Close the loop (Days 1–3, May 20–22) ✅ MOSTLY DONE

- ✅ **Lever C** — custom MC + bool answerer at `nsvqa/vqa/answer_timelogic.py`
- ✅ **Lever D** — 6 TimeLogic few-shots in `puls/prompts.py`; smoke_v5 ran clean
- ✅ **EvalAI postprocess** — `scripts/build_submission.py` produces valid 2000-entry JSON
- ✅ **Re-smoke 20Q** — smoke_v5 (PULS+NSVS) + smoke_v6 (answerer-only) done
- ✅ **Submission file built** — `baseline_cpu_v01/submission.json` ready
- ⏳ **Levers B + E still pending** — moved to Phase 2 (they're for Submission #2, the GPU pipeline)

### Phase 1.5 — Upload + decide (Day 1, May 20 TODAY)

This is the new day-1 ask. The strategic question is: does Config 0 already perform well enough that NSVS is a marginal improvement, or is interval retrieval doing meaningful work?

**Day 1 — Wed May 20 (TODAY) — Upload, score, decide**
- 🎯 **Upload `baseline_cpu_v01/submission.json` to EvalAI val phase.** Uses 1/50 daily val budget. Submission #1.
- 🎯 Wait for score (usually <1 hr).
- 🎯 **Decision point — based on val score**:
  - **Score ≥ 60%**: We're already near the val leaderboard top (team0001 64.80, cola 64.40). Config 0 surprised us → invest the rest of the week in scaling this same approach (gpt-5.2 high-reasoning, ensemble, frame-sampling tuning). De-prioritize NSVS / Lever B.
  - **Score 50–60%**: In the mid-pack of the val leaderboard. NSVS interval retrieval *might* close the gap. Run Submission #2 (NSVS+GPU pipeline) to find out. Keep both tracks alive.
  - **Score 40–50%**: Beats the host baseline (43.15) but won't win. NSVS is probably load-bearing. Prioritize Lever B and Submission #2.
  - **Score < 40%**: Below host baseline. Plumbing bug — wrong question_id mapping, choice extraction is off, MC↔letter conversion broken. Debug before doing anything else.
- 🎯 **Per-mode breakdown** of val score (MC vs bool) — EvalAI doesn't expose this per-mode, but our own dump of `baseline_cpu_v01/per_entry/` lets us see which `mode` got which answer. Cross-reference once we have the overall score.
- 🎯 In parallel: start Lever B work on the server (server-side agent task) so we're not idle while EvalAI scores.
- If time: file an issue on `Swetha5/TimeLogic` about the 17 missing `ct_*` videos — they're absent from the official zip. Don't block the submission on it.

### Phase 2 — GPU pipeline + first NSVS submission (Days 2–4, May 21–23)

Goal: get the *actual* paper pipeline running and produce Submission #2, then compare it to Config 0.

**Day 2 — Thu May 21 — Fix Lever B**
- 🎯 **Lever B: InternVL2-8B device-map** — grep the actual module names in `transformers` InternVL2 implementation; fix `assign_device_map` and `split_model` in `nsvqa/nsvs/vlm/internvl.py`. Validate it loads + the un-mapped layers warning goes away.
- 🎯 20Q smoke with InternVL2-8B on the smoke_v5 entries → confirm prop-detection quality jump vs. 2B.
- 🎯 Begin Lever E (sharding) scaffolding in parallel.
- 🎯 If Lever B drags: fall back to InternVL2-2B for Submission #2 (accept ~3–5 point accuracy hit) and don't lose another day.

**Day 3 — Fri May 22 — Parallelize**
- 🎯 **Lever E: Parallel sharding** — verify `--total_splits N` partitions work, no GPU collisions, output files merge correctly. Test on 200Q across 4 GPUs.
- 🎯 200-Q val NSVS pass (Config B) → get a wall-clock estimate before committing 2000-Q runs.
- 🎯 **Download test set** (`test_videos.zip` + `timelogic_test_data.json`) so it's staged when we need it. Background download.

**Day 4 — Sat May 23 — Submission #2: first full NSVS val**
- 🎯 **Full 2000-Q val run, Config B** (paper baseline + Lever D prompts) on 8 GPUs sharded. Expect ~4 hr.
- 🎯 Submit to EvalAI val phase → **Submission #2**.
- 🎯 **Compare Config 0 (Sub #1) vs. Config B (Sub #2)** — the headline experiment.
- 🎯 Per-operator breakdown using `operator_guess` from the loader. Find the worst 3 categories.

### Phase 3 — Ablation sweep (Days 5–6, May 24–25)

Goal: figure out which axis (PULS quality, NSVS interval, VQA strength) is doing the work. Each ablation = one val submission.

**Day 5 — Sun May 24 — Ablate VQA + PULS**
- 🎯 **Val sub #3: Config C** (paper baseline but VQA = gpt-5.2 on NSVS-cropped clip). Isolates "stronger answer on cropped clip vs. full clip".
- 🎯 **Val sub #4: Config D** (PULS = gpt-5.2 + VQA = gpt-5.2). Isolates "stronger specs" axis.
- 🎯 Compare deltas across Sub #1 (Config 0), #2 (Config B), #3 (Config C), #4 (Config D). Update `repo-plan.md` and `results.md` with which lever moved the needle.
- 🎯 Start fixing the worst per-operator buckets via targeted few-shots in PULS.

**Day 6 — Mon May 25 — Threshold tuning + test prep**
- 🎯 Sweep τ (satisfaction threshold) and γ (smoothing) — run 3 short val passes (200Q each) varying just these. Pick the best, run a full val with the best.
- 🎯 Confirm test data is unzipped + integrity-checked.
- 🎯 Lock in "best val config so far" for first test submission tomorrow.
- 🎯 Begin scaffolding the tech report — Overleaf CVPR template, copy methodology from AAAI-26 NeuS-QA paper, leave numbers blank.

### Phase 4 — Test phase entry (Day 7, May 26)

**Day 7 — Tue May 26 — First test submission**
- 🎯 **First TEST submission** with best val-tuned config (must be public for prize eligibility — set the flag in EvalAI).
- 🎯 Continue val tuning (operator-specific prompts, α/β extension sweeps).
- 🎯 Log everything into the report's `results.md` table as raw data.

### Phase 5 — Push for the win (Days 8–11, May 27–30)

Goal: pull the test score above ~57% (current #1: anmspro 56.80). Keep the report drafting alongside.

**Day 8 — Wed May 27 — Operator-specific tuning**
- 🎯 Targeted few-shot examples for the bottom-3 operators (likely Until/Since/While). One val sub per change.
- 🎯 Try **ensemble**: run Config B + Config D in parallel, vote on disagreements with o3 as tiebreaker. Expensive but high-signal.
- 🎯 Second test submission with best config.

**Day 9 — Thu May 28 — Lock in best, start polishing report**
- 🎯 Promote winning config from val ablations → test. Third test submission.
- 🎯 Begin polishing report prose. By end of day: 60% drafted.
- 🎯 Save ~150 val submissions and ~6 test submissions in reserve for final-day surprises.

**Day 10 — Fri May 29 — Final tuning passes**
- 🎯 2–3 more test submissions exploring last-mile gains (e.g., majority-vote ensemble of 3 configs).
- 🎯 Report 80% drafted. Per-operator accuracy table populated. Compute-footprint paragraph populated.

**Day 11 — Sat May 30 — Lock-in day**
- 🎯 **Final test submission** with our best config — verify it's set to **public** in EvalAI (prize requirement).
- 🎯 Report 100% drafted. Two passes of proofreading. Compile final PDF in CVPR template.
- 🎯 **Buffer day** — assume something will break.

### Phase 6 — Submit (Day 12, May 31)

**Day 12 — Sun May 31 — Submit by 16:59 PST**
- 🎯 Morning: re-verify final test submission is public + matches the report's numbers exactly.
- 🎯 Submit report PDF.
- 🎯 Final session log entry; harvest resume lines + slide-deck retrospective.

## Submissions ledger (fill in as we go)

| # | Date | Phase | Config | Score | Notes |
|---|---|---|---|---|---|
| 1 | 2026-05-20 | val | **0 — CPU baseline** (`baseline_cpu_v01`) | **50.5** | Full 2k. PULS gpt-5.2 + 8-frame gpt-5.2 vision on full clip. No NSVS. Floor for later submissions. |
| 2 | 2026-05-20 | val | B-ish — InternVL2-8B NSVS + gpt-5.2 VQA (`nsvs_sub2_v2`) | **48.75** | 1983 videos merged; 1161 non-empty FOI; underperformed Sub #1 by 1.75. |
| 3a | 2026-05-20 | val | **Routing — FOI-quality proxy** (`sub3a_foi_proxy`) | **49.0** | Did not beat Sub #1 (50.5). |
| 3b | 2026-05-20 | val | **Routing — bf+mc+>60s carve-out** (`sub3b_bf_mc_gt60`) | **48.95** | Did not beat Sub #1. |
| 4 | 2026-05-21 | val | **Tiebreaker ensemble** — gpt-5.2 judge on 452 disagreements | **50.2** | -0.3 vs Sub #1; judge could not reliably beat baseline on disagreements. |
| 5B | 2026-05-21 | val | **Paper-faithful @ 3fps** — gpt-4o PULS, InternVL2-8B, ffmpeg crop, Qwen2.5-VL-7B | TBD | tmux `sub5b_paper_faithful_3fps`. 1fps partial at `sub5b_paper_faithful/` abandoned. |
| 6 | 2026-05-22 | val | + Storm-P logging → confidence-gated routing (Variant A) | TBD | Requires code change in `nsvqa/nsvs/nsvs.py` + re-run NSVS. Replaces val-overfit bucket rule. |
| 7 | 2026-05-23 | val | + spatial hybrid (NSVS frames + global padding) | TBD | If Subs 3-6 plateau before 55%, escalate to spatial hybrid. |
| 8 | 2026-05-25 | val | best stack (routing + α/β + ensemble) | TBD | Locks in val champion config. |
| 9 | 2026-05-26 | **test** | best val config | TBD | First test submission. |
| 10 | 2026-05-27 | test | + operator-specific prompts on worst buckets | TBD | |
| 11 | 2026-05-28 | test | + multi-pass self-consistency on hard ones | TBD | |
| 12 | 2026-05-29 | test | refinement of #11 | TBD | |
| 13 | 2026-05-30 | **test (FINAL)** | E — Premium | TBD | **Public — prize eligible** |

## Sub #2 post-mortem (2026-05-20 evening)

**Result**: Sub #2 (NSVS pipeline, InternVL2-8B propositions + gpt-5.2 vision answerer on FOI frames) scored 48.75% — 1.75 pts below Sub #1's 50.5%.

**What was actually run vs. paper**: differences from literal paper NeuS-QA pipeline:

| Paper NeuS-QA | What Sub #2 ran |
|---|---|
| Local downstream VLM (Qwen2.5-VL / LLaVA-OneVision) | gpt-5.2 vision (API) — likely STRONGER |
| ffmpeg-crop to V' | FOI frame sampling (equivalent for API answerer) |
| target_identification α/β temporal extension | **UNCLEAR — may have been skipped** ⚠️ |
| Storm satisfaction probability per entry | **Not logged** — prevents Variant A confidence routing |

Sub #2 is NeuS-QA-flavored, not paper-faithful. The VLM swap likely helps; the missing α/β extension likely hurts; the missing Storm-P log limits our ability to route principally.

**Diagnostic findings**:

- 41.45% of Sub #2 entries had `-1` FOI (empty satisfying interval); pipeline fell back to ~Sub #1 behavior for those
- Non-`-1` FOI disagreement rate (Sub #1 vs Sub #2): 27.56%
- `-1` FOI disagreement rate: 15.52% (the 12-pt gap = pure NSVS effect when it fires)
- Sub #1 vs Sub #2 agreement: 77.4% (1548 questions); disagreement: 22.6% (452 questions)
- Among 452 disagreements: Sub #1 net advantage = +35, which implies ~244 vs ~208 only if every disagreement has exactly one correct answer. This is aggregate score math, not row-level ground truth.
- **Oracle routing ceiling** (perfectly picking between Sub #1 and Sub #2 per question): ~60.9%
- **Realistic ceiling with heuristic routing**: 52-55% (captures 30-50% of oracle gap)

**Worst disagreement bucket**: `bf + mc + >60s` — 34.6% disagreement rate on 367 questions. NSVS most disruptive on long Breakfast-style multiple-choice videos.

**Likely root causes** (ranked, updated 2026-05-20 evening after target_id verification):
1. **PULS proposition grounding** — abstract propositions InternVL2 can't score reliably (per VLTL-Bench); overnight diagnostic should quantify this
2. **Storm interval quality on TimeLogic operators** — Storm was tuned on LongVideoBench's 4 operators (T3E/E3E/T3O/O3O); TimeLogic has 16 (Until, Since, While, etc.) where Storm intervals may diverge from what the question requires
3. **Short-clip degeneracy** — ~50% of val clips are <30s, median 3.16s; NSVS can't meaningfully crop those (already partially handled — `-1` FOI fallback)
4. **Residual causal precursor loss** — even with α=−10s padding, on long videos (>60s) the cropped clip still loses 80%+ of context; this matches the bf+mc+>60s being the worst bucket
5. ~~target_identification skipped~~ — **REFUTED 2026-05-20 evening; it did run with reasonable α/β values**

## Sub #3 routing experiment design

Built two submissions to test different hypotheses:

- **Sub #3a (FOI-quality proxy)**: routes 1188 to Sub #1, 812 to Sub #2. Trust NSVS only when FOI is non-empty AND meaningfully cropped.
- **Sub #3b (bucket rule)**: routes 367 to Sub #1 (`bf + mc + >60s`), 1633 to Sub #2. Narrow carve-out.

Submitted both 2026-05-20 evening. Expected outcomes:

- Sub #3b: 50.5-52.5% if NSVS is net-positive outside the carve-out
- Sub #3a: 50-53% — wider net catches more "NSVS hurts" cases but also discards some "NSVS helps" cases

**Known limitation**: both rules were derived from val disagreements → mild val-overfitting risk. Sub #3b's bucket features (source, mode, duration) are causal-sounding and should transfer to test; Sub #3a's FOI-quality proxy is more empirical. For test, prefer Variant A (Storm-P gate) once Storm-P logging is added (Sub #6 territory).

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Sub #3a and #3b both fail to beat 50.5 | Medium | Means heuristic routing alone isn't enough; escalate to tiebreaker ensemble (Sub #4) and target_identification re-run. |
| target_identification was skipped (likely) and re-running it doesn't help | Low-Medium | If α/β extension doesn't recover the gap, the causal-precursor story is weaker than we thought; pivot to spatial hybrid retrieval. |
| Sub #1 score is below host baseline (<43.15) | Low — resolved (50.5) | N/A |
| Sub #1 score is 60+ → NSVS may be redundant | Low — didn't happen | N/A |
| Lever B (8B device-map) drags past Day 2 | Medium | Fall back to InternVL2-2B for Submission #2. Accept ~3–5 point accuracy hit rather than lose a day. |
| Lever E parallel sharding has subtle bugs | Medium | Test on 200Q first. Worst case: sequential 8B on 1 GPU is 16–33hr — fits in Day 4 if Day 2's 8B is ready. |
| OpenAI quota / rate-limit on gpt-5.2 | Low-Medium | Config 0 already validated 2000 sequential calls. Headroom check for parallel calls on Day 5. Fall back to local Qwen for VQA if hit. |
| 17 missing `ct_*` videos | Confirmed | Defaulted to `"Yes"` — best guess for bool (matches Yes 44/56 distribution). Flag organizers via GitHub issue. Don't block submit. |
| Score plateaus 45-55%, can't crack 57% | Medium-High (this is the hard part) | Pivot to ensemble + per-operator targeted prompts. Use Phase 5 entirely on this. |
| Last-day infrastructure failure | Low | Day 11 is buffer; final submission locked Day 10 evening. |

## Open questions to resolve

- **GPT-5.4 access**: PI said it was being sorted on a separate key. Status check on day 2.
- **Workshop attendance / authorship**: from `project-context.md` open questions — should ask Minkyu before day 7.
- **API budget cap**: estimate above is $500–$800. Confirm with Minkyu before running Config D/E at scale.
- **Tech report ownership**: confirm solo draft + Minkyu/Harsh review is OK.

## Day-of-week pacing (because it matters)

May 20 (Wed) → 21 (Thu) → 22 (Fri) → 23 (**Sat**) → 24 (**Sun**) → 25 (Mon) → 26 (Tue) → 27 (Wed) → 28 (Thu) → 29 (Fri) → 30 (**Sat**) → 31 (**Sun, DEADLINE 16:59 PST**).

Heavy-compute / long-attended runs should land **Sat May 23 and Sun May 24** (first full val sweep) since those are weekend-of-the-most-uninterrupted-time. Buffer day Sat May 30 should remain pure buffer.
