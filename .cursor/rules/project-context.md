# TimeLogic Challenge — NeuS-QA Submission

Personal working brief. Source of truth for this project — re-read at the top of every session.
Last updated: 2026-05-19.

**Where this lives**: `.cursor/rules/project-context.md` in `adihebbalae/NeuS-QA` fork. Cursor and Claude Code both auto-load this on every agent invocation. Edit on the laptop clone, push, then `git pull` on the server. (Soft convention: laptop owns this file; the server owns `setup.md`.)

## The ask in one paragraph

Adapt the existing NeuS-QA pipeline to run on the TimeLogic Video-QA benchmark and submit to EvalAI challenge #2690 (CVPR 2026 VidLLMs Workshop). **Hard deadline: 2026-05-31 16:59 PST** — 12 days from today. Two deliverables: (1) public test-phase submission of predicted answers in EvalAI's JSON format, and (2) a CVPR-format technical report (PDF), reviewed by organizers, with winning reports published on the workshop page and arXiv. This is a systems-dev task, not research — the pipeline is already written and benchmarked on LongVideoBench / CinePile. Adapt loaders → run → post-process → submit → write report.

## Why this matters

Warm-up project for the AFRL-funded multi-agent / multi-camera video search work. After this ships, I roll onto extending NeuS-QA to multi-agent video search and co-author the next paper. The workshop is part of CVPR 2026, June 4 in Denver, with a $6,000+ prize pool across workshop challenges. Leaderboard placement plus a clean technical report keep the broader project credible with AFRL — Sandeep needs publications/demos to defend the funding.

## Strategic posture (decided 2026-05-19)

