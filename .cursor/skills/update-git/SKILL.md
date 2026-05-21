---
name: update-git
description: Sync TimeLogic project work to GitHub. Use when the user says "update git", "sync git", "push updates", or asks to update session logs, references, results, and files that need to be synced.
disable-model-invocation: true
---

# Update Git

## Meaning

When the user says **"update git"**, do all project bookkeeping needed to make GitHub reflect the current state of work.

This means:

1. Update the daily session log in `sessions/YYYY-MM-DD.md`.
2. Update `sessions/INDEX.md` if the day's headline changed or a new day started.
3. Update `RESULTS.md` when there are new submissions, diagnostics, scores, artifacts, or strategic conclusions.
4. Update `.cursor/rules/` context files when future agents need the new fact automatically.
5. Add or update scripts/docs that make the result reproducible.
6. Commit and push the relevant repo changes to `origin` on the current working branch.

## Workflow

1. Check current repo state:

```bash
git status --short
git diff --stat
git log -3 --oneline
```

2. Identify what needs syncing:

- New scores or EvalAI outcomes -> `RESULTS.md`, daily session log, possibly `.cursor/rules/next-days-plan.md`.
- New generated submission path -> `RESULTS.md` and daily session log. Do not commit large output JSONs unless explicitly requested.
- New scripts -> commit the script and document the output path it produces.
- New operational lesson -> daily session log; `.cursor/rules/workflow.md` only if it should guide future agents.
- New strategy or project status -> `RESULTS.md` and `.cursor/rules/project-context.md` or `.cursor/rules/next-days-plan.md` when useful.

3. Make focused edits. Keep raw artifacts out of git unless the user explicitly asks.

4. Validate edited files:

- Use lints for changed code/docs when available.
- For generated submission JSONs, validate row count, unique IDs, answer format, and annotation order before documenting readiness.

5. Commit and push:

```bash
git add <relevant files>
git commit -m "$(cat <<'EOF'
<concise message>

EOF
)"
git push origin <current-branch>
git status --short
```

## Commit Style

Use concise messages matching the repo style:

- `docs(results): log Sub #4 tiebreaker result`
- `feat(scripts): add routed submission builder`
- `docs(sessions): update daily progress log`

## Do Not Commit

- API keys or `.env`
- Large output files under `/mnt/Data/...` or `/home/ah66742/timelogic-data/outputs/...`
- Model checkpoints, videos, logs, caches, or `.venv`
- Unrelated user changes unless they are part of the requested sync

## Final Response

Report:

- Commit hash and branch pushed
- Main files updated
- Any local artifact paths that were documented but not committed
- Anything intentionally left uncommitted
