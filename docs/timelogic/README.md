# TimeLogic challenge (CVPR 2026) — fork documentation

**Status: closed** (EvalAI deadline 2026-05-31). This fork adapted [NeuS-QA](https://github.com/UTAustin-SwarmLab/NeuS-QA) for [TimeLogic](https://eval.ai/web/challenges/challenge-page/2690/overview).

## Start here

| Doc | Purpose |
| --- | --- |
| [`RESULTS.md`](../../RESULTS.md) | Scores, submission table, closure summary |
| [`TAINTED_SUBMISSIONS.md`](TAINTED_SUBMISSIONS.md) | Runs that must not be cited or uploaded |
| [`FOI_FIX_DIAGNOSTIC.md`](FOI_FIX_DIAGNOSTIC.md) | Target-ID / FOI ordering bug case study |
| [`sessions/INDEX.md`](../../sessions/INDEX.md) | Day-by-day work log |
| [`.cursor/rules/project-context.md`](../../.cursor/rules/project-context.md) | Challenge brief + final outcomes |

## Final scores

| Phase | Score | Submission |
| --- | ---: | --- |
| Val (best) | **53.35** | Sub #5B — `sub5b_paper_faithful_3fps_fix2` |
| Test (official) | **47.97** | Sub #7b — `submission_sub7b.json` |
| Test (local, not uploaded) | — | Sub #9 PULS v2 — `submission_sub9_pulsv2_test.json` |

Run artifacts live on the server at `/mnt/Data/ah66742/timelogic/outputs/` (not in git).

## Repo layout (after cleanup)

```
NeuS-QA/
├── nsvqa/              # Pipeline code (loaders, PULS, NSVS, VQA)
├── scripts/            # Active runners + builders (see scripts/README.md)
├── scripts/archive/    # One-off / superseded scripts (challenge-era)
├── diagnostics/        # Kept analysis summaries (see diagnostics/README.md)
├── submissions/        # EvalAI JSON copies + MANIFEST.json
├── sessions/           # Daily journals (2026-05-19 … 2026-05-31)
├── docs/timelogic/     # This folder
└── .cursor/rules/      # Agent context (project-context, workflow, setup)
```

## Diagnostics

Headline findings: [`diagnostics/sub5b_failure_audit_v3/FINDINGS.md`](../../diagnostics/sub5b_failure_audit_v3/FINDINGS.md).  
Dropped experiment (GPT-5.2 NSVS swap): [`archive/diagnostic-3-dropped.md`](archive/diagnostic-3-dropped.md).