- **Target outcome: win the prize.** Need ~57%+ on test phase (current #1 is anmspro at 56.80; val top is 64.80). Plan for aggressive tuning: multi-backbone, per-operator prompt tuning, threshold sweeps. Accept higher compute spend.
- **Test phase: submit early and often.** Test phase is already open (since May 18). Once the smoke run works on val, also push to test to confirm scoring works there. Use both leaderboards as signal. Budget is 1000 total test submissions — plenty of room. Final submission on May 31 must be public.
- **Tech report: draft in parallel, rough and unpolished.** Treat it as a running document of structured pure data — log every config, ablation, and number as it lands. Don't polish prose until the last 2–3 days. Avoids both last-week scramble and rewriting churn.

## People

- **Minkyu Choi** — 3rd-year PhD, day-to-day point of contact. Assigning the work, paying for Cursor (reimburses via Venmo, owe him the receipt). One of the NeuS-QA authors.
- **Harsh Goel** — co-author of NeuS-QA. Created the shared slide deck I update daily for progress.
- **Sandeep Chinchali** — PI / lab director. Cares strongly about staying within AFRL proposal scope. Likely interacts via group calls only.
- **Other co-authors**: Sahil Shah, S P Sharan, Mustafa Munir. Philip / OB / SP attend deepfake-related calls.

## Methodology — NeuS-QA in one diagram

```
NL question ──► LQ2TL (LLM, few-shot)
                  │
                  ├──► atomic propositions P = {p1, p2, ...}
                  └──► temporal-logic spec φ (□, ◇, X, U operators)

Video (frames) ─► VLM proposition detector (InternVL2-8B, ~1-3 fps)
                       │
                       ▼
                Video automaton A_V  (states = frames,
                                      labels = detected props,
                                      transitions = Markov chain)
                       │
                       ▼
                STORM / Stormpy probabilistic model checker
                       │
                       ▼
                P[A_V ⊨ φ] ──► smoothed ──► satisfying interval [t_start, t_end]
                       │
                       ▼
                Temporal extension (α, β) ──► trim video to V′
                       │
                       ▼
                Downstream VLM (Qwen2.5-VL / GPT-5.4 / Aria / LLaVA-OneVision) answers q on V′
```

Key implementation knobs:

- Proposition extractor uses Yes/No logits, calibrated on a held-out set.
- Frame step κ controls window granularity (default ~3 fps).
- Satisfaction threshold τ governs when a segment "matches" the spec.
- Temporal extension (α, β) pads the matched interval forward/backward — important for "before/after" queries.
- The pipeline is **training-free and plug-and-play** — no fine-tuning. Iteration is fast: change prompts, thresholds, or backbone and re-run.

Paper headline: ~10% absolute accuracy improvement over plain VLM prompting on LongVideoBench T3E/E3E/T3O/O3O, and even outperforms human-annotated GT clips when both are fed to the same VLM (59% vs 52%).

## Challenge specifics

- **Workshop**: 2nd VidLLMs Workshop @ CVPR 2026, Denver, June 4, 2026. Room 3A-3D.
- **Challenge runs**: Apr 14 → May 31, 2026, 16:59 PST.
- **Prize pool**: $6,000+ across workshop challenges.

**Phases**

- **Validation Phase** (Apr 14 → May 31): 2k QA pairs. 50/day · 400/month · 800 total · 3 concurrent. Open now.
- **Test Phase** (May 18 → May 31): 3k QA pairs incl. hidden test questions. 100/day · 500/month · 1000 total · 3 concurrent. **Open now**. Submission must be public to be prize-eligible.

**Submission format** — JSON file, one entry per question:

- Multiple-choice: `{"question_id": "1", "answer_choice": "D"}`
- Boolean: `{"question_id": "2", "answer_choice": "Yes"}` or `"No"`
- Metric: Overall Accuracy.

**Rules** (key)

- Test/val data **must not** be used for training (supervised or self-supervised). Other datasets OK. NeuS-QA is training-free, so this is automatic.
- No human labelling on test videos.
- No model-size restriction.
- Public submission required in test phase to be prize-eligible.
- Technical report in CVPR format (PDF) required, reviewed by organizers. Winners get published on workshop site + arXiv.

**Current leaderboards (snapshot 2026-05-19)**

- **Val (dev split)**: team0001 64.80 · cola 64.40 · Cadence 63.45 · anmspro 62.20 · iLearn_Time 54.10 · Host baseline (Qwen3VL) 43.15 · FueledByCoffee 22.05.
- **Test split**: anmspro 56.80 · Host baseline (QwenVL) 39.97 · others 0.00 (likely broken submissions).
- Read: clearing the host baseline is easy; winning needs ~57%+ on test. Top val scores cluster 62–65% — realistic ceiling.

## Dataset — TimeLogic / TLQA

- Source paper: "TimeLogic: A Temporal Logic Benchmark for Video QA", arXiv 2501.07214 (Jan 2025).
- **Challenge dataset repo** (this is the authoritative source for the challenge, NOT the lab repo): https://github.com/Swetha5/TimeLogic (branch `challenge`, data under `/data/`).
- Challenge splits: **val 2k QA** + **test 3k QA**, covering 16 temporal operators (Before, After, Until, Since, ordering, etc.). Mix of multiple-choice and Yes/No.
- Video downloads:
  - Val: `https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/val_videos.zip` — **23.4 GB**, staged to `/mnt/Data/ah66742/timelogic/raw/`
  - Test: `https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/test_videos.zip` — not yet downloaded
- Test annotations JSON: `https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/timelogic_test_data.json` — not yet downloaded
- **Status (2026-05-19 end of day)**: val annotations and videos downloaded + integrity-checked + unzipped to `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos/`. Test split not yet pulled.
- **Actual val schema** (per `Swetha5/TimeLogic@challenge/data/val/timelogic_val_data.json`): list of dicts with only `question_id`, `video_id`, `mode` (`"mc"` or `"bool"`), `question`. **No `candidates`, no ground-truth field, no operator label.** MC choices are embedded inside the question string (`"... Is it Option A: ..., Option B: ..., Option C: ..., Option D: ..."`). Counts: 1200 MC + 800 bool. Videos pull from 4 source datasets: `agqa`, `bf` (Breakfast), `ct`, `star` — 500 questions each, 940 unique video files across the 2000 questions. The loader at `nsvqa/datamanager/timelogic.py` extracts MC options via regex (100% match rate) and synthesizes `["Yes","No"]` candidates for bool.

## Codebases

- **My fork**: https://github.com/adihebbalae/NeuS-QA — clone on server at `/home/ah66742/NeuS-QA`. Working branch: `timelogic-adapt`. Single source of truth for both code and project context (this file).
- **NeuS-QA upstream**: https://github.com/UTAustin-SwarmLab/NeuS-QA (Python, last updated Apr 27 2026).
- **TimeLogic challenge code/data**: https://github.com/Swetha5/TimeLogic (Swetha is one of the organizers). Server clone at `/home/ah66742/TimeLogic-Specs/upstream/` (held out of the fork to keep upstream changes traceable).
- **Lab GitHub org**: https://github.com/UTAustin-SwarmLab (useful neighbours: `Neuro-Symbolic-Video-Search-Temporal-Logic`, `NeuS-V`, `nsvs`, `Multi-Camera`).
- **Project page**: https://utaustin-swarmlab.github.io/NeuS-QA/.

## Cross-machine sync architecture (2026-05-19)

- The fork is the bridge between two agent surfaces:
  - **Laptop / Claude (this chat)** — strategy, doc edits, planning. Edits `.cursor/rules/project-context.md` and `.cursor/rules/repo-plan.md`; pushes.
  - **Server / Cursor agent + Claude Code** — code execution, smokes, runs. Edits `.cursor/rules/setup.md` (host facts), `nsvqa/...`, `scripts/...`, `sessions/...`; pushes.
- Cursor reads everything in `.cursor/rules/*.md` and adds it to the agent's system context every invocation. Claude Code reads the same files plus `CLAUDE.md` at repo root.
- Daily flow: each side pulls before starting a session and pushes after touching context. `git pull --rebase` catches the common cases; for the rare conflict on `repo-plan.md` we resolve manually.
- The local `_SwarmLab/` folder on the laptop is **scratch only** — anything I want either agent to see goes through the fork.

## Stakeholder loop / cadence

- **Daily**: 15-min standup + push updates to the shared slide deck.
- **Slide deck** (created): keep terse and visual — what shipped, what broke, what's blocked. Pull straight from the day's session log under `sessions/YYYY-MM-DD.md` → `## For the daily slide`.
- **Cursor**: paid; receipt sent → Venmo reimbursement from Minkyu pending.

### Session logging convention

- One markdown file per working day at `sessions/YYYY-MM-DD.md`, first-person intern-style journal. Lives in the fork (NOT under `.cursor/rules/` so the per-session size doesn't tax every prompt).
- Template + workflow in `sessions/README.md`; `sessions/new.sh` creates today's file from the template.
- Every entry has fixed sections so we can grep later: `## What shipped`, `## What broke / what I learned`, `## Numbers`, `## Tomorrow / open questions`, `## For the daily slide`, `## Resume-line drafts`, `## Compute footprint`, `## Local changes today`.
- `sessions/INDEX.md` keeps a one-line summary per day so any agent can quickly see "what's been done" without loading every log file.
- At end of project: harvest `## Resume-line drafts` and `## What shipped` across all sessions into the technical report, the slide deck retrospective, and the resume.

### Compute mindfulness (no one else on cluster, but track anyway)

- Sandeep / lab-admin have green-lit using as much compute as we need on `ece-859525`, but we still log what we used per session so we can answer "how much did this cost?" later and avoid runaway runs.
- Log per session: peak GB on each GPU we touched, wall-clock GPU-time, OpenAI $, disk added (on `/mnt/Data` and `/home`), EvalAI submissions used (val N/50, test N/100).
- Defaults: single-GPU dev iteration; only fan out to multiple GPUs via `--total_splits` for full val/test runs.
- Long-running runs (>10 min) always go in `tmux` with logs to `<output_dir>/run.log`; the agent detaches and waits for a manual ping. See `.cursor/rules/workflow.md`.

## Working environment

- **Compute**: SSH'd Linux server (`ece-859525`) with 8× RTX A5000. Cursor for editing, Claude in this chat for thinking/planning, Claude Code as a possible overnight agent.
- **Storage**: local `/mnt/Data/ah66742/timelogic/` for dataset + outputs (NAS not yet mounted, lab-admin OK'd staying local).
- **Setup details**: `.cursor/rules/setup.md` — actual bootstrap as it exists on this server (env, paths, what was skipped).
- **Repo plan**: `.cursor/rules/repo-plan.md` — file-by-file map of where TimeLogic plugs in (plus a "verified on-disk" addendum and smoke-run report).
- **Operating rules**: `.cursor/rules/workflow.md` — tmux for long tasks, model selection, branching, commit style.
- **Daily session logs**: `sessions/YYYY-MM-DD.md` — intern-journal of what shipped, what broke, what to do tomorrow, compute used. See `sessions/README.md` and `sessions/INDEX.md`.

## Next actions (checklist)

Setup
- [x] Cursor subscription paid (receipt → Minkyu for Venmo)
- [x] Shared slide deck bookmarked
- [x] Forked `UTAustin-SwarmLab/NeuS-QA` (origin: `adihebbalae/NeuS-QA`)
- [x] Registered on EvalAI for challenge #2690, created team
- [x] Cloned NeuS-QA + ran `uv sync` (Python 3.12 venv at `NeuS-QA/.venv`; verified prebuilt `stormpy==1.11.3` wheel works without a custom Storm build)
- [x] Compute confirmed: 8× RTX A5000 (24 GB each) on host `ece-859525`
- [x] OpenAI key present in `~/.env`
- [x] Cloned TimeLogic val annotations (`Swetha5/TimeLogic@challenge`)
- [x] Val videos zip download to `/mnt/Data/ah66742/timelogic/raw/` (23.4 GB)
- [x] GitHub auth set up; `timelogic-adapt` branch pushed
- [x] `.cursor/rules/` + `sessions/` migrated into the fork (single source of truth)
- [ ] Download test annotations + test videos zip — defer until val pipeline runs end-to-end
- [ ] Get `/nas` CIFS share mounted on `ece-859525` by lab-admin (currently unwritable); not blocking, but needed to share artifacts with the rest of the lab
- [x] PI confirmed: use GPT-5.4 as the production model. **Constraint (2026-05-19 evening)**: lab OpenAI key does NOT have 5.4/5.5 access. PI says use 5.2 (released Dec 2025, closest available) — pending PI to grant 5.4 access on a different key. Current tiering: gpt-4o-mini for dev iteration, gpt-5.2 for val/test, gpt-5 as backup. See `.cursor/rules/workflow.md`.

Pipeline (highest priority — start today)
- [x] Clone NeuS-QA fork, install deps; Stormpy/Storm install gotcha resolved (prebuilt wheel works)
- [x] Inspect `Swetha5/TimeLogic` data format; write `TimeLogic` loader yielding `(video_path, question, answer_choices, question_id, question_type)` — note the MC vs Yes/No split
- [ ] Map TimeLogic's 16 temporal operators onto NeuS-QA's LQ2TL prompt templates — likely need new few-shot examples per operator family **(lever D — in progress)**
- [ ] Confirm/extend NeuS-QA's downstream VLM prompt to handle Yes/No outputs (paper benchmarks were MC-only) **(lever C)**
- [x] Smoke test on 5 mixed val questions end-to-end; sanity-check that answers are sensible
- [ ] Re-smoke on 20 questions after lever D **(lever A)**
- [ ] Fix `internvl.py` device-map so InternVL2-8B can shard across GPUs **(lever B)**
- [ ] Write EvalAI post-processor: pipeline output → JSON in `{"question_id": ..., "answer_choice": ...}` format

Validation phase submissions (already open — 800-submission budget, use it)
- [ ] First full val run (2k Q) with paper-best config: InternVL2-8B propositions + GPT-5.4 downstream
- [ ] Submit to val phase (private) to verify scoring pipeline works end-to-end
- [ ] Iterate: tune LQ2TL prompts for TimeLogic operators, tune τ and (α, β) per operator family, swap downstream VLM

Test phase submissions (already open since May 18 — 1000-submission budget)
- [ ] Plan ≥2 days buffer before May 31 for final test-phase submissions
- [ ] First test-phase submission with best val-tuned config
- [ ] Final submission must be public for prize eligibility

Technical report (CVPR format PDF, due May 31) — keep rough/unpolished, log data as it lands
- [ ] Spin up Overleaf doc in CVPR LaTeX template, lift methodology paragraphs from the AAAI-26 NeuS-QA paper as a starting scaffold
- [ ] Maintain a `results.md` (or LaTeX table) inside the report — every config run, every accuracy number, every ablation, dumped raw
- [ ] Log per-operator accuracy breakdowns as they come in (16 operators → 16 rows)
- [ ] Polish into prose only in final 2–3 days (~May 28–31)

## Open questions

1. **Target ambition**: are we aiming to win ($6K, need ~57%+ test), top-3, or a credible mid-pack result? Drives how much I burn on tuning. (Working assumption: win.)
2. **Tech report ownership**: solo draft and Minkyu/Harsh review? Acceptable to lift methodology sections from the AAAI-26 NeuS-QA paper and adapt?
3. **API budget**: shared OpenAI key for GPT-5.4 / 5.5, or do I expense it? If expense, what's the cap?
4. **Authorship on the report**: how should I list authors / lab affiliation? Anything sensitive about arXiv-publishing if we win?
5. **Workshop attendance**: anyone going to Denver on June 4 to present? Travel-support deadline (Apr 30) is past.
6. **AFRL eligibility**: Sandeep was checking international-student eligibility. Doesn't block challenge entry but may affect prize claim — any update?

## Quick reference

- Challenge URL: https://eval.ai/web/challenges/challenge-page/2690/overview
- Workshop URL: https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/
- NeuS-QA paper (AAAI-26): https://ojs.aaai.org/index.php/AAAI/article/view/37834 — arXiv 2509.18041
- TimeLogic paper: https://arxiv.org/abs/2501.07214
- TimeLogic challenge repo: https://github.com/Swetha5/TimeLogic
- NeuS-QA upstream: https://github.com/UTAustin-SwarmLab/NeuS-QA
- My fork: https://github.com/adihebbalae/NeuS-QA
- Validation videos zip: https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/val_videos.zip
- Test videos zip: https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/test_videos.zip
- Test annotations JSON: https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/timelogic_test_data.json
- STORM model checker: https://www.stormchecker.org/
- Backbones used in paper: InternVL2-8B (propositions); Qwen2.5-VL-7B / GPT-4o / Aria / LLaVA-OneVision-7B (downstream).
