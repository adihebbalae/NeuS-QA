# Working notes for Claude Code

This is Adi's fork of NeuS-QA, being adapted for the CVPR 2026 TimeLogic Challenge.

## Read these first (in this order)

1. `.cursor/rules/project-context.md` — scope, deadline (T-12 days from 2026-05-19), target outcome, leaderboard snapshot.
2. `.cursor/rules/setup.md` — bootstrap already done on this host (`ece-859525`), paths, env, what to skip.
3. `.cursor/rules/repo-plan.md` — file-by-file edit plan, what's been done, what's pending.
4. `.cursor/rules/workflow.md` — operating rules (tmux for long tasks, model selection, branching, commit style, sync).
5. `sessions/INDEX.md` — one-line summary of every prior working day; read the most recent log file in full before starting work.

## Operating rules

- **Long-running commands (> 5–10 min) go in `tmux`, then stop polling.** State "Task started in tmux session `<name>`. Please ping me when it completes." Keep doing non-conflicting work; end the turn cleanly if there is none. See `.cursor/rules/workflow.md`.
- **Working branch is `timelogic-adapt`**, not `main`.
- **Default OpenAI model is `gpt-5.4-mini` for dev**, `gpt-5.4` for val/test runs. PI's recc.
- **Single source of truth is this fork.** Cursor on the server, Claude in chat (laptop), and you (Claude Code on the server) all read `.cursor/rules/`. Push after any edit; the other side pulls.

## What NOT to commit

- `.env` / API keys
- Anything under `outputs/`, `models/`, `checkpoints/`, `*.log`, `.venv/` (covered by `.gitignore`)
- Anything under `/mnt/Data/ah66742/timelogic/...` (that lives outside the repo on purpose)

## Where things live

- Code: `nsvqa/`, `scripts/` in this repo
- Strategy / status: `.cursor/rules/`
- Daily logs / history: `sessions/`
- Dataset + outputs (not in repo): `/mnt/Data/ah66742/timelogic/`
- Upstream TimeLogic clone (not in repo): `/home/ah66742/TimeLogic-Specs/upstream/`
- Python env (not in repo): `.venv/` in this repo, managed by `uv` (Python 3.12)

## Update protocol

If you change any file under `.cursor/rules/` or `sessions/`, commit and push before ending the turn so the laptop side can pull. Don't bundle context-doc edits with code edits in the same commit.
