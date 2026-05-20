# Workflow rules — TimeLogic / NeuS-QA fork

Operating rules that apply to every agent session (Cursor on the server, Claude in chat, Claude Code overnight). Cursor auto-loads this file as system context. Keep it short and prescriptive.

Last updated: 2026-05-19.

## Long-running tasks (tmux rule)

If a requested command or script is expected to take longer than 5–10 minutes to execute (e.g. heavy model loads, large smokes, full-val/test runs, dataset downloads, video transcodes):

1. **Execute the command inside a new `tmux` session.** Use a descriptive session name (`smoke_v5`, `val_full_a`, `internvl8b_dl`).
2. **Detach from the session immediately.** Use `tmux new-session -d -s <name> "..."` so the agent never attaches in the first place.
3. **Do NOT poll or check the terminal output.**
4. **State**: `Task started in tmux session <name>. Please ping me when it completes.`
5. Then **stop polling that task**, but **keep doing non-conflicting work** in the current turn — drafting prompts, updating docs, prepping the next experiment. Anything that does not depend on the tmux task's output is fair game.
6. If there is no non-conflicting work to do, end the turn cleanly and wait for the user's ping.

Patterns for #5 (productive work while a tmux job runs):

- update `.cursor/rules/*` based on findings so far
- draft the next session log entry
- prepare the next command line / config file
- read code we haven't read yet
- write a small test or sanity script

Never (#5):

- run another tmux job that touches the same output directory
- modify a file the tmux job is reading or writing
- start a second GPU-heavy process on the same device

## Model selection (OpenAI)

PI's recommendation (2026-05-19): use **GPT-5.4** for production runs. **Constraint (confirmed 2026-05-19 evening)**: the lab OpenAI key from the ECCV submission does NOT have GPT-5.4 / 5.5 access. PI said "use 5 and 5.2 for now" while sorting out 5.4 access. Tiering within what's actually available:

| Use case | Model | Reason |
| --- | --- | --- |
| Dev iteration on PULS / target_identification | `gpt-4o-mini` | $0.15/$0.60 per 1M, cheapest with vision, fine for the structured-JSON PULS task |
| Smoke runs (≤ 50 entries) | `gpt-4o-mini` | Same |
| Val phase EvalAI submission | `gpt-5.2` | $1.75/$14 per 1M, 400K context, vision, configurable reasoning effort (none/low/medium/high/xhigh), released Dec 2025, "previous frontier model" per OpenAI |
| Test phase EvalAI submission (final) | `gpt-5.2` | Default; closest available to PI's gpt-5.4 pick |
| Backup if 5.2 doesn't help / regressions | `gpt-5` | Original GPT-5, older but still flagship-class |
| Once lab key gets 5.4 access | `gpt-5.4` then `gpt-5.4-mini` | Promote — check `--puls-model` default at that point |

Other available models on the lab key (not currently used): `gpt-5.2-codex` (coding-tuned, overkill for PULS), `o3` (reasoning, can be a tiebreaker on hard ones), `gpt-4`/`gpt-4-turbo`/`gpt-4o` (legacy, dropped — 5.2 strictly better at this point), `gpt-3.5-turbo` (too weak), Embeddings/Speech (not used), 14 UT-Austin fine-tuned `gpt-4o-mini` checkpoints from prior projects (not used).

When switching models for a run, log the model in the session entry under `## Numbers` so accuracy deltas can be attributed correctly.

**Methodology rule**: change one thing at a time. Don't change prompts AND model in the same smoke run if you want to isolate the effect. Lever D smoke (v5) used new prompts + the old `gpt-4o`; the next smoke that swaps to `gpt-4o-mini` (cheaper) or `gpt-5.2` (more capable) keeps prompts fixed so the model delta is isolated.

## Branching

- `main` — stable, matches what we'd PR upstream. Currently has only `b2a848b` (Python pin).
- `timelogic-adapt` — working branch. All TimeLogic-specific code lives here. Default branch for active work.
- Feature branches (`prompts-v2`, `vqa-bool`, etc.) — branch off `timelogic-adapt` only if a change is risky enough to want isolation. Merge back fast.

Never force-push `main` or `timelogic-adapt` unless the user explicitly asks.

## Commit message style

`type(scope): subject` on the first line, ≤ 72 chars. Optional body for the why. Examples:

```
fix(puls): substitute repeated propositions in TL specs

process_specification's substitution loop only ran when a proposition
appeared exactly once in the spec, so any prop reused later in the same
formula was left as an unquoted natural-language literal.
```

```
feat(scripts): add TimeLogic pipeline driver
```

```
docs(context): record cross-machine sync architecture
```

Types we use: `fix`, `feat`, `docs`, `chore`, `refactor`, `test`, `perf`. Scopes: `puls`, `nsvs`, `vqa`, `datamanager`, `scripts`, `context`, `setup`, `repo-plan`, `workflow`, `sessions`, `gitignore`.

## Cross-machine sync

- The fork is the source of truth for both code and project context.
- Each side `git pull --rebase` before starting a session.
- Each side pushes after touching any file under `.cursor/rules/`, `sessions/`, or `nsvqa/...`.
- Soft ownership convention to reduce conflicts:
  - **Laptop / Claude chat** owns `.cursor/rules/project-context.md` (strategy, planning)
  - **Server / Cursor agent** owns `.cursor/rules/setup.md` (host facts)
  - Both edit `.cursor/rules/repo-plan.md` and `sessions/*` (rebase carefully)

## Session-log discipline

- One file per working day at `sessions/YYYY-MM-DD.md` (see `sessions/README.md`).
- Update `sessions/INDEX.md` (one line per day) when starting a new day.
- Don't dump full logs into the session entry — reference the path on `/mnt/Data/ah66742/timelogic/outputs/...`.
- End every entry with `## Tomorrow / open questions` so the next morning is unblocked.

## What never goes in this repo

- `.env` / API keys
- Anything under `outputs/`, `models/`, `checkpoints/`, `*.log`, `.venv/` (covered by `.gitignore`)
- Anything under `/mnt/Data/ah66742/...` (that's NAS-staged, not the repo)
- Anything under `_SwarmLab/` on the laptop (scratch only)
