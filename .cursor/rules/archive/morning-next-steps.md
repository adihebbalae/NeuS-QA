# Morning next steps — 2026-05-21

Written by tonight-Adi for sleepy-Adi. Read this first; ignore everything else until you've worked through it.

Today's date: 2026-05-21. Deadline: 2026-05-31 16:59 PST (10 days).

## 30-second status

- Sub #1 (CPU baseline, no NSVS): **50.5%** ✅
- Sub #2 (paper-faithful NSVS — confirmed includes α/β extension): **48.75%** ⚠️
- Sub #3a (FOI-quality routing) + Sub #3b (bucket routing): submitted last night, scores should be back
- Overnight jobs: Sub #4 tiebreaker, PULS grounding diagnostic — flag files at `outputs/sub4_tiebreaker/DONE` and `outputs/_diagnostics/puls_grounding/DONE`

## Step 1 — Drink coffee. Then check four numbers (5 min)

```bash
# Did overnight jobs finish?
test -f /mnt/Data/ah66742/timelogic/outputs/sub4_tiebreaker/DONE && echo SUB4_READY
test -f /mnt/Data/ah66742/timelogic/outputs/_diagnostics/puls_grounding/DONE && echo PULS_DIAG_READY

# What did EvalAI say?
# → log into eval.ai, check val phase scores for sub3a, sub3b
```

Numbers to write down:

- Sub #3a score: ____
- Sub #3b score: ____
- Sub #4 finished overnight: yes / no
- PULS diag finished overnight: yes / no

## Step 2 — Branch based on Sub #3 results (5 min thinking, no code yet)

**Read this once carefully before doing anything.**

The decision tree below picks your next experiment. Sub #1 baseline = 50.5.

### Branch A — Sub #3b > 51% (bucket routing works)

The `bf+mc+>60s` carve-out hypothesis is validated. NSVS is genuinely helpful outside that bucket.

→ Next: submit Sub #4 (tiebreaker), expect it to do even better. Then in afternoon, focus on widening the carve-out (maybe `+ ct + >60s`?) and re-running.

### Branch B — Sub #3a > Sub #3b AND > 51% (broader routing works)

NSVS confidence is the right signal, bucket rule is too narrow. Storm-P gating (Variant A) would be even better.

→ Next: prioritize the **NSVS re-instrumentation** to log Storm probabilities. Then re-run NSVS once with Storm-P logging on. Estimate: 2hr code change + 4hr re-run = afternoon-evening job.

### Branch C — Both Sub #3a and Sub #3b ≤ 50.5 (routing doesn't help)

The routing hypothesis is weaker than expected. NSVS is bad in places we can't predict from observable features alone.

→ Next: submit Sub #4 (tiebreaker ensemble) — this is the heaviest intervention. If even gpt-5.2-as-judge can't recover, the gap to top is structural, not routing-fixable. Then pivot to **spatial hybrid** (NSVS frames + global padding to VLM).

### Branch D — Sub #3a or #3b broke (submission format error, EvalAI errored)

Plumbing issue, not science.

→ Validate the submission JSON locally first. Re-submit fixed version. Burns one daily slot, no biggie (only 2/50 used so far today).

## Step 3 — Update PI/daily slide (5 min)

Pull from `## For the daily slide` in `sessions/2026-05-20.md`. Add today's numbers. One bullet on Sub #3 result + next move. Don't over-explain in the slide — the trend matters more than the absolute number.

## Step 4 — Execute the chosen branch (rest of the morning)

Whichever branch above, do it. Don't try to do all branches in parallel; pick one based on the data.

Reminder: **don't submit anything to test phase yet** (still 0/1000). Only when val score ≥55% does test get touched.

## Important context you may have forgotten while sleeping

- **target_identification DID run in Sub #2**. The α/β extension was active (median α=−10s, β=+10s). So the "Sub #2 lost because it stripped causal context" theory is partially refuted — the crop wasn't strict, and it still underperformed. This means there's no easy fix from "enable α/β." It was already enabled.

- **The tech report headline is now**: "Paper-faithful NeuS-QA (with α/β extension) underperforms a global-VLM-with-PULS-hint baseline by 1.75pts on TimeLogic, contradicting the paper's +10% claim on LongVideoBench." This is a real negative result on a sister benchmark — that's a publishable finding regardless of leaderboard placement.

- **Don't be over-specific in Cursor prompts on implementation details.** Be strict on discipline (STOP RULE, output paths, no polling) but loose on script structure / function names / prompt templates. The earlier polling violation wasn't a specificity problem — it was a discipline problem.

- **Server-side Cursor has been making commits to other docs** (project-context.md, repo-plan.md, sessions/2026-05-20.md, RESULTS.md). Before doing any work, `git pull --rebase origin timelogic-adapt` on laptop AND server. Resolve conflicts in `repo-plan.md` carefully — both sides edit it.

## What NOT to do today

- ❌ Submit to test phase. Hold the budget.
- ❌ Run paper-faithful 200Q baseline with local Qwen. We don't need it anymore — Sub #2 *is* paper-faithful (target_identification confirmed). The diagnostic value is gone.
- ❌ Chase the "competitive intelligence" team-identification rabbit hole from the Gemini research doc.
- ❌ Add more major features before submitting Sub #4. One change at a time.

## Asks to escalate to Minkyu / PI today (Slack / standup)

- API budget cap for the week? Tiebreaker + Storm-P re-run + future ensembles = ~$200-400 if all run.
- Authorship + reviewer cycle plan for the tech report (CVPR template).
- Update Sandeep on the negative result framing — it's actually a stronger contribution than "we won the leaderboard" since it implies TimeLogic's operators behave differently from LongVideoBench.

## End-of-morning checkpoint

Should be done with Step 4 around lunch. Update `sessions/2026-05-21.md` with today's `## What shipped` and `## Numbers`.

Afternoon plan branches further based on what Step 4 produced — don't plan it in advance, decide based on the morning's score deltas.
