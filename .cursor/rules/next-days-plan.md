# Next-days plan — TimeLogic submissions, May 20 → May 31

Strategic ops doc for the back half of the challenge. Read alongside `project-context.md` (target outcome, levers, leaderboards) and `repo-plan.md` (file-by-file edit map).

**Where this lives**: `.cursor/rules/next-days-plan.md` in `adihebbalae/NeuS-QA` fork. Auto-loaded by Cursor + Claude Code. Laptop owns updates (same convention as `project-context.md`).

Last updated: 2026-05-20 (revised after morning sync — `baseline_cpu_v01` complete).

## Where we are right now (status snapshot)

**Big jump since the 2026-05-19 evening commit**: levers C and D are done, Submission #1 (`baseline_cpu_v01`) scored 50.5 on EvalAI val, and the NSVS/GPU path is now running as `nsvs_sub2_v2`.

- ✅ **Lever D**: 6 TimeLogic-specific few-shot examples added to `nsvqa/puls/prompts.py`. smoke_v5 (20Q) ran with 0 errors — fixed both the "always after" negation bug and the earlier `always_before` KeyError.
- ✅ **Lever C**: custom answerer at `nsvqa/vqa/answer_timelogic.py` handling both MC and bool. Driver scripts: `scripts/answer_entries.py`, `scripts/build_submission.py`, `scripts/run_baseline_cpu.py`.
- ✅ **smoke_v6**: answerer-only 20Q smoke on smoke_v5 entries. Done.
- ✅ **Submission #1 / `baseline_cpu_v01` complete** — EvalAI val **AvgAcc 50.5**. Full 2000-question JSON at `/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json`.
  - PULS 2000/2000 ok; answers 1983/2000 ok (17 missing ct_* videos defaulted to `"Yes"` — they're absent from the official zip)
  - 154.8 min wall time, exit 0
  - MC roughly balanced; bool Yes 44% / No 56% — not collapsed to a single answer
- ✅ **Lever B smoke**: `smoke_v8_8b_reuse` completed 20/20 NSVS with 10/20 non-empty `frames_of_interest`.
- ⏳ **Sub #2 in flight**: `nsvs_sub2_v2` runs 8 InternVL2-8B shards, then `sub2_finish_v2` merges + answers with gpt-5.2 on `frames_of_interest`.
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
| 2 | 2026-05-23 | val | B (full) — first NSVS pass | | Paper baseline + Lever D prompts. Compare to Sub #1. |
| 3 | 2026-05-24 | val | C — gpt-5.2 VQA on NSVS clip | | Tests "stronger answer on cropped clip" |
| 4 | 2026-05-24 | val | D — gpt-5.2 PULS + VQA | | Tests "stronger specs" |
| 5 | 2026-05-26 | val | best-tuned τ/γ | | Threshold sweep winner |
| 6 | 2026-05-26 | **test** | best val config | | First test submission |
| 7 | 2026-05-27 | test | + operator-specific prompts | | |
| 8 | 2026-05-28 | test | + ensemble + o3 tiebreaker | | |
| 9 | 2026-05-29 | test | best so far | | |
| 10 | 2026-05-30 | **test (FINAL)** | E — Premium | | **Public — prize eligible** |

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Sub #1 score is below host baseline (<43.15) | Low | Indicates plumbing bug (question_id mapping, choice extraction, MC↔letter). Catch on Day 1 and debug immediately. |
| Sub #1 score is 60+ → NSVS may be redundant | Medium | Good problem to have. Pivot from "build GPU pipeline" to "scale Config 0" — high-reasoning gpt-5.2, ensemble, more frames. Lever B becomes optional. |
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
